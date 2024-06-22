import cv2
import mediapipe as mp

# Definindo cores específicas para cada dedo
fingertip_colors = [
    (255, 0, 0),  # Thumb (0, 1, 2, 3, 4)
    (0, 255, 0),  # Index (5, 6, 7, 8)
    (0, 0, 255),  # Middle (9, 10, 11, 12)
    (255, 255, 0),  # Ring (13, 14, 15, 16)
    (0, 255, 255)   # Pinky (17, 18, 19, 20)
]

def draw_landmarks(img, hand_landmarks, connections):
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    # Desenhando as conexões e pontos padrão
    mp_drawing.draw_landmarks(
        img,
        hand_landmarks,
        connections,
        mp_drawing_styles.get_default_hand_landmarks_style(),
        mp_drawing_styles.get_default_hand_connections_style())

    # Desenhando as pontas dos dedos com cores específicas
    for idx, lm in enumerate(hand_landmarks.landmark):
        if 0 <= idx <= 4:
            color = fingertip_colors[0]
        elif 5 <= idx <= 8:
            color = fingertip_colors[1]
        elif 9 <= idx <= 12:
            color = fingertip_colors[2]
        elif 13 <= idx <= 16:
            color = fingertip_colors[3]
        elif 17 <= idx <= 20:
            color = fingertip_colors[4]
        else:
            color = (255, 255, 255)  # Branco como fallback
        
        cv2.circle(img, (int(lm.x * img.shape[1]), int(lm.y * img.shape[0])), 7, color, -1)
        cv2.putText(img, str(idx), (int(lm.x * img.shape[1]), int(lm.y * img.shape[0])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
