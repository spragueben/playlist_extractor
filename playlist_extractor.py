# 2022.07.26 11:04PM

# Filename: playlist_extractor.py
# Author: Ben Sprague

import os
import sys
import time
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
import webbrowser
import tkinter as Tk
import shutil
import platform
import subprocess
from os.path import exists

PLAYLIST_URL = input(f"\nWhat is the web address (url) of the playlist you would like to watch with VLC? (or just press <ENTER> to try a sample)\n> ") or "https://www.youtube.com/playlist?list=PLN-FMT_Cr3Zxz3rUXmQJrz9ij0GhdEiI1"
print(f"\nThe url of the selected playlist is: {PLAYLIST_URL}")
PLAYLIST_TITLE = input("\nPlease enter a name for your playlist.\n> ") or "My_Playlist"
VLC_PATH = "/Applications/VLC.app/Contents/MacOS/VLC"
PROJECT_ROOT = os.getcwd()
VIRTUAL_ENV = sys.prefix
print(f"Playlist title: {PLAYLIST_TITLE}\nPlaylist location:{PROJECT_ROOT}\n\nPlease wait a moment while the webdriver retrieves your page.")

exe = shutil.which('chromedriver')
proceed_prompt = "\n------------------ Press <ENTER> to continue ------------------"
paginator =    "\n---------------------------------------------------------------"
env_bin = os.path.join(sys.prefix, "bin")

def trim(docstring):
    if not docstring:
        return ''
    lines = docstring.expandtabs().splitlines()
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    trimmed = [lines[0].strip()]
    if indent < sys.maxsize:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    return '\n'.join(trimmed)

DRIVER_PATH = os.path.join(env_bin,"chromedriver")
if platform.system() == "Windows":
    DRIVER_PATH = os.path.join(env_bin,"chromedriver.exe")

if exists(DRIVER_PATH) == False:
    while os.path.splitext(exe)[0] != DRIVER_PATH:
        print(f'''\nWe recommend having chromedriver installed in your virtual environment bin folder: {env_bin}''')
        if exe:
            print(f"\nYou have chromedriver installed here: {exe}")
            if input(f'''\nRun chromedriver from its current location? {exe} (y/[n])? ''').lower() in ['y','yes']:
                print(f"{paginator}\nRunning chromedriver from {exe}")
                break

        if shutil.which('chromedriver', path = DRIVER_PATH) == None:

            if input(f'''{paginator}\nWould you like to install chromedriver in your {env_bin} directory ([y]/n)? ''').lower() in ['y','yes','']:
                
                print(paginator)
                print("The path to your environment's bin directory is here: ", os.path.join(sys.prefix,bin))
                
                if input(trim('''\nIn a moment, we will open a guide to downloading the right version of chrome driver, and we recommend (again) that you download chromedriver into your environment's bin directory

                To open a guide on installing the correct version of chrome driver, press any key (then enter). Otherwise, just press enter and we will skip right to the downloads page. ''')).strip() != "":
                    webbrowser.open("https://sites.google.com/a/chromium.org/chromedriver/downloads/version-selection")
                
                else:
                    webbrowser.open("https://chromedriver.chromium.org/downloads")
                    
                print(paginator)
                print("\nThe download guide can be found here: https://sites.google.com/a/chromium.org/chromedriver/downloads/version-selection")
                print("\nThe url for downloading chromedriver is: https://chromedriver.chromium.org/downloads")
                input(proceed_prompt)
                temp = input(trim('''\nOnce downloaded, we'll (still) need the path to your chromedriver installation.

                Though you're free to put it somewhere else, we recommend you put it in you environment's bin directory.

                When you have the chromedriver executable where you want it, paste the path here or press enter to browse for it. 
                ''')) or None
                
                if temp:
                    DRIVER_PATH = temp
                
                else: 
                    try:
                        from tkFileDialog import askopenfilenames
                    except:
                        from tkinter import filedialog

                    Tk().withdraw() 
                    filenames = filedialog.askopenfilenames() 

                    DRIVER_PATH = filenames
                    input(proceed_prompt)
                    exe = DRIVER_PATH

# https://stackoverflow.com/questions/53657215/running-selenium-with-headless-chrome-webdriver/53657649#53657649

from selenium.webdriver.chrome.options import Options
chrome_options = Options()
#chrome_options.add_argument("--disable-extensions")
#chrome_options.add_argument("--disable-gpu")
#chrome_options.add_argument("--no-sandbox") # linux only
chrome_options.add_argument("--headless")
# chrome_options.headless = True # also works
# driver = webdriver.Chrome(options=chrome_options)

driver = webdriver.Chrome(executable_path = DRIVER_PATH, options=chrome_options)
driver.get(PLAYLIST_URL)
time.sleep(5)

soup = BeautifulSoup(driver.page_source, 'html.parser')

links_html = []
for link in soup.find_all('a', href=True):
    links_html.append(link['href'])

links_list_1 = [url1 for url1 in links_html if "/watch?v" in url1]
links_list_2 = [url2 for url2 in links_list_1 if "&index=" in url2]

addon_result = []
for i in links_list_2:
    if i not in addon_result:
        addon_result.append(i)

url_list = []
for i in range(len(addon_result)):
    url_list.append("https://www.youtube.com" + addon_result[i])

youtube_junk_urls = ["Shorts","YouTube Home", "Home", "Explore", "Subscriptions", "Library", "History", "Share link", "Next (SHIFT+n)"]

title_list = []
for name in soup.find_all('a', title=True):
    a = name['title']
    if a not in youtube_junk_urls:
        title_list.append(a)  

duration_html = []
for label in soup.find_all('span'):
    value = label.get('aria-label')
    if value is not None:
        duration_html.append(value)

author_template = []
for label in soup.find_all('a'):
    if label.get('dir') == 'auto':
        a = label.get_text()
        
        author_template.append(a)
author_list = author_template[2:]

seconds_per_unit = {"s": 1, "m": 60, "h": 3600} 
def convert_to_seconds(s):
    return int(s[:-1]) * seconds_per_unit[s[-1]] 

import re 
reg = r'([0-9]+\s[^0-9])' 

def convert_to_ms(s): 
    return int(s[:-1]) * seconds_per_unit[s[-1]] * 1000 

def convert_durations(duration_list):         
    l = duration_list[:]                      
    for i in range(len(l)):                   
        l[i] = re.findall(reg,l[i].strip())   
        for a in range(len(l[i])):            
            l[i][a] = convert_to_ms(l[i][a])  
        l[i] = sum(l[i])                      
    return l                                  
duration_list = convert_durations(duration_html) 

dict 		= {'location': url_list , 'title': title_list, 'creator': author_list, 'duration': duration_list, 'annotation':title_list, 'genre':title_list}
df			= pd.DataFrame.from_dict(dict, orient='index')
df.iloc[4]  = "description content via the 'annotation' xml tag"
df.iloc[5]  = "ain't no genre when it's gone"

import xml.etree.ElementTree as xml

root            = xml.Element('playlist')
title           = xml.SubElement(root, 'title')
trackList       = xml.SubElement(root,'trackList')
title.text      = PLAYLIST_TITLE
columns         = df.columns
rows            = df.index

root.set('xmlns','http://xspf.org/ns/0/')
root.set('xmlns:vlc','http://www.videolan.org/vlc/playlist/ns/0/')
root.set('version', '1')

for column in columns:
    entry = xml.SubElement(trackList, 'track')
    for row in df.index:
        schild = row
        child = xml.SubElement(entry, str(schild))  
        child.text = str(df[column][schild])

xml_data = xml.tostring(root)  

with open(os.path.join(PROJECT_ROOT,"playlist.xspf"), 'w') as f:  
    f.write(xml_data.decode('utf-8'))

x = {'YouTube_Video_URL': url_list ,'Playlist_Item_Title': title_list , 'Runtime': duration_list , 'Author': author_list}

df_videodata = pd.DataFrame.from_dict(x, orient='index')

ext_list = ['.mp4', '.mkv', '.avi', '.flv', '.mov', '.wmv', '.vob',
'.mpg','.3gp', '.m4v', '.m3u']		

check_subdirectories = False		

class Playlist:
	"""Build xml playlist."""
	
	def __init__(self):
	
		self.playlist = xml.Element('playlist')
		self.tree = xml.ElementTree(self.playlist)
		self.playlist.set('xmlns','http://xspf.org/ns/0/')
		self.playlist.set('xmlns:vlc','http://www.videolan.org/vlc/playlist/ns/0/')
		self.playlist.set('version', '1')

		self.title = xml.Element('title')
		self.playlist.append(self.title)
		self.title.text = 'Playlist'

		self.trackList = xml.Element('trackList')
		self.playlist.append(self.trackList)

	def add_track(self, path, dataframe=""):
	
		track 			= xml.Element('track')
		location 		= xml.Element('location')
		location.text = path
		track.append(location)
		self.trackList.append(track)
	
	def get_playlist(self):
		return self.playlist

class Videos:
	"""Manage files (videos) to be added to the playlist."""
	def __init__(self):
		pass

	def remove_nonvideo_files(self,file_list):
	
		for index,file_name in enumerate(file_list[:]):
			
			if file_name.endswith(tuple(ext_list)) or file_name.endswith(tuple(ext.upper() for ext in ext_list)):
				pass
			else:
				file_list.remove(file_name)
		return file_list
	
	def edit_paths(self, video_files):
	
		for index in range(len(video_files)):
			video_files[index] =( 
			'file:///' + os.path.join(video_files[index])).replace('\\','/')
		return video_files
	
	def get_videos(self):
	
		if check_subdirectories == True:
			pathlist = [os.getcwd()]	
			for root, dirs, files in os.walk(os.getcwd()):
				for name in dirs:
						subdir_path = os.path.join(root, name)
						if subdir_path.find('\.') != -1:	
							pass
						else:
							pathlist.append(subdir_path)
							
			videos = []
			for path in pathlist:
				all_files = os.listdir(path)
				for f in self.remove_nonvideo_files(all_files):
					location = path+ '\\' + f
					videos.append(location)
			return videos	
		else:
			videos = []
			all_files = os.listdir()
			for f in self.remove_nonvideo_files(all_files):
					location = os.getcwd() + '\\' + f
					videos.append(location)
			return videos

def main():	
	playlist = Playlist()
	videos = Videos()
	
	video_files = videos.get_videos()
	video_paths = videos.edit_paths(video_files)
	
	for path in video_paths:
		playlist.add_track(path)
	
	playlist_xml = playlist.get_playlist()
	with open('songs.xspf','w') as mf:
		mf.write(xml.tostring(playlist_xml).decode('utf-8'))

main()

subprocess.Popen([VLC_PATH, '--playlist-autostart', 'playlist.xspf'])
driver.quit()