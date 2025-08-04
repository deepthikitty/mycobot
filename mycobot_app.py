import streamlit as st
import datetime
import requests
import json
import pandas as pd
import os
import speech_recognition as sr

# === CONFIGURATION ===
TOGETHER_API_KEY = "34fd9c74150ef46528dd487841a21c3500de59791b22a102c1305e2beee7f2e3"
TOGETHER_ENDPOINT = "https://api.together.xyz/v1/chat/completions"
MODEL = "mistralai/Mistral-7B-Instruct-v0.1"

st.set_page_config(page_title="MycoBot: Mushroom Assistant", layout="wide")
st.title("MycoBot – Urban Mushroom Farming Assistant")

# === Load FAQ backup ===
@st.cache_data
def load_faq_json():
    try:
        with open("offline_faq.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

faq_data = load_faq_json()

# === Chat History file
HISTORY_FILE = "chat_history.csv"
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w") as f:
        f.write("timestamp,question,answer\n")

def log_chat(q, a):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now()},{q.replace(',', ';')},{a.replace(',', ';')}\n")

# === Ask AI function
def ask_mycobot(prompt):
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are MycoBot, an expert in mushroom farming. Answer clearly, practically, and concisely."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    try:
        response = requests.post(TOGETHER_ENDPOINT, headers=headers, json=payload)
        result = response.json()
        answer = result["choices"][0]["message"]["content"] if "choices" in result else "❌ No valid response from MycoBot."
        log_chat(prompt, answer)
        return answer
    except:
        for q, a in faq_data.items():
            if q.lower() in prompt.lower():
                return f"(Offline FAQ) {a}"
        return "API call failed and no offline match found."

# === Voice input function ===
def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except:
        return "Sorry, could not understand."

# === Tabs ===
tabs = st.tabs([
    "💬 Chat", "🌱 Substrate Recommender", "📦 Yield Estimator", "🦠 Symptom Diagnosis",
    "📅 Cultivation Calendar", "🗂️ Farm Tracker", "📤 Log Export", "📈 Environment Logger",
    "📝 Growth Journal", "📍 Vendor Finder", "🧰 Tool Recommender", "🌐 Community Advice",
    "🎥 Training Videos", "💰 Profit Estimator Tool", "🍄 Mushroom Health Scoring",
    "📜 My Chat History"
])

# === 💬 Chat Tab
with tabs[0]:
    st.subheader("Ask MycoBot Anything About Mushroom Farming")
    col1, col2 = st.columns([3, 1])
    with col1:
        user_input = st.text_area("Type your question", key="text_q")
    with col2:
        audio_file = st.file_uploader("Or upload voice (.wav)", type=["wav"])
        if audio_file:
            with open("temp.wav", "wb") as f:
                f.write(audio_file.getbuffer())
            user_input = transcribe_audio("temp.wav")
            st.info(f"Transcript: {user_input}")

    if st.button("Ask MycoBot"):
        if user_input.strip():
            answer = ask_mycobot(user_input)
            st.markdown("### 🤖 MycoBot says:")
            st.write(answer)
        else:
            st.warning("Please enter or upload a question.")

# === 🌱 Substrate Recommender
with tabs[1]:
    st.subheader("Substrate Recommendation")
    species = st.selectbox("Mushroom Species", ["Agaricus", "Oyster", "Shiitake"], key="subs")
    setup = st.selectbox("Farming Setup", ["Terrace", "Indoor", "Balcony", "Greenhouse"])
    city = st.text_input("City/Climate Zone", "Mumbai")
    if st.button("Recommend Substrate"):
        query = f"What is the best substrate to grow {species} mushrooms in {setup} setup in {city}?"
        st.write(ask_mycobot(query))

# === 📦 Yield Estimator
with tabs[2]:
    st.subheader("Estimate Mushroom Yield")
    species = st.selectbox("Species", ["Agaricus", "Oyster", "Shiitake"], key="yield")
    area = st.number_input("Area (sq ft)", min_value=1)
    substrate = st.selectbox("Substrate", ["Wheat Straw", "Manure", "Saw Dust"])
    if st.button("Estimate Yield"):
        query = f"Estimate yield for {species} using {substrate} over {area} sq ft."
        st.write(ask_mycobot(query))

# === 🦠 Symptom Diagnosis
with tabs[3]:
    st.subheader("Diagnose Problems")
    symptoms = st.text_area("Describe the issue")
    if st.button("Diagnose"):
        query = f"My mushrooms have: {symptoms}. What is the cause and solution?"
        st.write(ask_mycobot(query))

# === 📅 Cultivation Calendar
with tabs[4]:
    st.subheader("Generate Cultivation Calendar")
    species = st.selectbox("Mushroom Type", ["Agaricus", "Oyster", "Shiitake"], key="calendar")
    start = st.date_input("Start Date", datetime.date.today())
    if st.button("Generate Calendar"):
        query = f"Give a cultivation schedule for {species} starting from {start}."
        st.write(ask_mycobot(query))

# === 🗂️ Farm Tracker
with tabs[5]:
    st.subheader("Farm Task Logger")
    task_date = st.date_input("Date", datetime.date.today(), key="logdate")
    task = st.text_area("Task")
    if st.button("Log Task"):
        with open("farm_log.csv", "a") as f:
            f.write(f"{task_date},{task}\n")
        st.success(f"Saved task for {task_date}: {task}")

# === 📤 Log Export
with tabs[6]:
    st.subheader("Download Farm Log")
    if os.path.exists("farm_log.csv"):
        df = pd.read_csv("farm_log.csv", names=["Date", "Task"])
        st.dataframe(df)
        st.download_button("📥 Download Log", df.to_csv(index=False), file_name="farm_log.csv")
    else:
        st.info("No tasks logged yet.")

# === 📈 Environment Logger
with tabs[7]:
    st.subheader("Record Environment Data")
    temp = st.number_input("Temperature (°C)", step=0.1)
    humidity = st.number_input("Humidity (%)", step=1.0)
    env_date = st.date_input("Date", datetime.date.today(), key="env")
    if st.button("Log Environment"):
        with open("env_log.csv", "a") as f:
            f.write(f"{env_date},{temp},{humidity}\n")
        st.success("Environment log saved.")

# === 📝 Growth Journal
with tabs[8]:
    st.subheader("Growth Journal Entry")
    journal_date = st.date_input("Journal Date", datetime.date.today(), key="journal")
    notes = st.text_area("Your observations")
    photo = st.file_uploader("Upload a photo", type=["jpg", "jpeg", "png"])
    if st.button("Save Journal Entry"):
        with open("journal_log.csv", "a") as f:
            f.write(f"{journal_date},{notes}\n")
        if photo:
            with open(f"photo_{journal_date}.jpg", "wb") as img:
                img.write(photo.getbuffer())
        st.success("Journal entry saved.")

# === 📍 Vendor Finder
with tabs[9]:
    st.subheader("Find Vendors for Mushroom Farming")
    location = st.text_input("Enter your city or region")
    if st.button("Find Vendors"):
        query = f"List mushroom farming vendors, spawn suppliers, and grow bag sellers in {location}."
        st.write(ask_mycobot(query))

# === 🧰 Tool Recommender
with tabs[10]:
    st.subheader("Recommend Tools or Equipment")
    need = st.text_input("What do you need help choosing?")
    if st.button("Recommend Tool"):
        query = f"What is the best tool or equipment for: {need}?"
        st.write(ask_mycobot(query))

# === 🌐 Community Advice Fetcher
with tabs[11]:
    st.subheader("Ask What the Community Recommends")
    query = st.text_area("What should I ask the online mushroom community?")
    if st.button("Get Community Advice"):
        prompt = f"Summarize what mushroom growers say online about: {query}."
        st.write(ask_mycobot(prompt))

# === 🎥 Training Video Links
with tabs[12]:
    st.subheader("Suggest Learning Videos")
    topic = st.text_input("What do you want to learn?")
    if st.button("Find Videos"):
        prompt = f"Suggest some YouTube videos or playlists that teach: {topic} related to mushroom cultivation."
        st.write(ask_mycobot(prompt))

# === 💰 Profit Estimator Tool
with tabs[13]:
    st.subheader("Estimate Your Farming Profit")
    species = st.selectbox("Species", ["Agaricus", "Oyster", "Shiitake"], key="profit")
    area = st.number_input("Area (sq ft)", min_value=1, key="area_profit")
    substrate = st.selectbox("Substrate Type", ["Wheat Straw", "Manure", "Saw Dust"], key="substrate_profit")
    cost = st.number_input("Estimated Total Cost (₹)", min_value=0)
    if st.button("Estimate Profit"):
        prompt = f"Estimate profit for growing {species} mushrooms over {area} sq ft using {substrate}, with a total cost of ₹{cost}. Include potential revenue and margin."
        st.write(ask_mycobot(prompt))

# === 🍄 Mushroom Health Scoring
with tabs[14]:
    st.subheader("Get Mushroom Health Score")
    description = st.text_area("Describe the visual appearance or health of your mushroom batch")
    if st.button("Score Health"):
        prompt = f"Based on this description: '{description}', rate the health of this mushroom crop out of 10 and suggest improvements."
        st.write(ask_mycobot(prompt))

# === 📜 Chat History
with tabs[15]:
    st.subheader("🕓 Your Chat History")
    if os.path.exists(HISTORY_FILE):
        df = pd.read_csv(HISTORY_FILE)
        st.dataframe(df)
        st.download_button("📥 Download Chat History", df.to_csv(index=False), file_name="mycobot_chat_history.csv")
    else:
        st.info("No chat history found.")
