import cs50

def main():
    # get number
    print("Number: ", end="")
    number = cs50.get_int()
    
    # retry if not valid
    while number < 1:
        print("Retry: ", end="")
        number = cs50.get_int()
    
    # check to see if credit card is valid
    if not checkSum(number):
        print("INVALID")
        
    # get the number of digits in the number    
    length = len(str(number))
    
    # determine who makes the card
    if length == 15:
        A = number // 10000000000000
        if A == 34 or A == 37:
            print("AMEX")
        
    elif length == 16:
        A = number // 100000000000000
        B = number // 1000000000000000
        if A > 50 and A < 56:
            print("MASTERCARD")
        elif B == 4:
            print("VISA")
            
    elif length == 13:
        A = number // 1000000000000
        if A == 4:
            print("VISA")
            
    else:
        print("Card manufacturer not recognized")
    
# check sum function
def checkSum(n):
    
    secondSum = 0
    lastSum = 0
    checksumNumber1 = n
    checksumNumber2 = n
    
    # loop to get the second to last digit sum
    while checksumNumber2 > 0:
        
        digit = (((checksumNumber2 // 10) % 10) * 2)
        
        if digit > 9:
            secondSum = secondSum + (digit % 10) + 1
        else:
            secondSum = secondSum + digit
        
        checksumNumber2 = checksumNumber2 // 100
    
    # loop to get the last digit sum    
    while checksumNumber1 > 0:
        digit = checksumNumber1 % 10
        lastSum = lastSum + digit
        
        checksumNumber1 = checksumNumber1 // 100
    
    # add the sums together
    digitSum = lastSum + secondSum
    
    # return true or false based on sums modulo by 10
    if (digitSum % 10 != 0):
        return False;
    else:
        return True;

if __name__ == "__main__":
    main()    