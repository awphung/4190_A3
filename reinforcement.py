import sys
import numpy
import random

#GLOBAL GRID PARAMETERS
horizontal = 1
vertical = 1
terminals = []
boulders = []
start = []
state = []
#nextState = []
k = 0
episodes = 0
discount = 1
alpha = 0.5
noise = 0
transition = 0

def readGridFile(file):
    global horizontal, vertical, k, episodes, discount, alpha, noise, transition, state

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
    state = start #Initializes the state to the starting state of our robot

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

#helper function for properly addressing the action taken in the next iteration or episode
def actualAction(action):
    #1 = east 2 = north 3 = west 4 = south
    actionVal = 0
    match action:
        case 1:
            actionVal = numpy.random.choice([1, 2, 4], p=[1-noise, noise/2, noise/2])
        case 2:
            actionVal = numpy.random.choice([2, 1, 3], p=[1-noise, noise/2, noise/2])
        case 3:
            actionVal = numpy.random.choice([3, 2, 4], p=[1-noise, noise/2, noise/2])
        case 4:
            actionVal = numpy.random.choice([4, 3, 1], p=[1-noise, noise/2, noise/2])
    return actionVal

#this determines the next state for the RL/Q value part of this, WIP
def newState(state, action):
    # 1 = east 2 = north 3 = west 4 = south
    match action:
        case 1:
            if state[1] + 1 > horizontal:
                nextState = state
            else:
                nextState = [state[0], state[1] + 1]
        case 2:
            if state[0] - 1 < 0:
                nextState = state
            else:
                nextState = [state[0] - 1, state[1]]
        case 3:
            if state[1] - 1 < 0:
                nextState = state
            else:
                nextState = [state[0], state[1] - 1]
        case 4:
            if state[0] + 1 > vertical:
                nextState = state
            else:
                nextState = [state[0] + 1, state[1]]
    
    #Checks if next state is a rock, if so state is changed to stay the same
    for rocks in boulders:
        if rocks == nextState:
            nextState = state
    return nextState

#another helper for the RL/Q value part of this assignment
def chooseActionStoch(self):
    return numpy.choice([1, 2, 3, 4])

def chooseActionVIter(self):
    return self

# Helper for the MDP of the assignment
def valueIter(self, k):
    t = 0
    while t < k: #garbage filler code wip
        if self.terminalCheck:
            t = 0
        else:
            t = 0
    return t

def terminalCheck(self):
    for terminalState in terminals:
        if terminalState == self.state:
            return True
        else:
            return False
        
def qLearning():
    #Stored dictionary of q values for each state
    #Stored as [State][Action - 1] where state = [x, y]
    qValues = {}
    myState = []

    #Initalizes q value dictionary
    #Indexed by a state (x, y) for location and stores a list of qvalues
    #List contains q values according to the action index - 1 (Ex: North is 2, but is stored as 1 in list ect)
    for i in range(vertical):
        for k in range(horizontal):
            qValues[(i,k)]=[0,0,0,0]
    
    #Sets current state to start state
    myState.append(start[0])
    myState.append(start[1])

    #Takes random action and checks
    #action = numpy.random.choice([1, 2, 3, 4])
    #action = actualAction(action)
    #print(action)
    myState = newState(myState, 1)
    print(myState)
    
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
    #printGrid(grid)

    #Starts QLearning
    qLearning()

    #Closes files
    gridFile.close()