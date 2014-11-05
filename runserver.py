#!/usr/bin/python2
import socket
import threading
import random

#-------------------------------------------------------------------------
##########################################################################
#-------------------------------------------------------------------------

class c_thread(threading.Thread):
   def __init__(self, client, ip):
      threading.Thread.__init__(self)
      self._client = client
      self._ip = ip

   def run(self):
      try:
         self._rcvd = self._client.recv(1024)
         print self._rcvd
         self._client.send(serverchallenge(self._rcvd))

         self._action = self._client.recv(1024)
         if self._action[0] == 'r':
            self._client.send(register(self._action))

         elif self._action[0] == 'c' and c_thread.clientchallenge(self):
            if self._action[1] == 'q':
               emailr = self._client.recv(1024)
               self._client.send(request(emailr))
            elif self._action[1] == 'm':
               l = self._action.split(";")
               info = self._client.recv(1024)
               self._client.send(modify(l[1], info))

         self._client.close()
      except:
         self._client.close()
      
   def clientchallenge(self):
      l = self._action.split(";")
      exists, user = buscar(l[1]) # email
      if exists:
         info = user.split(";")
         x = random.randint(2, int(info[2]))
         fx = (x**3 + 2) % int(info[2])
         self._client.send(str(x))
         efxc = int(self._client.recv(1024))
         fxc = modExp(efxc, int(info[1]), int(info[2]))
         if fxc == fx:
            self._client.send("1:The user is valid.")
            return True
         else:
            self._client.send("0:The user is invalid.")
            return False
      else:
         self._client.send("0")
         return False

#-------------------------------------------------------------------------
##########################################################################
#-------------------------------------------------------------------------

def buscar(email):
   f = open("registro.dat", 'r')
   for line in f:
      user = line.split(";")
      if user[0] == email:
         return True, line
   return False, None

def register(option):
   #El primer campo de info corresponde a la opcion, el segundo al email,el tercero a e, el cuarto a la n y el quinto a la ip.
   info = option.split(";")
   exists, user = buscar(info[1])
   if not exists:
      print "Registering:", info[1:]
      f = open("registro.dat", 'a')
      f.write(option[2:] + '\n')
      f.close()
      return "Registered!"
   else:
      return "Failed. This email is not available."

def modify(email, info):
   print email, info
   f = open("datos.dat", 'r')
   archivo = f.readlines()
   lista = []
   for line in archivo:
      user = line.split(";")
      if user[0] != email:
         lista.append(user)
      else:
         lista.append(email+';'+info+'\n')
   f.close()
   f = open("datos.dat", 'w')
   f.write(lista)
   f.close()
   return "Modified"


def request(emailr):
   exists, info = buscar(emailr)
   if exists:
      return info
   else:
      return '0'

def modExp(a, b, n):
   res = 1
   pot = a % n
   while b > 0:
      if b % 2 == 1:
         res = (res * pot) % n
      b >>= 1
      pot = (pot * pot) % n
   return res

def serverchallenge(x):
   e = 670655
   d = 2097647
   n = 4560161
   fxs = (int(x)**2 + 25) % n
   efxs = modExp(fxs, d, n)
   return str(efxs)


#######################################################################
      
serversocket = socket.socket()
host = socket.gethostname()
port = 9000
serversocket.bind((host, port))

serversocket.listen(5)
while True:
   client, ip = serversocket.accept()
   print "Connection established", ip
   ct = c_thread(client, ip)
   ct.run()
