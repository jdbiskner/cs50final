import crypt
import sys
import itertools
import string

# test python crack.py 50.jPgLzVirkc
def main():

    # exit if command line args not provided    
    if len(sys.argv) != 2:
        print("Usage: python crack.py hash")
        exit(1)

    # send input hashed password and salt to crack function
    crack(str(sys.argv[1]), ''.join({sys.argv[1][0] + sys.argv[1][1]}))

# function to crack a password
def crack(inputHash, salt):    

    # begin iterating through possible passwords
    for i in range(5):
        
        # create a list of possible passwords based on length defined in i
        passwordList = itertools.product(string.ascii_letters, repeat = i)
        
        # iterate through password list
        for password in passwordList:
        
            # checking each one for hashing
            crackedHash = crypt.crypt(''.join(password), salt)
            
            # check to see if the hashes match
            if crackedHash == inputHash:
                print(''.join(password))
                exit(0)
    
    # stop after the key becomes to large
    print('The key is too big. Stopping')
    exit(1)

# begins in main
if __name__ == "__main__":
    main()