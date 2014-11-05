#!/usr/bin/python2
import socket
from random import randint
from sys import argv
from rsa import rsa
from os import mkdir
from os.path import exists

ayuda = """Options:
   -k Runs the RSA algorithm to create a Public Key and a Private Key.
   -r Register a user in the repository.
   -q Request someone's public key.
   -c Modify a public key in the repository.
   -e Encrypt a message (digital signature, receiver's public key).
   -d Decrypt a message.
   -m Convert a decrypted string to a readable message. You must get the string using this script. This option is used in -d.
   """
#-------------------------------------------------------------------------
# CLASE CLIENTE Socket ---------------------------------------------------

class client():
   def __init__(self):
      self._s = socket.socket() # Socket object
      self._host = socket.gethostname() #The server ip, localhost for testing
      self._port = 9000 # Defines the port

   def sconnect(self):
      self._s.connect((self._host, self._port)) # Tries to connect

   def ssendrecv(self, option): # Send a string and receive an answer
      self._s.send(option)
      self._received = self._s.recv(1024)
      print self._received
      return self._received

   def sclose(self):
      self._s.close() # Close the connection

#-------------------------------------------------------------------------
#-------------------------------------------------------------------------

def register():
   cl = client()
   cl.sconnect()
   if istheserver(cl):
      email = raw_input("Email:")
      if exists(email):
         f = open(email + "/id_rsa.pub", 'r')
         publickey = f.readline().split(";")
         e = publickey[0]
         n = publickey[1]
      else:
         e = raw_input("Public Key:\ne:")
         n = raw_input("n:")
      info = "r" + ";" + email + ";" + e + ";" + n
      result = cl.ssendrecv(info)
   cl.sclose()

def modify():
   cl = client()
   cl.sconnect()
   if istheserver(cl) and istheclient(cl, 'm'):
      e = raw_input("Enter e:")
      n = raw_input("Enter n:")
      info = e + ";" + n
      result = cl.ssendrecv(info)
      
def query():
   cl = client()
   cl.sconnect()
   if istheserver(cl) and istheclient(cl, 'q'):
      emailr = raw_input("Email requested:")
      user = cl.ssendrecv(emailr)
      if user[0] == '0':
         print "Email is not registered."
      else:
         saveuser(user)         
   else:
      print "Failed."
   cl.sclose()

def saveuser(user):
   info = user.split(";")
   if not exists('.' + info[0]):
      mkdir('.' + info[0])
   f = open('.' + info[0] + '/.id_rsa.pub', 'w')
   f.write(info[1] + ';' + info[2])
   f.close()

def encrypt():
   emails = raw_input("Enter your email >> ")
   try:
      f = open(emails + "/id_rsa", 'r')
      privatekeys = f.readline().split(";")
      ds = int(privatekeys[0])
      ns = int(privatekeys[1])
      f.close()
   except:
      ds = input("Enter your private key\nd:")
      ns = input("n:")

   emailr = raw_input("Enter the receiver email >> ")
   try:
      f = open("." + emailr + "/.id_rsa.pub", 'r')
      publickeyr = f.readline().split(";")
      er = int(publickeyr[0])
      nr = int(publickeyr[1])
      f.close()
   except:
      er = input("Enter the receiver public key\ne:")
      nr = input("n:")
      
   message = raw_input("Enter the message to send >> ")
   nmessage = ''
   for char in message:
      nmessage += str(ord(char)).zfill(3)
   encrypted = ''
   block = 3
   stringnumber = ''
   i = 0
   for char in nmessage:
      stringnumber += char
      i += 1
      if i == block:
         number = int(stringnumber)
         stringnumber = ''
         i = 0
         signature = modExp(number, ds, ns)
         encrypted += str(modExp(signature, er, nr)).zfill(8)
   try:
      number = int(stringnumber)
      signature = modExp(number, ds, ns)
      encrypted += str(modExp(signature, er, nr)).zfill(8)
   except:
      print 'Encrypted'
   print "Encrypted message:", encrypted

def decrypt(encrypted):
   emailr = raw_input("Enter your email >> ")
   try:
      f = open(emailr + "/id_rsa", 'r')
      privatekeyr = f.readline().split(";")
      dr = int(privatekeyr[0])
      nr = int(privatekeyr[1])
      f.close()
   except:
      dr = input("Enter your private key\nd:")
      nr = input("n:")

   emails = raw_input("Enter sender's email >> ")
   try:
      f = open("." + emails + "/.id_rsa.pub", 'r')
      publickeys = f.readline().split(";")
      es = int(publickeys[0])
      ns = int(publickeys[1])
      f.close()
   except:
      es = input("Enter sender's public key\ne:")
      ns = input("n:")
   decrypted = ''
   block = 8 # the number of characters in the encrypted string
   stringnumber = ''
   signature = ''
   i = 0
   try:
      for char in encrypted:
         stringnumber += char
         i += 1
         if i == block:
            number = int(stringnumber)
            stringnumber = ''
            i = 0
            signature = modExp(number, dr, nr)
            decrypted += str(modExp(signature, es, ns)).zfill(3)
      try:
         number = int(stringnumber)
         signature = modExp(number, dr, nr)
         decrypted += str(modExp(signature, es, ns)).zfill(3)
      except:
         print 'Decrypted'
      print "Decrypted:", decrypted
      message = getmessage(decrypted)
      return message
   except:
      return "Could not be decrypted"
   
def getmessage(decrypted): 
   # Converts a decrypted value to a readable message
   message = ''
   i = 0 
   block = 3
   caracter = ''
   for char in decrypted:
      caracter += char
      i += 1
      if i == block:
         i = 0
         message += chr(int(caracter))
         caracter = ''
   try:
      message += chr(int(caracter))
   except:
      'Decrypted'
   return message
      
def modExp(a, b, n): # Modular exponentiation
   res = 1
   pot = a % n
   while b > 0:
      if b % 2 == 1:
         res = (res * pot) % n
      b >>= 1
      pot = (pot * pot) % n
   return res

def istheserver(cl):
   e = 670655
   n = 4560161
   x = randint(2, n)
   efxs = int(cl.ssendrecv(str(x)))
   fxs = modExp(efxs, e, n) # Decrypt fxs
   fxc = (x**2 + 25) % n # f(x) Challenge
   print "Fx Server:", fxs
   print "Fx Client:", fxc
   if fxs == fxc: 
      print "This is the server."
      return True
   else:
      print "This is not the server."
      return False

def istheclient(cl, p):
   email = raw_input("Enter your email:")
   if not exists(email):
      print "First of all try 'client.py -k' option."
      return False
   else:
      f = open(email + '/id_rsa', 'r')
      privatekey = f.readline().split(";")
      d = int(privatekey[0])
      n = int(privatekey[1])
      x = int(cl.ssendrecv("c" + p + ";" + email))
      if x != 0: # If client exists
         fx = (x**3 + 2) % n # f(x) Challenge
         efx = modExp(fx, d, n) # Signature
         print efx
         isit = cl.ssendrecv(str(efx)) 
         if isit[0] == '1': # Si aprobo este cliente
            return True
         else: #Si no aprobo
            return False
      else:
         print "Email not registered."
         return False
   
try:
   option = argv[1]
except:
   option = None
   print ayuda

if option == "-h":
   print ayuda
elif option == "-k":
   email = raw_input("Your email: ")
   rsa(email)
elif option == "-r":
   register()
elif option == "-q":
   query()
elif option == "-e":
   encrypt()
elif option == "-d":
   text = raw_input("Ciphertext >> ")
   print decrypt(text)
elif option == "-m":
   decrypted = raw_input("Decrypted string >> ")
   getmessage(decrypted)
elif option == "-c":
   modify()
else:
   print "   Enter a valid option. -h displays the help.\n"
