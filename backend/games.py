# Okay, so if you want to make a game, make a self contained function here that can take the target pool as an input
import ctypes
import datetime
import os
import pickle
import random
import sys
import time
from . import targetSend
from .formatters import formatters
from operator import itemgetter


class _CursorInfo(ctypes.Structure):
    """The current state of mr blinky"""
    _fields_ = [("size", ctypes.c_int),
                ("visible", ctypes.c_byte)]

def hide_cursor():
    """Hides the blinky cursor when called"""
    if os.name == 'nt':
        ci = _CursorInfo()
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
        ci.visible = False
        ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))
    elif os.name == 'posix':
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

def show_cursor():
    """Shows the blinky cursor"""
    if os.name == 'nt':
        ci = _CursorInfo()
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
        ci.visible = True
        ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))
    elif os.name == 'posix':
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

def cacheGame(main, huntList, gameType):
    """
    This function takes the final huntList and dumps and serialises until the next time the program runs
    :param main: GameEngine's main class
    :param huntList: the list of pairs/targets for the game
    :param gameType: what's the name of the game?
    :return:
    """
    if not os.path.exists(main.cacheDir):  # if the cache dir doesnt exist, make it
        os.mkdir(main.cacheDir)
    if not os.path.exists("{}/{}".format(main.cacheDir, gameType.lower())):  # make a folder for this game type
        os.mkdir("{}/{}".format(main.cacheDir, gameType.lower()))

    with open("{}/{}/{}.txt".format(main.cacheDir, gameType.lower(), time.strftime("%Y%m%d%H%M%S", time.gmtime())),
              "wb") as fp:
        pickle.dump(huntList, fp)  # serialise and save the current game, LUV U PICKLE <3

    while len(os.listdir("{}/{}".format(main.cacheDir, gameType.lower()))) > main.weeksWithoutRepeat:
        # we only need 6 games history, so kill the rest off
        # aka while we have more than 6 files, delete the oldest file
        oldest_file = min(os.listdir("{}/{}".format(main.cacheDir, gameType.lower())),
                          key=lambda x: datetime.datetime.strptime(
                              time.ctime(
                                  os.path.getctime(os.path.join("{}/{}".format(main.cacheDir, gameType.lower()), x))),
                              '%a %b %d %H:%M:%S %Y'))
        os.unlink("{}/{}/{}".format(main.cacheDir, gameType.lower(), oldest_file))
        

def preventRepeat(main, pair, gameType):
    """
    This function makes sure that the member gets a unique target for at least [weeksWithoutRepeat] weeks
    :param main: GameEngine's main class
    :param pair: the pair of members youre trying not to repeat
    :param gameType: what kind of game is this?
    :return:
    """
    if not os.path.exists("{}/{}".format(main.cacheDir,
                                         gameType.lower())):  # if there isnt a cache folder, this is obviously the first run, and no checks are needed
        return True
    if len(main.pastHunt) == 0:  # if we havent prepared the list yet
        for filename in os.listdir(
                "{}/{}".format(main.cacheDir, gameType.lower())):  # for every file it can find in the cache directory
            with open("{}/{}/{}".format(main.cacheDir, gameType.lower(), filename),
                      'rb') as fp:  # open it in binary-read mode
                temp = pickle.load(fp)  # deserialise the data and dump it in temp
                for item in temp:
                    item = [item[0]['name'], item[1]['name']]
                    main.pastHunt.append(item)  # dump the values here for future use
    pair = [pair[0]['name'], pair[1]['name']]
    if pair in main.pastHunt:  # if the hunter has hunted this person before, return false
        if main.debugMode:
            print("Not pairing {} with {} due to repeat".format(pair[0], pair[1]))
        return False
    return True  # return true if this is a new pairing


def theHunt(main):
    main._clearScreen()
    
    print("Generating targets for", len(main.targetPool), "members...")
    availableTargets = []  # targets who havent been assigned yet
    huntList = []  # the game's current pairs (targets)
    
    for member in main.targetPool:
        availableTargets.append(member)
    badPair = False
    for member in main.targetPool:
        while True:
            target = random.choice(availableTargets)  # pick a random member for a target
            if target != member:  # make sure the member wont be targeting themselves
                if preventRepeat(main, [member, target], "theHunt"):  # makes sure the member doesnt get the same target for at least [weeksWithoutRepeat] weeks
                    huntList.append([member, target])  # put the pairing in a list for later
                    availableTargets.remove(target)  # remove the target from the pool
                    break  # stop looping on this member
                elif len(availableTargets) <= 5:  # if there arent enough targets to give the member a unique one
                    badPair = True  # restart the whole assignment process
                    break  # kill the loop
            else:
                if len(
                        availableTargets) == 1:  # if there is only 1 possible target, and thats the member, kill the loop and start again
                    badPair = True
                    break
    if badPair:
        theHunt(main)  # if for whatever reason a good match cant be made, the function gets restarted
        return  # not necesary but looks nicer when debugging

    main._clearScreen()
    os.system("cls")
    print("{B}{T} members in the hunt{D}\n".format(B=formatters.bold, D=formatters.default, T=len(main.targetPool)))
    for member in huntList:
        print("{G}{}{D} is hunting {G}{}{D}".format(member[0]['name'],
                                                    member[1]['name'], G=formatters.green, D=formatters.default))

    if input("\nIs this hunt accepted? ").lower() in ["n", "no", "nope"]:
        theHunt(main)
        return  # not necessary but looks nicer when debugging
    else:
        f = open("currentHunt.txt", "w")
        f.seek(0)  # not necessary but better safe than sorry
        for member in huntList:
            f.write("{}  ===>  {}\n".format(member[0]['name'], member[1]['name']))
    cacheGame(main, huntList, "theHunt")  # serialise the hunt for next time
    if input("Send target emails?") in ['y', 'yes', 'yep']:
        main._clearScreen()
        targetSend.SMEmail().huntSendTargets(huntList)

def zombies(main):
    names = []
    for member in main.targetPool:
        if member['kills'] <= 9:
            names.append(member)
    repeat = True
    while repeat:
        patientZero = random.choice(names)
        names.remove(patientZero)
        humanLeader = random.choice(names)
        names.remove(humanLeader)
        if preventRepeat(main, [patientZero, humanLeader], "zombieGame"):
            repeat = False
    main._clearScreen()
    print("{P}{realName}{D} aka {P}{assassinName}{D} is the leader of the humans".format(P=formatters.purple,
                                                                                         D=formatters.default,
                                                                                         realName=humanLeader['name'],
                                                                                         assassinName=humanLeader['alias']))
    print("{R}{realName}{D} aka {G}{assassinName}{D} has been infected with the Z Virus".format(R=formatters.red,
                                                                                                G=formatters.green,
                                                                                                D=formatters.default,
                                                                                                realName=patientZero['name'],
                                                                                                assassinName=
                                                                                                patientZero['alias']))
    print("In 24 hours the CDC will identify them")
    if input("Do you accept these leaders?") in ['n', 'no']:
        zombies(main)
        return
    else:
        cacheGame(main, [patientZero, humanLeader], "zombieGame")

def VIP(main):
    main._clearScreen()
    noKillClub = []
    membersList = []

    for member in main.targetPool:
        if member['kills'] == 0:
            noKillClub.append(member)
        else:
            membersList.append(member)

    tempList = list(sorted(membersList, key = itemgetter('kills'), reverse=True))
    top = tempList[:5]
    team1Leader = random.choice(top)
    top.remove(team1Leader)
    team2Leader = random.choice(top)
    top.remove(team2Leader)
    tempList.remove(team1Leader)
    tempList.remove(team2Leader)

    numOfLists = 2
    result = [[] for i in range(numOfLists)]
    sums = [0]*numOfLists
    i = 0
    for member in tempList:
        result[i].append(member)
        sums[i] += member['kills']
        i = sums.index(min(sums))

    team1 = result[0]
    team2 = result[1]

    for member in noKillClub:
        if len(team1) <= len(team2):
            team1.append(member)
        elif len(team2) <= len(team1):
            team2.append(member)

    print(formatters.purple, "Team 1:", formatters.default)
    for member in team1:
        print("'{}' aka '{};".format(member['name'], member['alias']))
    print("\nTotal members:", len(team1), "\n{}VIP:".format(formatters.blue),
          str(team1Leader).replace("[", "").replace("]", ""), formatters.default)
    print(formatters.purple, "Team 2:", formatters.default)
    for member in team2:
        print("'{}' aka '{};".format(member['name'], member['alias']))
    print("\nTotal members:", len(team2), "\n{}VIP:".format(formatters.blue),
          str(team2Leader).replace("[", "").replace("]", ""), formatters.default)

    cosmetic = "y"
    if not main.detailMode:
        cosmetic = input("\n\nView team skill? ")
        if cosmetic in ['y', 'yes', 'yep']:
            main.detailMode = True
    if main.detailMode:
        main._clearScreen()
        print(formatters.purple, "Team 1:", formatters.default)
        for member in team1:
            print("Name:{name} aka {alias}|| Kills: {kills}|| Credits {credits}"
                  .format(**member))
        print("\nTeam Skill:", sums[0], "\nTotal members:", len(team1), "\n{}VIP:".format(formatters.blue),
              str(team1Leader).replace("[", "").replace("]", ""), formatters.default)

        print(formatters.purple, "Team 2:", formatters.default)
        for member in team2:
            print("Name:{name} aka {alias}|| Kills: {kills}|| Credits {credits}"
                  .format(**member))
        print("\nTeam Skill:", sums[1], "\nTotal members:", len(team2), "\n{}VIP:".format(formatters.blue),
              str(team2Leader).replace("[", "").replace("]", ""), formatters.default)
        print("\n\nView team skill?", cosmetic)
    if input("Are these teams accepted? ") not in ['y' or 'yes', 'yep']:
        VIP(main)
        return
    # targetSend.SMEmail().VIPSendTargets(team1, team1Leader)

def Juggernaut(main):
    main._clearScreen()
    hide_cursor()
    startTime = time.time()
    option = 0
    while (startTime - time.time()) >= -3:
        option = random.randint(0, len(main.targetPool) - 1)
        print(main.targetPool[option]['name'], "is the first juggernaut!                   ", end='\r')
    accepted = False
    while not accepted:
        if preventRepeat(main, main.targetPool[option]['name'], "juggernaut") == False:
            option += 1
            if option >= len(main.targetPool) - 1:
                option = 0
        else:
            accepted = True

    print(main.targetPool[option]['name'], "is the first juggernaut")
    show_cursor()
    if input("Do you accept? ") in ['n', 'no', 'nope']:
        Juggernaut(main)
        return
    else:
        cacheGame(main, main.targetPool[option]['name'], "juggernaut")

def TeaParty(main):
    main._clearScreen()
    icon = """
    ~
    ~
  .---.
  `---'=.
  |   | |
  |   |='
  `---'"""
    print(icon, "\nGenerating Teams")
    memberList = []
    noKillClub = []
    guests = []
    for member in main.targetPool:
        if member['kills'] == 0:
            noKillClub.append(member)
        else:
            memberList.append(member)

    numOfLists = 2
    result = [[] for i in range(numOfLists)]
    sums = [0] * numOfLists
    i = 0
    for member in memberList:
        result[i].append(member)
        sums[i] += member['kills']
        i = sums.index(min(sums))

    bodyGuards = result[0]
    infiltrators = result[1]

    for member in noKillClub:
        if len(bodyGuards) <= len(infiltrators):
            bodyGuards.append(member)
        elif len(infiltrators) <= len(bodyGuards):
            infiltrators.append(member)

    host = random.choice(bodyGuards)
    bodyGuards.remove(host)

    random.shuffle(bodyGuards)
    random.shuffle(infiltrators)
    guests += bodyGuards[:5]
    guests += infiltrators[:5]
    for member in guests:
        try:
            bodyGuards.remove(member)
        except ValueError:
            pass
        try:
            infiltrators.remove(member)
        except ValueError:
            pass
    main._clearScreen()
    print(icon)
    print("The host is", host['name'], "!\n")
    print(formatters.purple, "Bodyguards:", formatters.default)
    for member in bodyGuards:
        print("{} aka {}".format(member['name'], member['alias']))
    print(formatters.purple, "\nInfiltrators:", formatters.default)
    for member in infiltrators:
        print("{} aka {}".format(member['name'], member['alias']))
    print(formatters.purple, "\nGuests", formatters.default)
    for member in guests:
        print("{} aka {}".format(member['name'], member['alias']))
    input()




