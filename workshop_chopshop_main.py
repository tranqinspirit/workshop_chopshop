import os, re, configparser
from requests_html import HTMLSession
import time
#for the file editing?
#from threading import Thread
#from multiprocessing import Pool


# DEBUG #
DEBUG_OVERALL = True
DEBUG_RUNTIME = True
DEBUG_RUNTIME_MODCOUNT = False 
DEBUG_CONFIG_CREATE = True
DEBUG_GAMEFILE_READING = False
DEBUG_MODTITLE_BUILD = False
DEBUG_GAMELIST_CLASS = True
DEBUG_GAMELIST_CLASS_OUTPUT = False
#########

class GameEntry:
    def __init__(self, ID, nameOfFile):
        self.appID = ID
        self.modsInstalled = []
        self.fileName = nameOfFile
    
    def createTitle(self, title):
        self.gameTitle = title
    
    def printModList(self, entry):
        if entry == "All":
            for x in self.modsInstalled:
                print("Mods (" + x +"): " + self.modsInstalled)
        else:
            print(self.modsInstalled[entry])
    
    def printFileName(self):
        print("File Name : " + self.fileName)
    
    def printID(self):
        print("GameID : " + self.appID)
            
    def printTitle(self):
        print("Title is: " + self.gameTitle)


def cleanFileName(fileName):
    
    cleanedName = ''.join(filter(lambda x: x.isdigit(), fileName))
    
    return cleanedName;

def getModTitleFromInternet(modURL, webSession):
    
    #Get the title of the page to use for the key in the config sections  
    webResponse = webSession.get(modURL)
    modTitle = webResponse.html.find('title', first=True)
    foundTitle = str(modTitle.html)
    foundTitle = re.sub(r'.*:',"", foundTitle)
    foundTitle = foundTitle.replace("</title>", "")
    if DEBUG_MODTITLE_BUILD:
        print("Mod Title: " + foundTitle)

    return foundTitle;

def buildExemptionList(GameLocation):
    ModLocation = os.path.join(GameLocation, 'workshop')
    GameFileList = []
    ExemptionList = []
    
    for file in os.listdir(GameLocation):
        if file.endswith('.acf'):             
            if "installdir" not in open(os.path.join(GameLocation,file), "r", encoding='utf-8', errors='ignore').read():
                continue;  
            file = file.replace("manifest","workshop")
            GameFileList.append(file)
      
    # iterate through mod directory -> if not found in game directory, add to exemptions
    for fileName in os.listdir(ModLocation):
        if fileName.endswith('.acf'):         
            if (fileName not in GameFileList):
                fileName = fileName.replace("appworkshop_","")
                fileName = fileName.replace(".acf", "")  
                ExemptionList.append(cleanFileName(fileName))
                
    return ExemptionList;

def getGameIDs(GameLocation, GameList, GameExemptionList, workshopFile):

    for fileName in os.listdir(GameLocation):
        if fileName.endswith('.acf') and (int(cleanFileName(fileName)) not in GameExemptionList):
            gameFile = open(os.path.join(GameLocation,fileName,), "r", encoding='utf-8', errors='ignore')
            for line in gameFile:
                if "appid" in line:                             
                    appID = re.search(r'\d+', line).group(0) 
                elif "name" in line:
                    gameName = re.sub(r'\"name\"+\t\s','',line)
                    gameName = " ".join(gameName.split())
                    gameName = gameName.replace("\"", "")
                    if DEBUG_GAMELIST_CLASS:
                        tempEntry = GameEntry(appID, fileName)
                        tempEntry.gameTitle = gameName
                        GameList.append(tempEntry)
                        # Don't lose any time directly writing to this so might as well get it done
                        # Also appropriate to add it as we get the entries, yay efficiency!
                        workshopFile[tempEntry.appID] = {}
                        workshopFile[tempEntry.appID]['Title'] = gameName
                    else:
                        GameList[appID] = gameName
                    # for whatever reason, it doesn't want to write if i use "with open" so need to manually close here
                    gameFile.close()
                    break;
    return;

def getModListOneGame(ModLocation, fileName):
    if os.path.isfile(os.path.join(ModLocation,fileName)):
        if DEBUG_RUNTIME_MODCOUNT:
            modListRuntime = time.time()
        with open(os.path.join(ModLocation,fileName), "r", encoding='utf-8', errors='ignore') as modFile:
            modList = []          
            for line in modFile:
                if "WorkshopItemDetails" in line:
                    modFile.close();
                    break
            
                if not (re.search("[a-zA-Z]", line)) and "{" not in line and "}" not in line:
                    modID = line
                    modID = modID.replace("\"", "")
                    modID = "".join(modID.split())
                    modList.append(modID)
            if DEBUG_RUNTIME_MODCOUNT:
                print("Mod list runtime - file: " + cleanFileName(fileName) + ": " + str(time.time() - modListRuntime))
            return modList# indented with the for loop

def main():
    if DEBUG_RUNTIME:
        ProgramRuntime = time.time()
    SteamLocation = os.chdir('C:\\Program Files (x86)\\Steam')
    GameLocation = os.path.join(os.getcwd(), 'steamapps')
    GameExemptionList = []
    ModLocation = os.path.join(GameLocation, 'workshop')
    
    if DEBUG_GAMELIST_CLASS:
        GameList = []
        webSession = HTMLSession()
    else:
        GameList = {}
    
    configExists = os.path.exists('./workshop_config.txt')
    
    if DEBUG_CONFIG_CREATE:
        if os.path.isfile("workshop_config.txt"):
            configExists = False
            os.remove("workshop_config.txt")
            print("DELETING PRESENT CONFIG FILE")
    
    if configExists:
        
        #do OTHERSTUFF
        print("FOUND CONFIG FILE")
        
    else:
        workshop_config = configparser.ConfigParser()
        
        workshop_config['Directories'] = {}
        workshop_config['Directories']['Steam'] = os.path.realpath(SteamLocation)
        workshop_config['Directories']['Games'] = os.path.realpath(GameLocation)
        
        if DEBUG_OVERALL:
            print("Building Exemption List..")
        if DEBUG_RUNTIME:
            ExemptionTime = time.time()
        GameExemptionList = buildExemptionList(GameLocation)
        if DEBUG_OVERALL:
            print("Exemption List Completed.")
        if DEBUG_RUNTIME:
                print("Exemption List Runtime: " + str(time.time() - ExemptionTime))
        # Get games and their IDs
        if DEBUG_OVERALL:
            print("Creating Game List...")
        if DEBUG_RUNTIME:
            GameListCreateTime = time.time()
        getGameIDs(GameLocation, GameList, GameExemptionList, workshop_config)
        if DEBUG_OVERALL:
            print("Game List Creation Completed")
        if DEBUG_RUNTIME:
            print("Game List Runtime: " + str(time.time() - GameListCreateTime))
        if DEBUG_GAMELIST_CLASS_OUTPUT:
            for entry in GameList:
                entry.printFileName()
                entry.printID()
                entry.printTitle()
        
        if DEBUG_OVERALL:
            print("File Writing Started...")
        if DEBUG_RUNTIME:
            WritingRuntime = time.time()  
            
        # Fill out the mods as well
        if DEBUG_OVERALL:
            print("Mod List Compilation Starting...")
        if DEBUG_RUNTIME:
            ModListCompileTime = time.time()
        
        if DEBUG_RUNTIME:  
            print("Mod URL Parsing Started...") 
        # Create corresponding number of threads to how many items we have? Or do chunks
        # Thread A goes and gets the mod list -> puts it in queue
        # -> Thread B pulls from queue + pops off so other threads dont care -> gets URL 
        for entry in GameList:
            if DEBUG_RUNTIME:
                ModUrlTime = time.time()                   
            modFileName = entry.fileName.replace("appmanifest","appworkshop")
            modList = getModListOneGame(ModLocation, modFileName)
            if modList:
                for mod in modList:
                    webURL = "https://steamcommunity.com/sharedfiles/filedetails/?id=" + mod
                    mod_title = getModTitleFromInternet(webURL, webSession)
                    workshop_config[cleanFileName(entry.fileName)][mod_title] = webURL
                if DEBUG_RUNTIME:
                    print("Mod URL Runtime (file: " + cleanFileName(entry.fileName) + "): " + str(time.time() - ModUrlTime))
        
        if DEBUG_OVERALL:
            print("Mod List Compilation Completed")
        if DEBUG_RUNTIME:
            print("Mod List Runtime: " + str(time.time() - ModListCompileTime))
            
        with open('workshop_config.txt', 'w') as configFile:
            workshop_config.write(configFile)
            if DEBUG_OVERALL:
                print("File Writing Completed")   
            if DEBUG_RUNTIME:
                print("Writing Runtime: " + str(time.time() - WritingRuntime))
    if DEBUG_RUNTIME:
        print("Total time: " + str(time.time() - ProgramRuntime)) 
    return;


if __name__ == '__main__':
    main()
