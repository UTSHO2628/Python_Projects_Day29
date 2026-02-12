import tkinter as tk
import pyttsx3
import speech_recognition as sr
import mysql.connector
import cv2
from PIL import Image, ImageTk

# Initialize Text-to-Speech Engine
engine = pyttsx3.init()

# Tkinter Window setup.
root = tk.Tk()
root.title("Campus Voice Assistant")
root.geometry("700x600")
root.config(bg="#ececec")

# Background Image (Optional, you can remove if not needed)
bg_image = tk.PhotoImage(file="background_image.png")
background_label = tk.Label(root, image=bg_image)
background_label.place(relwidth=1, relheight=1)

# Frame for content
content_frame = tk.Frame(root, bg="white", bd=10, relief="solid", padx=20, pady=20)
content_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.7)

# Welcoming text
label_text = tk.Label(content_frame, text="Loading...", font=("Helvetica", 16, "bold"), fg="#333", bg="white")
label_text.pack(pady=10)

# Create a Text-to-Speech function
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to recognize speech input
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            label_text.config(text=f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            speak("Sorry, I didn't understand that.")
            label_text.config(text="Sorry, I didn't understand that.")
            return None
        except sr.WaitTimeoutError:
            speak("No input detected.")
            label_text.config(text="No input detected.")
            return None

# Fetch answer from the database
def fetch_answer(question):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="campus_bot"
        )
        cursor = connection.cursor()
        query = "SELECT answer FROM faq WHERE question LIKE %s"
        cursor.execute(query, (f"%{question}%",))
        result = cursor.fetchone()
        connection.close()
        return result[0] if result else "Sorry, I don't have an answer for that."
    except mysql.connector.Error as err:
        return f"Database error: {err}"

# Function to interact with voice commands
def process_voice_command():
    query = listen()
    if query:
        if "thanks" in query or "exit" in query:
            speak("Goodbye! See you soon!")
            label_text.config(text="Goodbye! See you soon!")
            root.quit()
        else:
            answer = fetch_answer(query)
            speak(answer)
            label_text.config(text=f"Answer: {answer}")
            play_video("robot_video.mp4")  # Play video when an answer is given

# Create a button to start the voice command process
def on_enter(e):
    button.config(bg="#45a049")

def on_leave(e):
    button.config(bg="#4CAF50")

button = tk.Button(content_frame, text="Ask Me", font=("Helvetica", 14, "bold"), bg="#4CAF50", fg="white", relief="raised", bd=5, command=process_voice_command)
button.pack(pady=20)
button.bind("<Enter>", on_enter)
button.bind("<Leave>", on_leave)

# Play video function
def play_video(video_path):
    # OpenCV to play video
    cap = cv2.VideoCapture(video_path)
    while(cap.isOpened()):
        ret, frame = cap.read()
        if not ret:
            break

        # Resize the video to fit the screen (adjust to fit the Tkinter window size)
        frame = cv2.resize(frame, (root.winfo_width(), root.winfo_height()))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert the frame into an image for tkinter
        frame_image = Image.fromarray(frame)
        frame_image = ImageTk.PhotoImage(frame_image)
        
        # Display the video frame on the Tkinter window
        label_video.config(image=frame_image)
        label_video.image = frame_image
        
        root.update()

    cap.release()

# Create a label to display the video frame
label_video = tk.Label(content_frame, bg="white")
label_video.pack(pady=10)

# Function to show robot face and greeting message after loading
def initial_greeting():
    speak("Hello! I am your campus assistant. Ask me anything!")
    label_text.config(text="Hello! I am your campus assistant. Ask me anything!")
    
    # Load robot face image and display it after greeting
    face_image = tk.PhotoImage(file="robot_face.png")
    label_face = tk.Label(content_frame, image=face_image, bg="white")
    label_face.pack(pady=20)
    label_face.image = face_image  # Keep a reference to avoid garbage collection

# Call the initial greeting function after a brief delay
root.after(2000, initial_greeting)  # Delay of 2 seconds before showing greeting and face

# Start the Tkinter event loop
root.mainloop()
