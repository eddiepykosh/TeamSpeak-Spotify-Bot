import sys
import time
import requests
import ts3
from urllib.parse import quote
import json
import threading
import os
import stockquotes
import tts
from dotenv import load_dotenv

load_dotenv()


exitFlag = 0
goodid = os.getenv('KNOWN_SPOTIFY_DEVICE') #A already know Spotify Device ID
n = 0

# Methods
class myThread(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.keepalive = True

    def run(self):
        global n
        print("Starting " + self.name)
        if self.name == "Thread-1":
            startup()
        else:
            try:
                naming(n)
            except:
                with ts3.query.TS3ClientConnection(os.getenv('BOTS_TS3_CLIENT_LOCATION')) as tsconn:
                    tsconn.auth(apikey=os.getenv('BOTS_TS3_AUTHKEY'))
                    tsconn.use()
                    tsconn.sendtextmessage(targetmode=2, target=1,
                                       msg="[color=orange]Something is wrong with the entire naming thread.  Good luck guessing what is wrong because I put the entire thing in a try catch, restarting script in 15 seconds...[/color]") #just kill it all and restart
                    import webbrowser
                    url = os.getenv('SPOTIFY_API_WEBSITE')
                    webbrowser.open_new_tab(url)
                    time.sleep(15)
                    os.system("taskkill /im chrome.exe /f")
                    os.execv(sys.executable, ['python'] + sys.argv)


def naming(n):
    global thread2
    with ts3.query.TS3ClientConnection(os.getenv('BOTS_TS3_CLIENT_LOCATION')) as tsconn:
        tsconn.auth(apikey=os.getenv('BOTS_TS3_AUTHKEY'))
        tsconn.use()

        try:
            x = requesting("playing", tsconn)
            #print(x)
            if x != "STATUS_NO_SONG_PLAYING" and x is not None:
                j = json.loads(x)
                try:
                    tsconn.clientupdate(client_nickname="Music Bot - "+str(j["item"]["name"][0:18]))
                    tsconn.sendtextmessage(targetmode=2, target=1, msg="Now playing [color=aqua]" + str(j["item"]["name"]) + "[/color].")
                except:
                    tsconn.whoami()
                    pass
            time.sleep(5)
            if thread2.keepalive and n<500:
                naming(n+1)
            else:
                thread2 = myThread(2, "Thread-2")
                thread2.start()
        except:
            tsconn.sendtextmessage(targetmode=2, target=1,msg="[color=orange]Spotify Auth Key went south so I am resetting and script will restart in 15 seconds[/color]")
            #authGen = requests.get(os.getenv('SPOTIFY_API_WEBSITE'))
            import webbrowser
            url = os.getenv('SPOTIFY_API_WEBSITE')
            webbrowser.open_new_tab(url)
            time.sleep(15)
            os.system("taskkill /im chrome.exe /f")
            # remove the comment in the below line when running in powershell
            os.execv(sys.executable, ['python'] + sys.argv)


def convertMillis(millis):
    data = []
    millis = int(millis)
    seconds = (millis / 1000) % 60
    data.append(str(int(seconds)))
    minutes = (millis / (1000 * 60)) % 60
    data.append(int(minutes))
    data = ['%02d' % float(x) for x in data]
    return data[0], data[1]


def requesting(command, tsconn):

    r = requests.get(os.getenv('SPOTIFY_API_WEBSITE') + "api?command=" + command) #Send Command to API
    x = r.text
    if x[0] == "<":
        tsconn.sendtextmessage(targetmode=2, target=1, msg="[color=red]Shits down[/red]")
    elif x == "ERROR_NO_VALID_AUTH_TOKENS":
        tsconn.sendtextmessage(targetmode=2, target=1, msg="[color=red]No valid auth tokens[/color]")
    else:
        return x


def setdevice(nid):
    global goodid
    if nid == "":
        return goodid
    else:
        goodid = nid


def follow(thefile, tsconn):
    loopCount = 0 #600 = 1 minute - will reset when someone sends a command
    print('counter reset')
    thefile.seek(0, 2)
    while True:
        loopCount+=1
        if loopCount == 600:
            tsconn.send_keepalive()
            print('sent a keepalive for thread 1')
            loopCount = 0
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line  # litteraly no idea how it work, just does


def userinput(command, inputs, tsconn): #Transforms Userinput to command for API

    songName = " ".join(command[1::])
    print(songName)
    if inputs == "queue":
        url = "queue"
        text = "Queueing"
    else:
        url = "play"
        text = "Playing"

    if songName[0:9] == "[URL]http":
        lst = songName.split("/")
        songName = str(("spotify:" + lst[-3] + ":" + lst[-2]).rstrip("["))
        songName = songName.split("?")
        x = requesting(url + "&playObject=" + songName[0], tsconn)
        tsconn.sendtextmessage(targetmode=2, target=1, msg=text + " [color=aqua]" + songName[0] + "[/color].")
    elif songName[0:7] == "spotify:":
        tsconn.sendtextmessage(targetmode=2, target=1, msg=text + " [color=aqua]" + songName + "[/color].")
        id = setdevice("")
        if id is "":
            tsconn.sendtextmessage(targetmode=2, target=1, msg="Try setting the device id.")
        else:
            request = requesting("setdevice&device_id=" + id)
            x = requesting(url + "&playObject=" + songName, tsconn)
            print(x)
    else:
        searchtype = "track"
        songName = songName.split(" ")
        if songName[0] == "album" or songName[0] == "playlist":
            searchtype = songName[0]
            songName.remove(songName[0])
        songName = " ".join(songName).split(" by ")
        if len(songName) > 1:
            searchtype += ",artist"
            request = requesting(
                "search&name=" + quote(songName[0]) + "%20" + quote(songName[1]) + "&type=" + searchtype, tsconn)
            print("search&name=" + quote(songName[0]) + "%20" + quote(songName[1]) + "&type=" + searchtype)
        else:
            # api?command=search&name=Fever Dream&type=(OPTIONAL WITH TRACK BEING DEFAULT) track,artist,playlist,album
            request = requesting("search&name=" + quote(songName[0]) + "&type=" + searchtype, tsconn)
            print("search&name=" + quote(songName[0]) + "&type=" + searchtype)

        x = requesting("playing", tsconn)
        if x == "STATUS_NO_SONG_PLAYING" or x is None:
            # requests the currently paused song to continue playing
            f = requesting("play", tsconn)
            print(f)
        j = json.loads(request)
        try:
            uri = j["tracks"]["items"][0]["uri"]
            request = requesting(url + "&playObject=" + uri, tsconn)
            tsconn.sendtextmessage(targetmode=2, target=1, msg=text + " [color=aqua]" + j["tracks"]["items"][0]["name"] + "[/color].")
            print(request)
        except:
            tsconn.sendtextmessage(targetmode=2, target=1, msg="[color=orange]No results[/color]")


def startup():

    with ts3.query.TS3ClientConnection(os.getenv('BOTS_TS3_CLIENT_LOCATION')) as tsconn:
        tsconn.auth(apikey=os.getenv('BOTS_TS3_AUTHKEY'))
        tsconn.use()

        # Somehow it fucking works, don't ask
        tsconn.sendtextmessage(targetmode=2, target=1, msg="Hello World!")
        try:
            tts.play("Hello world")
        except:
            tsconn.sendtextmessage(targetmode=2, target=1, msg="TTS is offline! :(")
        # Should send to Teamspeak "Hello World" if working

        varCommand = ' !'  # What the bot looks for

        logfile = open(
            os.getenv('TS3_CLIENT_LOGFILE_PATH'),
            "r")
        # Channel Log file location

        loglines = follow(logfile, tsconn)
        for line in loglines:
            # print(line)
            if varCommand in line:
                print('Command found')
                # print(line)
                command = line.split(varCommand, maxsplit=1)[1]
                command = command.rstrip().split(" ")
                print(command)
                if command[0] == 'stop':
                    tsconn.sendtextmessage(targetmode=2, target=1, msg="lol nice try")
                    #thread2.keepalive = False
                    #os._exit(1)

                # ----------------------------------------------------------------------------------------------------------
                elif command[0] == 'play' and len(command) > 1: #goes to spotify commands (userinput method)
                    userinput(command, "play", tsconn)
                # ----------------------------------------------------------------------------------------------------------
                elif command[0] == 'play':
                    # getting the status code of playing ie. determining if a song is playing
                    x = requesting("playing", tsconn)
                    if x != "STATUS_NO_SONG_PLAYING" and x is not None:
                        j = json.loads(x)
                        if not j["is_playing"]:
                            x = "STATUS_NO_SONG_PLAYING"


                    if x == "STATUS_NO_SONG_PLAYING" or x is None:

                        # requests the currently paused song to continue playing
                        id = setdevice("")
                        if id is "":
                            tsconn.sendtextmessage(targetmode=2, target=1, msg="Try setting the device id.")
                        else:
                            r = requesting("setdevice&device_id=" + id, tsconn)
                            print(r)
                            f = requesting("play", tsconn)
                            tsconn.sendtextmessage(targetmode=2, target=1, msg="Resuming music.")
                            print(f)
                    elif x == "pass":
                        pass

                    else:
                        p_sec, p_min = convertMillis(j["progress_ms"])
                        d_sec, d_min = convertMillis(j["item"]["duration_ms"])
                        tsconn.sendtextmessage(targetmode=2, target=1, msg=j["item"][
                                                                               "name"] + " already playing. [color=red]" + p_min + ":" + p_sec + " - " + d_min + ":" + d_sec + "[/color]")
                # ----------------------------------------------------------------------------------------------------------
                elif command[0] == 'pause':
                    r = requesting("pause", tsconn)
                    # print(r)
                    tsconn.sendtextmessage(targetmode=2, target=1, msg="Stopping the music")
                # ----------------------------------------------------------------------------------------------------------
                elif command[0] == 'skip':
                    r = requesting("next", tsconn)
                    # print(r)
                    tsconn.sendtextmessage(targetmode=2, target=1, msg="Skipping song")
                # ----------------------------------------------------------------------------------------------------------
                elif command[0] == 'queue' and len(command) > 1:
                    userinput(command, "queue", tsconn)

                # ----------------------------------------------------------------------------------------------------------


                elif command[0] == "stonks":
                    userStock = command[1]
                    tsconn.sendtextmessage(targetmode=2, target=1, msg="[color=orange]Stonks is deprecated. Blame Yahoo[/color]")
                    # try:
                    #     stockProcess = stockquotes.Stock(userStock)
                    #     if (stockProcess.increase_percent > 0 ):
                    #
                    #         tsconn.sendtextmessage(targetmode=2, target=1,
                    #                                msg=userStock.upper() + " current is worth $" + str(
                    #                                    stockProcess.current_price) + "([color=green]" + str(
                    #                                    stockProcess.increase_percent) + "%[/color])")
                    #         tts.play(userStock.replace("", " ")[1: -1] + " is going for $" + str(
                    #                                    stockProcess.current_price) + " and is up " + str(
                    #                                    stockProcess.increase_percent) + " percent")
                    #
                    #
                    #     else:
                    #         tsconn.sendtextmessage(targetmode=2, target=1,
                    #                                msg=userStock.upper() + " current is worth $" + str(
                    #                                    stockProcess.current_price) + "([color=red]" + str(
                    #                                    stockProcess.increase_percent) + "%[/color])")
                    #         tts.play(userStock.replace("", " ")[1: -1] + " is going for $" + str(
                    #             stockProcess.current_price) + " and is down " + str(
                    #             stockProcess.increase_percent) + " percent")
                    # except:
                    #     tsconn.sendtextmessage(targetmode=2, target=1, msg="[color=orange]Invaild ticker[/color]")
                elif command[0] == "tts":
                    ttsCommand = " ".join(command[1::])
                    if len(ttsCommand) > 1000:
                        tts.play("Please send a shorter message.")
                    else:
                        tts.play(ttsCommand)

                elif command[0]=='reboot':
                    os.execv(sys.executable, ['python'] + sys.argv)
                # ----------------------------------------------------------------------------------------------------------
                elif command[0] == "help":
                    # this formatting looks stupid here but great on teamspeak
                    tsconn.sendtextmessage(targetmode=2, target=1, msg="\n[b]Known Commands[/b]\n"
                                                                       "[b]devices[/b]                                 Returns a list of possible devices.\n"
                                                                       "[b]setdevice [i]<device id>[/i][/b]     Sets a device to be controlled by this bot.\n"
                                                                       "[b]help[/b]                                       Displays this help menu\n"
                                                                       "[b]pause[/b]                                    Pauses the current song.\n"
                                                                       "[b]play[/b]                                       Unpauses the current song.\n"
                                                                       "[b]play [i]<song name>[/i][/b]            Starts playing the song requested.\n "
                                                                       "[b]queue [i]<songname>[/i][/b]         Adds the requested song to the song queue\n"
                                                                       "[b]skip[/b]                                        Skips the current song.\n")
                # ----------------------------------------------------------------------------------------------------------
                elif command[0] == "help' for a list of commands.":
                    pass
                # ----------------------------------------------------------------------------------------------------------
                # ----------------------------------------------------------------------------------------------------------
                elif command[0] == "reboot": #wont work in pycharm (just ends the script.. need to use powershell or cmd
                    tsconn.sendtextmessage(targetmode=2, target=1, msg="One sec Cheif, rebooting now")
                    os.execv(sys.executable, ['python'] + sys.argv)
                # ----------------------------------------------------------------------------------------------------------
                elif command[0] == "devices":
                    x = requesting("devices", tsconn)
                    j = json.loads(x)
                    names = []
                    ids = []
                    string = "\n"
                    for x in j["devices"]:
                        names.append(x["name"])
                        ids.append(x["id"])
                    for x in range(len(names)):
                        string = string + str(x + 1) + ". " + names[x] + " - " + ids[x] + "\n"
                    tsconn.sendtextmessage(targetmode=2, target=1, msg=string)
                # ----------------------------------------------------------------------------------------------------------
                elif command[0] == "setdevice" and command[1] is not None:
                    setdevice(command[1])
                    tsconn.sendtextmessage(targetmode=2, target=1, msg="Device id set to " + command[1] + ".")
                # ----------------------------------------------------------------------------------------------------------
                elif command[0] == "time":
                    x = requesting("playing", tsconn)
                    if x != "STATUS_NO_SONG_PLAYING" and x is not None:
                        j = json.loads(x)
                        p_sec, p_min = convertMillis(j["progress_ms"])
                        d_sec, d_min = convertMillis(j["item"]["duration_ms"])
                        tsconn.sendtextmessage(targetmode=2, target=1,
                                               msg="There is a song playing or paused. [color=red]" + p_min + ":" + p_sec + " - " + d_min + ":" + d_sec + "[/color]")
                    else:
                        tsconn.sendtextmessage(targetmode=2, target=1, msg="No song is playing or paused.")
                # ----------------------------------------------------------------------------------------------------------
                # ----------------------------------------------------------------------------------------------------------
                else: #need to send a keepalive somewhere or open only 1 telenet that the threads share
                    tsconn.sendtextmessage(targetmode=2, target=1,
                                           msg="Command not understood type '!help' for a list of commands.")

                # Create new threads

thread1 = myThread(1, "Thread-1")
thread2 = myThread(2, "Thread-2")

thread1.daemon=True
# Start new Threads
thread1.start()
thread2.start()


