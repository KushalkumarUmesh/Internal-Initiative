# import copy
# l1=[1,2,3,4]
# l2=l1
# l2.append(6)
# print(l1)
# print(l2)
# ------------------
import re
# s='KushalKumar'
# p='us'
# i=re.split(s,p)
# j=re.subn('k',p,s)
# o=re.subn(p,'k',s)
# print(o)
# print(s)
# -------------------
# import numpy as np
# arr=np.array([1,2,3,4,5])
# print(arr.argsort()[-3:][::-1])
# --------------------------------
# import numpy as np
# a=np.array([1,2,3,4,5])
# p=np.percentile(a,50)
# print(p)
# -----------------------------------
class Animal:
   def eat(self):
      print("It eats insects.")
   def sleep(self):
      print("It sleeps in the night.")

class Bird(Animal):
   def fly(self):
      print("It flies in the sky.")

   def sing(self):
      print("It sings a song.")
      print(issubclass(Bird, Animal))

Koyal= Bird()
print(isinstance(Koyal, Bird))

Koyal.eat()
Koyal.sleep()
Koyal.fly()
Koyal.sing()