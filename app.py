import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, RTCConfiguration
import cv2
import numpy as np

# ================= CONFIGURARE PAGINĂ =================
st.set_page_config(page_title="INSTA FRAME FULLSCREEN", layout="wide")

# CSS pentru Full Screen și ascunderea meniurilor inutile
st.markdown("""
<style>
    #root > div:nth-child(1) > div > div > div > div > section > div { padding-top: 0rem; }
    .stApp { background: black; }
    iframe { border: none; width: 100vw; height: 80vh; }
    .fullscreen-btn {
        background-color: #FF00FF;
        color: white;
        padding: 10px 20px;
        border-radius: 20px;
        text-align: center;
        cursor: pointer;
        font-weight: bold;
        display: inline-block;
        margin: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Detector de fețe stabil (OpenCV)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

class InstaFrameTransformer(VideoTransformerBase):
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        for (x, y, w, h) in faces:
            color = (255, 0, 255) # Magenta Instagram
            l, t = 40, 6 # Lungime colț și grosime
            
            # Desenăm Rama (cele 8 linii pentru colțuri)
            cv2.line(img, (x, y), (x + l, y), color, t)
            cv2.line(img, (x, y), (x, y + l), color, t)
            cv2.line(img, (x + w, y), (x + w - l, y), color, t)
            cv2.line(img, (x + w, y), (x + w, y + l), color, t)
            cv2.line(img, (x, y + h), (x + l, y + h), color, t)
            cv2.line(img, (x, y + h), (x, y + h - l), color, t)
            cv2.line(img, (x + w, y + h), (x + w - l, y + h), color, t)
            cv2.line(img, (x + w, y + h), (x + w, y + h - l), color, t)

        return img

st.title("📸 INSTA FACE FRAME - LIVE")

# Buton Full Screen (JavaScript)
if st.button("Toggle Full Screen 📺"):
    st.components.v1.html("""
        <script>
            var elem = window.parent.document.documentElement;
            if (!window.parent.document.fullscreenElement) {
                elem.requestFullscreen();
            } else {
                window.parent.document.exitFullscreen();
            }
        </script>
    """, height=0)

# Lansare Video Streamer
webrtc_streamer(
    key="insta-filter",
    video_transformer_factory=InstaFrameTransformer,
    rtc_configuration=RTCConfiguration(
        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    ),
    media_stream_constraints={"video": True, "audio": False},
)
