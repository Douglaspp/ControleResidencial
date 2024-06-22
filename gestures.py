def is_volume_up(landmarks):
    return (
        landmarks[20].y > landmarks[19].y and
        landmarks[16].y > landmarks[15].y and
        landmarks[12].y > landmarks[11].y and
        landmarks[4].y < landmarks[11].y and
        landmarks[8].y < landmarks[7].y and
        landmarks[8].y < landmarks[6].y
    )

def is_volume_down(landmarks):
    return (
        landmarks[20].y > landmarks[19].y and
        landmarks[16].y > landmarks[15].y and
        landmarks[12].y > landmarks[11].y and
        landmarks[8].y > landmarks[7].y and
        landmarks[4].y > landmarks[7].y and
        landmarks[4].y > landmarks[8].y
    )

def is_power_on_off(landmarks):
    return (
        landmarks[20].y > landmarks[19].y and
        landmarks[16].y > landmarks[15].y and
        landmarks[12].y > landmarks[11].y and
        landmarks[4].y > landmarks[20].y and
        landmarks[4].y > landmarks[16].y and
        landmarks[4].y > landmarks[12].y
    )

def is_fav(landmarks):
    return (
        landmarks[20].y < landmarks[19].y and
        landmarks[19].y < landmarks[17].y and
        landmarks[4].y < landmarks[16].y and
        landmarks[4].y < landmarks[12].y and
        landmarks[4].y < landmarks[8].y and
        landmarks[16].y > landmarks[13].y and
        landmarks[12].y > landmarks[9].y and
        landmarks[8].y > landmarks[5].y
    )

def recognize_gesture(landmarks):
    if is_volume_up(landmarks):
        return 'Volume Up'
    elif is_volume_down(landmarks):
        return 'Volume Down'
    elif is_power_on_off(landmarks):
        return 'Power On/Off'
    elif is_fav(landmarks):
        return 'Fav'
    return None
