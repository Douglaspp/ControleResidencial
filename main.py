from flask import Flask, render_template, Response, request
import threading
import cv2
import mediapipe as mp
import time
from gestures import recognize_gesture
from http_commands import handle_gesture, send_favorite_channel_commands, update_channel_file
from coloring import draw_landmarks

app = Flask(__name__)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.2, min_tracking_confidence=0.5)

cap = cv2.VideoCapture(0)

gesture_start_time = None
last_command_time = None
current_gesture = None
detected_gesture = ""

@app.route('/')
def index():
    with open('favorite_channels.txt', 'r') as file:
        channels = [line.strip() for line in file if line.strip()]
    return render_template('index.html', channels=channels)

@app.route('/save', methods=['POST'])
def save_channels():
    channels = request.form['channels']
    channels_list = channels.split(',')
    with open('favorite_channels.txt', 'a') as file:  # Abra no modo append para adicionar ao invés de sobrescrever
        for channel in channels_list:
            if channel.strip():  # Certifique-se de que não salva canais vazios
                file.write(f"{channel.strip()}\n")
    return '', 204  # Retorne status 204 sem conteúdo

@app.route('/remove', methods=['POST'])
def remove_channel():
    channel = request.form['channel']
    with open('favorite_channels.txt', 'r') as file:
        lines = file.readlines()
    with open('favorite_channels.txt', 'w') as file:
        for line in lines:
            if channel not in line.strip("\n"):
                file.write(line)
    return '', 204  # Retorne status 204 sem conteúdo

def generate_frames():
    global detected_gesture
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(frame_rgb)

            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    landmarks = hand_landmarks.landmark
                    gesture = recognize_gesture(landmarks)
                    detected_gesture = gesture  # Atualiza o gesto detectado

            # Exibe o gesto detectado na tela
            cv2.putText(frame, f"Gesto: {detected_gesture}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def start_server():
    app.run(host='0.0.0.0', port=8081)  # Executa o Flask em uma porta diferente

def run_detection():
    global gesture_start_time, last_command_time, current_gesture, detected_gesture

    prev_frame_time = 0  # Adiciona controle de tempo anterior
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        current_frame_time = time.time()
        if current_frame_time - prev_frame_time >= 1/30:  # Processa em 30 FPS
            prev_frame_time = current_frame_time
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(frame_rgb)

            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    landmarks = hand_landmarks.landmark
                    gesture = recognize_gesture(landmarks)
                    print(f"Gesture recognized: {gesture}")

                    detected_gesture = gesture  # Atualiza o gesto detectado
                    gesture_start_time, last_command_time = handle_gesture(gesture, gesture_start_time, last_command_time)

            else:
                current_gesture = None
                gesture_start_time = None
                last_command_time = None
                detected_gesture = ""  # Limpa o gesto detectado quando nenhuma mão é detectada

            # Exibe o gesto detectado na tela
            cv2.putText(frame, f"Gesto: {detected_gesture}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

            cv2.imshow('Hand Gesture Recognition', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def main():
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    run_detection()

if __name__ == "__main__":
    main()
