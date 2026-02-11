import streamlit as st
import time, random, urllib.parse
import numpy as np
from PIL import Image
import cv2
import streamlit.components.v1 as components

# ================= IMPORT AI & FRAME =================
try:
    from deepface import DeepFace
    import mediapipe as mp
    AI_READY = True
    # Inițializare detector pentru ramă
    mp_face_detection = mp.solutions.face_detection
    face_detector = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)
except ImportError:
    AI_READY = False

# ================= CONFIG =================
st.set_page_config(page_title="HERCULE AI - THE BEAST DJ", layout="wide")

st.markdown("""
<style>
    .main { background:#0e1117; color:white; }
    iframe { border-radius:20px; border:4px solid #1ed760; box-shadow: 0px 0px 25px #1ed760; }
    .timer-box { font-size: 40px; font-weight: bold; color: #ff4b4b; text-align: center; border: 2px solid #ff4b4b; border-radius: 15px; padding: 10px; margin-bottom: 20px; }
    .btn-spotify { background-color: #1DB954; color: white; padding: 15px; border-radius: 30px; text-align: center; font-weight: bold; display: block; text-decoration: none; margin-bottom: 10px; font-size: 18px; }
    .btn-festify { background-color: #f25c05; color: white; padding: 15px; border-radius: 30px; text-align: center; font-weight: bold; display: block; text-decoration: none; font-size: 18px; }
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
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    results = face_detector.process(img_np)
    
    if results.detections:
        for detection in results.detections:
            bbox = detection.location_data.relative_bounding_box
            ih, iw, _ = img_bgr.shape
            x, y, w, h = int(bbox.xmin * iw), int(bbox.ymin * ih), int(bbox.width * iw), int(bbox.height * ih)
            color = (255, 0, 255) # Magenta
            l, t = 40, 5
            # Colțuri
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

# --- LOGICA TIMER ---
now = time.time()
elapsed = now - st.session_state.last_time
timp_ramas = max(0, 120 - int(elapsed))

st.title("🎰 HERCULE AI - THE ULTIMATE DJ ENGINE")
col1, col2 = st.columns([1, 1.2])

with col1:
    st.markdown(f'<div class="timer-box">⏱️ AUTO-SCAN: {timp_ramas:02d}s</div>', unsafe_allow_html=True)
    cam = st.camera_input("📸 AI EYE ACTIVATED")
    source = cam
    if source:
        img_raw = Image.open(source).convert("RGB")
        img_with_frame = apply_face_frame(img_raw)
        st.image(img_with_frame, caption="Face Frame Active", use_column_width=True)
        
        emotion = get_vibe(img_raw)
        vibe_category = emotion if emotion in MUSIC_DB else "neutral"
        piesa = random.choice(MUSIC_DB[vibe_category])
        st.session_state.song, st.session_state.query = piesa, urllib.parse.quote(piesa)
        st.session_state.last_time = time.time()
        
        st.markdown(f"### 🎭 Emoție: **{emotion.upper()}** | 🎵 Melodie: **{piesa}**")
        st.markdown(f'<a href="https://www.youtube.com/results?search_query={st.session_state.query}" target="_blank" class="btn-youtube">▶️ PLAY ON YOUTUBE</a>', unsafe_allow_html=True)

with col2:
    if st.session_state.query:
        yt_url = f"https://www.youtube.com/embed?listType=search&list={st.session_state.query}&autoplay=1"
        st.markdown(f'<iframe width="100%" height="450" src="{yt_url}" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>', unsafe_allow_html=True)

if timp_ramas > 0:
    time.sleep(2)
    st.rerun()
