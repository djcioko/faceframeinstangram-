import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import cv2
import mediapipe as mp
import numpy as np

# Setări pagină
st.set_page_config(page_title="Face Frame AI", layout="centered")

# Inițializare MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
face_detector = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)

class FaceFrameTransformer(VideoTransformerBase):
    def transform(self, frame):
        # Convertim frame-ul primit de la camera web în format OpenCV
        img = frame.to_ndarray(format="bgr24")

        # Procesare pentru detecție
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = face_detector.process(img_rgb)

        if results.detections:
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                ih, iw, _ = img.shape
                x, y, w, h = int(bbox.xmin * iw), int(bbox.ymin * ih), \
                             int(bbox.width * iw), int(bbox.height * ih)

                # Desenăm rama stil Instagram (Color: Magenta/Neon)
                color = (255, 0, 255)
                t = 4
                l = 40
                
                # Colțuri
                cv2.line(img, (x, y), (x + l, y), color, t)
                cv2.line(img, (x, y), (x, y + l), color, t)
                cv2.line(img, (x + w, y), (x + w - l, y), color, t)
                cv2.line(img, (x + w, y), (x + w, y + l), color, t)
                cv2.line(img, (x, y + h), (x + l, y + h), color, t)
                cv2.line(img, (x, y + h), (x, y + h - l), color, t)
                cv2.line(img, (x + w, y + h), (x + w - l, y + h), color, t)
                cv2.line(img, (x + w, y + h), (x + w, y + h - l), color, t)

        return img

st.title("📸 Face Frame AI")
st.info("Apasă pe butonul 'SELECT DEVICE' de mai jos și apoi pe 'START' pentru a porni camera.")

# AICI se deschide camera (înlocuiește cv2.VideoCapture)
webrtc_streamer(
    key="face-frame",
    video_transformer_factory=FaceFrameTransformer,
    rtc_configuration={ # Această setare ajută la conexiunea prin firewall-uri
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    }
)
