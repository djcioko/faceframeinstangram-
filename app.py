import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import cv2
import mediapipe as mp
import numpy as np

# Configurare MediaPipe
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)

class FaceFrameTransformer(VideoTransformerBase):
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")

        # Procesare imagine
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = face_detection.process(img_rgb)

        if results.detections:
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                ih, iw, _ = img.shape
                x, y, w, h = int(bbox.xmin * iw), int(bbox.ymin * ih), \
                             int(bbox.width * iw), int(bbox.height * ih)

                # Desenare Face Frame (Stil Instagram)
                color = (255, 0, 255) # Roz/Magenta
                t = 4 # Grosime linie
                length = 40 # Lungime colț
                
                # Colț Stânga Sus
                cv2.line(img, (x, y), (x + length, y), color, t)
                cv2.line(img, (x, y), (x, y + length), color, t)
                
                # Colț Dreapta Sus
                cv2.line(img, (x + w, y), (x + w - length, y), color, t)
                cv2.line(img, (x + w, y), (x + w, y + length), color, t)

                # Colț Stânga Jos
                cv2.line(img, (x, y + h), (x + length, y + h), color, t)
                cv2.line(img, (x, y + h), (x, y + h - length), color, t)

                # Colț Dreapta Jos
                cv2.line(img, (x + w, y + h), (x + w - length, y + h), color, t)
                cv2.line(img, (x + w, y + h), (x + w, y + h - length), color, t)

        return img

st.title("📸 Face Frame Filter")
st.write("Efect stil Instagram folosind MediaPipe și Streamlit.")

webrtc_streamer(key="example", video_transformer_factory=FaceFrameTransformer)
