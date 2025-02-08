from fastapi import FastAPI
from bs4 import BeautifulSoup
import requests

app = FastAPI()

url = "https://raag.fm"

def scrape_album_songs(url: str):
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Parse the page content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Initialize a list to store album songs data
    album_songs_data = []
    
    # Find the div with the class "green" that contains the album name
    album_name_div = soup.find("div", class_="bg-success text-white pt-1 pl-2 pb-1 pr-1 mt-2 green")
    
    if album_name_div:
        # Get the album name
        album_name = album_name_div.find("font", color="red").text.strip()
        
        # Find the parent div containing the list of songs
        song_list_divs = album_name_div.find_all_next("ul", style="list-style:none;list-style-position: inside;padding-left: 0;color: #cbcbcb;")
        
        for song_list_div in song_list_divs:
            song_data = {}
            
            # Find all the li tags (songs) within the list
            song_list = song_list_div.find_all("li", class_="border-bottom p-2")
            
            for song in song_list:
                song_link = song.find("a", class_="touch")
                
                if song_link:
                    song_title = song_link.get_text()
                    song_url = song_link["href"]
                    song_name = song_link.get_text().split("(")[0].strip()  # Extract only song name
                    
                    # Add song data to the list
                    song_data = {
                        "song_name": song_name,
                        "song_title": song_title,
                        "song_url": song_url,
                     
                    }
                    album_songs_data.append(song_data)
        list=[]
        img_tag = soup.find("div", class_="col-12 col-sm-12 col-md-5").find("img")
        img_src = img_tag["src"] if img_tag else None
   
    list.append({"album":album_name,"banner":img_src,"songs":album_songs_data})
                    
    return list

def singles_track():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return [], []
    
    soup = BeautifulSoup(response.text, "html.parser")
    hindi_tracks = []
    punjabi_tracks = []

    track_sections = soup.find_all("div", class_=["orange", "blue", "violett", "yellow"])

    for section in track_sections:
        parent_div = section.find_parent("div", class_="col-12 col-sm-12 col-md-12")
        if not parent_div:
            continue

        category_name = section.text.strip()
        track_links = parent_div.find_all("figure", class_="top-song")

        for figure in track_links:
            track_anchor = figure.find("a", class_="touch")
            track_img = figure.find("img")

            if track_anchor and track_img:
                track_title = track_anchor["title"]
                track_url = track_anchor["href"]
                img_src = track_img["src"]

                track_data = {"title": track_title, "img": url+img_src, "url": track_url}

                if "Punjabi" in category_name:
                    punjabi_tracks.append(track_data)
                elif "Hindi" in category_name:
                    hindi_tracks.append(track_data)

    return punjabi_tracks, hindi_tracks

@app.get("/scrape/singles")
def get_singles():
    punjabi_songs, hindi_songs = singles_track()
    return {"Punjabi Songs": punjabi_songs, "Hindi Songs": hindi_songs}


def scrape_raag_fm():
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    songs_data = []

    track_sections = soup.find_all("div", class_=["orange", "blue", "violett", "yellow", "grey", "green"])

    for section in track_sections:
        list = []
        parent_div = section.find_parent("div", class_="col-12 col-sm-12 col-md-6 mb-2")
        if not parent_div:
            continue

        head = section.get_text().split("View All")[0].strip()
        song_containers = parent_div.find_all('div', class_='song-list-guri')

        for container in song_containers:
            link_tag = container.find('a', class_='touch')
            song_name = link_tag.get('title')
            artist_name = link_tag.find('span', style="display: block;color: #ff0202;").text.strip()
            album_link = link_tag.get('href')
            image_url = container.find('img')['src']

            list.append({
                'song_name': song_name,
                'artist_name': artist_name,
                'album_link': album_link,
                'image_url': url + image_url
            })

        if list:
            songs_data.append({head: list})

    return songs_data

@app.get("/scrape/raag_fm")
def get_raag_fm_songs():
    songs = scrape_raag_fm()
    return {"Songs": songs}


def scrape_audio_and_image(track_url: str):
    response = requests.get(track_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    audio_source = soup.find('audio', id='audioPlayer').find('source')['src']
    image_url = soup.find('img', class_='songcover')['src']

    return audio_source, image_url

@app.get("/scrape/audio_image")
def get_audio_image(track_url: str):
    audio_url, img_url = scrape_audio_and_image(track_url)
    return {"Audio URL": audio_url, "Image URL": img_url}

@app.get("/")
def main():
    return "hi"

@app.get("/scrape_album_songs")
def get_album_songs(url: str):
    album_songs = scrape_album_songs(url)
    return album_songs


