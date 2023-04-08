import sys
import numpy
import random
import copy

# GLOBAL GRID PARAMETERS
horizontal = 1
vertical = 1
terminals = []
mdpTerminals = []
boulders = []
mdpBoulders = []
start = []
state = []
k = 0
episodes = 0
mdpk = 0
rlepisodes = 0
mdcoord = []
rlcoord = []
mdcommand = []
rlcommand = []
discount = 1
alpha = 0.5
noise = 0
transition = 0


def readGridFile(file):
    global horizontal, vertical, k, episodes, discount, alpha, noise, transition, state

    # GRID DIMENSIONS
    # Gets first two lines and reads them to get horizontal and vertical dimensions of grid
    line = file.readline().split("=")
    horizontal = int(line[1].replace("\n", ""))
    line = file.readline().split("=")
    vertical = int(line[1].replace("\n", ""))

    # STATES
    # Gets terminal states
    # Splits line on "{" to make a list and loops through each of its entries
    line = file.readline().split("{")
    for i in range(2, len(line)):
        # Each list element is split on "}" and pops the first element of the result
        state = line[i].split("}").pop(0)

        # Splits state on ","" to get elements and converts them all to ints
        state = state.split(",")
        # Translates the horizontal and vertical notation to row and column notation
        mdpState = copy.deepcopy(state)
        state[0], state[1] = state[1], state[0]
        mdpState[0], mdpState[1] = (vertical - 1) - int(mdpState[1]), mdpState[0]
        state = [int(i) for i in state]
        mdpState = [int(i) for i in mdpState]
        # Appends modified state list to the terminals list
        terminals.append(state)
        # MdpTerminals contains the translated coordinates of the terminal states
        mdpTerminals.append(mdpState)

    # Gets boulder states
    line = file.readline().split("{")  # Splits line on "{" to make a list
    for i in range(2, len(line)):
        # Each list element is split on "}" and pops the first element of the result
        state = line[i].split("}").pop(0)

        # Splits state on ","" to get elements and converts them all to ints
        state = state.split(",")
        mdpState = copy.deepcopy(state)
        # Translates from horizontal and vertical to row and column again
        mdpState[0], mdpState[1] = (vertical - 1) - int(mdpState[1]), mdpState[0]
        state = [int(i) for i in state]

        mdpState = [int(i) for i in mdpState]

        state[0], state[1] = state[1], state[0]

        # Appends modified state list to the boulders list
        boulders.append(state)
        # Appends translated coordinates list to mdpBoulders list
        mdpBoulders.append(mdpState)

    # Gets start state
    # Reads in line and splits string on curly braces
    # Then splits on ',' to get the two coordinates of the starte state and appends them
    line = file.readline().split("{")
    state = line[1].split("}")[0].split(",")
    start.append(int(state[1]))
    start.append(int(state[0]))
    state = start  # Initializes the state to the starting state of our robot

    # MODEL PARAMETERS
    # Gets integers for remaining model paramters
    line = file.readline().split("=")
    k = int(line[1].replace("\n", ""))  # K (Depth)
    line = file.readline().split("=")
    episodes = int(line[1].replace("\n", ""))  # Number of Episodes
    line = file.readline().split("=")
    discount = float(line[1].replace("\n", ""))  # Discount
    line = file.readline().split("=")
    alpha = float(line[1].replace("\n", ""))  # alpha
    line = file.readline().split("=")
    noise = float(line[1].replace("\n", ""))  # Noise
    line = file.readline().split("=")
    transition = float(line[1].replace("\n", ""))  # Transition Cost

# Reads in the result.txt file used for evaluating various queries
# Processes the queries into two lists, one for MDP and one for RL
def readResultFile(file):
    global mdcommand, rlcommand
    for line in file:
        line = line.split(',')
        line[4] = line[4].strip('\n')
        if line[3] == 'MDP':
            mdcommand.append(line)
        elif line[3] == 'RL':
            rlcommand.append(line)

# Processes the queries in the mdcommand list
# Executes value iteration for mdpk steps
# Appends the result of each MDP query to the command
def runMDPQuery(grid):
    global mdpk, mdcoord, mdcommand, k, vertical
    # Translates from horizontal and vertical notation to row and column notation
    row = (vertical - 1) - int(mdcommand[0][1])
    col = int(mdcommand[0][0])
    # Sets the number of iterations it should process, given from the query
    mdpk = int(mdcommand[0][2])
    # Runs the value iteration for mdpk steps
    valueGrid, policyGrid = valueIterationAgent(grid, mdpk)
    # Translates the policy grid result to plain english
    match policyGrid[row][col]:
        case '←':
            mdcommand[1].append('Go West')
        case '↑':
            mdcommand[1].append('Go North')
        case '→':
            mdcommand[1].append('Go East')
        case '↓':
            mdcommand[1].append('Go South')
        case 'E':
            mdcommand[1].append('Exit')

    # Appends the value of the specified cell here
    mdcommand[0].append(valueGrid[row][col])

def getGrid():
    # Grid to be built
    grid = []
    row = []

    # Instantiates grid
    for i in range(horizontal):
        row.append(0)
    for i in range(vertical):
        grid.append(list(row))

    # Assigns the states given in global lists
    for state in mdpTerminals:
        grid[state[0]][state[1]] = state[2]

    # Assigns boulder states
    for state in mdpBoulders:
        grid[state[0]][state[1]] = "#"

    # Returns completed grid
    return grid


def printGrid(grid):
    for i in range(vertical):
        print(grid[i])


# Helper function for properly addressing the action taken in the next iteration or episode
# Takes into account noise
def actualAction(action):
    # 1 = east 2 = north 3 = west 4 = south
    actionVal = 0
    match action:
        case 1:
            actionVal = numpy.random.choice([1, 2, 4], p=[1 - noise, noise / 2, noise / 2])
        case 2:
            actionVal = numpy.random.choice([2, 1, 3], p=[1 - noise, noise / 2, noise / 2])
        case 3:
            actionVal = numpy.random.choice([3, 2, 4], p=[1 - noise, noise / 2, noise / 2])
        case 4:
            actionVal = numpy.random.choice([4, 3, 1], p=[1 - noise, noise / 2, noise / 2])
    return actionVal

# Returns a list of the possible actions that can be taken given the chosen action
# Rule being, one cannot go in the opposite direction they've chosen
def getPossibleActions(action):
    # 1 = east 2 = north 3 = west 4 = south
    actions = []
    match action:
        case 1:
            actions.append(1)
            actions.append(2)
            actions.append(4)
        case 2:
            actions.append(2)
            actions.append(1)
            actions.append(3)
        case 3:
            actions.append(3)
            actions.append(2)
            actions.append(4)
        case 4:
            actions.append(4)
            actions.append(3)
            actions.append(1)
    return actions


# This determines the next state for the RL/Q value part of the algorithm
def newState(state, action):
    # 1 = east 2 = north 3 = west 4 = south
    match action:
        case 1:
            if state[1] + 1 >= horizontal:
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
            if state[0] + 1 >= vertical:
                nextState = state
            else:
                nextState = [state[0] + 1, state[1]]

    # Checks if next state is a rock, if so state is set back to original state, not having moved
    for rocks in boulders:
        if rocks == nextState:
            nextState = state
    return nextState

# Returns the value for the given state, returns 0 if a boulder is passed, which is shouldn't
def getValueFromState(grid, state):
    if grid[state[0]][state[1]] != '#':
        return grid[state[0]][state[1]]
    return 0

# Function that grabs the safest action away from the minimal value
# Used to combat policy from suggesting we walk into a negative terminal state
# Effectively returns the opposite action from the given action
def grabSafeAction(action):
    # 1 = east 2 = north 3 = west 4 = south
    safe = 0
    match action:
        case 1:
            safe = 3
        case 2:
            safe = 4
        case 3:
            safe = 1
        case 4:
            safe = 2
    return safe

# Computes the action we should take given the values available to us in this state
def computeActionFromValues(grid, state):
    actions = []
    actionVals = []
    # We get a list of all states we visit in all 4 directions
    for i in range(4):
        nextState = newState(state, i + 1)
        actions.append(nextState)
    # We iterate over all of these states, determining their values
    for actionState in actions:
        val = getValueFromState(grid, actionState)
        actionVals.append(val)
    # Here we determine our final action based on the index of the highest value returned from visiting a state
    finalAction = actionVals.index(max(actionVals)) + 1
    maxVal = max(actionVals)
    tie = []
    # If there are identical max values we append them here
    for test in actionVals:
        if test == maxVal:
            tie.append(test)
    # If there are more than 2 identical max values, this means there is only one way to proceed to avoid the min value
    # The opposite direction of the minimum value given from the states
    if len(tie) > 2:
        minAction = min(actionVals) + 1
        finalAction = grabSafeAction(minAction) + 1
    return finalAction

# Computes the value we are going to assign this state after this iteration of value iteration
def computeQValueFromValues(grid, state, action):
    global noise, transition, discount
    reachedStates = []
    values = []
    # Grabs all the possible actions from this action direction
    actions = getPossibleActions(action)
    # Iterates through them, appending the states we reach into the reachedStates list
    for nextAction in actions:
        reachedStates.append(newState(state, nextAction))
    # Iterates through the reached states, appending their values to values list
    for reachedState in reachedStates:
        values.append(getValueFromState(grid, reachedState))

    # Calculates the value to assign this state from the summation of all possible actions' states
    # This is just the bellman equation
    valueForThisState = (1-noise)*(transition + (discount*values[0])) + (noise/2)*(transition + (discount*values[1])) + (noise/2)*(transition + (discount*values[2]))
    return valueForThisState


# ValueIterationAgent for this assignment
def valueIterationAgent(grid, iterations):
    global  horizontal, vertical, discount, transition, boulders, terminals
    policyGrid = []
    for i in range(iterations):
        # We preserve the original states of the grid and clone to update for the next iteration
        newGrid = copy.deepcopy(grid)
        policy = copy.deepcopy(newGrid)
        for row in range(vertical):
            for col in range(horizontal):
                isTerm = terminalCheckMDP([row, col])
                # If the state isn't a boulder or a terminal state, we perform calculations
                if newGrid[row][col] != '#' and isTerm is False:
                    newAction = computeActionFromValues(grid, [row, col])
                    # 1 = east 2 = north 3 = west 4 = south
                    match newAction:
                        case 1:
                            policy[row][col] = '→'
                        case 2:
                            policy[row][col] = '↑'
                        case 3:
                            policy[row][col] = '←'
                        case 4:
                            policy[row][col] = '↓'

                    newValue = computeQValueFromValues(grid, [row, col], newAction)
                    # Rounds the values to 3 decimal points
                    newGrid[row][col] = round(newValue,3)
                elif isTerm is True:
                    policy[row][col] = 'E'
        grid = copy.deepcopy(newGrid)
        policyGrid = copy.deepcopy(policy)
    return grid, policyGrid

#Checks if a state is a terminal state
def terminalCheck(curr):
    result = False
    for terminalState in terminals:
        if curr[0:2] == terminalState[0:2]:
            result = True

    return result

#Checks if a state is a terminal state, using translated coordinates
def terminalCheckMDP(curr):
    result = False
    for terminalState in mdpTerminals:
        if curr[0:2] == terminalState[0:2]:
            result = True

    return result

#Returns a new action for the robot to take
#Gets an action based onm the exploration policy, and adds random noise to it before returning
def getAction():
    action = numpy.random.choice([1, 2, 3, 4])
    action = actualAction(action)
    return action

#Optional method call
#Takes in a q value grid and rounds the values to 3 decimal places
#Usefull for readability during output, butfor accuracy do not call until output is needed
def roundQvalues(values):
    decNum = 3

    for row in values:
        for entry in range(horizontal):
            if type(row[entry]) is list:
                for i in range(4):
                    row[entry][i] = round(row[entry][i], decNum)
            elif type(row[entry]) is float:
                row[entry] = round(row[entry], decNum)



# Returns an updated q(s, a) for an action a from s
# The parameters are:
#   qValue --> The current value of q(s, a) to be changed, this is an int
#   reward --> The reward of s', the state we wnd up in, this is an int
#   nextState --> A list of all of a state s' q values
def updateQValue(qValue, reward, nextState):
    #Case 1: state is a regular state, take the best q value
    if type(nextState) is list:
        return (1 - alpha) * qValue + alpha * (reward + discount * max(nextState))
    
    #Case 2: State is a terminal state and only has one 1 value
    else:
        return (1 - alpha)*qValue + alpha*(reward + discount*nextState) 

#Returns a grid that contains the best policy for a q value grid
#Gets the max q value for each empty cell and assigns it a direction
def getQPolicy(grid):
    output = copy.deepcopy(grid)

    #Creates output table
    for i in range(vertical):
        for k in range(horizontal):
            entry = grid[i][k]

            #Case 1: i, k is an empty state
            if type(grid[i][k]) is list:

                #Gets max value of q values and gets list of all the occurences of it
                #If there is only one max, then it is chosen for the policy
                #If there is more then one, then one is randomly chosen
                value = max(entry)
                indexes = [i for i, j in enumerate(entry) if j == value]
                indexes = random.choice(indexes) + 1

                #Gives direction arrow based on index picked
                match indexes:
                    case 1:
                        output[i][k] = '→'
                    case 2:
                        output[i][k] = '↑'
                    case 3:
                        output[i][k] = '←'
                    case 4:
                        output[i][k] = '↓'

            #Case 2: i, k is a rock
            elif entry == None:
                output[i][k] = '#'

            #Case 3: i, k is a terminal state
            else:
                output[i][k] = 'E'

    return output

#Takes in a qvalue grid that indexes starting at 0, 0, and reverses it vertivally to start from (0, vertical - 1)
def reverseQGrid(grid):
    #Step 1: Inverts row order
    grid.reverse()

    #Step 2: Swaps north and south q values
    for row in grid:
        for values in row:
            if type(values) is list:
                values[1], values[3] = values[3], values[1]
 
#Implements the qlearning algorithm
#Creates a q value grid world and runs the number of episodes given in the file
#At the enp rpints out the final values and the best policy
def qLearning():
    # Stored dictionary of q values for each state
    # Stored as [State][Action - 1] where state = [x, y]
    qValues = []
    qRow = []

    #Keep track of current and next state during processing
    currState = []
    nextState = []

    #Processes first 3 parts of rl command and parses them to numbers
    for entries in rlcommand:
        entries[0] = int(entries[0])
        entries[1] = int(entries[1])
        entries[2] = int(entries[2])

    #Stores list of time steps from result.txt to stop processing to query the current state of the machine
    stopList = [sublist[2] for sublist in rlcommand]

    #Keeps track of the episode we are on
    currEpisode = 1

    #Instantiates q value grid
    #Indexed by a state (x, y) for location and stores a list of qvalues
    #List contains q values according to the action index - 1 (Ex: North is 2, but is stored as 1 in list ect)
    for i in range(horizontal):
        qRow.append(0)
    for i in range(vertical):
        qValues.append(list(qRow))
    for i in range(horizontal):
        for k in range(vertical):
            qValues[i][k] = [0, 0, 0, 0]

    # Sets Terminal states to only have 1 q value as there is only one action there
    for term in terminals:
        qValues[term[0]][term[1]] = 0

    #Sets boulder locations to contain no values
    for b in boulders:
        qValues[b[0]][b[1]] = None

    # Sets current state to start state
    currState.append(start[0])
    currState.append(start[1])

    #Takes random action and checks
    while currEpisode <= episodes:
        #If current state is an exit state, only option is to exit
        if terminalCheck(currState):
            terminal = []

            #Gets the terminal state at currstate
            for terminalState in terminals:
                if currState[0:2] == terminalState[0:2]:
                    terminal = terminalState

            #Updates predicted qvalue of terminal state
            qValues[currState[0]][currState[1]] = (1 - alpha) * qValues[currState[0]][currState[1]] + alpha*terminal[2]

            # Resets start state
            currState = []
            currState.append(start[0])
            currState.append(start[1])

            #Increments episode counter
            currEpisode += 1

            #Checks if previously completed episodes is one of the stop points
            #If so loops through each command matching the time stamp and processes its query
            #Answer is appended to the command (Will be stored under index 5)
            if(currEpisode - 1 in stopList):
                for command in rlcommand:
                    if command[2] == currEpisode - 1:
                        #Gets the entry of the qvalue matrix equal to the coordanites given and matches the query
                        entry = qValues[command[1]][command[0]]
                        match command[4]:
                            #Gets the best q value for the passed coordanites
                            case "bestQValue":
                                if type(entry) is list:
                                    command.append(max(entry))
                                else:
                                    command.append(entry)
                            #Gets the best policy for the passed coordanates
                            case "bestPolicy":
                                #Gets the best policy from list of q values
                                #If 2 values tie, one is randomly selected
                                if type(entry) is list:
                                    value = max(entry)
                                    indexes = [i for i, j in enumerate(entry) if j == value]
                                    indexes = random.choice(indexes) + 1
                                    match indexes:
                                        case 1:
                                            command.append("Go East")
                                        case 2:
                                            command.append("Go South")
                                        case 3:
                                            command.append("Go West")
                                        case 4:
                                            command.append("Go North")
                                    
                                else:
                                    command.append("Exit")

        #Else, moves through world and gets state values
        else:
            # Choose action
            action = getAction()

            # Gets destination state
            nextState = newState(currState, action)

            #Update q value
            qValues[currState[0]][currState[1]][action-1] = updateQValue(qValues[currState[0]][currState[1]][action - 1], transition, qValues[nextState[0]][nextState[1]])
            currState = nextState
    
    #Reverses grid to the preferred orientation
    reverseQGrid(qValues)

    #Rounds q values to 2 decimal places for output
    roundQvalues(qValues)

    #Prints final q value grid
    print("Q Value Grid: ")
    printGrid(qValues)
    print("Optimal Policy Grid: ")
    printGrid(getQPolicy(qValues))
    print()


if __name__ == "__main__":
    # Opens files given on command line
    print("Opening files:")
    gridFile = open(sys.argv[1])
    resultFile = open(sys.argv[2])

    # Gets the parameters from the grid file and stores them
    print("Reading Grid Configuration File:")
    readGridFile(gridFile)
    readResultFile(resultFile)

    # Reads file in and constructs the grid
    print("Constructing Gridworld:")
    grid = getGrid()
    queryGrid = copy.deepcopy(grid)
    printGrid(grid)

    # Starts Value Iteration

    print("Starting Value Iteration")
    mdpgrid, policyGrid = valueIterationAgent(grid, k)

    print("State Value Grid:")
    printGrid(mdpgrid)
    print("Optimal Policy Grid:")

    printGrid(policyGrid)

    # Starts QLearning
    print("Starting Q Learning")
    qLearning()

    #mdp query handling
    #grid = getGrid()

    runMDPQuery(grid)
    print("Value iteration query results:")
    for mdpResult in mdcommand:
        print(mdpResult)

    #Outputs RL Queries
    print("Q Learning Answers")
    for ans in rlcommand:
        print(ans)


    # Closes files
    gridFile.close()
