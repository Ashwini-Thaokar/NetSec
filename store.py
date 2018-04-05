import os
import sys
import base64
import socket
from random import randint
import binascii

#import file to get data
h= open(os.path.join(sys.path[0], "dht_data"), "r")

node_ids= [0xac00, 0xb600, 0xa600, 0x9000]
UDP_PORTS= [2086, 2091, 2083, 2072]

#define socket
UDP_IP ="172.18.0.252"
client_sock= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


#create nonce
num= randint(0,1000)
nonce=(num&(0xffff)).to_bytes(2, byteorder='big')


code2= (2).to_bytes(1, byteorder='big')
id_length= (2).to_bytes(4, byteorder='big')
data_length=(128).to_bytes(4, byteorder='big')
for id in range(0,4):
  UDP_PORT= UDP_PORTS[id]
  client_sock.connect((UDP_IP, UDP_PORT))
  node_id=(node_ids[id]).to_bytes(2, byteorder='big')
  for x in range(1,17):
    data=base64.b64decode(str(h.readlines(x)))
    message2=b"".join([code2, id_length, node_id, id_length, nonce, data_length, data])
    client_sock.send(message2)
    response, address=client_sock.recvfrom(1024)
    print (str(binascii.hexlify(response)))
client_sock.close()
h.close()

