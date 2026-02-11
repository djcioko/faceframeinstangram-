import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, RTCConfiguration
import cv2
import numpy as np

st.set_page_config(page_title="Insta Face Tracking", layout="wide")

# CSS pentru a face video-ul să ocupe tot ecranul pe cât posibil
st.markdown("""
<style>
    .main { background: black; }
    div[data-testid="stVerticalBlock"] > div:has(iframe) { 
        display: flex; justify-content: center; 
    }
</style>
""", unsafe_allow_html=True)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

class FaceTrackingTransformer(VideoTransformerBase):
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        h, w, _ = img.shape
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) > 0:
            # Luăm prima față detectată
            (x, y, fw, fh) = faces[0]
            
            # Calculăm zona de zoom (adăugăm un padding în jurul feței)
            padding = 100
            x1 = max(0, x - padding)
            y1 = max(0, y - padding)
            x2 = min(w, x + fw + padding)
            y2 = min(h, y + fh + padding)
            
            # Tăiem imaginea (Crop)
            face_zone = img[y1:y2, x1:x2]
            
            # Redimensionăm înapoi la dimensiunea originală (Efectul de Zoom)
            img = cv2.resize(face_zone, (w, h), interpolation=cv2.INTER_LINEAR)
            
            # Desenăm rama de Insta pe imaginea deja mărită
            # (Rama va sta acum la marginile feței detectate)
            color = (255, 0, 255)
            thickness = 8
            l = 60
            # Colțuri desenate relativ la noul frame mărit
            cv2.line(img, (50, 50), (50 + l, 50), color, thickness)
            cv2.line(img, (50, 50), (50, 50 + l), color, thickness)
            cv2.line(img, (w-50, 50), (w-50-l, 50), color, thickness)
            cv2.line(img, (w-50, 50), (w-50, 50 + l), color, thickness)
            cv2.line(img, (50, h-50), (50 + l, h-50), color, thickness)
            cv2.line(img, (50, h-50), (50, h-50-l), color, thickness)
            cv2.line(img, (w-50, h-50), (w-50-l, h-50), color, thickness)
            cv2.line(img, (w-50, h-50), (w-50, h-50-l), color, thickness)

        return img

st.title("🎬 INSTA FACE TRACKING LIVE")

webrtc_streamer(
    key="face-tracking",
    video_transformer_factory=FaceTrackingTransformer,
    rtc_configuration=RTCConfiguration(
        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    ),
    media_stream_constraints={"video": True, "audio": False},
)
