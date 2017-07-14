/**
 * Copies a BMP piece by piece, just because.
 */

#include <stdio.h>
#include <stdlib.h>

#include "bmp.h"

void upscale(BITMAPINFOHEADER bi, int scale, FILE* input, FILE* output, int in_padding, int out_padding);
void downscale(BITMAPINFOHEADER in_bi, BITMAPINFOHEADER out_bi, FILE* input, FILE* output);

int main(int argc, char *argv[])
{
    // ensure proper usage
    if (argc != 4)
    {
        fprintf(stderr, "Usage: ./copy n infile outfile\n");
        return 1;
    }

    // remember filenames and float
    float f;
    sscanf(argv[1], "%f", &f);
    char *infile = argv[2];
    char *outfile = argv[3];

    // open input file 
    FILE *inptr = fopen(infile, "r");
    if (inptr == NULL)
    {
        fprintf(stderr, "Could not open %s.\n", infile);
        return 2;
    }

    // open output file
    FILE *outptr = fopen(outfile, "w");
    if (outptr == NULL)
    {
        fclose(inptr);
        fprintf(stderr, "Could not create %s.\n", outfile);
        return 3;
    }

    // read infile's BITMAPFILEHEADER
    BITMAPFILEHEADER bf;
    fread(&bf, sizeof(BITMAPFILEHEADER), 1, inptr);

    // read infile's BITMAPINFOHEADER
    BITMAPINFOHEADER bi;
    fread(&bi, sizeof(BITMAPINFOHEADER), 1, inptr);

    // ensure infile is (likely) a 24-bit uncompressed BMP 4.0
    if (bf.bfType != 0x4d42 || bf.bfOffBits != 54 || bi.biSize != 40 || 
        bi.biBitCount != 24 || bi.biCompression != 0)
    {
        fclose(outptr);
        fclose(inptr);
        fprintf(stderr, "Unsupported file format.\n");
        return 4;
    }

    // change header file detail
    /**
     * biHeight
     * biWidth
     * biSize (including pixels and padding)
     *  bi.biSizeImage = ((sizeof(RGBTriple) * bi.Width) + padding) * abs(bi.biHeight)
     * bfSize
     *  including pixels, padding and headers
     *  = biSizeImage + sizeof(BITMAPFILEHEADER) + (BITMAPINFOHEADER)
     */
    
    // create copies of headers for future write to output
    BITMAPINFOHEADER out_bi = bi;
    BITMAPFILEHEADER out_bf = bf;
    
    // Set the width and height of the output file
    out_bi.biHeight = (bi.biHeight * f);
    out_bi.biWidth = (bi.biWidth * f);

    // determine padding for input and output scanlines
    int in_padding = (4 - (bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;
    int out_padding = (4 - (out_bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4; 
    
    // set size for file and info header of output
    out_bi.biSizeImage = ((sizeof(RGBTRIPLE) * out_bi.biWidth) + out_padding) * abs(out_bi.biHeight);
    out_bf.bfSize = out_bi.biSizeImage + sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER);
    
    // write outfile's BITMAPFILEHEADER
    fwrite(&out_bf, sizeof(BITMAPFILEHEADER), 1, outptr);

    // write outfile's BITMAPINFOHEADER
    fwrite(&out_bi, sizeof(BITMAPINFOHEADER), 1, outptr);

    // check for upscale or downscale
    if (f >= 1)
    {
        upscale(bi, f, inptr, outptr, in_padding, out_padding);
    }
    else if (f < 1)
    {
        downscale(bi, out_bi, inptr, outptr);
    }
    
    // close infile
    fclose(inptr);

    // close outfile
    fclose(outptr);

    // success
    return 0;
}

// Function to upscale an image.
void upscale(BITMAPINFOHEADER bi, int scale, FILE* input, FILE* output, int in_padding, int out_padding)
{
    int len_scanline = ((bi.biWidth * sizeof(RGBTRIPLE)) + in_padding);
    
    // iterate over infile's scanlines
    for (int i = 0, biHeight = abs(bi.biHeight); i < biHeight; i++)
    {
        for (int v = 0; v < scale; v++)
        {
            // move the file pointer to the beginning of the scanline
            if (v > 0)
            {
                fseek(input, len_scanline * -1, SEEK_CUR);
            }
            // iterate over pixels in scanline
            for (int j = 0; j < bi.biWidth; j++)
            {
                // temporary storage
                RGBTRIPLE triple;
    
                // read RGB triple from infile
                fread(&triple, sizeof(RGBTRIPLE), 1, input);
    
                // write RGB triple to outfile for f times.
                for (int k = 0; k < scale; k++)
                {
                    fwrite(&triple, sizeof(RGBTRIPLE), 1, output);
                }
                
            }
    
            // skip over padding, if any
            fseek(input, in_padding, SEEK_CUR);
    
            // then add it back (to demonstrate how)
            for (int k = 0; k < out_padding; k++)
            {
                fputc(0x00, output);
            }
        }    
    }
}


/** Function to downscale an image.
 * Sourced from https://cs50.stackexchange.com/questions/9956/hacker4-resize-cant-resize-when-factor-is-a-decimal-number
 */
void downscale(BITMAPINFOHEADER in_bi, BITMAPINFOHEADER out_bi, FILE* input, FILE* output)
{
    // Width Ratio
    float widthR = in_bi.biWidth / out_bi.biWidth;
    
    // Height Ratio
    float heightR = in_bi.biHeight / out_bi.biHeight;
    
    // Determine padding
    int in_padding = (4 - (in_bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;
    int out_padding = (4 - (out_bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4; 
    
    for (int i = 0; i < abs(out_bi.biHeight); i++)
    {
        int scanlineIndex;
        scanlineIndex = i * heightR;
    
        // seek to the beginning of the scanline whose index is scanlineIndex    
        fseek(input, sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER), SEEK_SET);
        for (int j = 0; j < scanlineIndex; j++)
        {
            fseek(input, (sizeof(RGBTRIPLE) * in_bi.biWidth) + in_padding, SEEK_CUR);
        }
    
        // create an RGBTRIPLE array named triples of length oldWidth
        RGBTRIPLE triples[in_bi.biWidth];
        
        // read the whole scanline into triples
        for (int j = 0; j < in_bi.biWidth; j++)
        {
            fread(&triples[j], sizeof(RGBTRIPLE), 1, input);
        }
    
        for (int j = 0; j < out_bi.biWidth; j++)
        {
            int pixelIndex;
            pixelIndex = j * widthR;
            fwrite(&triples[pixelIndex], sizeof(RGBTRIPLE), 1, output);
        }
 
        // add the new padding       
        for (int k = 0; k < out_padding; k++)
        {
            fputc(0x00, output);
        }
    }
}