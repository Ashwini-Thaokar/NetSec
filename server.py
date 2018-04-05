

import os
import sys
from protocol import *
from routing_table import Node, Kbucket
from random import randint
import socket
import binascii
import base64


#socket to connect to bootstrap
UDP_IP ="172.18.0.252"
UDP_PORT= 3337
server_sock= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_sock.bind(("127.0.0.1", 5080))

#global parameters

node_id=(int('0x8B00', 16)).to_bytes(2, byteorder='big')

#nonce
num= randint(0,1000)
nonce=(num&(0xffff)).to_bytes(2, byteorder='big')

id_length= (2).to_bytes(4, byteorder='big')



def parser(tup):
 dotted_ip=tup[0].split(".")
 ip0= int(dotted_ip[0]).to_bytes(1, byteorder='big')
 ip1= int(dotted_ip[1]).to_bytes(1, byteorder='big')
 ip2= int(dotted_ip[2]).to_bytes(1, byteorder='big')
 ip3= int(dotted_ip[3]).to_bytes(1, byteorder='big')
 undotted_ip=b"".join([ip0, ip1, ip2, ip3])
 port= int(tup[1]).to_bytes(2, byteorder='big')
 nodeid=int(tup[2], 16).to_bytes(2, byteorder='big')
 version= (4).to_bytes(1, byteorder='big')
 entry= b"".join([version, undotted_ip, id_length, nodeid])
 return entry


def getEntries():
 tuple= kbucket_obj.array
 e1= parser(tuple[0])
 e2=parser(tuple[1])
 e3= parser(tuple[2])
 e4=parser(tuple[3])
 return b"".join([e1, e2, e3, e4])

while True:
 request, address = server_sock.recvfrom(1024)
 response= request
 code= response[:1]
 response_nonce=response[11:13]
 requesting_node_id=response[5:7]
 option = int(str(code)[5:-1])
 print (option)
 resp_code=(option+1).to_bytes(1, byteorder='big')
 
#Respond to Ping Request
 if option == 0:
  #ping_code=(1).to_bytes(1, byteorder='big')
  message= b"".join([resp_code, id_length, node_id, id_length, response_nonce])
 # server_sock.sendto(message, address)

#Respond to Store Request 
 elif option == 2:
  #store_code=(3).to_bytes(1, byteorder='big')
  message= b"".join([resp_code, id_length, node_id, id_length, response_nonce])
#  server_sock.sendto(message, address)

#Respond to Find_Node Request
 elif option == 4:
  #find_node_code=(5).to_bytes(1, byteorder='big')
  array= kbucket_obj.array
  entries= getEntries()
  entry_len= (len(entries)).to_bytes(4, byteorder='big')
  message= b"".join([resp_code, id_length, node_id, id_length, response_nonce, entry_len, entries]) #
#  server_sock.sendto(message, address)

#Respond to Find_Value Request
 elif option == 6:
  #find_value_code=(7).to_bytes(1, byteorder='big')
  message= b"".join([resp_code, id_length, node_id, id_length, response_nonce, entry_len, entries]) 
#  server_sock.sendto(message, address)

#BadRequest
 else:
  error_code=(8).to_bytes(1, byteorder='big')
  msg='bad request'
  encoded_error_msg=binascii.hexlify(base64.b64encode(msg.encode('ascii')))
  error_length= (len(encoded_error_msg)).to_bytes(4, byteorder='big')
  error_msg=(int(encoded_error_msg, 16)).to_bytes(32, byteorder='big')
  message=b"".join([error_code, id_length, node_id, id_length, nonce, error_length, error_msg])
  #print (error)
  # print(str((binascii.hexlify(error)))[2:-1])
 server_sock.sendto(message, address)
