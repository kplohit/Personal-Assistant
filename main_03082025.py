import speech_recognition as sr
import pyttsx3
import json
import os
import logging
import objectDetection.object_detection as obj_detect
import genericQuery.generic_queries as generic_queries
import IOT.led as iot

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
