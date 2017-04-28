#include <stdio.h>
#include <cs50.h>
#include <string.h>
#include <ctype.h>

string encrypt(int key, string entry);

int main(int argc, string argv[])
{
    // Verify number of arguments is valid
    if(argc != 2)
    {
        // return error code for imprpoer cmd ln arguments.
        printf("ERROR: Single number expected after ./caeser\n");
        return 1;
    }
    
    else
    {
        // Set the entered key to an integer
        int key = atoi(argv[1]);
        
        // Get the text for entry
        printf("plaintext: ");
        string plaintext = get_string();
        
        // Run the cipher and return the output
        printf("ciphertext: %s\n", encrypt(key, plaintext));

    }
}

// Function for turning an entered text into ciphered text, using a key passed by the user. 
string encrypt(int key, string entry)
{
    char ciphertext[strlen(entry)];    
        
    for(int i = 0, b = strlen(entry); i < b; i++)
    {
        // Check to see if the char is an alpha char        
        if(isalpha(entry[i]))
        {
           // Is the char an uppercase char?
           if(isupper(entry[i]))
           {
               // For changing upper case letters
                ciphertext[i] = (((entry[i] - 65) + key) % 26) + 65;
           }
           else
           {
               // For changing lower case letters
                ciphertext[i] = (((entry[i] - 97) + key) % 26) + 97;
           }
           
        }
        else
        {
            ciphertext[i] = entry[i];
        }
    }
    
    // Return the ciphertext
    string text = ciphertext;
    return text;
}