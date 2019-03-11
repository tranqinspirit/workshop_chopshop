import os, re, configparser
from requests_html import HTMLSession

# DEBUG #
DEBUG_CONFIG = True
DEBUG_CONFIG_CREATE = True
DEBUG_CONFIG_WRITE = False
DEBUG_GAMEFILE_READING = False
DEBUG_MAIN_GAMELIST = False
DEBUG_MODLIST_CREATE = False
DEBUG_MODLIST_CREATE_OUTPUT = False
DEBUG_EXEMPTION_BUILD = False
DEBUG_MODTITLE_BUILD = False
#########

def cleanFileName(fileName):
    
    cleanedName = ''.join(filter(lambda x: x.isdigit(), fileName))
    
    return cleanedName;


def buildExemptionList(GameLocation):
    ModLocation = os.path.join(GameLocation, 'workshop')
    GameFileList = []
    ExemptionList = []
    
    #some presets
    #PresetExemptions = [228980]  
    #ExemptionList.extend(PresetExemptions)
    
    for file in os.listdir(GameLocation):
        if file.endswith('.acf'):
            file = file.replace("manifest","workshop")
            GameFileList.append(file)
        
    # iterate through mod directory -> if not found in game directory, add to exemptions
    for fileName in os.listdir(ModLocation):
        if fileName.endswith('.acf'):
            if DEBUG_EXEMPTION_BUILD:
                print(fileName + " found in workshop directory")
           
            if (fileName not in GameFileList):
                if DEBUG_EXEMPTION_BUILD:
                    print("EXEMPTION ITEM (pre): " + str(fileName) + "\n")
                fileName = fileName.replace("appworkshop_","")
                fileName = fileName.replace(".acf", "")
                if DEBUG_EXEMPTION_BUILD:
                    print("EXEMPTION ITEM (post): " + str(fileName))    
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

def getModTitleFromInternet(modURL):
    
    #Get the title of the page to use for the key in the config sections
    session = HTMLSession()
    webResponse = session.get(modURL)
    modTitle = webResponse.html.find('title', first=True)
    foundTitle = str(modTitle.html)
    foundTitle = re.sub(r'.*:',"", foundTitle)
    foundTitle = foundTitle.replace("</title>", "")
    if DEBUG_MODTITLE_BUILD:
        print("Mod Title: " + foundTitle)

    return foundTitle;

def getModList(GameLocation, workshopFile, GameExemptionList):
    ModLocation = os.path.join(GameLocation, 'workshop')
    modList = []
    for fileName in os.listdir(ModLocation):
        cleaned_filename = (cleanFileName(fileName))
        if fileName.endswith('.acf') and (cleaned_filename not in GameExemptionList):
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
                    mod_key = 1
                    if DEBUG_MODLIST_CREATE_OUTPUT:
                        print("Mod List: "), print(modList)
                    #what if instead, we just directly wrote to the config file?
                    for item in modList:                  
                        webURL = "https://steamcommunity.com/sharedfiles/filedetails/?id=" + item 
                        mod_title = getModTitleFromInternet(webURL)
                        workshopFile[cleanFileName(fileName)][mod_title] = webURL
                        mod_key += 1       

    return;

def main():
    
    SteamLocation = os.chdir('C:\\Program Files (x86)\\Steam')
    GameLocation = os.path.join(os.getcwd(), 'steamapps')
    GameExemptionList = []
    
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
            # delete the key/rename the section and stuff after?
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
