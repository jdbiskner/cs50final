/*
Compile With
clang -ggdb3 -O0 -std=c11 -Wall -Werror -Wshadow crack.c -lcrypt -lcs50 -lm -o crack

Tests
andi: ./crack 50.jPgLzVirkc hi
jason: ./crack 50YHuxoCN9Jkc JH
malan: ./crack 50QvlJWn2qJGE NOPE
mzlatkova: ./crack 50CPlMDLT06yY ha
patrick: ./crack 50WUNAFdX/yjA Yale
rbowden: ./crack 50fkUxYHbnXGw rofl
summer: ./crack 50C6B0oz0HWzo FTW
stelios: ./crack 50nq4RV/NVU0I ABC
wmartin: ./crack 50vtwu4ujL.Dk haha
zamyla: ./crack 50i2t3sOSAZtk lol
*/

#define _XOPEN_SOURCE
#include <unistd.h>
#include <stdio.h>
#include <cs50.h>
#include <string.h>

char alphaIncrement(char letter, int incrementer);

int main(int argc, string argv[])
{
    // Return error if arguments are not 2
    if(argc != 2)
    {
        printf("Usage: ./crack hash\n");
        return 1;
    }
    
    else
    {   
        // Get the salt from the first two chars of the entered string
        char salt[2] = { argv[1][0], argv[1][1]};
        
        // Save the entered hash
        string inputHash = argv[1];
        
        // Create an array of letters for referring to a-z,A-Z
        char letterBank[52];
        letterBank[0] = 'a';
        for(int i = 1; i < 52; i++)
        {
            letterBank[i] = alphaIncrement(letterBank[i-1], 1);
        }
        
        // Prepare the test key length
        int keyLen = 2;
        
        // Run the key test generate and test loop until the answer is found, or the key is too big
        while(keyLen < 6)
        {   
            // Initialize our test key
            char key[keyLen];
            for(int i = 0; i < keyLen; i++)
            {
                // Temporarily setting to test break on line 91; return to a when done
                key[i] = 97;
            }
           
            // NULL end the char array
            key[keyLen - 1] = '\0';
           
            // Set these variables for the test process
            int currentChar = 0;
            int currentLetter = 0;
            int stopLoop = 0;
            
            while(1)
            {
                // If the current char I'm focusing on is Z, set it to A, and increment the char to the right
                while(key[currentChar] == 90)
                {   
                    // Set the current char from Z to a
                    key[currentChar] = letterBank[0];
                    
                    // Reset the current char
                    currentLetter = 0;

                    // Focus on the next char
                    currentChar++;
                    if(currentChar == keyLen - 1)
                    {
                        stopLoop = 1;
                        break;
                    }
                    
                    
                    if(key[currentChar] != 90)
                    {
                        key[currentChar] = alphaIncrement(key[currentChar], 1);
                        currentChar = 0;
                    }
                    
                    
                }
                
                if(stopLoop == 1)
                {
                    stopLoop = 0;
                    break;
                }
                
                if(key[currentChar] == 90)
                {
                    
                }
                
                key[currentChar] = letterBank[currentLetter];
                
                currentLetter++;
                
                string crackedHash = crypt(key, salt);
                
                if(strcmp(crackedHash, inputHash) == 0)
                {
                printf("%s\n", key);
                return 0;
                } 
        
            }
        
            keyLen++;
        
        }
        
        printf("The key is too big. Stopping\n");
        return 0;
    }
}

// Increments an alphabetical char, wrapping from a-z,A-Z
char alphaIncrement(char letter, int incrementer)
{
    for(int i = 0; i < incrementer; i++)
    {
        if(letter > 96 && letter < 122)
            {
                letter = letter + 1;
            }
    
        else if(letter == 122)
            {
                letter = 65;
            }
    
        else if(letter > 64 && letter < 90)
            {
                letter = letter + 1;
            }
    
        else if(letter == 90)
            {
                letter = 97;
            }
    }
    
    return letter;
}