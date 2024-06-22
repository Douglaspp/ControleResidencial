import time
import requests
import threading

# URLs dos comandos para os números de 0 a 9
NUMERIC_COMMANDS = {
    '0': "http://192.168.15.5/cm?cmnd=IRSend%20%7B%22Protocol%22%3A%22RC6%22%2C%22Bits%22%3A36%2C%22Data%22%3A%220xC80702600%22%2C%22DataLSB%22%3A%220x30010E6400%22%2C%22Repeat%22%3A0%7D",
    '1': "http://192.168.15.5/cm?cmnd=IRSend%20%7B%22Protocol%22%3A%22RC6%22%2C%22Bits%22%3A36%2C%22Data%22%3A%220xC80702601%22%2C%22DataLSB%22%3A%220x30010E6480%22%2C%22Repeat%22%3A0%7D",
    '2': "http://192.168.15.5/cm?cmnd=IRSend%20%7B%22Protocol%22%3A%22RC6%22%2C%22Bits%22%3A36%2C%22Data%22%3A%220xC80702602%22%2C%22DataLSB%22%3A%220x30010E6440%22%2C%22Repeat%22%3A0%7D",
    '3': "http://192.168.15.5/cm?cmnd=IRSend%20%7B%22Protocol%22%3A%22RC6%22%2C%22Bits%22%3A36%2C%22Data%22%3A%220xC8070A603%22%2C%22DataLSB%22%3A%220x30010E65C0%22%2C%22Repeat%22%3A0%7D",
    '4': "http://192.168.15.5/cm?cmnd=IRSend%20%7B%22Protocol%22%3A%22RC6%22%2C%22Bits%22%3A36%2C%22Data%22%3A%220xC80702604%22%2C%22DataLSB%22%3A%220x30010E6420%22%2C%22Repeat%22%3A0%7D",
    '5': "http://192.168.15.5/cm?cmnd=IRSend%20%7B%22Protocol%22%3A%22RC6%22%2C%22Bits%22%3A36%2C%22Data%22%3A%220xC8070A605%22%2C%22DataLSB%22%3A%220x30010E65A0%22%2C%22Repeat%22%3A0%7D",
    '6': "http://192.168.15.5/cm?cmnd=IRSend%20%7B%22Protocol%22%3A%22RC6%22%2C%22Bits%22%3A36%2C%22Data%22%3A%220xC80702606%22%2C%22DataLSB%22%3A%220x30010E6460%22%2C%22Repeat%22%3A0%7D",
    '7': "http://192.168.15.5/cm?cmnd=IRSend%20%7B%22Protocol%22%3A%22RC6%22%2C%22Bits%22%3A36%2C%22Data%22%3A%220xC8070A607%22%2C%22DataLSB%22%3A%220x30010E65E0%22%2C%22Repeat%22%3A0%7D",
    '8': "http://192.168.15.5/cm?cmnd=IRSend%20%7B%22Protocol%22%3A%22RC6%22%2C%22Bits%22%3A36%2C%22Data%22%3A%220xC80702608%22%2C%22DataLSB%22%3A%220x30010E6410%22%2C%22Repeat%22%3A0%7D",
    '9': "http://192.168.15.5/cm?cmnd=IRSend%20%7B%22Protocol%22%3A%22RC6%22%2C%22Bits%22%3A36%2C%22Data%22%3A%220xC8070A609%22%2C%22DataLSB%22%3A%220x30010E6590%22%2C%22Repeat%22%3A0%7D"
}

VOLUME_UP_URL = "http://192.168.15.5/cm?cmnd=IRSend%20%7B%22Protocol%22%3A%22RC6%22%2C%22Bits%22%3A36%2C%22Data%22%3A%220xC8070A610%22%2C%22DataLSB%22%3A%220x30010E6508%22%2C%22Repeat%22%3A0%7D"
VOLUME_DOWN_URL = "http://192.168.15.5/cm?cmnd=IRSend%20%7B%22Protocol%22%3A%22RC6%22%2C%22Bits%22%3A36%2C%22Data%22%3A%220xC80702611%22%2C%22DataLSB%22%3A%220x30010E6488%22%2C%22Repeat%22%3A0%7D"
POWER_ON_OFF_URLS = [
    "http://192.168.15.5/cm?cmnd=IRSend%20%7B%22Protocol%22%3A%22RC6%22%2C%22Bits%22%3A36%2C%22Data%22%3A%220xC8070260C%22%2C%22DataLSB%22%3A%220x30010E6430%22%2C%22Repeat%22%3A0%7D",
    "http://192.168.15.5/cm?cmnd=IRSend%20%7B%22Protocol%22%3A%22SAMSUNG%22%2C%22Bits%22%3A32%2C%22Data%22%3A%220xE0E040BF%22%2C%22DataLSB%22%3A%220x70702FD%22%2C%22Repeat%22%3A0%7D",
    "http://192.168.15.5/cm?cmnd=IRSend%20%7B%22Protocol%22%3A%22NIKAI%22%2C%22Bits%22%3A24%2C%22Data%22%3A%220xD5F2A%22%2C%22DataLSB%22%3A%220xB0FA54%22%2C%22Repeat%22%3A0%7D"
]

CHANNELS_FILE = "favorite_channels.txt"
stop_flag = False
fav_thread = None
current_gesture = None
current_channel_index = 0
sending_channels = False

def send_command(url):
    try:
        response = requests.get(url)
        print(f"Command sent: {url} - Response: {response.status_code}")
    except Exception as e:
        print(f"Error sending command: {e}")

def send_command_async(url):
    thread = threading.Thread(target=send_command, args=(url,))
    thread.start()

def update_channel_file(channels, current_channel_index):
    with open(CHANNELS_FILE, 'w') as file:
        for i, channel in enumerate(channels):
            if channel.strip():  # Certifique-se de que não salva canais vazios
                if i == current_channel_index:
                    file.write(f"*:{channel.strip()}\n")
                else:
                    file.write(f"{i+1}:{channel.strip()}\n")

def send_favorite_channel_commands(channels):
    global current_channel_index, stop_flag, current_gesture, sending_channels

    if not channels:
        print("No channels to send.")
        sending_channels = False
        return

    while not stop_flag:
        # Verifica continuamente o estado do gesto
        if current_gesture != "Fav":
            print("Gesture changed, stopping favorite channel commands.")
            sending_channels = False
            return
        
        channel_number = channels[current_channel_index]
        if channel_number:
            print(f"Sending channel {channel_number}")
            for digit in str(channel_number):
                print(f"Preparing to send digit {digit}")
                if current_gesture != "Fav" or stop_flag:
                    print("Gesture changed, stopping favorite channel commands.")
                    sending_channels = False
                    return
                if digit in NUMERIC_COMMANDS:
                    print(f"Sending digit {digit}")
                    send_command(NUMERIC_COMMANDS[digit])
                    time.sleep(0.3)  # Espera entre os dígitos
            
            # Atualiza o índice do canal atual e salva no arquivo
            current_channel_index += 1
            if current_channel_index >= len(channels):
                current_channel_index = 0
                print("Retornando ao início da lista de canais.")
            update_channel_file(channels, current_channel_index)
            
            # Substitua o time.sleep(3) por um loop para não bloquear a leitura do gesto
            end_time = time.time() + 3
            while time.time() < end_time:
                if current_gesture != "Fav" or stop_flag:
                    print("Gesture changed, stopping favorite channel commands.")
                    sending_channels = False
                    return
                time.sleep(0.1)
        else:
            update_channel_file(channels, current_channel_index)
            sending_channels = False
            return

def handle_gesture(gesture, gesture_start_time, last_command_time):
    global current_gesture, fav_thread, stop_flag, sending_channels

    current_time = time.time()
    #print(f"Current time: {current_time}, Gesture start time: {gesture_start_time}, Last command time: {last_command_time}")

    if gesture_start_time is None:
        gesture_start_time = current_time

    if gesture == "Volume Up":
        if current_time - gesture_start_time >= 2:
            if last_command_time is None or current_time - last_command_time >= 2:
                send_command_async(VOLUME_UP_URL)
                last_command_time = current_time

    elif gesture == "Volume Down":
        if current_time - gesture_start_time >= 2:
            if last_command_time is None or current_time - last_command_time >= 2:
                send_command_async(VOLUME_DOWN_URL)
                last_command_time = current_time

    elif gesture == "Power On/Off":
        if current_time - gesture_start_time >= 5:
            for url in POWER_ON_OFF_URLS:
                send_command_async(url)
                
            return None, None

    elif gesture == "Fav":
        if current_time - gesture_start_time >= 2:
            if not sending_channels:  # Inicia o envio apenas se não estiver enviando atualmente
                print(f"Gesture detected: {gesture}, starting favorite channel commands.")
                with open(CHANNELS_FILE, 'r') as file:
                    channels = [line.strip().split(':')[1] for line in file if line.strip() and ':' in line]
                print(f"Channels loaded: {channels}")
                stop_flag = False
                current_channel_index = 0
                sending_channels = True
                fav_thread = threading.Thread(target=send_favorite_channel_commands, args=(channels,))
                fav_thread.start()
            current_gesture = "Fav"
            return gesture_start_time, current_time

    else:
        stop_flag = True
        current_gesture = None
        sending_channels = False
        print("Gesture changed, stopping favorite channel commands.")

    return gesture_start_time, last_command_time
