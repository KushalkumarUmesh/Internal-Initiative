# def fib(n):
#     if n < 0:
#         print('not valid')
#     elif n==1:
#         return 0
#     elif n==2:
#         return 1
#     else:
#         return fib(n-1) + fib(n-2)          

# print(fib(9))
#---------------------------------
# Function for nth fibonacci number - Space Optimisataion
# Taking 1st two fibonacci numbers as 0 and 1

def fibonacci(n):
	a = 0
	b = 1
	if n < 0:
		print("Incorrect input")
	elif n == 0:
		return a
	elif n == 1:
		return b
	else:
		for i in range(2,n):
			c = a + b
			a = b
			b = c
		return b

# Driver Program

print(fibonacci(8))

#This code is contributed by Saket Modi
