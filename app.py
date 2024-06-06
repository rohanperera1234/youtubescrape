import streamlit as st
import pandas as pd
from yt_dlp import YoutubeDL
from datetime import datetime, timedelta
import pytz
import time

# Function to format the date
def format_date(date_str):
    return pd.to_datetime(date_str, format='%Y%m%d').strftime('%Y-%m-%d')

# Function to format the duration
def format_duration(duration):
    minutes, seconds = divmod(duration, 60)
    hours, minutes = divmod(minutes, 60)
    return f'{hours:02}:{minutes:02}:{seconds:02}'

# Function to scrape YouTube videos
def scrape_youtube_videos():
    ydl_opts = {
        'extract_flat': 'in_playlist',
        'force_generic_extractor': True,
        'playlistend': 10  
    }

    with YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info('https://www.youtube.com/@TVDeranaOfficial/videos', download=False)
        
        # Extract video details
        videos = []
        if 'entries' in result:
            for entry in result['entries']:
                video_info = ydl.extract_info(f'https://www.youtube.com/watch?v={entry["id"]}', download=False)
                duration = video_info.get('duration', 'N/A')
                formatted_duration = format_duration(duration) if duration != 'N/A' else 'N/A'
                videos.append({
                    'Title': entry['title'],
                    'URL': f'https://www.youtube.com/watch?v={entry["id"]}',
                    'Upload Date': format_date(video_info.get('upload_date', 'N/A')),
                    'Views': video_info.get('view_count', 'N/A'),
                    'Duration': formatted_duration
                })

        # Create DataFrame
        df = pd.DataFrame(videos)
        return df

# Function to calculate the time remaining until the next 1:12 PM
def time_until_next_run():
    sri_lanka_tz = pytz.timezone('Asia/Colombo')
    current_time = datetime.now(sri_lanka_tz)
    next_run_time = current_time.replace(hour=14, minute=10, second=0, microsecond=0)
    if current_time >= next_run_time:
        next_run_time += timedelta(days=1)
    time_remaining = next_run_time - current_time
    return time_remaining, next_run_time

# Streamlit app
def main():
    st.title("YouTube Video Scraper")

    # Get current time in Sri Lanka
    sri_lanka_tz = pytz.timezone('Asia/Colombo')
    current_time = datetime.now(sri_lanka_tz)
    st.write(f"Current time in Sri Lanka: {current_time.strftime('%Y-%m-%d %H:%M')}")

    time_remaining, next_run_time = time_until_next_run()
    hours, remainder = divmod(time_remaining.total_seconds(), 3600)
    minutes, _ = divmod(remainder, 60)
    st.write(f"Next scheduled run time: {next_run_time.strftime('%Y-%m-%d %H:%M')}")
    st.write(f"Time remaining until next run: {int(hours)} hours and {int(minutes)} minutes")

    # Check if it's 1:12 PM
    if current_time.hour == 13 and current_time.minute == 12:
        st.write("Running YouTube scraper...")
        df = scrape_youtube_videos()
        st.write(df)
    else:
        st.write("YouTube scraper will run at 1:12 PM Sri Lankan time every day.")

    # Refresh the app every minute
    time.sleep(60)
    st.experimental_rerun()

if __name__ == "__main__":
    main()
