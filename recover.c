#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

typedef uint8_t BYTE;

int search_JPEG(BYTE buffer[], FILE* inptr);

int main(int argc, char *argv[])
{
    // Ensure proper usuage
    if (argc != 2)
    {
        fprintf(stderr, "Usage: ./recover filename\n");
        return 1;
    }
    
    // remember filenames
    char *infile = argv[1];

    // open input file 
    FILE *inptr = fopen(infile, "r");
    if (inptr == NULL)
    {
        fprintf(stderr, "Could not open %s.\n", infile);
        return 2;
    }    
    
    // initialize check memory block
    BYTE buffer[512];

    // initialize filenumber counter
    int filenumber = 0;
    char *filename = malloc(sizeof(char));
    if (filename == NULL)
    {
        fprintf(stderr, "Memory not available\n");
        return 5;
    }

    // status tracker for file OPEN/CLOSED
    int JPEG_open = 0;
    FILE *img = NULL;

    // run a search on the file, returning result if JPEG found    
    int searchResult = search_JPEG(buffer, inptr);\
    
    // search for JPEGs
    while (searchResult > 0)
    {
        // Start new JPEG when a new one is found
        if (searchResult == 1)
        {
            // close the existing JPEG, if it exists
            if (JPEG_open == 1)
            {
                fclose(img);
                JPEG_open = 0;
            }
        
            // create a new JPEG
            sprintf(filename, "%03i.jpg", filenumber);   
            filenumber++;
        
            // open file and error check
            img = fopen(filename, "w");
            if (img == NULL)
            {
                fprintf(stderr, "Could not open %s.\n", infile);
                return 3;
            }
            JPEG_open = 1;
        
            // write the block to the file
            fwrite(buffer, 512, 1, img);
        }
        
        // continue existing JPEG when a new one isn't found
        if (searchResult == 2 && JPEG_open == 1)
        {
            fwrite(buffer, 512, 1, img);
        }
        
        searchResult = search_JPEG(buffer, inptr);
    }
    
    // free memory
    free(filename);
    
    // close infile
    fclose(inptr);
    
    // success
    return 0;
    
}


// function to search through a file for JPEGS, returning different results
int search_JPEG(BYTE* buffer, FILE* inptr)
{
    while (fread(buffer, 512, 1, inptr) == 1)
    {
        // check to see if block begins as JPEG
        if (buffer[0] == 0xff &&
            buffer[1] == 0xd8 &&
            buffer[2] == 0xff &&
            (buffer[3] & 0xf0) == 0xe0)
        {
            // new JPEG found
            return 1;
        }    
        else
        {
            // not a new JPEG
            return 2;
        }    
    }
    
    // EOF reached
    return 0;
}