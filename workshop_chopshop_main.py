import os, re, configparser

# DEBUG #
DEBUG_CONFIG = True
DEBUG_CONFIG_WRITE = False
DEBUG_GAMEFILE_READING = False
DEBUG_CONFIG_GAMELIST_POST = False
#########


def cleanFileName(fileName):
    
    cleanedName = ''.join(filter(lambda x: x.isdigit(), fileName))
    
    return cleanedName;



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



def getModList(GameLocation, GameList, GameExemptionList):
    
    
    return;


def main():
    
    SteamLocation = os.chdir('C:\\Program Files (x86)\\Steam')
    GameLocation = os.path.join(os.getcwd(), 'steamapps')
    GameExemptionList = {-1, 228980}
    
    GameList = {}
    GameModList = {} 
    
    configExists = os.path.exists('./workshop_config.txt')
    
    if DEBUG_CONFIG:
        if os.path.isfile("workshop_config.txt"):
            configExists = False
            os.remove("workshop_config.txt")
    
    if configExists:
        
        #do OTHERSTUFF
        print("FOUND CONFIG FILE")
        
    else:
        workshop_config = configparser.ConfigParser()
        
        workshop_config['Directories'] = {}
        workshop_config['Directories']['Steam'] = os.path.realpath(SteamLocation)
        workshop_config['Directories']['Games'] = os.path.realpath(GameLocation)
        
        # Get games and their IDs
        getGameIDs(GameLocation, GameList, GameExemptionList)
        if DEBUG_CONFIG_GAMELIST_POST:
            print("DEBUGGING GAMELIST")
            for x in GameList:
                print(x), print(GameList[x]), print("\n")
                
        # Fill out the mods as well
        #getModList(GameLocation, GameModList, GameExemptionList)
                
        for x in GameList:
            if DEBUG_CONFIG_WRITE:
                print("WRITING STARTED")
            #for y in ModList:
                # this should cycle through all of the mod IDs listed and attach them to their name under the [Game]     
            #   workshop_config[GameList[x]][ModList[x]] = ModList[x][y]
            workshop_config[GameList[x]] = {}
            workshop_config[GameList[x]]['Game ID'] = x
        
        if DEBUG_CONFIG_WRITE:
            print("WRITING ENDED")   
        with open('workshop_config.txt', 'w') as configFile:
            workshop_config.write(configFile)
     
    return;


if __name__ == '__main__':
    main()