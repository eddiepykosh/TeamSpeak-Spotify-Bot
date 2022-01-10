**Note - Due to nature of this, this is not scalable for others.  Just a proof of concept that I co-wrote for my friend's TeamSpeak Server**
The Spotify portion of this works as follows:

1. Bot Owner Authencates Spotify Creds into a website, we will call it Spotify Web Bridge (website was created by a friend.  site is private, sorry)
2. After authencation, Bot Owner uses !setdevice in TS3 chat to have Spotify API do actions to their Spotify client
3. Bot is Ready
-------
1. Python Script receives request from a TeamSpeak User via a log file.
2. Python transforms request into a link to send to Spotify Web Bridge
3. Request is sent to Spotify Web Bridge
4. Spotify Web Bridge then asks Spotify API to do an action to Bot Owner's Spotify client
-------
This things needs quite a few libraries to work.  Just check the import line of the python files for what you need.
**Be sure for the TeamSpeak API to use "pip install ts3query NOT pip install ts3**

This was built on Windows Server but probably could get functioning on Linux
Uses Python 3.10.0
You'll need a install of a Spotify Client and TeamSpeak 3 
You'll also need a virtual audio cable (or something similar) to pump Spotify audio into TeamSpeak.
Proper values set in the .env file

This also uses AWS Polly. I did not built that part of the bot.  If you do not have AWS Polly setup, no worries, the bot should just ignore the TTS stuff (just don't use !TTS) 
