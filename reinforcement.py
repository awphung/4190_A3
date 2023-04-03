import sys

#GLOBAL GRID PARAMETERS
horizontal = 1
vertical = 1
terminals = []
boulders = []
start = []
k = 0
episodes = 0
discount = 1
alpha = 0.5
noise = 0
transition = 0

def readGridFile(file):
    global horizontal, vertical, k, episodes, discount, alpha, noise, transition 

    #GRID DIMENSIONS
    #Gets first two lines and reads them to get horizontal and vertical dimensions of grid
    line = file.readline().split("=")
    horizontal = int(line[1].replace("\n", ""))
    line = file.readline().split("=")
    vertical = int(line[1].replace("\n", ""))

    #STATES
    #Gets terminal states
    #Splits line on "{" to make a list and loops through each of its entries
    line = file.readline().split("{")
    for i in range(2, len(line)):
        #Each list element is split on "}" and pops the first element of the result
        state = line[i].split("}").pop(0) 

        #Splits state on ","" to get elements and converts them all to ints
        state = state.split(",")
        state = [int(i) for i in state]

        #Appends modified state list to the terminals list
        terminals.append(state) 
    
    #Gets boulder states
    line = file.readline().split("{") #Splits line on "{" to make a list
    for i in range(2, len(line)):
        #Each list element is split on "}" and pops the first element of the result
        state = line[i].split("}").pop(0)

        #Splits state on ","" to get elements and converts them all to ints
        state = state.split(",")
        state = [int(i) for i in state]

        #Appends modified state list to the boulders list
        boulders.append(state)

    #Gets start state
    #Reads in line and splits string on curly braces
    #Then splits on ',' to get the two coordinates of the starte state and appends them
    line = file.readline().split("{")
    state = line[1].split("}")[0].split(",")
    start.append(int(state[0]))
    start.append(int(state[1]))

    #MODEL PARAMETERS
    #Gets integers for remaining model paramters
    line = file.readline().split("=")
    k = int(line[1].replace("\n", ""))            # K (Depth)
    line = file.readline().split("=")
    episodes = int(line[1].replace("\n", ""))     # Number of Episodes
    line = file.readline().split("=")
    discount = float(line[1].replace("\n", ""))   # Discount
    line = file.readline().split("=")
    noise = float(line[1].replace("\n", ""))      # Noise
    line = file.readline().split("=")
    transition = float(line[1].replace("\n", "")) # Transition Cost

#Reads in a passed grid file and constructs the corrisponding grid
def getGrid(file):
    #Grid to be built
    grid = []
    row = []

    #Instantiates grid
    for i in range(horizontal):
        row.append(0)
    for i in range(vertical):
        grid.append(list(row))
    
    #Assigns the states given in global lists
    for state in terminals:
        grid[state[0]][state[1]] = state[2]
    
    #Assigns boulder states
    for state in boulders:
        grid[state[0]][state[1]] = "#"
    
    #Returns completed grid
    return grid

def printGrid(grid):
    for i in range(vertical):
        print(grid[i])

if __name__ == "__main__":
    #Opens files given on command line
    print("Opening files:")
    gridFile = open(sys.argv[1])
    resultFile = ""

    #Gets the parameters from the grid file and stores them
    print("Reading Grid Configuration File:")
    readGridFile(gridFile)

    #Reads file in and constructs the grid
    print("Constructing Gridworld:")
    grid = getGrid(gridFile)
    printGrid(grid)
    
    #Closes files
    gridFile.close()