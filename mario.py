import cs50

def main():
    
    # prompt for the height
    while True:
        print("Height: ", end="")    
        height = cs50.get_int()
        if height < 23 or height > 0:
                break
    pryamid(height)

def pryamid(height):
    
    # counter variables
    s = height - 1
    h = height - s

    # print pryamid 
    for i in range(height):
        
        # print spaces
        print(" " * s, end="")
        
        # print hashes for left pyramind
        print("#" * h, end="")
            
        # print the gap
        print(" ", end="")
        
        # print hashes for right pyramind
        print("#" * h, end="")
    
        # line break
        print()
        
        # increment counters
        s -= 1
        h += 1

if __name__ == "__main__":
    main()