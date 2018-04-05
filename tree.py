from pptree import *

root= "172.18.0.252, 1337, ffff"
left="172.18.0.252, 2086, ac00"
right="172.18.0.252, 2072, 9000"
left1="172.18.0.252, 2083, a600"
left2="172.18.0.252, 2091, b600"
root= Node("ffff")

left = Node("ac00", root)
right = Node("9000", root)

left1 = Node("a600", left)
left2 = Node("b600", left)

print_tree(root)

