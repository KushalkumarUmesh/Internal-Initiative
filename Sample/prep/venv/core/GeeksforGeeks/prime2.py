num=int(input('enter a number'))
if num>1:
    for i in (2,num):
        if (num%i==0):
            print('not a prime number')
            break
        else:
            print('prime number')
            break
else:
    print('not a prime number')

