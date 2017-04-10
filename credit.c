//validate company's indentifier
//validate number's length
//test number: 378282246310005

#include <cs50.h>
#include <stdio.h>

bool checkSum(long long n);
int digitCount(long long n);

int main(void)
{
    long long number;
    
    //Get number
    printf("Number: ");
    number = get_long_long();
    while (number < 1)
        {
        printf("Retry: ");
        number = get_long_long();
        }

    //Checksum procedure
    bool validNumber = checkSum(number);
    //Return result to user
    if(validNumber != true)
        {
            printf("INVALID\n");
        }

    //Get the count of digits in number. 
    int numberdigitCount = digitCount(number);
    
    // Company Identifiers
    switch(numberdigitCount) 
    {
        
        case 15 :
        {
            int A = number / 10000000000000;
            if (A == 34 || A == 37)
            {
                printf("AMEX\n");
            }
            break;
        }
            
       case 16 :
        {
            int A = number / 100000000000000;
            int B = number / 1000000000000000;
            if (A > 50 && A < 56)
            {
                printf("MASTERCARD\n");
            }
            else if (B == 4)
            {
                printf("VISA\n");
            }
            break;
        }
        
       case 13 :
        {
            int A = number / 1000000000000;
            if (A == 4)
            {
                printf("VISA\n");
            }
            break;
        }
        
       default : 
        break;
   
    }
}    

///////////////////////////////////////////////////////////////

//Function for getting count of digits in a number.
int digitCount(long long n)
{
    int digitCounter = 0;
    
    while(n > 0)
    {
        n = n / 10;
        digitCounter++;
    }
    
    return digitCounter;
}

//Function for getting Y or N on validity of number entered.
bool checkSum(long long n)
{
    //Checksum procedure    
    long long digit;
    int secondSum = 0;
    int lastSum = 0;
    long long checksumNumber1 = n;
    long long checksumNumber2 = n;

    //Loop to get the second to last digit sum
    while(checksumNumber2 > 0)
        {
        digit = checksumNumber2 / 10;
        digit = digit % 10;
        digit = digit * 2;
        
        if(digit > 9)
            {
            int digitTen = digit % 10;
            secondSum = secondSum + digitTen + 1;
            }
        else
            {
            secondSum = secondSum + digit;
            }
    
        checksumNumber2 = checksumNumber2 / 100;
        }

    //Loop to get the last digit sum.
    while(checksumNumber1 > 0)
        {
        digit = checksumNumber1 % 10;
        lastSum = lastSum + digit;     
    
        checksumNumber1 = checksumNumber1 / 100;
        }
         
    int digitSum = lastSum + secondSum;
   
    if(digitSum % 10 != 0)
        {
            return false;
        }
        else
        {
            return true;
        }
}