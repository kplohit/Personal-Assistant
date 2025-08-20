import speech_recognition as sr
import pyttsx3
import json
import os
import logging
import objectDetection.object_detection as obj_detect
import genericQuery.generic_queries as generic_queries
import computerOperations.computer_operations as computer_ops
import IOT.led as iot
import webbrowser

MEMORY_FILE = "learned.json"

# Configure logging
# logging.basicConfig(level=logging.DEBUG)

# Load or initialize memory
memory = {"conversations": []}
if os.path.exists(MEMORY_FILE):
    try:
        with open(MEMORY_FILE, "r") as file:
            data = file.read().strip()
            if data:
                memory = json.loads(data)
    except (json.JSONDecodeError, IOError) as e:
        logging.warning(f"Couldn't load memory. Reason: {e}")

# Text-to-Speech initialization
engine = pyttsx3.init()

def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

# Speech-to-Text with improved error handling
def listen():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
    except Exception as e:
        speak(f"Error with microphone: {e}")
        return ""

    try:
        query = recognizer.recognize_google(audio)
        print("You:", query)
        return query.lower()
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
        return ""
    except sr.RequestError:
        speak("Speech service is down.")
        return ""

# Function to start object detection
def start_object_detection():
    try:
        logging.debug("Starting object detection...")
        speak("Opening object detection...")
        obj_detect.start_detection()
        speak("Object detection closed. What else can I do?")
    except Exception as e:
        logging.error(f"Error during object detection: {e}")
        speak("There was an issue with object detection. Please try again.")


def handle_youtube_command(command):
    """Handles all YouTube-related commands"""
    command = command.lower()

    # If just "open youtube" without search terms
    if command == "open youtube":
        webbrowser.open("https://www.youtube.com")
        speak("Opening YouTube")
        return

    # Extract search query
    query = extract_search_query(command)

    # If no query found but command contains "youtube"
    if not query and "youtube" in command:
        speak("What would you like me to search for on YouTube?")
        query = listen()
        if not query:
            webbrowser.open("https://www.youtube.com")
            speak("Opening YouTube")
            return

    # If we have a query, handle it
    if query:
        # Direct play if command includes play
        if any(keyword in command for keyword in ["play", "song", "music", "video"]):
            if computer_ops.play_youtube_video(query):
                speak(f"Playing {query}")
            else:
                speak("I couldn't play that video")
            return

        # Otherwise show search results with options
        results = computer_ops.search_youtube_with_options(query)
        if results:
            speak(f"I found {len(results)} results for {query}")
            speak("Here are the top options:")

            for i, video in enumerate(results[:3], 1):
                speak(f"Option {i}: {video['title']}")

            speak("Which one would you like to play? Say 'first', 'second', or 'third'")

            selection = listen()
            if selection:
                if "first" in selection or "one" in selection or "1" in selection:
                    computer_ops.play_youtube_video(query, 0)
                elif "second" in selection or "two" in selection or "2" in selection:
                    computer_ops.play_youtube_video(query, 1)
                elif "third" in selection or "three" in selection or "3" in selection:
                    computer_ops.play_youtube_video(query, 2)
                else:
                    webbrowser.open(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")
                    speak("Opening search results")
        else:
            speak("I couldn't find any results for that search")
    else:
        webbrowser.open("https://www.youtube.com")
        speak("Opening YouTube")


def extract_search_query(command):
    """Extracts search query from command"""
    command = command.lower()
    for trigger in ["search for", "search", "find", "play", "youtube"]:
        if trigger in command:
            query = command.split(trigger)[-1].strip()
            query = query.replace(" on youtube", "").replace(" in youtube", "")
            return query
    return command


# Save memory to disk
def save_memory():
    logging.debug("Saving memory...")
    with open(MEMORY_FILE, "w") as file:
        json.dump(memory, file, indent=4)
    logging.debug("Memory saved successfully.")

# Main assistant loop
def run_assistant():
    speak("Hello! I'm your assistant. What can I do for you?")
    while True:
        command = listen()
        if command:
            logging.debug(f"User command: {command}")
            memory["conversations"].append({"user": command})

            # Handle generic queries (time, weather, etc.)
            response = generic_queries.handle_generic_query(command)
            if response:
                speak(response)
                memory["conversations"].append({"assistant": response})
                continue

            # LED control
            if "led on" in command:
                iot.led_on()
                speak("Turning LED on.")
                continue
            elif "led off" in command:
                iot.led_off()
                speak("Turning LED off.")
                continue

            # Object detection
            if "object" in command or "detect" in command:
                start_object_detection()
                continue

            # Computer operations
            if "lock computer" in command or "i'm going away" in command:
                if computer_ops.lock_computer():
                    speak("Computer locked. See you later!")
                else:
                    speak("I couldn't lock the computer. Please try manually.")
                continue

            elif "i'm back" in command or "unlock computer" in command :
                # speak("Please say your password to unlock.")
                speak("For security reasons, I can't automatically unlock your computer.")
                speak("Please unlock it manually. I'm ready when you are!")
                password = listen()
                if password:
                    if computer_ops.unlock_computer(password):
                        speak("Welcome back! Computer unlocked.")
                    else:
                        speak("Unlock attempt completed.")
                continue


            #elif "open youtube" in command:
            elif any(keyword in command.lower() for keyword in
                         ["youtube", "search", "find", "play song", "play music", "play video"]):
                handle_youtube_command(command)
                #if "search" in command:
                #    query = command.split("search")[-1].strip()
                #    computer_ops.open_youtube(query)
                #    speak(f"Searching YouTube for {query}")
                #else:
                #    computer_ops.open_youtube()
                #    speak("Opening YouTube")
                continue


            elif "play movie" in command or "play music" in command:
                media_type = "movie" if "movie" in command else "music"
                speak(f"Which {media_type} would you like to play?")
                media_name = listen()
                if media_name:
                    # In a real implementation, you'd map this to actual file paths
                    speak(f"Playing {media_name} {media_type}")
                    # computer_ops.play_media(path_to_media) - implement this with your media library
                continue

            elif "open file" in command:
                speak("Which file would you like to open?")
                file_name = listen()
                if file_name:
                    # In a real implementation, you'd map this to actual file paths
                    speak(f"Opening {file_name}")
                    # computer_ops.open_file(path_to_file) - implement this with your file system
                continue

            # Exit command
            if "exit" in command or "quit" in command:
                speak("Saving memory. Goodbye!")
                save_memory()
                break

            # Fallback response
            response = "I'm still learning. I noted that."
            speak(response)
            memory["conversations"].append({"assistant": response})

# Graceful exit
def cleanup():
    speak("Saving memory. Goodbye!")
    save_memory()
    engine.stop()


if __name__ == "__main__":
    try:
        run_assistant()
    except KeyboardInterrupt:
        cleanup()
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        cleanup()
