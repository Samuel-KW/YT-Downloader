
file_output = 'songs/'
new_songs_dir = 'new_songs/'

playlists_dir = 'Takeout/YouTube and YouTube Music/playlists'
file_type = 'm4a'

failed_ids = []


import os, re

import yt_dlp
from colorama import Fore, init
from shutil import copyfile

from mutagen.mp4 import MP4


init(convert = True) if os.name == 'nt' else init()

print(Fore.MAGENTA + '\nYouTube Downloader')
print(Fore.WHITE + 'https://github.com/Samuel-UC\n\n')
        

class YoutubeDownloader:

    def __init__(self):
        self.downloadedIds = set()
        self.saveNewSongs = False

        self.filesDownloaded = 0
        self.filesToDownload = 0

        self.failedIDs = set()

    def start(self, inputDir, outputDir, newSongDir, fileType):
        
        # Get songs from takeout
        ids = self.getTakeoutSongs(inputDir)
        print(f'{Fore.CYAN}Parsed takeout data from {Fore.YELLOW}{inputDir}')
        
        # Fetch previously downloaded songs
        self.downloadedIds.update(self.getFiles(outputDir))
        print(f'\n{Fore.CYAN}Fetched ({Fore.YELLOW}{len(ids)}{Fore.CYAN}) previously downloaded songs from {Fore.YELLOW}{outputDir}')

        # Remove duplicate songs
        self.removeSetDuplicates(ids, self.downloadedIds)
        self.filesToDownload = len(ids)
        print(f'\n{Fore.CYAN}Removed duplicate songs.\nTotal unique songs: {Fore.YELLOW}{len(ids)}')

        print(f'\n{Fore.CYAN}Would you like to save new songs to {Fore.YELLOW}{newSongDir}{Fore.CYAN}?{Fore.WHITE}')
        if input('(y/n): ') == 'y':
            self.saveNewSongs = True
            self.deleteFolderContents(newSongDir)


        ydl_opts = {
            'format': 'm4a/bestaudio/best',
            'outtmpl': file_output + '%(id)s.%(ext)s',
            'progress_hooks': [self.onDownloadProgress],

            'postprocessors': [{
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            }, {  # Extract audio using ffmpeg
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
            }],
            'ffmpeg_location': 'C:\\Program Files\\ffmpeg\\bin',
            'ignoreerrors': True,
            'logger': LogHandler
        }


        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(ids)

        if len(self.failedIDs) > 0:
            print(Fore.YELLOW + 'Failed to fetch ' + str(len(failed_ids)) + ' videos.')
            print(Fore.WHITE + '\n'.join(failed_ids))

    def removeSetDuplicates(self, arr1: set, arr2: set):
        for val in arr2:
            if val in arr1:
                arr1.remove(val)

        return arr1

    def getFiles(self, directory):
        
        files = set()

        for file in os.listdir(directory):
            full_path = os.path.join(directory, file)
            if os.path.isfile(full_path):
                file_name = os.path.splitext(file)[0]
                files.add(file_name)

        return files
    
    # Parse data from Google takeout playlist data
    def getTakeoutSongs(self, directory):
        
        playlist_files = os.listdir(directory)
        print(Fore.WHITE + 'Select playlist to download:\n')

        for i in range(len(playlist_files)):
            print(Fore.YELLOW, '[' + str(i) + ']', Fore.CYAN, playlist_files[i])

        print(Fore.WHITE)

        selected = None
        while not selected:
            try:
                selected = playlist_files[int(input())]
            except:
                print(Fore.RED + 'Invalid selection.' + Fore.WHITE)

        print(Fore.CYAN + '\nParsing playlist:', Fore.YELLOW + selected)

        contents = open(os.path.join(directory, selected)).read().splitlines()[8:]
        urls = set()

        for line in contents:
            section = line.split(',')[0].strip()
            if len(section) == 11:
                urls.add(section)

        return urls
    
    # Delete the contents of a folder
    def deleteFolderContents(self, directory):

        files = os.listdir(directory)
        if len(files) < 1:
            return

        print(f'\n{Fore.RED}Are you sure you want to delete all files in {Fore.YELLOW}{directory}{Fore.RED}?')

        print(f'{Fore.RED}You will be deleting {Fore.YELLOW}{len(files)}{Fore.RED} files.')

        if len(files) > 0:
            print(Fore.RED + 'Preview of files:')
            for file in files[:5]:
                print(Fore.YELLOW, file)

        print(Fore.WHITE)

        if input('Are you sure? (y/n): ') == 'y':
            for file in files:
                os.remove(os.path.join(directory, file))

    def onDownloadProgress(self, info):
        
        if info['status'] == 'error':
            print(info['info_dict'])
            #self.failedIDs.add('')

        if info['status'] == 'finished':
            if os.name == 'nt':
                self.filesDownloaded += 1
                os.system(f'title Progress: {self.filesDownloaded} / {self.filesToDownload}')


class LogHandler:


    def error(msg):
        pass

    def warning(msg):
        pass

    def debug(msg):
        pass

dl = YoutubeDownloader()
dl.start(playlists_dir, file_output, new_songs_dir, file_type)