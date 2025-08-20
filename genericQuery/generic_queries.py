import datetime
import pytz
from geopy.geocoders import Nominatim
import requests
from timezonefinder import TimezoneFinder
import re

# --- TIME QUERY ---

def get_time_in_location(location):
    try:
        geolocator = Nominatim(user_agent="assistant")
        location_data = geolocator.geocode(location)
        if not location_data:
            return f"Sorry, I couldn't find the location: {location}."

        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lng=location_data.longitude, lat=location_data.latitude)
        if not timezone_str:
            return f"Couldn't determine the timezone for {location}."

        timezone = pytz.timezone(timezone_str)
        local_time = datetime.datetime.now(timezone)
        return f"The current time in {location} is {local_time.strftime('%I:%M %p')}."
    except Exception as e:
        return f"Error getting time for {location}: {e}"

# --- WEATHER QUERY ---

def get_weather(location, when="today"):
    API_KEY = "05f07b646c8b07ef6286e25067949dfa"  # Replace with your actual OpenWeatherMap API key
    try:
        geolocator = Nominatim(user_agent="assistant")
        location_data = geolocator.geocode(location)
        if not location_data:
            return f"Couldn't find the location {location}."

        lat, lon = location_data.latitude, location_data.longitude
        url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        response = requests.get(url).json()

        # Check for errors in response
        if response.get("cod") != "200":
            return f"Weather API error: {response.get('message', 'Unknown error')}"

        # Basic current weather info
        if when.lower() in ["today", "now"]:
            weather = response["list"][0]
            description = weather["weather"][0]["description"]
            temp = weather["main"]["temp"]
            return f"The weather in {location} today is {description} with a temperature of {temp}°C."

        return f"Weather forecast for '{when}' in {location} is not implemented yet."

    except Exception as e:
        return f"Error getting weather for {location}: {e}"

# --- LOCATION EXTRACTION ---
"""
def extract_location_from_command(command):
    # Use regex to extract location (after 'in', 'for', 'at', or at end of sentence)
    match = re.search(r"(?:in|at|for|of)?\s*([\w\s]+?)\s*(weather|time|report)?$", command.strip(), re.IGNORECASE)
    if match:
        possible_location = match.group(1).strip()
        if possible_location and possible_location.lower() not in ["weather", "time", "report"]:
            return possible_location
    return None
"""
def extract_location_from_command(command):
    command = command.lower()
    """
    Extracts the most likely location name from the spoken command by removing
    known keywords that aren't part of location names.
    """

    # Common non-location keywords to remove
    cleanup_words = {
        "what's", "what", "is", "the", "weather", "report", "time",
        "in", "at", "for", "on", "tell", "me", "show", "give", "of"
    }

    # Split the command and filter out unwanted words
    words = command.split()
    location_words = [word for word in words if word not in cleanup_words]

    # Return the remaining words as the location
    if location_words:
        return " ".join(location_words).strip()

    return None

# --- MAIN HANDLER ---

def handle_generic_query(command):
    command = command.lower()

    if "time" in command:
        location = extract_location_from_command(command) or "India"
        return get_time_in_location(location)

    elif "weather" in command or "weather report" in command:
        location = extract_location_from_command(command) or "India"
        if "tomorrow" in command:
            when = "tomorrow"
        elif "week" in command:
            when = "week"
        elif "month" in command:
            when = "month"
        else:
            when = "today"
        return get_weather(location, when)

    return None
