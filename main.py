import os
import pprint
import re
import shutil
import sys
from collections import defaultdict
from time import sleep

from backend import backendGoogle
from backend import cosmetics
from backend import formatters
from backend import games
from backend import menu
from backend import responseHandler as RH


# todo: Support for configuration file to help future committees after I, Dan, leave
# todo: Support for generating a killsheet for other societies -- unlikely, but a nice thought
# todo: COMMENTS! I really let the commenting slack, i should fix that
# todo: Make game definitions easier to make
# todo: Improve UI in all sections of the program, no more Y/N typing
# todo: Add self authentication script, so anyone can run this
# todo: Backup past hunts to the cloud. Maybe Gists?

class Main:
    def __init__(self, argv=None):
        """Defines variables that the main class will use"""
        self.cacheDir = "cache"  # the directory of the cache
        self.pprint = pprint.PrettyPrinter().pprint  # pprint instance so i dont need to type as much
        self.offline = False  # used to flag if the code is running without google, can be manually set
        self.values = []  # temporary variable holding EVERYTHING google sends back
        self.pastHunt = []  # a list holding all past hunts/teams/whatever tf you want
        self.targetPool = []   # a list of members opted in the hunt this week
        self.optOut = []  # a list of members opted out, deprecated
        self.weeksWithoutRepeat = 6  # how many weeks gameEngine should try not to repeat for
        self.games = games
        self.logo = cosmetics.getLogo()

        self.rank = None
        self.firstName = None
        self.lastName = None
        self.optIn = None
        self.alias = None
        self.ID = None
        self.timetable = None
        self.kills = None
        self.credits = None
        self.bounty = None
        self.notes = None

        ### Overrides ###
        self.debugMode = True  # disables cosmetics, and enables more verbose outputs
        self.detailMode = False  # detailed output by default, where applicable
        self.incCouncil = True  # default to include council, and not ask
        self.paidCheck = False  # Should gameEngine reject people who havent paid?
        self.timetableCheck = False  # Should gameEngine reject people without timetables?

    def debugPrint(self, message, pretty=False):
        if self.debugMode:
            if pretty:
                print("DEBUG: ", end="")
                self.pprint(message)
            else:
                print("DEBUG:", message)

    def clearScreen(self):
        """Wrapper function to clear the screen and keep the logo on screen"""
        os.system("cls")
        if not self.debugMode:
            print(self.logo)
        else:
            print("LordOfPolls' GameEngine".center(65, "="))
        print("")

    def _cleanSlate(self):
        """Nukes all of GameEngine's stored data for a clean slate, gettit?"""
        os.system("cls")
        print(formatters.formatters.red, "CLEARING ALL SAVED DATA", formatters.formatters.default)
        sleep(1)
        print("Deleting OptOut.txt")
        try:  # Using loads of try and except conditions because i dont want the entire function to stop if one fails
            os.unlink("OptOut.txt")
        except OSError:
            pass
        print("Deleting currentHunt.txt")
        try:
            os.unlink("currentHunt.txt")
        except OSError:
            pass
        print("Deleting offlineMemberList")
        try:
            os.unlink("offlineMemberList")
        except OSError:
            pass
        print("Deleting cache dir")
        shutil.rmtree("cache", ignore_errors=True)  # rmtree removes a directory and EVERYTHING in it, no matter what
        shutil.rmtree("DEBUGCache", ignore_errors=True)
        print("Clean Slate completed...")
        if not self.debugMode:
            print("Exiting Game Engine in...", end="\r")
            print("Exiting Game Engine in... 3", end="\r")
            sleep(1)
            print("\rExiting Game Engine in... 2", end="\r")
            sleep(1)
            print("\rExiting Game Engine in... 1", end="\r")
            sleep(1)
        exit(0)

    def _dumpAndOpen(self):
        """Dumps the current targetpool to a file and opens it"""
        f = open("temp.txt", "w")
        f.write("**KILLSHEET DUMP**\n\n")
        for member in self.targetPool:
            formatted = "{}: {}|| Kills: {} || Credits: {}".format(
                member['rank'], member['name'],
                member['kills'], member['credits']
            )
            f.write(formatted)
            f.write("\n")
        f.close()
        self.clearScreen()
        print("Waiting for notepad to close...")
        os.system("notepad.exe temp.txt")
        os.unlink("temp.txt")
        print("File deleted, resuming")

    def _options(self):
        """Check if Council to be included in target pool"""
        if self.incCouncil is None:
            council = input("Opt in Council? ")
            self.incCouncil = RH.yesorno(council)
        else:
            self.incCouncil = False

        # Opt out menu`
        self.clearScreen()

    def _processMembers(self):
        data = defaultdict()  # creates an empty, assignable dictionary

        self.debugPrint("Determining rows...")
        self.rank = self.values[0].index("Rank")
        self.firstName = self.values[0].index("First Name")
        self.lastName = self.values[0].index("Last Name")
        self.optIn = self.values[0].index("Opt In")
        self.alias = self.values[0].index("Assassin Alias")
        self.ID = self.values[0].index("ID/Email")
        self.timetable = self.values[0].index("Timetable Link")
        self.kills = self.values[0].index("Kills")
        self.credits = self.values[0].index("Credits")
        self.bounty = self.values[0].index("Bounty")
        self.notes = self.values[0].index("Notes")
        self.values.remove(self.values[0])
        self.debugPrint([self.rank, self.firstName, self.lastName, self.optIn, self.alias, self.ID, self.kills, self.credits, self.bounty, self.notes], pretty=True)

        for row in self.values:
            try:
                if row[self.optIn] == "TRUE" and "{} {}".format(row[self.firstName], row[self.lastName]) not in self.optOut: #  are they in the opt out list?
                    if row[self.rank] == "Council" and not self.incCouncil:  # is this a council member, and are we including them?
                        self.debugPrint("{} is Council, and council are opted out".format(row[1] + " " + row[2]))
                    elif "No Membership Paid" in row[self.notes] and self.paidCheck:
                        self.debugPrint("{} {} hasn't paid membership, unable to opt in".format(row[self.firstName], row[self.lastName]))
                    elif "Strike: II" in row[self.notes]:
                        self.debugPrint("{} {} has 2 strikes, unable to opt in".format(row[self.firstName], self.lastName))
                    else:
                        # the basic data structure of a member, will be replaced with a class rather than a dictionary
                        data = {'rank': row[self.rank],
                                'name': row[self.firstName]+ " " + row[self.lastName],
                                'alias': row[self.alias],
                                'id': row[self.ID],
                                'timetable': None if row[self.timetable] == "Pending" else row[self.timetable],
                                'kills': float(re.sub("[^0-9]", "", str(row[self.kills]))),
                                'credits': float(re.sub("[^0-9]", "", str(row[self.credits]))),
                                'notes': row[self.notes]
                                }
                        self.targetPool.append(data)  # add this member to the targetPool
                        self.debugPrint("{} has been opted in".format(data['name']))
                elif row[self.optIn] == "FALSE" and row[self.rank] != "Council" and "{} {}".format(row[self.firstName], row[self.lastName]) not in self.optOut:
                    # Is this person set to be opted out on the killSheet?
                    self.debugPrint("{} is set to opt out on the sheet".format(row[self.firstName] + " " + row[self.lastName]))
            except Exception as e:
                # if this code EVER hits an error, i can put money on it being a formatting error on the killSheet
                print("Unable to add {} due to invalid data formatting || {}".format(row[self.firstName], e))
        self.debugPrint("{} members opted in\n{} members opted out".format(len(self.targetPool), len(self.values)-len(self.targetPool)))

    def mainMenu(self):
        if not self.debugMode:
            cosmetics.fullScreen()
            if self.offline:  # let the user know game engine is running offline
                cosmetics.logo = "{} OFFLINE MODE {}\n{}".format(formatters.formatters.red,
                                                            formatters.formatters.default,
                                                            self.logo)
            sleep(0.5)
            cosmetics.printLogo()

        print("Loading KillSheet Data...", end="\r")
        self.values = backendGoogle.getValues(self.offline)  # get the killSheet data from google sheets
        if not self.debugMode:
            sleep(0.1)
            print(formatters.formatters.green + "Loading KillSheet Data...        " + formatters.formatters.default)

        print("Processing members...", end="\r")
        self._processMembers()
        if not self.debugMode:
            sleep(0.1)
            print(formatters.formatters.green + "Processing members...          " + formatters.formatters.default)

        print("Ready!")
        if not self.debugMode:
            sleep(0.7)

        self._options()
        if not self.debugMode:
            menuManager = menu.Engine(coreLoop=self)
            menuManager.loop()
        else:
            games.theHunt(self)

    def updateMembers(self):
        self.values = []
        self.targetPool = []
        self.values = backendGoogle.getValues(self.offline)
        self._processMembers()
        print("Members list updated")

if __name__ == "__main__":
    # the code wont execute if you import it, only if you open it
    assassin = Main(sys.argv[1:])  # run the innit code once ONLY (apparently this was necessary :( )
    assassin.mainMenu()  # BOOT
