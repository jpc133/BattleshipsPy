import random
import os
import winsound

emptySquareChar = "-"
missChar = "M"
hitChar = "H"
killChar = "$" #Used in board[0][0] to denote user wanting to quit
announceShipHit = False
limitedAmmo = False
MaxRounds = 20 #Used as turn limit when limitedAmmo = True
extendedShips = False #When True a frigate is added, it's a length 3 ship with symbol F
enableRadar = True #When true if a 3x3 grid centered on a guess contains a ship a near miss message is displayed

""" Returns a 2D Array of given dimensions """
def SetUpBoard(size):
    board = []
    for x in range(size):
        board.append([])
        for y in range(size):
            board[x].append(emptySquareChar)
    return board

""" Returns an array of ships, a ship is an array of a [name,length,symbol] """
def SetUpShips():
    ships = []
    ships.append(["Aircraft Carrier",5,"A"])
    ships.append(["Battleship",4,"B"])
    ships.append(["Submarine",3,"S"])
    ships.append(["Destroyer",3,"D"])
    ships.append(["Patrol Boat",2,"P"])
    if extendedShips == True:
        ships.append(["Frigate",3,"F"])
    return ships

""" Displays the menu, used with GetMainMenuChoice """
def DisplayMenu():
    print("1: Start new game")
    print("2: Load training game")
    print("3: Load game")
    print("9: Quit")

""" Gets the selected option on the main menu and makes sure it's valid, used with display menu """
def GetMainMenuChoice():
    while True:
        inputNum = input()
        if inputNum.isdigit():
            if int(inputNum) in [1,2,3,9]:
                return int(inputNum)
        print("Invalid choice, please enter a single number to pick the option")

""" Places all the ships given in 'ships' on a given 'board', all placements are valid - if valid placement is impossible an error is thrown """
def PlaceRandomShips(board,ships):
    size = len(board)
    for i in range(len(ships)):
        validDetails = []
        valid = False
        while valid == False:
            randx = random.randint(0,size-1)
            randy = random.randint(0,size-1)
            randorientation = random.randint(1,2)
            if randorientation == 1:
                randorientation = "Vertical"
            else:
                randorientation = "Horizontal"
            valid = ValidateBoatPosition(ships[i],[randx,randy],randorientation,board)
            if valid == True:
                validDetails = [ships[i],[randx,randy],randorientation]
        board = PlaceShip(validDetails[0],validDetails[1],validDetails[2],board)
    return board

""" returns bool Validates a ship can be placed at a given location on the board, e.g. no intersections """
def ValidateBoatPosition(ship,position,orientation,board):
    size = len(board)
    for z in range(ship[1]):
        if(orientation == "Vertical"):
            if position[1]+z > size-1:
                return False
            if board[position[0]][position[1]+z] != emptySquareChar:
                return False
        else:
            if position[0]+z > size-1:
                return False
            if board[position[0]+z][position[1]] != emptySquareChar:
                return False
    return True

""" Returns board, Places a ship, the locations validity isn't checked so it may overwrite existing ships """
def PlaceShip(ship,position,orientation,board):
    for z in range(ship[1]):
        if(orientation == "Vertical"):
            board[position[0]][position[1]+z] = ship[2]
        else:
            board[position[0]+z][position[1]] = ship[2]
    return board

""" Prints a given board of any square dimensions """
def PrintBoard(board):
    size = len(board)

    locationLine = "  "
    for i in range(size):
        locationLine += " " + str(i)
    print(locationLine)

    for y in range(size):
        curLine = ""
        for x in range(size):
            if board[x][y] == missChar:
                curLine += '\033[92m' + " " + missChar + '\033[0m'
                continue
            if board[x][y] == hitChar:
                curLine += '\033[91m' + " " + hitChar + '\033[0m'
                continue
            curLine += '\033[94m' + " " + emptySquareChar + '\033[0m'
        print(str(y) + " " + curLine)
    

""" Validates and then makes a player move on a given board """
def MakePlayerMove(board,ships):
    size = len(board)
    valid = False
    guessPos = []
    while valid == False:
        print("Please make a move in the form x,y or S to save, Q to quit")
        guess = input()
        if guess == "S":
            print("Please provide a filename for your save file")
            filename = input()
            SaveGame(filename,board)
        if guess == "Q":
            board[0][0] = killChar
            return board
        if guess.find(",") == -1:
            continue
        parts = guess.split(",")
        if not parts[0].isnumeric():
            continue
        if not parts[1].isnumeric():
            continue
        parts[0] = int(parts[0])
        parts[1] = int(parts[1])
        if parts[0] < 0 or parts[0] > size-1:
            continue
        if parts[1] < 0 or parts[1] > size-1:
            continue
        guessPos = [int(parts[0]),int(parts[1])]
        valid = True
    hitShip = True
    os.system("cls")
    if board[guessPos[0]][guessPos[1]] == emptySquareChar:
        print("Miss")
        hitShip = False
    if board[guessPos[0]][guessPos[1]] == missChar:
        print("Hit a previous miss!")
        hitShip = False
    if board[guessPos[0]][guessPos[1]] == hitChar:
        print("Hit a previous hit")
        hitShip = False
    if hitShip == True:
        shipHit = "Ghost Ship (ERROR OCCURRED)"
        for i in range(len(ships)):
            if ships[i][2] == board[guessPos[0]][guessPos[1]]:
                shipHit = ships[i][0]
        if announceShipHit:
            print("You hit a " + shipHit)
        else:
            print("Hit!")

    if hitShip == False:
        if HitRadar([guessPos[0],guessPos[1]],board):
            print("Enemy Near!")
        else:
            print("All quiet")

    if hitShip == True and (board[guessPos[0]][guessPos[1]] != hitChar and board[guessPos[0]][guessPos[1]] != missChar):
        board[guessPos[0]][guessPos[1]] = hitChar
        #http://soundbible.com/1986-Bomb-Exploding.html
        winsound.PlaySound("BombSound2.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
    elif hitShip == False and (board[guessPos[0]][guessPos[1]] != hitChar and board[guessPos[0]][guessPos[1]] != missChar):
        board[guessPos[0]][guessPos[1]] = missChar
        winsound.PlaySound("MissileSound2.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)

    return board

""" Returns bool, checks whether a board only contains blanks, misses and hits """
def CheckWin(board):
    size = len(board)
    for x in range(size):
        for y in range(size):
            if board[x][y] not in [emptySquareChar,missChar,hitChar]:
                return False
            else:
                continue
    return True

""" Checks the 3x3 grid centered on position in board for ships, returns true if a ship was found """
def HitRadar(position, board):
    size = len(board)
    surrounding = ""
    #Top Left
    if position[0] > 0 and position[1] > 0:
        surrounding += board[position[0]-1][position[1]-1]
    #Top
    if position[1] > 0:
        surrounding += board[position[0]][position[1]-1]
    #Top Right
    if position[0]+1 < size and position[1] > 0:
        surrounding += board[position[0]+1][position[1]-1]
    #Left
    if position[0] > 0:
        surrounding += board[position[0]-1][position[1]]
    #Center
    #Doesn't need to be checked
    #Right
    if position[0]+1 < size:
        surrounding += board[position[0]+1][position[1]]
    #Bottom Left
    if position[0] > 0 and position[1]+1 < size:
        surrounding += board[position[0]-1][position[1]+1]
    #Bottom Center
    if position[1]+1 < size:
        surrounding += board[position[0]][position[1]+1]
    #Bottom Right
    if position[0]+1 < size and position[1]+1 < size:
        surrounding += board[position[0]][position[1]+1]
    if(len(surrounding.replace(emptySquareChar ,"").replace(hitChar,"").replace(missChar,"")) > 0):
        return True
    else:
        return False

""" Starts a battleship game where the player tries to guess where randomly placed ships are, takes a board and ships in there can be created using SetUpBoard and SetUpShips """
def PlayGame(board,ships):
    gameWon = False
    moves = 0
    while gameWon == False:
        PrintBoard(board)
        MakePlayerMove(board,ships)
        if board[0][0] == "$":
            print("Quitting game!")
            return
        moves = moves + 1
        gameWon = CheckWin(board)
        if limitedAmmo == True and moves >= MaxRounds:
            #http://soundbible.com/1830-Sad-Trombone.html
            winsound.PlaySound("SadTrombone.wav",winsound.SND_FILENAME | winsound.SND_ASYNC)
            PrintBoard(board)
            print("GAME OVER! You ran out of ammo!")
            break
    if gameWon:
        #http://soundbible.com/1003-Ta-Da.html
        winsound.PlaySound("TaDaSound.wav",winsound.SND_FILENAME | winsound.SND_ASYNC)
        PrintBoard(board)
        print("You've sunk all the ships! it took you " + str(moves) + " moves")

""" Loads a board from a given file and returns it """
def LoadGame(filename):
    file = open(filename,"r")
    lines = file.readlines()
    board = []
    for line in lines:
        board.append(list(line))
    file.close()
    return board

def SaveGame(filename,board):
    try:
        file = open(filename,"x")
        file.writelines(GetSaveableBoard(board))
        file.close()
        print("Saved")
        return
    except FileExistsError:
        while True:
            print("File exists, Do you want to overwrite it? Y/N")
            answer = input()
            if answer == "Y":
                file = open(filename,"a")
                file.truncate(0)
                file.writelines(GetSaveableBoard(board))
                print("Saved")
                return
            if answer == "N":
                while True:
                    print("Do you want to provide a different file name? Y/N")
                    answer2 = input()
                    if answer2 == "Y":
                        filenameNew = input()
                        SaveGame(filenameNew,board)
                        return
                    if answer2 == "N":
                        print("Didn't save file")
                        return

def GetSaveableBoard(board):
    size = len(board)
    lines = []
    for y in range(size):
        curLine = ""
        for x in range(size):
            curLine += board[x][y]
        lines.append(curLine+"\n")
    return lines

def Main():
    keepPlaying = True
    while keepPlaying == True:
        board = SetUpBoard(10)
        ships = SetUpShips()

        DisplayMenu()
        choice = GetMainMenuChoice()

        #Normal Game
        if choice == 1:
            board = PlaceRandomShips(board,ships)
            PlayGame(board,ships)
        #Training Game
        if choice == 2:
            board = LoadGame("training.txt")
            PlayGame(board,ships)
        if choice == 3:
            valid = False
            while valid == False:
                print("Please enter a filename")
                filename = input()
                valid = os.path.exists(filename)
                if valid == True:
                    board = LoadGame(filename)
                    PlayGame(board,ships)
                else:
                    print("File not found")      
        #End
        if choice == 9:
            print("Exit? Are you sure? Y/N")
            if input() == "Y":
                keepPlaying = False

Main()