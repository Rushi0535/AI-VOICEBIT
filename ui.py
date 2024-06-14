import streamlit as st
import speech_recognition as sr
import pyttsx3
from llm import chat
import random
import os

st.set_page_config(page_title="SOU AI", page_icon='assets/Silver Oak University (Favicon).svg')

# Predefined username and password
USERNAME = "KIOSK_USER"
PASSWORD = "SOURocks@802"

# Function to recognize speech and convert it to text
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)# Adjust for ambient noise
        with st.spinner("Listening..."):
            audio = recognizer.listen(source)
    try:
        query = recognizer.recognize_google(audio)
        st.success(f"Your Question: {query}")
        return query
    except sr.UnknownValueError:
        st.error("Sorry, I did not understand that.")
        return None

# Function to convert text to speech and save it as an audio file
def speak(response, voice='female', speed=150, filename="response.mp3"):
    engine = pyttsx3.init()
    
    # Set properties
    voices = engine.getProperty('voices')
    if voice == 'male':
        engine.setProperty('voice', voices[0].id)  # Male voice
    else:
        engine.setProperty('voice', voices[1].id)  # Female voice
    engine.setProperty('rate', speed)  # Speed
    
    engine.save_to_file(response, filename)
    engine.runAndWait()
    return filename

# Function to display fun facts about Silver Oak University
def show_fun_fact():
    fun_facts = [
        "The university hosts an annual cultural fest entitled 'Junnon' of 4-5 days having more than 200 performances in each day.",
        "Silver Oak University has a strong alumni network with graduates working in top companies worldwide and often they are invited to campus to guide the students.",
        "The university offers over 15 different clubs and organizations for students to join for 360 degree development.",
        "Silver Oak University has an AI-powered campus with numerous student projects. This AI system is one example of AI projects which makes Silver Oak University an AI Hub for the students.",
        "Silver Oak University has an International Organization entitled 'IEEE STUDENT BRANCH' which is Region 10's (i.e Asia-pacific) Outstanding Student Branch."
    ]
    st.write("Until the response is being generated, I think you should know this fact below:-")
    st.info(random.choice(fun_facts))

# Function to authenticate the user
def authenticate(username, password):
    return username == USERNAME and password == PASSWORD

# Streamlit app
def main():
    st.sidebar.image("assets/Silver Oak University.svg", width=300)
    hide_img_fs = '''
    <style>
    button[title="View fullscreen"]{
        visibility: hidden;}
    </style>
    '''
    st.markdown(hide_img_fs, unsafe_allow_html=True)
    st.title("Silver Oak University's AI Assistant")
    st.header("AI Is Here To Provide You Information")
    
    # Sidebar options
    st.sidebar.title("AI Configurations")
    input_mode = st.sidebar.radio("Select Input Mode", ('Voice', 'Text'))
    voice_type = st.sidebar.radio("Select Voice Type", ('Male', 'Female'))
    voice_speed = st.sidebar.slider("Select Voice Speed", 50, 300, 150)
    st.sidebar.caption("Recommended Voice Speed: 160")
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

    if input_mode == 'Voice':
        st.write("Click the button below for your questions")
        if st.button("Start Asking", key="ask_button"):
            text = recognize_speech()
            show_fun_fact()
            if text:
                with st.spinner("Generating response..."):
                    response = chat(text)
                    st.success("Response generated!")
                    st.write(f"Response: {response}")
                    
                    # Convert the response to speech and save it as an audio file
                    audio_file = speak(response, voice=voice_type.lower(), speed=voice_speed)
                    
                    # Play the audio file using Streamlit
                    with open(audio_file, "rb") as f:
                        audio_bytes = f.read()
                        st.audio(audio_bytes, format="audio/mp3",autoplay=True)
    else:
        user_input = st.text_input("Enter your question:")
        if st.button("Submit"):
            if user_input:
                show_fun_fact()
                with st.spinner("Generating response..."):
                    response = chat(user_input)
                    st.success("Response generated!")
                    st.write(f"Response: {response}")
                    
                    # Convert the response to speech and save it as an audio file
                    audio_file = speak(response, voice=voice_type.lower(), speed=voice_speed)
                    
                    # Play the audio file using Streamlit
                    with open(audio_file, "rb") as f:
                        audio_bytes = f.read()
                        st.audio(audio_bytes, format="audio/mp3")

# Authentication page
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Login"):
        if authenticate(username, password):
            st.session_state.logged_in = True
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    main()
else:
    login()
