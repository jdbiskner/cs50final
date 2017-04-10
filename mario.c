#include <cs50.h>
#include <stdio.h>

int main(void)
{
    
    int height;
    do
    {
        printf("Height: ");
        height = get_int();
    }
    while (height > 23 || height < 0);

    //Establish space and hash counters
    int s = height - 1;
    int h = height - s;

    for (int i = 0; i < height; i++)
    {

        // print spaces for left pyramid
        for(int is = 0; is < s; is++)
        {
            printf(" ");
        }
        
        // print hashes for left pyramid
        for(int ihl = 0; ihl < h; ihl++)
        {
            printf("#");
        }
        
        // print gap printf("  ");
        printf("  ");
        
        // print hashes for right pyramid
        for(int ihr = 0; ihr < h; ihr++)
        {
            printf("#");
        }
        
        // print line break
        printf("\n");
        
        //Increment space count and hash counts.
        s--;
        h++;
        
    }
}