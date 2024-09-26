import alpaca_trade_api as tradeapi
import spotipy
import random
import time
from spotipy.oauth2 import SpotifyOAuth


# Spotify Credentials
SPOTIPY_CLIENT_ID = 'c8eac05adc7e4592bf2349d60315fa00'
SPOTIPY_CLIENT_SECRET = '93be1a9c4cff4b95bfb86dc56442e367'
#ACCESS_TOKEN = 'BQBQ0AO5fjKVqc3s3czDDDdndNIaYiY7Pl40PDi5lVI1reED7C5xDHL1GyzszDug8YnvFraffBrIoz4Ib5ry3a-V-09zO_qtRuZzlE59_1aaW89-NfM'
REDIRECT_URI ='http://localhost:8888/callback/'


# Alpaca Credentials
ALPACA_API_KEY = 'PKUMP89HC1SD90KPIR0C'
ALPACA_API_SECRET = '6GRuTTaHVM9fTe07iUqH16zMgeUaKemPUCUGWSno'
ALPACA_BASE_URL = 'https://paper-api.alpaca.markets'

SCOPE = 'playlist-modify-private playlist-modify-public user-read-private user-read-email'

def get_spotify_token():
    # Use Spotipy's built-in OAuth handler to manage tokens
    sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE)
    
    token_info = sp_oauth.get_access_token(as_dict=True)  
    if not token_info or 'access_token' not in token_info:
        print("Error: Unable to get access token")
        return None
    
    return token_info  

alpaca = tradeapi.REST(ALPACA_API_KEY, ALPACA_API_SECRET, ALPACA_BASE_URL, api_version='v2')

# Define genres
genres = ['Pop', 'Rock', 'Hip-hop', 'Jazz', 'Classical', 'Electronic', 'Country', 'Rap','Latin','Indie','R&B','K-pop','Metal','Punk','Alternative', 'Fall','Chill']

def get_random_track(sp):
    """Fetch a random track from a random genre."""
    random_genre = random.choice(genres)
    results = sp.search(q=f'genre:{random_genre}', type='track', limit=10)
    if results['tracks']['items']:
        track = random.choice(results['tracks']['items'])
        print(f"Selected Track: {track['name']} by {track['artists'][0]['name']} in genre {random_genre}")
        return track
    return None

def trade_stock(symbol, qty, action):
    """Execute buy or sell orders based on the action."""
    try:
        # Check current position
        positions = alpaca.list_positions()
        current_position = next((pos for pos in positions if pos.symbol == symbol), None)

        if action == 'buy' and current_position is None:
            order = alpaca.submit_order(
                symbol=symbol,
                qty=qty,
                side='buy',
                type='market',
                time_in_force='gtc'
            )
            print(f"Buy Order Submitted: {order}")

        elif action == 'sell' and current_position is not None:
            order = alpaca.submit_order(
                symbol=symbol,
                qty=qty,
                side='sell',
                type='market',
                time_in_force='gtc'
            )
            print(f"Sell Order Submitted: {order}")

    except Exception as e:
        print(f"Error executing order: {e}")

def generate_playlist_based_on_stocks(sp, stocks):
    mood = (
    "happy" if any(stock['price_change'] > 0 for stock in stocks) else
    "sad" if all(stock['price_change'] < 0 for stock in stocks) else
    "energetic" if any(stock['price_change'] > 1 for stock in stocks) else
    "relaxed" if all(stock['price_change'] == 0 for stock in stocks) else
    "nostalgic"
)

    genre_mapping =  {
    "happy": ["Pop", "Dance", "Rock", "Electronic", "K-pop"],
    "sad": ["Chill", "Acoustic", "Classical", "Indie", "R&B"],
    "energetic": ["Hip-hop", "Punk", "Metal", "Alternative", "Rap"],
    "relaxed": ["Jazz", "Country", "Chill", "Fall", "Acoustic"],
    "nostalgic": ["Indie", "Alternative", "Classic Rock", "R&B", "Jazz"],
    "motivated": ["Electronic", "Rock", "Pop", "Hip-hop", "Metal"]
}
    genre = random.choice(genre_mapping[mood])
    results = sp.search(q=f'genre:{genre}', type='track', limit=10)
    
    if results['tracks']['items']:
        track_uris = [track['uri'] for track in results['tracks']['items']]
        playlist = sp.user_playlist_create(user=sp.current_user()['id'], name=f'My Playlist based on {genre}', public=True)
        sp.user_playlist_add_tracks(user=sp.current_user()['id'], playlist_id=playlist['id'], tracks=track_uris)
        print(f"Playlist created with {genre} tracks based on stock performance.")
    else:
        print(f"No tracks found for genre '{genre}'.")


def main():
    """Main function to run the trading logic."""
    token_info = get_spotify_token()
    if not token_info:
        return

    sp = spotipy.Spotify(auth=token_info['access_token'])  # Now token_info is a dictionary

    stocks_data = [
        {'symbol': 'AAPL', 'price_change': 1.5},
        {'symbol': 'GOOGL', 'price_change': -0.5},
        {'symbol': 'TSLA', 'price_change': 2.0}
    ]  # Example stock data structure

    while True:
        track = get_random_track(sp)
        if track:
            if any(stock['price_change'] > 0 for stock in stocks_data):  # If any stock is up
                trade_stock('AAPL', 1, 'sell')  # Sell AAPL if price increased
            else:
                trade_stock('AAPL', 1, 'buy')  # Otherwise, buy AAPL

            # Generate a playlist based on the stock data
            generate_playlist_based_on_stocks(sp, stocks_data)

        time.sleep(120)  # Wait before the next iteration
if __name__ == "__main__":
    main()
