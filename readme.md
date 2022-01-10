**Note - Due to nature of this, this is not scalable for others.  Just a proof of concept that I co-wrote for my friend's TeamSpeak Server**
The Spotify portion of this works as follows:

1. Bot Owner Authencates Spotify Creds into a website, we will call it Spotify Web Bridge (website was created by a friend.  site is private, sorry)
2. After authencation, Bot Owner uses !setdevice in TS3 chat to have Spotify API do actions to their Spotify client
3. Bot is Ready

1. Python Script receives request from a TeamSpeak User via a log file.
2. Python transforms request into a link to send to Spotify Web Bridge
3. Request is sent to Spotify Web Bridge
4. Spotify Web Bridge then asks Spotify API to do an action to Bot Owner's Spotify client
