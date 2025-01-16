import datetime
import pyttsx3
import speech_recognition as sr
import webbrowser
import requests
import wikipedia
from customtkinter import *
from tkinter import messagebox

# Initialize the text-to-speech engine
engine = pyttsx3.init()

def speak(text):
    """Speak out the given text and display it in the GUI."""
    text_box.insert(END, f"Assistant: {text}\n")  # Display in GUI
    text_box.see(END)  # Scroll to the end
    engine.say(text)  # Queue the speech
    engine.runAndWait()  # Process the speech without blocking GUI updates

def take_command():
    """Listen for a voice command and return it as text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Listening...")
        recognizer.pause_threshold = 1
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            speak("Recognizing...")
            command = recognizer.recognize_google(audio, language='en-in')
            text_box.insert(END, f"You said: {command}\n")  # Display in GUI
            text_box.see(END)
        except sr.UnknownValueError:
            speak("Sorry, I didn't understand that.")
            return take_command() #Retry if not understant 
        except sr.RequestError:
            speak("Network error.")
            return ""
    return command.lower()

def greet():
    """Greet the user based on the current time."""
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak("Good morning!")
    elif 12 <= hour < 18:
        speak("Good afternoon!")
    else:
        speak("Good evening!")
    speak("I am your virtual assistant. How can I help you today?")

def open_website(command):
    """Open a website dynamically based on the command."""
    words = command.split()
    for word in words:
        if word.lower() == "open":
            # Extract the website name (consider everything after "open")
            site_name = " ".join(words[words.index("open") + 1:]).lower()
            if not site_name:
                speak("Please provide the website name after 'open'.")
                return 
            # List of possible domain extensions
            possible_extensions = [
                ".com", ".org", ".net", ".info", ".biz", ".us", ".uk", ".ca", ".au", ".de",
                ".fr", ".jp", ".cn", ".br", ".ru", ".mx", ".it", ".edu", ".gov", ".mil",
                ".co", ".tv", ".int", ".name", ".pro", ".app", ".shop", ".blog", ".tech", 
                ".health", ".music", ".news", ".store", ".online", ".nyc", ".london", ".paris", ".tokyo"
            ]

            # Try adding each extension and attempt to open the website
            for ext in possible_extensions:
                url = f"https://www.{site_name}{ext}"
                try:
                    webbrowser.open(url)
                    speak(f"Opening {site_name}{ext}")
                    return  # Exit after successfully opening the site
                except Exception as e:
                    # If the website fails to open, try the next extension
                    continue
            # If no extension works, let the user know
            speak(f"Sorry, I couldn't open {site_name} with any known extension.")
            return
    speak("I didn't recognize the website name.")

def get_weather(city):
    """Fetch the current weather of a city using OpenWeatherMap API."""
    api_key = "b578d2328cb84738ace10e75493d8ece"  # Replace with your API key
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city}&appid={api_key}&units=metric"
    response = requests.get(complete_url)
    weather_data = response.json()
    if weather_data["cod"] != "404":
        main = weather_data["main"]
        temperature = main["temp"]
        weather_description = weather_data["weather"][0]["description"]
        return f"The temperature in {city} is {temperature}°C with {weather_description}."
    else:
        return "City not found."
    
def search_wikipedia(question):
    try:
        summary=wikipedia.summary(question,sentences=2)
        return summary
    except wikipedia.exceptions.DisambiguationError as err:
        return f"Your query is ambiguous. Did you mean: {', '.join(err.options[:3])}?"
    except wikipedia.exceptions.PageError as err:
        return "I was unable to find the answer"
    except Exception as err:
        return f"Error {err} has occured"

def process_command():
    """Process voice command and handle actions."""
    command = take_command()
    if not command:
        return

    if "open" in command:
        open_website(command)

    elif "time" in command:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The time is {current_time}")

    elif "weather" in command:
        speak("Please tell me the city name.")
        city = take_command()
        if city:
            weather = get_weather(city)
            speak(weather)

    elif "exit" in command or "quit" in command:
        speak("Goodbye! Have a great day ahead.")
        root.destroy()  # Close the GUI

    else:
        # If the command is a question, search Wikipedia
        question_keywords = ["what", "who", "how", "when", "why"]
        if any(keyword in command.lower() for keyword in question_keywords):
            speak("Searching Wikipedia...")
            result = search_wikipedia(command)
            speak(result)
        else:
            speak("Sorry, I didn't understand that. Can you please repeat?")

def change_color_them(event):
    try:
        if event == "Dark":
            set_appearance_mode("Dark")
        elif event == "Light":
            set_appearance_mode("Light")
        elif event == "system":
            set_appearance_mode("System")
    except Exception as err:
        messagebox.showerror("ERROR", "Unable to change the theme of the app")
def Main():
    global root,text_box
    try:
        # Initialize CustomTkinter GUI
        set_appearance_mode("dark")  # Light or Dark mode
        set_default_color_theme("blue")  # Theme color

        root = CTk()
        root.title("Virtual Assistant")
        root.geometry("600x400")

        # GUI Elements
        text_box = CTkTextbox(root, width=580, height=300, corner_radius=10)
        text_box.grid(row=0, column=0, padx=10, pady=10, columnspan=3)  # Span across 3 columns for better alignment

        listen_button = CTkButton(root, text="Listen", command=process_command, width=120, height=40)
        listen_button.grid(row=1, column=0, padx=5, pady=10, sticky="ew")  # Stretch the button to fit

        exit_button = CTkButton(root, text="Exit", command=root.destroy, width=120, height=40)
        exit_button.grid(row=1, column=2, padx=5, pady=10, sticky="ew")  # Stretch the button to fit

        display_theme = CTkComboBox(root, values=["Dark", "Light", "System"], command=change_color_them, width=120, height=40)
        display_theme.grid(row=1, column=1, padx=5, pady=10, sticky="ew")  # Centered in the middle column
        
        greet()  # Start with Greeting
        root.mainloop()
    except Exception as err:
        messagebox.showerror("ERROR","Unable to load the screen\nTry Again")

if __name__=="__main__":
    Main()