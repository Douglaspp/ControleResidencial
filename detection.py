import cv2
import mediapipe as mp
from gestures import recognize_gesture
from http_commands import handle_gesture
from coloring import draw_landmarks

def run_detection():
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(min_detection_confidence=0.9, min_tracking_confidence=0.9)
    cap = cv2.VideoCapture(0)
    gesture_start_time = None
    last_command_time = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(frame_rgb)
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                draw_landmarks(frame, hand_landmarks)
                gesture = recognize_gesture(hand_landmarks)
                if gesture:
                    gesture_start_time, last_command_time = handle_gesture(gesture, gesture_start_time, last_command_time)
                    cv2.putText(frame, gesture, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                else:
                    gesture_start_time = None

        cv2.imshow('Hand Gesture Recognition', frame)
        if cv2.waitKey(5) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
