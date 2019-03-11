import os, re, configparser

# DEBUG #
DEBUG_CONFIG = True
DEBUG_CONFIG_CREATE = True
DEBUG_CONFIG_WRITE = False
DEBUG_GAMEFILE_READING = False
DEBUG_MAIN_GAMELIST = False
DEBUG_MODLIST_CREATE = True
DEBUG_MODLIST_CREATE_OUTPUT = True
DEBUG_EXEMPTION_BUILD = True
#########

def cleanFileName(fileName):
    
    cleanedName = ''.join(filter(lambda x: x.isdigit(), fileName))
    
    return cleanedName;

def buildExemptionList(GameLocation):
    ModLocation = os.path.join(GameLocation, 'workshop')
    ExemptionList = []
    # iterate through mod directory -> if not found in game directory, add to exemptions
    for fileName in os.listdir(ModLocation):
        if fileName.endswith('.acf') and fileName not in os.listdir(GameLocation):
            if DEBUG_EXEMPTION_BUILD:
                print("EXEMPTION ITEM: " + str(fileName))
            ExemptionList.append(cleanFileName(fileName))
    
    return ExemptionList;

def getGameIDs(GameLocation, GameList, GameExemptionList):

    for fileName in os.listdir(GameLocation):
        if fileName.endswith('.acf') and (int(cleanFileName(fileName)) not in GameExemptionList):
            gameFile = open(os.path.join(GameLocation,fileName,), "r", encoding='utf-8', errors='ignore')
            for line in gameFile:
                if "appid" in line:                             
                    appID = re.search(r'\d+', line).group(0)
                    if DEBUG_GAMEFILE_READING:
                        print("appid is " + appID)   
                elif "name" in line:
                    gameName = re.sub(r'\"name\"+\t\s','',line)
                    gameName = " ".join(gameName.split())
                    gameName = gameName.replace("\"", "")
                    #gameName = re.search("[a-zA-Z]", line).group(0)
                    if DEBUG_GAMEFILE_READING:
                        print("game name is " + gameName)
                    GameList[appID] = gameName
                    break;
    return;

def getGameIDs2(GameLocation, GameList, GameExemptionList):
        
    for fileName in os.listdir(GameLocation):
        if fileName.endswith('.acf') and (int(cleanFileName(fileName)) not in GameExemptionList):
            with open(os.path.join(GameLocation,fileName,), "r", encoding='utf-8', errors='ignore') as gameFile:
                for line in gameFile:
                    if "appid" in line:                             
                        appID = re.search(r'\d+', line).group(0)
                        if DEBUG_GAMEFILE_READING:
                            print("appid is " + appID)   
                        elif "name" in line:
                            gameName = re.sub(r'\"name\"+\t\s','',line)
                            gameName = " ".join(gameName.split())
                            gameName = gameName.replace("\"", "")
                            #gameName = re.search("[a-zA-Z]", line).group(0)
                            if DEBUG_GAMEFILE_READING:
                                print("game name is " + gameName)
                                GameList[appID] = gameName
                                #gameFile.close()
                                break;
    return;



def getModList(GameLocation, workshopFile, GameExemptionList):
    ModLocation = os.path.join(GameLocation, 'workshop')
    modList = []
    NewGameList = {}
    for fileName in os.listdir(ModLocation):
        if fileName.endswith('.acf') and (int(cleanFileName(fileName)) not in GameExemptionList):
            with open(os.path.join(ModLocation,fileName,), "r", encoding='utf-8', errors='ignore') as modFile:
                if DEBUG_MODLIST_CREATE:
                    print("File: " + cleanFileName(fileName) + " opened")
                if DEBUG_MODLIST_CREATE:
                    if modList:
                        print("Previous mod list: "), print(modList)
                if DEBUG_MODLIST_CREATE:
                    if modList:
                        print("Mod List cleared")
                modList.clear()
                for line in modFile:
                    if "WorkshopItemDetails" in line:
                        modFile.close();
                        break
                                                
                    if not (re.search("[a-zA-Z]", line)) and "{" not in line and "}" not in line:
                        modID = line
                        modID = modID.replace("\"", "")
                        modID = "".join(modID.split())
                        modList.append(modID)
                        if modList:                      
                            NewGameList.update({cleanFileName(fileName) : modList})
                if DEBUG_MODLIST_CREATE_OUTPUT:
                    if modList:
                        print("Mod List: "), print(modList)
                        #what if instead, we just directly wrote to the config file?
                        for item in modList:                  
                            workshopFile.set(cleanFileName(fileName), 'Mods', item)
                        print("WorkshopFile key debug (post): "), print(workshopFile[cleanFileName(fileName)])           
                    #print("PRE-FILE CLOSE CHECK2: " + cleanFileName(fileName))#, print(NewGameList[cleanFileName(fileName)])
    #print(list(NewGameList))    
    #for key in NewGameList.items():
    #    print("KEYS: "), print(key)           

    return;


def main():
    
    SteamLocation = os.chdir('C:\\Program Files (x86)\\Steam')
    GameLocation = os.path.join(os.getcwd(), 'steamapps')
    GameExemptionList = []#{-1, 228980}
    
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
        
        GameExemptionList = buildExemptionList(GameLocation)
        
        # Get games and their IDs
        getGameIDs(GameLocation, GameList, GameExemptionList)
        if DEBUG_MAIN_GAMELIST:
            print("DEBUGGING GAMELIST")
            for x in GameList:
                print(x), print(GameList[x]), print("\n")
                
        for x in GameList:
            if DEBUG_CONFIG_WRITE:
                print("WRITING STARTED")
            #for y in ModList:
                # this should cycle through all of the mod IDs listed and attach them to their name under the [Game]     
            #   workshop_config[GameList[x]][ModList[x]] = ModList[x][y]
            #workshop_config[GameList[x] + " - " + x] = {} - puts name with appid
            
            # set it this way initially so it's easier to deal with in terms of loading in the mod lists..
            # delete the key/rename the section and stuff after
            workshop_config[x] = {}
            workshop_config[x]['Title'] = GameList[x]
        
        # Fill out the mods as well
        getModList(GameLocation, workshop_config, GameExemptionList)
        
        if DEBUG_CONFIG_WRITE:
            print("WRITING ENDED")   
        with open('workshop_config.txt', 'w') as configFile:
            workshop_config.write(configFile)
     
    return;


if __name__ == '__main__':
    main()
