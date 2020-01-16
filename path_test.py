from Graph import Graph;
from SecurityPolicyDatabase import SecurityPolicyDatabase
from SecurityAsscoiationDatabase import SecurityAssociationDatabase


g = Graph(4,2)

print(str(g))

t = g.path(1,14)
print(t)
t = g.path(2,14)
print(t)

