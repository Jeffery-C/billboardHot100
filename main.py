import requests
import os
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# user_date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
user_date = "2005-08-12"


def year2range(year: str) -> str:
    year_int = int(year)
    return f"{year_int-1}-{year_int}"


web_url = f"https://www.billboard.com/charts/hot-100/{user_date}"
response = requests.get(url=web_url)
response.raise_for_status()
web_text = response.text

soup = BeautifulSoup(markup=web_text, features="html.parser")

h3_tags = soup.select("li.lrv-u-width-100p ul.lrv-a-unstyle-list li h3")
span_tags = soup.select("li.lrv-u-width-100p ul.lrv-a-unstyle-list li h3 + *")
titles = []
artists = []
for i in range(len(h3_tags)):
    titles.append(h3_tags[i].getText().strip())
    artists.append(span_tags[i].getText().strip())
print(len(titles))
my_id = os.environ.get("Client ID")
my_secret = os.environ.get("Client Secret")
my_redirect_url = os.environ.get("Redirect URIs")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=my_id,
                                               client_secret=my_secret,
                                               redirect_uri=my_redirect_url,
                                               scope="playlist-modify-private"))


song_uris = []
year = year2range(user_date.split("-")[0])


def search_match(artists, search_result):
    for item in search_result["tracks"]["items"]:
        for artist in artists.lower().split():
            if artist in item["album"]["artists"][0]["name"].lower().split():
                return item["uri"]


for i in range(len(titles)):
    search_result = sp.search(q=f"track:{titles[i]} year:{year}", type='track')
    try:
        spotify_uri = search_match(artists=artists[i], search_result=search_result)
        if spotify_uri:
            song_uris.append(spotify_uri)
        else:
            print(f"{titles[i]} ({artists[i]}) doesn't exist in Spotify. Skipped.")
    except IndexError:
        print(f"{titles[i]} ({artists[i]}) doesn't exist in Spotify. Skipped.")


user_id = sp.current_user()["id"]
user_playlist = sp.user_playlist_create(user="j63007", name=f"{user_date} Billboard 100", public=False)
user_playlist_id = user_playlist["id"]
sp.user_playlist_add_tracks(user=user_id, playlist_id=user_playlist_id, tracks=song_uris)
