import cv2
import numpy as np
import HandTrackingModule as htm
import time
import pyautogui
from pynput.mouse import Button, Controller

mouse = Controller()
pyautogui.FAILSAFE = False

def start_drag():
    mouse.press(Button.left)

def stop_drag():
    mouse.release(Button.left)

wCam, hCam = 640, 480
frameR = 100  # Frame Reduction
smoothening = 7

pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
detector = htm.handDetector(maxHands=1)
wScr, hScr = pyautogui.size()


fingerConfig = {
    "allUp": [1, 1, 1, 1, 1],
    "allDown": [0, 0, 0, 0, 0],
    "move": [0, 1, 0, 0, 0],
    "rightClick": [1, 1, 1, 1],
    "leftClick": [0, 1, 1, 0, 0],
    "drag": [1, 0, 0, 0, 0],
    "scroll": [0, 1, 1, 1, 0]  # Assuming this configuration for scroll gesture
}

dragging = False
# previous_z = 0

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)
    # print(img.shape, wScr, hScr)
    
    if len(lmList) != 0:
        x1, y1, z1 = lmList[8][1:]
        x2, y2, z2 = lmList[4][1:]

    fingers = detector.fingersUp() 
    # f2 = detector.fingersHalfClosed()
    # print(f2)
    if len(fingers) != 0:
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
                      (255, 0, 255), 2)
        
        if not fingers == fingerConfig["allUp"]:  # If all fingers are up, do not move the mouse
            if fingers == fingerConfig["move"]:
                x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
                clocX = plocX + (x3 - plocX) / smoothening
                clocY = plocY + (y3 - plocY) / smoothening
                mouse.position = (clocX, clocY)
                cv2.circle(img, (x1, y1), 15, (0, 255, 0), cv2.FILLED)
                plocX, plocY = clocX, clocY
            
        # Left click when index finger moves significantly in the Z-axis
        # if abs(z1 - previous_z) > 0.015:  # Threshold value for Z-axis movement
        # if fingers[0] == 1 and fingers[2:] == [0,0,0] and f2[1] == 1:
        if fingers == fingerConfig["leftClick"]:
            cv2.circle(img, (x1, y1), 15, (0, 255, 0), cv2.FILLED)
            # print("Left Click")
            pyautogui.click(duration=0.17)
        
        # previous_z = z1

        if fingers[1:] == fingerConfig["rightClick"]:
            length, img, lineInfo = detector.findDistance(4, 17, img)
            if length < 30:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                pyautogui.rightClick(duration=0.1)
        
        if fingers == fingerConfig["drag"] :
            if not dragging:
                start_drag()
                dragging = True
            
            x4 = np.interp(x2, (frameR, wCam - frameR), (0, wScr))
            y4 = np.interp(y2, (frameR, hCam - frameR), (0, hScr))
            clocX = plocX + (x4 - plocX) / smoothening
            clocY = plocY + (y4 - plocY) / smoothening
            mouse.position = (clocX, clocY)
            cv2.circle(img, (x2, y2), 15, (0, 255, 0), cv2.FILLED)
            plocX, plocY = clocX, clocY
        else:
            if dragging:
                stop_drag()
                dragging = False

        if fingers == fingerConfig["scroll"]:
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
            clocY = plocY + (y3 - plocY) / smoothening
            scrollY = int((clocY - plocY) / 50)  # Adjust divisor to reduce scroll amount
            
            if scrollY != 0:  # Only scroll if there's a noticeable movement
                mouse.scroll(0, scrollY)
        
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                (255, 0, 0), 3)
    
    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xff == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()
