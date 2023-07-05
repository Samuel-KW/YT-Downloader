
file_data = 'data.csv'

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
        self.urls = []

# Get downloaded song information
def get_song_data():
    
    songs = []
    lines = open(file_data).read().split('\n')
    
    for line in lines:
        if len(line) > 5:
            songs.append(line.split(','))

    return songs

# Get audio files from YouTube video ID and save to directory        
def get_audio(url, directory, save_new=False):

    try:
        audio = pafy.new(url, basic=True, gdata=False)
        
        print(Fore.CYAN + 'Downloading' + Fore.YELLOW, audio.title + Fore.WHITE)
        
        # Get best audio quality
        audio_stream = audio.getbestaudio(preftype=file_type, ftypestrict=True)

        print()

        # Create filename
        filename = url + '.' + file_type

        # Parse data
        title  = re.sub('[^a-zA-Z0-9_]', '', re.sub(' ', '_', audio.title ))
        artist = re.sub('[^a-zA-Z0-9_]', '', re.sub(' ', '_', audio.author))
        
        # Save the file if isn't a duplicate
        if has_song(url, title, artist, False):

            print(Fore.RED + 'Song is already in collection:', Fore.YELLOW + audio.title)

            return
            
        else:

            filepath = os.path.join(directory, filename)
            audio_stream.download(filepath=filepath)

            try:
                audio = MP4(directory + filename)

                if not audio.tags:
                    audio.add_tags()
                
                audio.tags['\xa9nam'] = title
                audio.tags['\xa9ART'] = artist

                audio.tags['title'] = title
                audio.tags['artist'] = artist

                audio.save()
                
                if save_new:
                    copyfile(directory + filename, new_songs_dir + filename)
                    audio = MP4(new_songs_dir + filename)

                    if not audio.tags:
                        audio.add_tags()
                    
                    audio.tags['\xa9nam'] = title
                    audio.tags['\xa9ART'] = artist

                    audio.tags['title'] = title
                    audio.tags['artist'] = artist

                    audio.save()

            except Exception as e:

                print(Fore.RED + 'Error saving metadata:', e)

            songs.append([url, title, artist, filename])


        return filepath, filename

    except Exception as e:
        print(Fore.RED + str(e))
        failed_ids.append(url)

# Determine if song is already downloaded
def has_song(video_id, title='', artist='', strict=True):
    for song in songs:
        if song[0] == video_id:
            return True, song

        if not strict and song[1] == title and song[2] == artist:
            return True, song

    return False

# Save downloaded songs to file
def save_songs():
    data = []

    for song in songs:
        data.append(','.join(song))
    
    file = open(file_data, 'w')
    file.write('\n'.join(data))
    file.close()

def ytLog(info):
    if info['status'] == 'finished':
        print('Done downloading, now post-processing ...')

# Start download of songs from array of video IDs
def start(urls, directory, save_new=False):

    goodUrls = []

    for videoId in urls:
        index += 1

        is_downloaded = has_song(videoId);

        if not is_downloaded:
            goodUrls.append(videoId)
        else:
            print(Fore.RED + 'Song already downloaded:', Fore.YELLOW + is_downloaded[1][1])
        
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': 'new_songs/%(id)s.%(ext)s',
        'progress_hooks': [ytLog],
        'postprocessors': [{
            'key': 'FFmpegMetadata',
            'add_metadata': True,
        }, {  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }]
    }

    if os.name == 'nt':
        os.system('title Progress: ' + str(index) + ' / ' + str(len(urls)))

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download(urls)

    print(error_code)

    

    save_songs()
    

    print(Fore.CYAN + '\nFinished downloading' + Fore.YELLOW, len(urls), Fore.CYAN + 'audio files.\n')

# Parse data from Google takeout playlist data
def parse_from_takeout(directory):
    
    playlist_files = os.listdir(directory)
    print(Fore.WHITE + '\nSelect playlist to download:\n')

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
    urls = []

    for line in contents:
        section = line.split(',')[0].strip()
        if len(section) == 11:
            urls.append(section)

    return urls

# Delete the contents of a folder
def delete_folder(directory):
    print(Fore.RED + '\nAre you sure you want to delete all files in', Fore.YELLOW + directory + Fore.RED + '?')

    files = os.listdir(directory)
    print(Fore.RED + 'You will be deleting' + Fore.YELLOW, len(files), Fore.RED + 'files.\n')

    if len(files) > 0:
        print(Fore.RED + 'Preview of files:')
        for file in files[:5]:
            print(Fore.YELLOW, file)

    print(Fore.WHITE)

    if input('Are you sure? (y/n): ') == 'y':
        for file in files:
            os.remove(os.path.join(directory, file))

# Get previously downloaded songs
songs = get_song_data()
print(Fore.CYAN + 'Parsed CSV data from' + Fore.YELLOW, file_data)

# List of song IDs to download
urls = []

# Download from takeout
urls = parse_from_takeout(playlists_dir)

print(Fore.CYAN + 'Parsed playlist from' + Fore.YELLOW, playlists_dir)
print('\t', urls[0], '\n\t', urls[1], '\n\t', urls[2], '...')

save_new = False

print(Fore.CYAN + '\nWould you like to save new songs to', Fore.YELLOW + new_songs_dir + Fore.CYAN + '?' + Fore.WHITE)

if input('(y/n): ') == 'y':
    save_new = True
    delete_folder(new_songs_dir)

start(urls, file_output, save_new)

if len(failed_ids) > 0:
    print(Fore.YELLOW + 'Failed to fetch ' + str(len(failed_ids)) + ' videos.')
    print(Fore.WHITE + '\n'.join(failed_ids))
