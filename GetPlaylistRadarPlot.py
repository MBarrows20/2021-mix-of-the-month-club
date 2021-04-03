import yaml
import requests
import pandas as pd
import plotly.express as px

# Get Playlist Item Ids
AUTH_URL = 'https://accounts.spotify.com/api/token'
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID") 
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET") 
BASE_URL = 'https://api.spotify.com/v1/'

with open(r'docs\_data\playlists.yml') as file: 
    PLAYLIST_IDS = yaml.load(file, Loader=yaml.FullLoader)

# Authentication 
auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
})
auth_response_data = auth_response.json()
access_token = auth_response_data['access_token']
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer {token}'.format(token=access_token)
}

# Get tracks in a playlist
playlistParams = {
    'market': 'US',
    'fields': 'items(track(id))'
}
for playlist in PLAYLIST_IDS:

    r = requests.get(BASE_URL + 'playlists/'+ playlist['playlistID'] + '/tracks', headers = headers, params=playlistParams).json()
    track_ids = [x['track']['id'] for x in r['items']]


    #Get Each Song's Attributes
    songParams = {
        'ids': ','.join(track_ids)
    }
    r = requests.get(BASE_URL + 'audio-features', headers = headers, params = songParams )
    d = r.json()
    df = pd.DataFrame([x for x in d['audio_features']])
    df = df.loc[:,['danceability','energy','acousticness','instrumentalness','valence']]

    #Calculate Average Attribute Values for Playlist
    df_mean = pd.DataFrame(df.mean())
    df_mean.index.name = 'Characteristic'
    df_mean.reset_index(inplace=True)
    df_mean = df_mean.rename(columns = {0:'Value'})

    #Save radar visual of playlist characteristics
    fig = px.line_polar(df_mean, r='Value',theta='Characteristic', line_close=True)
    fig.update_traces(fill='toself')
    fig.write_image("./docs/assets/radarCharts/"+playlist['month']+playlist['year']+'-radar.png')