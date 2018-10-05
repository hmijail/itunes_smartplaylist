#! /usr/bin/env python3

# Export smart playlists from "iTunes Music Library.xml" to xsp files for Kodi

import os
import traceback


try:
    import itunessmart
except ImportError:
    import sys
    include = os.path.relpath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, include)
    import itunessmart
    print("Imported itunessmart from %s" % os.path.abspath(os.path.join(include, "itunessmart")))



if __name__ == "__main__":

    EXPORT_NESTED_RULES_AS_SUBPLAYLIST = True


    home = os.path.expanduser("~")
    folder = os.path.join(home,"Music/iTunes");
    iTunesLibraryFile = os.path.join(folder,"iTunes Music Library.xml")

    print("Reading %s . . . " % iTunesLibraryFile)
    with open(iTunesLibraryFile, "rb") as fs:
        # Read XML file 
        library = itunessmart.readiTunesLibrary(fs)
        persistentIDMapping = itunessmart.generatePersistentIDMapping(library)
        
        
    print("Library loaded!")
    
    userinput = input("Do you want to convert a (single) or (all) playlists? ")
    export_all = True
    if userinput.lower() in ("single", "1", "one"):
        export_all = False
    
    userinput = input("Do you want to export nested rules to sub-playlists? (yes/no) ")
    if userinput.lower() in ("n","no", "0"):
        EXPORT_NESTED_RULES_AS_SUBPLAYLIST = False
        
    # Decode and export all smart playlists

    parser = itunessmart.Parser()

    outputDirectory = os.path.abspath("out")

    if not os.path.exists(outputDirectory):
        os.makedirs(outputDirectory)
    
    if export_all:
        print("Converting playlists to %s" % outputDirectory)
    
    res = []
    for playlist in library['Playlists']:
        if 'Name' in playlist and 'Smart Criteria' in playlist and 'Smart Info' in playlist and playlist['Smart Criteria']:
            try:
                parser.update_data_base64(playlist['Smart Info'],playlist['Smart Criteria'])
            except Exception as e:
                try:
                    print("Failed to decode playlist:")
                    print(traceback.format_exc())
                    print(playlist['Name'])
                except:
                    print(playlist)
            
            try:
                res.append((playlist['Name'], parser.queryTree))
                if export_all:
                    itunessmart.createXSPFile(directory=outputDirectory, name=playlist['Name'], data=parser.queryTree, createSubplaylists=EXPORT_NESTED_RULES_AS_SUBPLAYLIST, persistentIDMapping=persistentIDMapping)
            except itunessmart.EmptyPlaylistException as e:
                print("%s is empty." % playlist['Name'])
            except Exception as e:
                try:
                    print("Failed to convert playlist:")
                    print(traceback.format_exc())
                    print(playlist['Name'])
                except:
                    print(playlist)
                    
                    
                    
    if not export_all:
        i = 1
        for pname,_ in res:
            print("%02d: %s" % (i, pname))
            i +=1 
            
        while True:
            i = input("Please give the number of the playlist (0 to exit): ")
            if i in ("0",""):
                break
            
            i = int(i)
            pname, ptree = res[i-1]
            print("Converting Playlist: %s" % pname)
            try:
                itunessmart.createXSPFile(directory=outputDirectory, name=pname, data=ptree, createSubplaylists=EXPORT_NESTED_RULES_AS_SUBPLAYLIST, persistentIDMapping=persistentIDMapping)
            except itunessmart.EmptyPlaylistException as e:
                print("%s is empty." % pname)
            except Exception as e:
                try:
                    print("Failed to convert playlist:")
                    print(traceback.format_exc())
                    print(pname)
                except:
                    print(ptree)
                    
                    
        
    print("All done!")
    userdata = os.path.expandvars(r"%appdata%\kodi\userdata\playlists\music") if os.path.exists(os.path.expandvars(r"%appdata%\kodi\userdata")) else os.path.expanduser(r"~/Library/Application Support/Kodi/userdata/playlists/music")
    print("You may copy the .xsp files to %s" % userdata)

