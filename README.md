# Music Manager
A convenient app to download and edit metadata for Spotify tracks and Youtube videos
### This app is for personal use only. Using any file generated by this app commercially may result in copyright infrigment!

![Promote](images/promo.png)

## Features
- Get liked tracks and playlists from Spotify \
  (You will need to bring your own Spotify API secrets. Get yours
[here](https://developer.spotify.com/). You can also request to use mine [here]())
#### NOTE: Please put the following addresses as Redirect URIs if you decide to use your own API key
```
http://localhost:1908
http://127.0.0.1:36914/spotify
```
- Get individual Youtube video or an entire playlist
- Search for the corresponding video on Youtube
- Download from Youtube
- Edit and write metadata (image included)

## How to install
- Download the latest build from [release](https://github.com/letiendat198/MediaManager/releases)
- Download [ffmpeg](https://www.ffmpeg.org/) binary and place ffmpeg.exe in the same folder with Music Manager.exe 
(Optionally, you can put ffmpeg.exe in PATH) \
**FFMPEG IS A MUST FOR DOWNLOAD FUNCTION TO WORK**

## How to build
- Install the dependencies in `requirements.txt` with `python3 -m pip install -r requirements.txt`
- Run `pyinstaller main.spec`
### Note: After building is completed, please move the `resources` folder from `dist` to root

## TODO
<details>
  <summary>Already done</summary>

- ~~Add Batch download Youtube~~
- ~~Allow user to specify download path~~
- ~~Change to id based storage~~
- ~~Create a DataHandler to handle all those playlist and stuffs~~
- ~~Fetch album data from Spotify and show it~~
- ~~Allow to add a Spotify playlist~~
- ~~Allow to add a Youtube video and playlist (I don't use YT playlist much so this gonna be put off :D)~~
- ~~Refresh yt-title when yt-url is changed~~
- ~~Show tracks separated by playlist~~ (And sorted by A-Z)
- ~~Batch get url skip songs that already have url~~
- ~~Store mp3 path info of songs~~
- ~~Validate downloaded info~~ (When hit Refresh) (Investigate missing downloads too - Probably overlapping song names)
- ~~Auto change mp3 metadata with supplied info~~ (When download, click "Save" or do Batch write metadata. Batch download 
not gonna write metadata. Write batch metadata manually)
- ~~Limit QThreadpool to something more reasonable so that 
Chrome webdriver not gonna murder someone machine~~ (Make a setting menu to set this too. Also 6 threads seems resonable)
- ~~Show album image~~ ~~(Rework showing logic: Prioritize embeded image)~~
- ~~Allow user to add album image~~
- ~~Delete button should delete downloaded track~~\
- ~~Allow user to add a mp3 file as download-path for songs~~
- ~~Add a button to choose download path~~
- ~~Allow user to choose whether to skip downloaded when doing batch download (Maybe get url too)~~ (Available in setting menu)
- ~~Allow user to add an mp3 file~~
- ~~Do import json~~ (Just copy-paste every json file in folder)
- ~~Add a settings menu~~
- ~~Change popups to actually look decent~~
- ~~Download video from Youtube now include thumbnails~~
</details>

- PARTIALLY REWRITE THE APP CAUSE I MADE AN UNMAINTAINABLE SPAGHETTI
- Rework Popup UI
- Allow importing a standalone audio file
- Add soundcloud ??
- Add Apple Music import through HTML (Cause I ain't paying 99$/year unless someone fund me)
- Use logger
- Use localization in entire app
- More features will be added later when I feel like it :D

## Issues tracker
<details>
  <summary>Fixed</summary>

- ~~Flickering popups~~ (Turns out you don't init QWidget many times. And don't restate UI elements many time. 
Just handle dynamic stuffs in a seperate function. Somehow only affected Download and Search)
- ~~Image chooser keep reopen~~ (Do not write .connect() in somewhere that run multiple time)
- ~~Song with same name will overlap when download~~ (File name now come with artist)
- ~~Delete button (Also other buttons too but less obvious) firing n times when used n times~~ (Again, do not write
.connect() somewhere it will be called multiple times)
- ~~DataManager may take 2 update first time to generate working data.json~~
</details>

- Write metadata is blocking GUI
- Batch get url may not close automatically
- A few things will crash randomly cause I can't squash all bugs (TODO: Add a logging system)
- Sometimes batch operations will fail with no apparent cause (More threads more fails, just retry or lower thread count in settings)
- Will add when remember

## License
    Music Manager is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
    You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>. 
