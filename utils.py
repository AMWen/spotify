# Import packages
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yaml
import pandas as pd

# Load client secrets (dict with client_id and client_secret)
client_secrets = yaml.load(open('secrets/client.yml').read(), yaml.FullLoader)

# API authentication
client_credentials_manager = SpotifyClientCredentials(**client_secrets)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Function to analyze a list of playlists
def analyze_playlist(playlist_ids):
    if isinstance(playlist_ids, str):
        playlist_ids = [playlist_ids]
    
    for i, playlist_id in enumerate(playlist_ids):
        # Loop through every track in the playlist, extract features and append the features to the playlist df
        tracks = sp.playlist_tracks(playlist_id)['items']

        for j, track in enumerate(tracks):
            # Get track and artist info
            track = track['track']
            artist = track['album']['artists'][0]
            album = sp.album(track["album"]["external_urls"]["spotify"])

            # Artist URI and info
            artist_uri = artist["uri"]
            artist_info = sp.artist(artist_uri)

            # Initial feature dict
            playlist_features = {
                'playlist_num': i,
                'artist': artist['name'],
                'album': track['album']['name'],
                'release_date': album["release_date"],
                'name': track['name'],
                'id': track['id'],
                'explicit': track['explicit'],
                'popularity': track['popularity'],
                'artist_pop': artist_info['popularity'],
                'artist_genres': artist_info['genres']
            }

            try:
                # Audio info ("danceability", "energy", "key", "loudness", "mode", "speechiness", "instrumentalness", "liveness", "valence", "tempo", "duration_ms", "time_signature")
                audio_info = sp.audio_features(track['id'])[0]

                # Add audio info
                playlist_features.update(audio_info)
                
                # Concat the dfs
                track_df = pd.DataFrame([playlist_features])

                if (i == 0) and (j == 0):
                    playlist_df = track_df
                else:
                    playlist_df = pd.concat([playlist_df, track_df], ignore_index=True)

            except:
                continue

        # Dedupe
        playlist_df['artists_song'] = playlist_df.apply(lambda row: row['artist'] + row['name'], axis=1)
        playlist_df.drop_duplicates('artists_song', inplace=True)

    return playlist_df