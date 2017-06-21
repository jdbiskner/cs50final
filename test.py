import itertools
import string
import crypt

# NOPE 50QvlJWn2qJGE

inputHash = '50QvlJWn2qJGE'

# begin iterating through possible passwords
for i in range(5):
    
    # create a list of possible passwords based on length defined in i
    passwordList = list(itertools.product(string.ascii_letters, repeat = i))
    
    # iterate through password list
    for password in passwordList:
        
        testPassword = str(''.join(password))
        
        # checking each one for hashing
        crackedHash = crypt.crypt(testPassword, '50')
        
        # check to see if the hashes match
        if crackedHash == inputHash:
            print(testPassword)
            exit(0)