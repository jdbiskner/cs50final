#include <cs50.h>
#include <stdio.h>

int main(void)
{
    printf("Minutes: ");
    int minutes;
    do
    {
        minutes = get_int();
    }
    while (minutes < 0);
    
    int bottles = (minutes * 192)/16;
    
    printf("Bottles: %i\n", bottles);
}