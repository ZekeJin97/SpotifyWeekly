import json
import boto3
import spotipy
import pylast
import os
import io
import pandas as pd
import logging
from spotipy.oauth2 import SpotifyOAuth

# 🔹 Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# 🔹 AWS S3 Setup
S3_BUCKET = os.getenv("S3_BUCKET")
if not S3_BUCKET:
    logger.error("S3_BUCKET environment variable is missing")
    raise ValueError("S3_BUCKET environment variable is missing")

s3 = boto3.client("s3")

# 🔹 Spotify API Credentials
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
SPOTIFY_REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")  # NEW: Refresh Token

if not all([SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, SPOTIFY_REFRESH_TOKEN]):
    logger.error("Missing one or more Spotify API credentials")
    raise ValueError("Missing Spotify API credentials")

# 🔹 Last.fm API Credentials
LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
LASTFM_API_SECRET = os.getenv("LASTFM_API_SECRET")
LASTFM_USERNAME = os.getenv("LASTFM_USERNAME")
LASTFM_PASSWORD_HASH = os.getenv("LASTFM_PASSWORD_HASH")  # Should already be hashed

if not all([LASTFM_API_KEY, LASTFM_API_SECRET, LASTFM_USERNAME, LASTFM_PASSWORD_HASH]):
    logger.error("Missing one or more Last.fm API credentials")
    raise ValueError("Missing Last.fm API credentials")

# 🔹 Authenticate with APIs
def get_spotify_client():
    """ Returns a Spotipy client with refreshed authentication. """
    auth_manager = SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope="user-top-read"
    )

    # Manually set the refresh token
    auth_manager.refresh_token = SPOTIFY_REFRESH_TOKEN

    # Get a new access token (this will auto-refresh)
    token_info = auth_manager.refresh_access_token(SPOTIFY_REFRESH_TOKEN)

    return spotipy.Spotify(auth=token_info['access_token'])

try:
    sp = get_spotify_client()
    logger.info("Spotify authentication successful")
except Exception as e:
    logger.error(f"Spotify authentication failed: {e}")
    raise

try:
    network = pylast.LastFMNetwork(api_key=LASTFM_API_KEY, api_secret=LASTFM_API_SECRET,
                                   username=LASTFM_USERNAME, password_hash=LASTFM_PASSWORD_HASH)
    logger.info("Last.fm authentication successful")
except Exception as e:
    logger.error(f"Last.fm authentication failed: {e}")
    raise

# 🔹 Lambda Function
def lambda_handler(event, context):
    """ Fetches top Spotify tracks (personal), gets Last.fm play counts, and saves data to S3. """
    try:
        # Fetch Top Tracks from Spotify (User's Personal Data)
        logger.info("Fetching top tracks from Spotify...")
        top_tracks = sp.current_user_top_tracks(time_range='short_term', limit=10)

        track_data = []
        for track in top_tracks.get('items', []):
            song_name = track['name']
            artist_name = track['artists'][0]['name']

            # Fetch play count from Last.fm
            try:
                lastfm_track = network.get_track(artist_name, song_name)
                play_count = lastfm_track.get_userplaycount() or 0  # Handle None values
            except Exception as e:
                logger.warning(f"Failed to fetch play count for {song_name} by {artist_name}: {e}")
                play_count = None  # Mark as None to avoid blocking execution

            track_data.append({"Song": song_name, "Artist": artist_name, "Play Count": play_count})

        # Convert to DataFrame
        df = pd.DataFrame(track_data)
        df["Week"] = pd.Timestamp.today().strftime('%Y-%W')

        # Convert DataFrame to CSV in memory
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        # Upload CSV to S3 directly
        csv_filename = f"weekly_play_counts_{pd.Timestamp.today().strftime('%Y-%W')}.csv"
        s3.put_object(Bucket=S3_BUCKET, Key=csv_filename, Body=csv_buffer.getvalue())

        logger.info(f"Successfully uploaded {csv_filename} to S3")

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Weekly Spotify Data Uploaded to S3!"})
        }

    except Exception as e:
        logger.error(f"Error in lambda_handler: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal Server Error", "error": str(e)})
        }
