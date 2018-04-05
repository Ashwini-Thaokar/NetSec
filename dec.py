#!/usr/bin/python3
import sys
import os
import pysodium
import socket
import base64
import struct
import binascii
import time
from req import Request

#UDP_IP = "127.0.0.1"
#UDP_PORT = 1337
#sock= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#sock.bind((UDP_IP, UDP_PORT))
keypair= pysodium.crypto_kx_keypair()

def getCert():
 f1= open(os.path.join(sys.path[0], "node.pub"), "r")
 cert=base64.b64decode(f1.read())
 f1.close()
 return cert

def getSecretKey(x):
 f2=open(os.path.join(sys.path[0], "node.sec"), "r")
 sec_key=base64.b64decode(f2.read())
 if x==0:
 #return encryption key
  secret_key=sec_key[4:36]
 else:
 #return signing key
  secret_key=sec_key[40:]
 f2.close()
 return secret_key

def generateQuery():
 cert= getCert() 
 hash=pysodium.crypto_generichash(cert, b'', 64)
 hash_len=(64).to_bytes(4, byteorder="big")
 query=(hash_len + hash)
 return query


def getStatus():
 query=generateQuery()
 query_sock= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
 query_sock.connect(("172.18.0.252", 3333))
 query_sock.send(query)
 status, address= query_sock.recvfrom(1024)
 #query_sock.close()
# print (status)
 return status

def getPropose(p):
 type_field= (0).to_bytes(1, byteorder='big')
 csp= (p).to_bytes(1, byteorder='big')
 #keypair= pysodium.crypto_kx_keypair()
 pk=keypair[0]
 pk_len= (len(pk)).to_bytes(4, byteorder='big')
 cert=getCert()
 status= getStatus()
 zero_vector= (0).to_bytes(64, byteorder='big')
 vector_len= (64).to_bytes(4, byteorder='big')
 s_k=getSecretKey(1)
 len_s_k=(len(s_k)).to_bytes(4, byteorder='big')
 message= type_field + csp + pk_len + pk + cert + status + vector_len + zero_vector
 sign=pysodium.crypto_sign_detached(message, s_k)
 sign_len= (len(sign)).to_bytes(4, byteorder='big')
 propose= type_field + csp + pk_len + pk + cert + status + sign_len + sign 
# print (propose)
 return propose

def getSocket():
 sock= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
 sock.bind(('', 1337))
 return sock

def getSocketResponse(message):
 sock=getSocket()
 addr=("172.18.0.252", 1337)
 sock.sendto(message, addr)
 resp= sock.recv(1024)
 return resp


def getCounterPropose():
 propose= getPropose(1)
 counter_propose= getSocketResponse(propose)
# print (counter_propose)
 return counter_propose

def getSessionKey(counter_propose):
 print (counter_propose)
 spk_len= int.from_bytes(counter_propose[2:6], byteorder= 'big')
 spk_int= int.from_bytes(counter_propose[6:(spk_len+6)], byteorder='big')
 spk= (spk_int).to_bytes(32, byteorder='big')
 q= pysodium.crypto_scalarmult_curve25519(keypair[1], spk)
 q_pk1_pk2= q+keypair[0]+spk
 session_key= pysodium.crypto_generichash(q_pk1_pk2, b'', 64)[:32]
 return session_key
 
def createAccept(counter_propose):
 csp= int.from_bytes(counter_propose[1:2], byteorder= 'big')
 print (csp)
 type_field=(1).to_bytes(1, byteorder='big')
 time_stamp= int(time.time())
 ts=time_stamp.to_bytes(8, byteorder='big')
 session_key= getSessionKey(counter_propose)
 if (csp==0):
  nonce_len=(8).to_bytes(4, byteorder='big')
  nonce= os.urandom(8)
  ad=type_field+nonce_len
  encrypted_ts= ts
 elif(csp==1):
  nonce_len=(12).to_bytes(4, byteorder='big') 
  nonce= os.urandom(12)
  ad=type_field+nonce_len
  encrypted_ts= pysodium.crypto_aead_chacha20poly1305_ietf_encrypt(ts, ad, nonce, session_key)
 elif (csp==2):
  nonce_len=(8).to_bytes(4, byteorder='big')
  nonce= os.urandom(8)
  ad=type_field+nonce_len
  encrypted_ts= pysodium.crypto_aead_chacha20poly1305_encrypt(ts, ad, nonce, session_key)
 else:
  print ("exit")
 accept= type_field + nonce_len + nonce + encrypted_ts
# print (accept)
 counter_accept= getSocketResponse(accept)
 print (counter_accept)
 return counter_accept

def sendData(accept):
 counter_propose= accept[0]
 counter_accept= accept[1]
 type_field= (2).to_bytes(1, byteorder='big') 
 len_nonce= int.from_bytes(counter_accept[1:5], byteorder='big')
 nonce=os.urandom(len_nonce)
 nonce_len= counter_accept[1:5]
 session_key=getSessionKey(counter_propose)
 req= Request(0)
 data= req.request()
 ad= type_field + nonce_len
 encrypted_data=pysodium.crypto_aead_chacha20poly1305_ietf_encrypt(data, ad, nonce, session_key)
 data_msg= type_field + nonce_len + nonce + encrypted_data
 resp= getSocketResponse(data_msg)
 print (resp)

def sendTerminate(counter_propose):
 type_field=(3).to_bytes(1, byteorder= 'big')
 nonce_len=(12).to_bytes(4, byteorder= 'big')
 nonce= os.urandom(12)
 ad=type_field+nonce_len
 session_key= getSessionKey(counter_propose)
 time_stamp= int(time.time())
 ts=time_stamp.to_bytes(8, byteorder='big')
 encrypted_ts= pysodium.crypto_aead_chacha20poly1305_ietf_encrypt(ts, ad, nonce, session_key)
 terminate= type_field + nonce_len + nonce + encrypted_ts
 addr=("172.18.0.252", 1337)
 sock= getSocket()
 sock.sendto(terminate, addr)
 

def main():
 counter_propose=getCounterPropose()
 counter_accept=createAccept(counter_propose)
 accept=([counter_propose, counter_accept])
 print (type(counter_accept))
 sendData(accept)
 sendTerminate(counter_propose)
 print ("exit")
main()

