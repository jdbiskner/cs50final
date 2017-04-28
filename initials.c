#include <stdio.h>
#include <cs50.h>
#include <string.h>
#include <ctype.h>

string get_Initials_Capital(string name);

int main(void)
{
   // Get the name for putting into initials
   string name = get_string();
   
   // Get the initials of the name entered and print that out in capital letters
   name = get_Initials_Capital(name);
   printf("%s\n", name);
   
}

// Function for getting initials of an entered string, returned in capitals
string get_Initials_Capital(string name)
{
   int a = 0;
   int b = strlen(name);
   char name_initials[b];
   int foo = 0;
   string initials = NULL;

   // Go through the whole string, char by char, to find the first non-space in each name.  
   while(a < b)
   {
      // If char is a space, move on to next char
      if(name[a] == 32)
      {
         a++;
      }
      
      // Else, store the first letter in the array
      else
      {
         name_initials[foo] = name[a];
         foo++;
         a++;
         
         // Then move on till another space is found, and repeat the rest of the loop
         while(name[a] != 32 && a < b)
         {
            a++;
         }  
      } 
   }
   
   // Loop the upper-casing of the string.
   for(int i = 0; i < b; i++)
   {
      name_initials[i] = toupper(name_initials[i]);
   }
   
   // Return array as string
   initials = name_initials;
   return initials;
}