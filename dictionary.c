/**
 * Implements a dictionary's functionality.
 * Help in creating trie received from: http://www.geeksforgeeks.org/trie-insert-and-search/
 */

#include <stdbool.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>

#include "dictionary.h"



// define structure for trie node
typedef struct node
{
    bool is_word;
    struct node *children[27];
} 
node;

// function to get a new node, initialized to NULL values
struct node *getNode(void)
{
    // make a new pointer to a node
    struct node *pNode = NULL;
    
    // create room on the heap for the pointer
    pNode = (struct node *)malloc(sizeof(struct node));
    if (pNode == NULL)
    {
        printf("Could not allocate memory for node in dictionary\n");
        return false;
    }
    
    // initialize values in the new node
    if (pNode)
    {
        pNode->is_word = false;
        
        for (int i = 0; i < 27; i++)
            pNode->children[i] = NULL;
    }
    return pNode;
}

// global variables
node *root = NULL;
unsigned int dictionary_size;

/**
 * Returns true if word is in dictionary else false.
 */
bool check(const char *word)
{
    // get ready to check each letter of the word, moving through our trie
    int word_size = strlen(word);
    node *trav = root;
    int n;
    
    // for each letter in input word
    for (int i = 0; i < word_size; i++)
    {
        // a letter was found, convert from ASCII to 1-26
        if (isalpha(word[i]))
        {
            // deals with uppercase/lowercase 
            if (word[i] < 97)
                n = word[i] % 65;
            else
                n = word[i] % 97;
        }
        
        // an apostrophe was found, convert from ASCII to 27th character         
        else if (word[i] == '\'')
            n = 26;
        
        // go to corresponding element in children
        trav = trav->children[n];
        
        // if the pointer is NULL, word is misspelled
        if (trav == NULL)
            return false;
        
        // if not NULL, move to next letter
    }
    
    // once at end of input word, check if is_word is true
    if (trav->is_word)
        return true;
    else
        return false;
}

/**
 * Loads dictionary into memory. Returns true if successful else false.
 * Implemented as a trie
 */
bool load(const char *dictionary)
{
    // open the file for dictionary
    FILE *source = fopen(dictionary, "r");
    if (source == NULL)
    {
        printf("Could not open %s.\n", dictionary);
        unload();
        return false;
    }
    
    // prepare to store words
    char word[LENGTH];
    int n;
    node *trav = NULL;
    
    // initialize root node branches to null
    root = getNode();
    
    // scan for word in dictionary
    while (fscanf(source,"%s", word) != EOF)
    {
        // reset the traversal pointer to the root   
        trav = root;
        
        // iterate through the word
        for (int size = strlen(word), index = 0; index < size; index++)
        {
            // a letter was found, convert from ASCII to 1-26
            if (isalpha(word[index]))
                n = word[index] % 97;
            
            // an apostrophe was found, convert from ASCII to 27th character         
            else if (word[index] == '\'')
                n = 26;
            
            // child node doesn't exist, make it
            if (trav->children[n] == NULL)
                trav->children[n] = getNode();
            
            // then look to the next pointer
            trav = trav->children[n];
        }
        
        // after the last char, set the current node to mark a word        
        trav->is_word = true;
        
        // count what number word this was
        dictionary_size++;
    }
   
    return true;
}

/**
 * Returns number of words in dictionary if loaded else 0 if not yet loaded.
 */
unsigned int size(void)
{
    return dictionary_size;
}

/**
 * Clears a node of all branch, leaf, and root.
 */ 
void clear(node* branch)
{
    // clear each of the 27 children
    for (int i = 0; i < 27; i++)
    {
        if (branch->children[i] != NULL)
            clear(branch->children[i]);
    }    
    
    // free the root
    free(branch);
}

/**
 * Unloads dictionary from memory. Returns true if successful else false.
 */
bool unload(void)
{
    // call the clear function
    clear(root);
 
    return true;
}

