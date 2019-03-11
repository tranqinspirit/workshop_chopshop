import os, re, configparser
from requests_html import HTMLSession
import time

# DEBUG #
DEBUG_OVERALL = True
DEBUG_RUNTIME = True
DEBUG_CONFIG_CREATE = True
DEBUG_GAMEFILE_READING = False
DEBUG_MODTITLE_BUILD = False
#########

def cleanFileName(fileName):
    
    cleanedName = ''.join(filter(lambda x: x.isdigit(), fileName))
    
    return cleanedName;

def buildExemptionList(GameLocation):
    ModLocation = os.path.join(GameLocation, 'workshop')
    GameFileList = []
    ExemptionList = []
    
    for file in os.listdir(GameLocation):
        if file.endswith('.acf'):
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

def getGameIDs(GameLocation, GameList, GameExemptionList):

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

def getModList(GameLocation, workshopFile, GameExemptionList):
    ModLocation = os.path.join(GameLocation, 'workshop')
    modList = []
    webSession = HTMLSession()
    
    for fileName in os.listdir(ModLocation):
        cleaned_filename = (cleanFileName(fileName))
        if fileName.endswith('.acf') and (cleaned_filename not in GameExemptionList):
            with open(os.path.join(ModLocation,fileName,), "r", encoding='utf-8', errors='ignore') as modFile:
                # Clean up
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
                    if DEBUG_RUNTIME:
                        print("Mod URL Started")
                        ModUrlTime = time.time()
                    mod_key = 1
                    #what if instead, we just directly wrote to the config file?
                    for item in modList:                  
                        webURL = "https://steamcommunity.com/sharedfiles/filedetails/?id=" + item 
                        mod_title = getModTitleFromInternet(webURL, webSession)
                        workshopFile[cleanFileName(fileName)][mod_title] = webURL
                        mod_key += 1
                    if DEBUG_RUNTIME:
                        print("Mod URL Runtime (file: " + cleanFileName(fileName) + "|entries:"+ str(mod_key) + "): " + str(time.time() - ModUrlTime))

    return;

def main():
    if DEBUG_RUNTIME:
        ProgramRuntime = time.time()
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
        getGameIDs(GameLocation, GameList, GameExemptionList)
        
        if DEBUG_OVERALL:
            print("WRITING STARTED")
        if DEBUG_RUNTIME:
            WritingRuntime = time.time()       
        for x in GameList:

            #for y in ModList:
                # this should cycle through all of the mod IDs listed and attach them to their name under the [Game]     
            #   workshop_config[GameList[x]][ModList[x]] = ModList[x][y]
            #workshop_config[GameList[x] + " - " + x] = {} - puts name with appid
            
            # set it this way initially so it's easier to deal with in terms of loading in the mod lists..
            # delete the key/rename the section and stuff after?
            workshop_config[x] = {}
            workshop_config[x]['Title'] = GameList[x]
        
        # Fill out the mods as well
        if DEBUG_OVERALL:
            print("Mod List Compilation Starting...")
        if DEBUG_RUNTIME:
            ModListCompileTime = time.time()
        getModList(GameLocation, workshop_config, GameExemptionList)
        if DEBUG_OVERALL:
            print("Mod List Compilation Completed")
        if DEBUG_RUNTIME:
            print("Mod List Runtime: " + str(time.time() - ModListCompileTime))
        with open('workshop_config.txt', 'w') as configFile:
            workshop_config.write(configFile)
            if DEBUG_OVERALL:
                print("WRITING ENDED")   
            if DEBUG_RUNTIME:
                print("Writing Runtime: " + str(time.time() - WritingRuntime))
    if DEBUG_RUNTIME:
        print("Total time: " + str(time.time() - ProgramRuntime)) 
    return;


if __name__ == '__main__':
    main()
