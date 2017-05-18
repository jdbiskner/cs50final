/**
 * fifteen.c
 *
 * Implements Game of Fifteen (generalized to d x d).
 *
 * Usage: fifteen d
 *
 * whereby the board's dimensions are to be d x d,
 * where d must be in [DIM_MIN,DIM_MAX]
 *
 * Note that usleep is obsolete, but it offers more granularity than
 * sleep and is simpler to use than nanosleep; `man usleep` for more.
 */
 
 // TODO: Clean up code
 // TODO: Comments
 
#define _XOPEN_SOURCE 500

#include <cs50.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

// constants
#define DIM_MIN 3
#define DIM_MAX 9

// board
int board[DIM_MAX][DIM_MAX];

// dimensions
int d;

// prototypes
void clear(void);
void greet(void);
void init(int board[d][d]);
void draw(int board[d][d]);
bool move(int board[d][d], int tile);
bool won(int board[d][d]);

int main(int argc, string argv[])
{
    // ensure proper usage
    if (argc != 2)
    {
        printf("Usage: fifteen d\n");
        return 1;
    }

    // ensure valid dimensions
    d = atoi(argv[1]);
    if (d < DIM_MIN || d > DIM_MAX)
    {
        printf("Board must be between %i x %i and %i x %i, inclusive.\n",
            DIM_MIN, DIM_MIN, DIM_MAX, DIM_MAX);
        return 2;
    }

    // open log
    FILE *file = fopen("log.txt", "w");
    if (file == NULL)
    {
        return 3;
    }

    // greet user with instructions
    greet();

    // initialize the board
    int board[d][d];
    init(board);

    // accept moves until game is won
    while (true)
    {
        // clear the screen
        clear();

        // draw the current state of the board
        draw(board);

        // log the current state of the board (for testing)
        for (int i = 0; i < d; i++)
        {
            for (int j = 0; j < d; j++)
            {
                fprintf(file, "%i", board[i][j]);
                if (j < d - 1)
                {
                    fprintf(file, "|");
                }
            }
            fprintf(file, "\n");
        }
        fflush(file);

        // check for win
        if (won(board))
        {
            printf("ftw!\n");
            break;
        }

        // prompt for move
        printf("Tile to move: ");
        int tile = get_int();
        
        // quit if user inputs 0 (for testing)
        if (tile == 0)
        {
            break;
        }

        // log move (for testing)
        fprintf(file, "%i\n", tile);
        fflush(file);

        // move if possible, else report illegality
        if (!move(board, tile))
        {
            printf("\nIllegal move.\n");
            usleep(500000);
        }

        // sleep thread for animation's sake
        usleep(500000);
    }
    
    // close log
    fclose(file);

    // success
    return 0;
}

/**
 * Clears screen using ANSI escape sequences.
 */
void clear(void)
{
    printf("\033[2J");
    printf("\033[%d;%dH", 0, 0);
}

/**
 * Greets player.
 */
void greet(void)
{
    clear();
    printf("WELCOME TO GAME OF FIFTEEN\n");
    usleep(2000000);
}

/**
 * Initializes the game's board with tiles numbered 1 through d*d - 1
 * (i.e., fills 2D array with values but does not actually print them).  
 */
void init(int board[d][d])
{
    // Initialize value to place in board based off of dimensions
    int count = (d*d) - 1;
    
    // Creat the board, step-by-step
    for(int i = 0; i < d; i++)
    {
        for(int j = 0; j < d; j++)
        {
            // If the dimensions' product is even, switch 1 and 2
            if(count == 2 && ((d*d) % 2) == 0)
            {
                board[i][j] = 1;
                board[i][j + 1] = 2;
                board[i][j + 2] = 0;
                break;
            }
            
            // Store the counter variable in the board and decrease the counter.
            board[i][j] = count;
            count--;
        }
    }
}

/**
 * Prints the board in its current state.
 */
void draw(int board[d][d])
{
    // Nested loop used to move through grid.
    for(int i = 0; i < d; i++)
    {
        for(int j = 0; j < d; j++)
        {
            // Checking for "blank space", AKA 0.
            if(board[i][j] == 0)
            {
                printf(" %c ", 95);
            }
            // Print extra space for single digit numbers to properly align board.
            else if(board[i][j] < 10)
            {
                printf(" %i ", board[i][j]);
            }
            // Print without extra space for all other numbers.
            else
            {
                printf("%i ", board[i][j]);
            }
        }
        
        // When row finishes, start new row in terminal.
        printf("\n");
    }
    
}

/**
 * If tile borders empty space, moves tile and returns true, else
 * returns false. 
 */
bool move(int board[d][d], int tile)
{
     // Linear search to find tile
     for(int i = 0; i < d; i++)
     {
         for(int j = 0; j < d; j++)
         {
             if(board[i][j] == tile)
             {
                // Conditionals to check if the tiles around the selected tile are the blank tile.
                // Accounts for edge cases so as not to check out of array bounds. 
                // Above
                if(i != 0 && board[i - 1][j] == 0)
                {
                    board[i - 1][j] = tile;
                    board[i][j] = 0;
                    return true;
                }
                // Below
                if(i != (d-1) && board[i + 1][j] == 0)
                {
                    board[i + 1][j] = tile;
                    board[i][j] = 0;
                    return true;
                    
                }
                // Left
                if(j != 0 && board[i][j - 1] == 0)
                {
                    board[i][j - 1] = tile;
                    board[i][j] = 0;
                    return true;
                }
                // Right
                if(j != (d-1) && board[i][j + 1] == 0)
                {
                    board[i][j + 1] = tile;
                    board[i][j] = 0;
                    return true;
                }
             }
         }
         
     }
    return false;
}

/**
 * Returns true if game is won (i.e., board is in winning configuration), 
 * else false.
 */
bool won(int board[d][d])
{
    // Initializing counter variable to compare board. 
    int count = 1;
    
    // Iterate through board for checking validity. 
    for(int i = 0; i < d; i++)
    {
        for(int j = 0; j < d; j++)
        {
            // When the counter has reached the product of board dimensions, the user must be right.
            if(count == (d*d))
            {
                return true;
            }
            // If the counter doesn't match what it should in the board, at any point.
            else if(count != board[i][j])
            {
                return false;
            }
            
            count++;
        }
    }
    return false;
}
