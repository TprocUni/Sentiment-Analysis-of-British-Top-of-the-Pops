import json
import csv
import glob
import requests
from time import time
from base64 import b64encode
from bs4 import BeautifulSoup
import re
import os
import time
import random

from tqdm import tqdm



class AlbumsToSongs:
    def __init__(self, albums):
        self.albums = albums
        self.song = []

        self.client_id = 'YOURCLIENTID'
        self.client_secret = 'YOURCLIENTSECRET'
        self.auth_url = "https://accounts.spotify.com/api/token"
        self.base_url = "https://api.spotify.com/v1/search"

        self.genius_base_url = "https://api.genius.com"
        self.genius_access_token = "YOURGENUISACCESSTOEKN-"

        self.auth_token = None
        self.auth_token_get_time = 0
    

    #----------------------------------------------FILE OPERATIONS----------------------------------------------#

    #gets albums from json files
    def read_from_csv(self, filename):
        filepath = f"{filename}"
        try:
            with open(filepath, newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                data = list(reader)
                return data
        except FileNotFoundError:
            return 0
        except Exception as e:
            return 0


    def sanitise_filename(self, name):
        return "".join([c for c in name if c.isalpha() or c.isdigit() or c == ' ']).rstrip().replace(' ', '_')


    # Saves songs to JSON files
    def write_to_json(self, year, month, filename, data):
        directory = f"data_songs/{year}/{month}"
        if not os.path.exists(directory):
            print("making new directory")
            os.makedirs(directory)
        filename = self.sanitise_filename(filename)
        filepath = f"{directory}/{filename}.json"
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=4)



    # gets a set of filenames, given a year (will return a list of all files for that year) or a year and 
    # month (will return a list of all files for that month in that year
    def get_filenames(self, year, month=None):
        year = str(year).zfill(4)  # Ensuring year is in XXXX format
        if month is None:
            pattern = f"data_albums/top_albums_{year}_*.csv"
        else:
            month = str(month).zfill(2)  # Ensuring month is in XX format
            pattern = f"data_albums/top_albums_{year}_{month}.csv"
        return glob.glob(pattern)
    



    #----------------------------------------------API OPERATIONS----------------------------------------------#


    # acquires the access token for the spotify API
    def get_access_token(self):
        # Encode as Base64
        auth_header = b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {"Authorization": f"Basic {auth_header}"}
        payload = {"grant_type": "client_credentials"}

        #get response from the server
        response = requests.post(self.auth_url, headers=headers, data=payload)
        if response.status_code == 200:
            token = response.json()['access_token']
        else:
            token = None
        
        #EXTRACT INFO
        self.auth_token = token
        self.auth_token_get_time = time.time()


    #should be called every iteration to ensure that the token is still valid
    def check_token_validity(self):
        current_time = time.time()
        if current_time - self.auth_token_get_time > 3600:  # 3600 seconds = 1 hour
            self.auth_token = self.get_access_token()


    #acquire album code needed to extract tracks from the album.
    def get_album_code_from_album_spotify(self, album_name, artist_name):
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        params = {"q": album_name, "type": "album", "limit": 50}
        print(f"album_name: {album_name}")
        response = requests.get(self.base_url, headers=headers, params=params)
        if response.status_code == 200:
            albums = response.json()['albums']['items']
            if albums:
                #go through each album, check if the artist is a match
                for album in albums:
                    print(f"artist name: {album['artists'][0]['name']}")
                    if album['artists'][0]['name'].lower() == artist_name.lower():
                        return album['id']
                print(f"Error: No album found matching artist name with {artist_name}.")
                return None
            else:
                return None
        else:
            #print(f"Error Status Code: {response.status_code}")
            #print(f"Error Response: {response.text}")
            print("----------------------------------NOT WORKING----------------------------------")
            return None


    # get tracks from the album using spotify API
    def get_tracks_from_album_spotify(self, album_code, artist_name):
        base_url = f"https://api.spotify.com/v1/albums/{album_code}"
        headers = {"Authorization": f"Bearer {self.auth_token}"}

        response = requests.get(base_url, headers=headers)

        if response.status_code == 200:
            #check that the artist is a match
            print (f"Artist name: {artist_name}")
            print (f"Response artist name: {response.json()['artists'][0]['name']}")
            if str(response.json()['artists'][0]['name']).lower() == str(artist_name).lower():
                # Process the response
                songDict = {}
                #add artist to songDict
                songDict['album'] = response.json()['name']
                songDict['artist'] = response.json()['artists'][0]['name']
                songDict['songs'] = []
                #add each track to songDict 'songs' = []
                for track in response.json()['tracks']['items']:
                    songDict['songs'].append(track['name'])

                return songDict
            else:
                print("Error: Artist name does not match the album artist name.")
                return None
        else:
            print(f"Error Status Code: {response.status_code}")
            print(f"Error Response: {response.text}")
            return None
        

    
    #get the genius url for the song
    def get_genius_url(self, song_name, artist_name):
        base_url = "https://api.genius.com"
        headers = {'Authorization': f'Bearer {self.genius_access_token}'}
        search_url = base_url + "/search?q="
        data = self.clean_song_name(song_name)
        search_url += data
        print(search_url)
        response = requests.get(search_url, headers=headers)
        if response.status_code == 200:
            json = response.json()
            song_info = None
            for hit in json["response"]["hits"]:
                if hit["result"]["primary_artist"]["name"].lower() == artist_name.lower():
                    song_info = hit
                    break
            if song_info:
                return song_info["result"]["url"]
            print("Not in Genius Database")
            return None
        else:
            print(f"Error Status Code: {response.status_code}")
            print(f"Error Response: {response.text}")
            return None
    

    def scrape_from_genius(self, url):
        if url is None:
            print(f"---------------------------------------NO URL GIVEN---------------------------------------")
        response = requests.get(url)
        if response.status_code == 200:
            html = BeautifulSoup(response.text, "html.parser")
            divs = html.find_all("div", class_=re.compile("^lyrics$|Lyrics__Container"))
            # This function ensures spaces are correctly inserted between elements
            add_space = lambda element: ' '.join(element.stripped_strings).replace(' ]', ']').replace('[ ', '[')

            lyrics = "\n".join([add_space(div) for div in divs])
            lyrics = re.sub(r'(\[.*?\])*', '', lyrics)
            lyrics = re.sub('\n{2}', '\n', lyrics)  # Reduce gaps between verses
            return lyrics#.strip("\n")
        else:
            None

    #----------------------------------------------DATA OPERATIONS----------------------------------------------#

    def clean_album_name(self, album_name):
        if album_name == "Unknown Album":
            return None
        if album_name[:3] == "New":
            album_name = album_name[3:]
        if album_name[:2] == "RE":
            album_name = album_name[2:]
        #for each word, make lowercase except for the first letter
        album_name = album_name.title()
        #convert album_name and artist_name to have %20 to replace every whitespace
        #cleaned_album_name = album_name.replace(" ", "%20")
        return album_name


    def clean_artist_name(self, artist_name):
        if artist_name == "Unknown Artist":
            return None
        #for each word, make lowercase except for the first letter
        artist_name = artist_name.title()
        #convert album_name and artist_name to have %20 to replace every whitespace
        cleaned_artist_name = artist_name.replace(" ", "%20")
        return cleaned_artist_name

    
    def clean_song_name(self, song_name):
        if song_name == "Unknown Song":
            return None
        song_name = re.sub(r"\s-\sRemastered\s\d{4}", "", song_name)

        #for each word, make lowercase except for the first letter
        song_name = song_name.title()
        #convert album_name and artist_name to have %20 to replace every whitespace
        cleaned_song_name = song_name.replace(" ", "%20")
        return cleaned_song_name
    

    def clean_album(album):
        pass


    def clean_song(song):
        pass

    #----------------------------------------------MAIN FUNCTION----------------------------------------------#


    def convert_all_albums_to_songs_for_year(self, year):
        startTimer = time.time()
        # Get last accessed filename.
        filenames = self.get_filenames(year)
        # Get access token for Spotify.
        self.get_access_token()
        # For each week of data.
        for filename in tqdm(filenames, desc="Processing files"):
            file = self.read_from_csv(filename)
            if file != 0:   
                file.pop(0)
                # Month.
                month = filename.split("_")[4].split(".")[0]
                print(month)
                print(filename)
                # For each album in the week.
                for album_data in file:
                    time.sleep(random.uniform(0.3,0.6))
                    #check access token is still valid
                    self.check_token_validity()
                    album = album_data[3]
                    album = self.clean_album_name(album)
                    artist = album_data[2]
                    #print(F"----------------------------------ALBUM: {album}----------------------------------")
                    album_code = self.get_album_code_from_album_spotify(album, artist)
                    if album_code:
                        songs = self.get_tracks_from_album_spotify(album_code, artist)
                        # For each song in the album.
                        if songs:
                            for song in songs['songs']:
                                #print(f"----------------------------------SONG: {song}----------------------------------")
                                url = self.get_genius_url(song, artist)
                                if url:
                                    lyrics = self.scrape_from_genius(url)
                                    # Save to data_songs/year/month folder.
                                    self.write_to_json(year, month, song, lyrics)
                                    print(f"Songs for album {album} saved successfully.")
                                else:
                                    print(f"Error: No lyrics found for song {song}.")
                        else:
                            print(f"Error: No songs found for album {album}.")
                    else:
                        print(f"Error: No album code found for album {album}.")
                else:
                    print(f"Error: File {filename} not found.")
        print(f"Time taken: {time.time() - startTimer} seconds.")







        #save to data_songs/year/month folder


    def main(self):
        filenames = self.get_filenames(2020)
        print(filenames)
        file = self.read_from_csv(filenames[0])
        print("----------------------------------")
        artist = file[3][2]
        album = file[3][3]
        print(album)

        self.get_access_token()
        print(f"auth_token = {self.auth_token}")

        print("----------------------------------")
        print(album)
        album_code = self.get_album_code_from_album_spotify(album, artist)

        print(f"album_code = {album_code}")
        songs = self.get_tracks_from_album_spotify(album_code, artist)

        print(songs)

        song = songs['songs'][0]
        print(song)

        month = "05"

        url = self.get_genius_url(song, artist)
        print(url)
        lyrics = self.scrape_from_genius(url)
        print(lyrics)
        self.write_to_json(2020, month, song, lyrics)


AtoS = AlbumsToSongs([])
#AtoS.main()




years = [year for year in range(2001, 2011)]  # Generate years from 1971 to 1990

for year in years:
    try:
        AtoS.convert_all_albums_to_songs_for_year(year)
    except Exception as e:
        with open("error_log.txt", "a") as file:
            file.write(f"Failed on year {year}: {e}\n")


