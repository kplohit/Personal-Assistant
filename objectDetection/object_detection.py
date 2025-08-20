import cv2
from ultralytics import YOLO
import pyttsx3
import speech_recognition as sr

# Initialize the YOLO model (make sure the model file is available)
model = YOLO("yolov8n.pt")  # Adjust path to your model

# Initialize text-to-speech engine
engine = pyttsx3.init()


def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()


# Function to list available cameras
def list_cameras():
    cameras = []
    for i in range(5):  # Checking for the first 5 possible camera indices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            cameras.append(i)
        cap.release()
    return cameras


# Function to listen for a command
'''
def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for command...")
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"Command received: {command}")
        return command
    except sr.UnknownValueError:
        print("Sorry, I didn't catch that.")
        return None
    except sr.RequestError:
        print("Speech service is down.")
        return None
'''
# Function to listen for a command
def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for command...")
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"Command received: {command}")
        if "go back to main menu" in command:
            return "back_to_main"
        return command
    except sr.UnknownValueError:
        print("Sorry, I didn't catch that.")
        return None
    except sr.RequestError:
        print("Speech service is down.")
        return None

# Function to detect objects in the frame
def detect_objects_in_frame(frame):
    results = model(frame)  # Run YOLO detection on the frame
    labels = results[0].names  # Access the 'names' attribute from the first element in the results list
    objects = results[0].boxes.xywh.cpu().numpy()  # Object positions (x_center, y_center, width, height)
    class_ids = results[0].boxes.cls.cpu().numpy()  # Class IDs for each detected object

    detected_labels = []
    for i, obj in enumerate(objects):
        x_center, y_center, width, height = obj
        x1, y1 = int(x_center - width / 2), int(y_center - height / 2)
        x2, y2 = int(x_center + width / 2), int(y_center + height / 2)

        class_id = int(class_ids[i])  # Get the class ID for the current object
        label = labels[class_id]  # Get the class name from labels
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Draw bounding box
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)  # Add label text
        detected_labels.append(label)  # Append the label to detected labels

    return frame, detected_labels


# Function to start object detection
'''
def start_detection():
    speak("Starting object detection. Please wait.")
    cameras = list_cameras()
    if len(cameras) == 0:
        speak("No camera found.")
        return

    camera_index = cameras[0]  # Use the first available camera
    cap = cv2.VideoCapture(camera_index)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        command = listen_for_command()  # Listen for commands like 'detect objects'
        if command and ("detect objects" in command or "recognize objects" in command):
            frame, detected_objects = detect_objects_in_frame(frame)
            objects_text = ', '.join(detected_objects)
            speak(f"I see: {objects_text}")

        # Display the camera feed with detected objects
        cv2.imshow("Camera Feed", frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
'''

# Function to start object detection
def start_detection():
    speak("Starting object detection. Please wait.")
    cameras = list_cameras()
    if len(cameras) == 0:
        speak("No camera found.")
        return

    camera_index = cameras[0]  # Use the first available camera
    cap = cv2.VideoCapture(camera_index)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        command = listen_for_command()  # Listen for voice command

        # ✅ Check for "go back to main menu"
        if command == "back_to_main":
            speak("Returning to main menu.")
            break

        if command and ("detect objects" in command or "recognize objects" in command):
            frame, detected_objects = detect_objects_in_frame(frame)
            objects_text = ', '.join(detected_objects)
            speak(f"I see: {objects_text}")

        # Display the camera feed with detected objects
        cv2.imshow("Camera Feed", frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
