import cv2
import mediapipe as mp
import time
from pynput.mouse import Button, Controller
import numpy as np

mouse = Controller()

# Function to move mouse to a position smoothly
def move_mouse_smoothly(target_x, target_y, duration=0.01):
    start_x, start_y = mouse.position
    steps = 50  # Number of steps to divide the movement
    dx = (target_x - start_x) / steps
    dy = (target_y - start_y) / steps
    delay = duration / steps

    for _ in range(steps):
        mouse.move(dx, dy)
        time.sleep(delay)

def click_mouse(button=Button.left):
    mouse.click(button)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=2)
mpDraw = mp.solutions.drawing_utils

pTime = 0
cTime = 0

def get_palm_center(hand_landmarks):
    # Select key landmarks on the palm: wrist, index MCP, pinky MCP, middle PIP
    palm_landmarks = [
        hand_landmarks.landmark[mpHands.HandLandmark.WRIST],
        hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_MCP],
        hand_landmarks.landmark[mpHands.HandLandmark.PINKY_MCP],
        hand_landmarks.landmark[mpHands.HandLandmark.MIDDLE_FINGER_PIP]
    ]
    
    cx = int(np.mean([lm.x for lm in palm_landmarks]) * w)
    cy = int(np.mean([lm.y for lm in palm_landmarks]) * h)
    return cx, cy

def is_fist(hand_landmarks):
    # A simple fist detection by checking the distance between the tip and the MCP of each finger
    fist = True
    for finger_tip, finger_mcp in [
        (mpHands.HandLandmark.THUMB_TIP, mpHands.HandLandmark.THUMB_MCP),
        (mpHands.HandLandmark.INDEX_FINGER_TIP, mpHands.HandLandmark.INDEX_FINGER_MCP),
        (mpHands.HandLandmark.MIDDLE_FINGER_TIP, mpHands.HandLandmark.MIDDLE_FINGER_MCP),
        (mpHands.HandLandmark.RING_FINGER_TIP, mpHands.HandLandmark.RING_FINGER_MCP),
        (mpHands.HandLandmark.PINKY_TIP, mpHands.HandLandmark.PINKY_MCP)
    ]:
        dist = np.linalg.norm([
            hand_landmarks.landmark[finger_tip].x - hand_landmarks.landmark[finger_mcp].x,
            hand_landmarks.landmark[finger_tip].y - hand_landmarks.landmark[finger_mcp].y
        ])
        if dist > 0.1:  # Adjust this threshold as needed
            fist = False
            break
    return fist

while True:
    success, frame = cap.read()
    if not success:
        break

    frameFlipped = cv2.flip(frame, 1)
    frameRGB = cv2.cvtColor(frameFlipped, cv2.COLOR_BGR2RGB)
    h, w, _ = frameFlipped.shape
    results = hands.process(frameRGB)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            cx, cy = get_palm_center(handLms)
            move_mouse_smoothly(cx, cy)

            if is_fist(handLms):
                click_mouse(Button.left)

            mpDraw.draw_landmarks(frameFlipped, handLms, mpHands.HAND_CONNECTIONS)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(frameFlipped, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_COMPLEX, 3, (225, 0, 225), 3)
    cv2.imshow("Image", frameFlipped)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
