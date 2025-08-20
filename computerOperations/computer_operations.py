import os
import subprocess
import time
import ctypes
import platform
import logging
import webbrowser
from youtubesearchpython import VideosSearch
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lock_computer():
    """Locks the computer based on the operating system."""
    try:
        system = platform.system()
        if system == "Windows":
            ctypes.windll.user32.LockWorkStation()
        elif system == "Darwin":  # macOS
            subprocess.run(['pmset', 'displaysleepnow'])
        elif system == "Linux":
            try:
                subprocess.run(['gnome-screensaver-command', '--lock'])
            except FileNotFoundError:
                subprocess.run(['xdg-screensaver', 'lock'])
        logger.info("Computer locked successfully")
        return True
    except Exception as e:
        logger.error(f"Error locking computer: {e}")
        return False

def unlock_computer(password: str):
    """Simulates unlocking by waiting and showing a message."""
    # Note: Actual unlocking requires system-level integration that's often not possible
    # This is a simulation that just shows a message
    print(f"Simulating unlock with password: {password}")
    time.sleep(2)  # Simulate unlock delay
    logger.info("Computer unlocked (simulated)")
    return True

def open_file(file_path: str):
    """Opens a file with the default application."""
    try:
        if os.path.exists(file_path):
            os.startfile(file_path) if platform.system() == "Windows" else subprocess.run(['open', file_path])
            logger.info(f"Opened file: {file_path}")
            return True
        else:
            logger.warning(f"File not found: {file_path}")
            return False
    except Exception as e:
        logger.error(f"Error opening file: {e}")
        return False

def play_media(media_path: str):
    """Plays media file with default player."""
    return open_file(media_path)


def play_youtube_video(search_query, video_index=0):
    """Search YouTube and play the specified video"""
    try:
        videos_search = VideosSearch(search_query, limit=5)
        results = videos_search.result()['result']

        if not results:
            return False

        if video_index >= len(results):
            video_index = 0

        video_url = results[video_index]['link']
        webbrowser.open(video_url)
        logging.info(f"Playing YouTube video: {video_url}")
        return True
    except Exception as e:
        logging.error(f"Error playing YouTube video: {e}")
        return False

def search_youtube_with_options(search_query):
    """Search YouTube and return results with options"""
    try:
        videos_search = VideosSearch(search_query, limit=5)
        results = videos_search.result()['result']

        if not results:
            return None

        return [{
            'title': video['title'],
            'url': video['link'],
            'duration': video['duration']
        } for video in results]
    except Exception as e:
        logging.error(f"YouTube search error: {e}")
        return None


def open_application(app_name: str):
    """Opens an application by name."""
    try:
        if platform.system() == "Windows":
            os.system(f'start "" "{app_name}"')
        elif platform.system() == "Darwin":
            subprocess.run(['open', '-a', app_name])
        elif platform.system() == "Linux":
            subprocess.run([app_name.lower()])
        logger.info(f"Opened application: {app_name}")
        return True
    except Exception as e:
        logger.error(f"Error opening application: {e}")
        return False