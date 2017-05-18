/**
 * helpers.c
 *
 * Helper functions for Problem Set 3.
 */
 
#include <cs50.h>

#include "helpers.h"

/**
 * Returns true if value is in array of n values, else false.
 * Binary Sort
 * Built with help from: https://www.topcoder.com/community/data-science/data-science-tutorials/binary-search/
 */
bool search(int value, int values[], int n)
{
    // Defining the beginning and end of the search area.
    int beginArray = 0;
    int endArray = n - 1;
    
    // Beginning the search. While total search area is greater than 1, do loop.
    while(beginArray <= endArray)
    {
        // Define the middle value
        int mid = (beginArray + (endArray + 1)) / 2;
        
        // Check if mid is correct. If not, resize search area.
        if(values[mid] == value)
        {
            return true;
        }
        else if(values[mid] > value)
        {
            // Move array to the left
            endArray = mid - 1;
        }
        else
        {
            // Move array to the right
            beginArray = mid + 1;
        }
    }    
    
    // Otherwise, none of the above is true, and the value doesn't exist
    return false;
}

/**
 * Sorts array of n values.
 */
void sort(int values[], int n)
{
    // Create a counting array
    int count[65536] = { 0 };
    
    // Increment the counting array using the passed array's values
    for(int i = 0; i < n; i++)
    {
        count[values[i]]++;
    }

    // Fill in the passed array with the counting array's values
    for(int i = 0, srtPosition = 0; i < 65536; i++)
    {
        // Find counters that have been used
        if(count[i] > 0)
        {
            // Fill in the sorted array based on how often that number appeared in the original array
            for(int j = 0; j < count[i]; j++)
            {
                values[srtPosition] = i;
                srtPosition++;
            }
        }
    }
    
    return;

}

