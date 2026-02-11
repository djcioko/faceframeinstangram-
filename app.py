import streamlit as st
import time, random, urllib.parse
import numpy as np
from PIL import Image
import cv2
import streamlit.components.v1 as components

# ================= IMPORT AI =================
try:
    from deepface import DeepFace
    AI_READY = True
except ImportError:
    AI_READY = False

# Încărcăm detectorul de fețe standard (OpenCV Haar Cascade)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# ================= CONFIG =================
st.set_page_config(page_title="HERCULE AI - THE BEAST DJ", layout="wide")

st.markdown("""
<style>
    .main { background:#0e1117; color:white; }
    iframe { border-radius:20px; border:4px solid #1ed760; box-shadow: 0px 0px 25px #1ed760; }
    .timer-box { font-size: 40px; font-weight: bold; color: #ff4b4b; text-align: center; border: 2px solid #ff4b4b; border-radius: 15px; padding: 10px; margin-bottom: 20px; }
    .btn-youtube { background-color: #FF0000; color: white; padding: 15px; border-radius: 30px; text-align: center; font-weight: bold; display: block; text-decoration: none; font-size: 18px; }
</style>
""", unsafe_allow_html=True)

if "last_time" not in st.session_state: st.session_state.last_time = time.time()
if "song" not in st.session_state: st.session_state.song = ""
if "query" not in st.session_state: st.session_state.query = ""

MUSIC_DB = {
    "happy": ["Bruno Mars - Marry You", "Pharrell Williams - Happy", "Daft Punk - Get Lucky"],
    "neutral": ["Abba - Dancing Queen", "The Weeknd - Blinding Lights"],
    "sad": ["Adele - Someone Like You", "Holograf - Sa nu-mi iei niciodata dragostea"],
    "angry": ["AC/DC - Thunderstruck", "Metallica - Enter Sandman"]
}

def apply_face_frame(image):
    img_np = np.array(image)
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    for (x, y, w, h) in faces:
        color = (255, 0, 255) # Magenta (Instagram Style)
        l, t = 40, 5 # Lungime colț și grosime
        # Desenare colțuri manuală
        cv2.line(img_bgr, (x, y), (x + l, y), color, t)
        cv2.line(img_bgr, (x, y), (x, y + l), color, t)
        cv2.line(img_bgr, (x+w, y), (x+w-l, y), color, t)
        cv2.line(img_bgr, (x+w, y), (x+w, y+l), color, t)
        cv2.line(img_bgr, (x, y+h), (x+l, y+h), color, t)
        cv2.line(img_bgr, (x, y+h), (x, y+h-l), color, t)
        cv2.line(img_bgr, (x+w, y+h), (x+w-l, y+h), color, t)
        cv2.line(img_bgr, (x+w, y+h), (x+w, y+h-l), color, t)
        
    return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

def get_vibe(img):
    if not AI_READY: return "neutral"
    try:
        res = DeepFace.analyze(np.array(img), actions=["emotion"], enforce_detection=False)
        return res[0]["dominant_emotion"]
    except: return "neutral"

# --- TIMER ---
now = time.time()
elapsed = now - st.session_state.last_time
timp_ramas = max(0, 120 - int(elapsed))

st.title("🎰 HERCULE AI - THE ULTIMATE DJ ENGINE")
col1, col2 = st.columns([1, 1.2])

with col1:
    st.markdown(f'<div class="timer-box">⏱️ AUTO-SCAN: {timp_ramas:02d}s</div>', unsafe_allow_html=True)
    cam = st.camera_input("📸 AI EYE ACTIVATED")
    
    if cam:
        img_raw = Image.open(cam).convert("RGB")
        # Aplicăm rama
        img_with_frame = apply_face_frame(img_raw)
        st.image(img_with_frame, caption="Face Scanned!", use_column_width=True)
        
        # Detecție emoție
        with st.spinner('Analizăm vibe-ul...'):
            emotion = get_vibe(img_raw)
            vibe_cat = emotion if emotion in MUSIC_DB else "neutral"
            piesa = random.choice(MUSIC_DB[vibe_cat])
            
            st.session_state.song = piesa
            st.session_state.query = urllib.parse.quote(piesa)
            st.session_state.last_time = time.time()
            
            st.success(f"🎭 Emoție: {emotion.upper()} | 🎵 Melodie: {piesa}")
            st.markdown(f'<a href="https://www.youtube.com/results?search_query={st.session_state.query}" target="_blank" class="btn-youtube">▶️ VEZI PE YOUTUBE</a>', unsafe_allow_html=True)

with col2:
    if st.session_state.query:
        yt_url = f"https://www.youtube.com/embed?listType=search&list={st.session_state.query}&autoplay=1"
        st.markdown(f'<iframe width="100%" height="450" src="{yt_url}" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>', unsafe_allow_html=True)

# Auto-refresh
if timp_ramas > 0 and not cam:
    time.sleep(2)
    st.rerun()
