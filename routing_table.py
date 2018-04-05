#!/usr/bin/python3

class Node:
    def __init__(self, ip, port=0, id=0):
        self.l = None
        self.r = None
        self.ip= ip
        self.port= port
        self.v= id
        self.t= (self.ip, self.port, self.v);

class Kbucket(object):
    def __init__(self, prefix):
       self.l = None
       self.r= None
       self.v= prefix    
       self.array= []
       self.set= set()
    
    def addNode(self, node):
        self.array.append(node.t) 
 
    
    def getNodeIDSet(self):
        node_id_set= set()
        for x in range(len(self.array)):
         node_tuple=self.array[x]
         node_id=node_tuple[2]
         node_id_set.add(node_id)
        return node_id_set

def find(root, kbucket, prefix=0):
    if root is None:
        root = kbucket
    if(prefix == kbucket.v):
        return kbucket
    elif(prefix < kbucket.v and kbucket.l != None):
        find(prefix, kbucket.l)
    elif(prefix > kbucket.v and kbucket.r != None):
        find(prefix, kbucket.r)


def binary_insert(root, kbucket):
    if root is None:
        root = kbucket
    else:
        if root.v > kbucket.v:
            if root.l is None:
                root.l = kbucket
            else:
                binary_insert(root.l, kbucket)
        else:
            if root.r is None:
                root.r = kbucket
            else:
                binary_insert(root.r, kbucket)

def in_order_print(root):
    if not root:
        return
    in_order_print(root.l)
    print (root.v)
    in_order_print(root.r)

def test():
    node1= Node("192.12.0.1", 1982, 0x8b00)
    node2= Node("192.12.0.2", 1983, 0x8c00)
    kbucket1=Kbucket(0b1)
    kbucket2=Kbucket(0b10)
    r=Kbucket(0b0)
    r.addNode(node1)
    r.addNode(node2)
    #r=Kbucket(0b0)
    binary_insert(r, kbucket1)
    binary_insert(r, kbucket2)
    in_order_print(r)
    print (kbucket1.array)
    print((find(0b10, r)).array)
    print (r.getNodeIDSet())
    

