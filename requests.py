import os
import sys
from routing_table import Node, Kbucket
from random import randint
import socket
import binascii
import base64

#socket to connect to bootstrap
UDP_IP ="127.0.0.1"
UDP_PORT= 5080
client_socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.connect((UDP_IP, UDP_PORT))

#global parameters

node_id=(int('0x8B00', 16)).to_bytes(2, byteorder='big')

#nonce
num= randint(0,1000)
nonce=(num&(0xffff)).to_bytes(2, byteorder='big')

id_length= (2).to_bytes(4, byteorder='big')

def request(code):

#Send Ping Request

 if (code==0):
  code1= (0).to_bytes(1, byteorder='big')
  ping_request= b"".join([code1, id_length, node_id, id_length, nonce])
  client_socket.send(ping_request)

#Send Store Request

 elif(code==2):
  code2= (2).to_bytes(1, byteorder='big')
  store_request=b"".join([code2, id_length, node_id, id_length, nonce, id_length, node_id])
  client_socket.send(store_request)

#Send Find_Node Request

 elif(code==4):
  code4= (4).to_bytes(1, byteorder='big')
  find_node_request=b"".join([code4, id_length, node_id, id_length, nonce, id_length, node_id])
  client_socket.send(find_node_request)

 elif(code==6):
  code6= (6).to_bytes(1, byteorder='big')
  find_value_request=b"".join([code6, id_length, node_id, id_length, nonce, id_length, node_id])
  client_socket.send(find_node_request)

def response(request):
 response, address= client_socket.recvfrom(1024)
 print (response)
 print (address)

def main():
 request(4)
 response(request)
 
main()
