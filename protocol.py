#!/usr/bin/python3

import os
import sys
import routing_table
from routing_table import Node, Kbucket
from random import randint
import socket
import binascii
import base64

#socket to connect to bootstrap
UDP_IP ="172.18.0.252"
UDP_PORT= 3337
client_sock= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_sock.connect(("172.18.0.252", 3337))

#global parameters

node_id=(int('0x8B00', 16)).to_bytes(2, byteorder='big')

#nonce
num= randint(0,1000)
nonce=(num&(0xffff)).to_bytes(2, byteorder='big')

id_length= (2).to_bytes(4, byteorder='big')

def request(code, nodeID):

#Send Find_Node Request

 code4= (4).to_bytes(1, byteorder='big')
 xnodeid= (int(nodeID, 16)).to_bytes(2, byteorder='big')
 find_node_request=b"".join([code4, id_length, node_id, id_length, nonce, id_length, xnodeid])
 client_sock.send(find_node_request)


def response(request, prefix):
 response, address=client_sock.recvfrom(1024)
# print (response)
 code= response[:1]
 response_nonce=response[11:13]
 requesting_node_id=response[5:7]
# print (code)
# print(response_nonce)
# print(node_id)

#Handle Find_Node response


 keys= response[17:]
# print(keys)
 version= keys[:1]
 if (int.from_bytes(version, byteorder='big')==4):
  #Add IPv4 nodes to list of nodes
  key_1 = []
  key_1 = keys[0:13]
  key_2 = []
  key_2 = keys[13:26]
  key_3 = []
  key_3= keys[26:39]
  key_4 = []
  key_4 = keys[39:52]
  myList= []
  myList.append(key_1)
  myList.append(key_2)
  myList.append(key_3)
  myList.append(key_4)
  kbucketnew= Kbucket(prefix)
  node_set= set()
  for x in range (0, 4):
  #extract IP address, port and node-id
   ip= str(int.from_bytes((myList[x])[1:2], byteorder='big'))+'.'+str(int.from_bytes((myList[x])[2:3], byteorder='big'))+'.'+str(int.from_bytes((myList[x])[3:4], byteorder='big'))+'.'+str(int.from_bytes((myList[x])[4:5], byteorder='big'))
   port= str(int.from_bytes(myList[x][5:7], byteorder= 'big'))
   node_id1= hex(int.from_bytes(myList[x][11:13], byteorder='big'))
   node_set.add(node_id1)
   node=Node(ip, port, node_id1)
   kbucketnew.addNode(node)
# print(kbucketnew.array)
 return kbucketnew


r=Kbucket(0b0)
request(4, '0x8b00')
kbucket_obj=response(request, 0b1)
f= kbucket_obj.getNodeIDSet()
#print (f)
#print (kbucketnew.array)
new= f.copy()
while(bool(f)):
 request(4, f.pop())
 new_kbucket_obj=response(request, 0b10)
 g= new_kbucket_obj.getNodeIDSet()
# print (g)
 union_set= new.union(g)
#print (union_set)
intersection= new ^ union_set
if (len(intersection)==0):
 print ('complete')
else: 
 while(bool(intersection)):
  request(4, intersection.pop())
  third_kb_object= response(request, 0b11)
  h= third_kb_object.getNodeIDSet()
  #print (h)
  union_set2= union_set.union(h)
  #print (union_set2)
  intersection2= new ^ union_set2
  if (len(intersection2)==0):
   print ("complete")


