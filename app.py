from flask import Flask,render_template,redirect,request
import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)


song_data = pd.read_csv("static/songs.csv")
music_data = pd.read_csv("static/Music_info.csv")
songs =song_data["name"].unique()
vectorize = pickle.load(open('static/vectors.pkl', 'rb'))
process = pickle.load(open('static/process.pkl', 'rb'))

def predict(song):
        
    song_input = song_data[song_data["name"] == song]
    if song_input.empty:
        return [],[]
    song_index = song_data[song_data["name"] == song].index
    
    transformed_input = process.transform(song_input)
    similarity = cosine_similarity(vectorize, transformed_input)
    songs = sorted(list(enumerate(similarity.tolist())),reverse=True,key=lambda x:x[1])[1:7]
    songs_name= []
    track_id=[]
    posters=[]
    artists=[]
    previews=[]
    for i in songs:
        songs_name.append(song_data.iloc[i[0]]["name"])
        track_id.append(song_data.iloc[i[0]]["spotify_id"])
        previews.append(music_data.iloc[i[0]]["spotify_preview_url"])
        

    posters, artists=get_track_info(track_id)
    return songs_name,track_id,posters,artists,previews


def init_spotify():
    """Initialize Spotify client with credentials from environment variables"""
    # Use environment variables for security
    client_id = os.getenv('SPOTIFY_CLIENT_ID', 'd2497d19fefb42f6b6792ee2f3471172')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET', '3000a8d3cf1d49769e0d8455027c5343')
    
    auth_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    )
    return spotipy.Spotify(auth_manager=auth_manager)


sp = init_spotify()
def get_track_info(track_ids):
    poster=[]
    artist=[]
    for track_id in track_ids:
        """Fetch both poster and artist in a single API call"""
        try:
            track = sp.track(track_id)
            poster.append(track['album']['images'][0]['url'] if track['album']['images'] else None)
            artist.append(track['artists'][0]['name'] if track['artists'] else "Unknown")
             
        except Exception as e:
            print(f"Could not fetch track info: {e}")
            return None, "Unknown"
    print(poster,artist)
    return poster,artist



@app.route('/')
def Starting_page():
    return render_template('email.html')

@app.route('/home', methods=['GET','POST'])
def home_page():
    Recommend_songs = []      # default value
    track_ids = []  
    poster = []
    author=[]
    origin_song = ""
    preview=[]
    if request.method=="POST":
        origin_song= request.form.get('song-input')
        Recommend_songs,track_ids,poster,author,preview =predict(origin_song)
    return render_template('index.html',Data=songs,songs=Recommend_songs,id =track_ids,poster=poster,author=author,original_song=origin_song,preview=preview)


@app.route('/linkedin')
def linkedin():
    return redirect('https://www.linkedin.com/in/dixit-prajapati-617996327')



@app.route('/github')
def Github():
    return redirect('https://github.com/Dixit-Prajapati-DS')

if __name__=="__main__":
    app.run(debug=True)