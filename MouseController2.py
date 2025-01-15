import ctypes
import cv2
import numpy as np
import HandTrackingModule as htm
import time
from pymouse import PyMouse
from pykeyboard import PyKeyboard

class MouseController:
    """
    A class to control the mouse using hand gestures.
    """
    def __init__(self, smoothening=7):
        self.smoothening = smoothening
        self.plocX, self.plocY = 0, 0  # Previous location
        self.clocX, self.clocY = 0, 0  # Current location
        self.dragging = False
        self.mouse = PyMouse()
        self.keyboard = PyKeyboard()

    def start_drag(self):
        """
        Starts a drag action by pressing the left mouse button.
        """
        self.mouse.press(self.clocX, self.clocY, 1)

    def stop_drag(self):
        """
        Stops a drag action by releasing the left mouse button.
        """
        self.mouse.release(self.clocX, self.clocY, 1)

    def move(self, img, x1, y1, frameR, wCam, hCam, wScr, hScr):
        """
        Moves the mouse cursor on the screen based on hand movements.
        
        Parameters:
        img (ndarray): Image frame.
        x1 (int): X-coordinate of the fingertip.
        y1 (int): Y-coordinate of the fingertip.
        frameR (int): Frame reduction.
        wCam (int): Width of the camera frame.
        hCam (int): Height of the camera frame.
        wScr (int): Width of the screen.
        hScr (int): Height of the screen. 
        """
        x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
        y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
        self.clocX = self.plocX + (x3 - self.plocX) / self.smoothening
        self.clocY = self.plocY + (y3 - self.plocY) / self.smoothening
        
        try:
            self.mouse.move(int(self.clocX), int(self.clocY))
        except Exception as e:
            print(f"Error setting cursor position ({x1}, {y1}), ({self.clocX}, {self.clocY}): {e}")
            
        self.plocX, self.plocY = self.clocX, self.clocY   
        cv2.circle(img, (x1, y1), 15, (0, 255, 0), cv2.FILLED)

    def left_click(self, img, x, y, frameR, wCam, hCam, wScr, hScr):
        """
        Simulates a left mouse click.
        
        Parameters:
        img (ndarray): Image frame.
        x (int): X-coordinate of the fingertip.
        y (int): Y-coordinate of the fingertip.
        """
        print(x,y,90)
        x3 = np.interp(x, (frameR, wCam - frameR), (0, wScr))
        y3 = np.interp(y, (frameR, hCam - frameR), (0, hScr))
        self.clocX = self.plocX + (x3 - self.plocX) / self.smoothening
        self.clocY = self.plocY + (y3 - self.plocY) / self.smoothening
        
        cv2.circle(img, (x, y), 15, (0, 255, 0), cv2.FILLED)
        
        self.mouse.click(1)
        

    def right_click(self, img, detector, finger1=8, finger2=12):
        """
        Simulates a right mouse click.
        
        Parameters:
        img (ndarray): Image frame.
        detector (object): Hand detector object.
        finger1 (int): Index of the first finger.
        finger2 (int): Index of the second finger.
        """
        length, img, lineInfo = detector.findDistance(finger1, finger2, img)
        if length < 30:
            cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
            self.mouse.click(2)

    def drag(self, img, detector, x1, y1, frameR, wCam, hCam, wScr, hScr, finger1=4, finger2=12, finger3=16):
        """
        Simulates a drag action by holding the left mouse button down and moving the cursor.
        
        Parameters:
        img (ndarray): Image frame.
        detector (object): Hand detector object.
        x1 (int): X-coordinate of the fingertip.
        y1 (int): Y-coordinate of the fingertip.
        frameR (int): Frame reduction.
        wCam (int): Width of the camera frame.
        hCam (int): Height of the camera frame.
        wScr (int): Width of the screen.
        hScr (int): Height of the screen.
        finger1 (int): Index of the first finger.
        finger2 (int): Index of the second finger.
        finger3 (int): Index of the third finger.
        """
        length1, img, lineInfo1 = detector.findDistance(finger1, finger2, img)
        length2, img, lineInfo2 = detector.findDistance(finger1, finger3, img)
        if length1 < 30 and length2 < 30:
            if not self.dragging:
                self.start_drag()
                self.dragging = True

            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
            self.clocX = self.plocX + (x3 - self.plocX) / self.smoothening
            self.clocY = self.plocY + (y3 - self.plocY) / self.smoothening
            self.mouse.move(int(self.clocX), int(self.clocY))
            self.plocX, self.plocY = self.clocX, self.clocY
            cv2.circle(img, (lineInfo1[4], lineInfo1[5]), 15, (0, 255, 0), cv2.FILLED)
            cv2.circle(img, (lineInfo2[4], lineInfo2[5]), 15, (0, 255, 0), cv2.FILLED)
        else:
            if self.dragging:
                self.stop_drag()
            self.dragging = False

    def scroll(self, img, detector, y1, frameR, hCam, hScr, finger1=8, finger2=12, finger3=16):
        """
        Simulates a scroll action.
        
        Parameters:
        img (ndarray): Image frame.
        detector (object): Hand detector object.
        y1 (int): Y-coordinate of the fingertip.
        frameR (int): Frame reduction.
        hCam (int): Height of the camera frame.
        hScr (int): Height of the screen.
        finger1 (int): Index of the first finger.
        finger2 (int): Index of the second finger.
        finger3 (int): Index of the third finger.
        
        """
        length1, img, lineInfo1 = detector.findDistance(finger1, finger2, img)
        length2, img, lineInfo2 = detector.findDistance(finger2, finger3, img)

        if length1 < 30 and length2 < 30:
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
            scrollY = int(np.clip((y3 - self.plocY) / 5, -3, 3))  # Adjust the divisor and clip values as needed

            if scrollY != 0:  # Only scroll if there's a noticeable movement
                self.mouse.scroll(vertical=scrollY)
            
            cv2.circle(img, (lineInfo1[4], lineInfo1[5]), 15, (0, 255, 0), cv2.FILLED)
            cv2.circle(img, (lineInfo2[4], lineInfo2[5]), 15, (0, 255, 0), cv2.FILLED)

def get_screen_resolution():
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

def main():
    """
    The main function to run the hand tracking and mouse control.
    """
    frameR = 100  # Frame reduction for gesture detection area
    smoothening = 6  # Smoothening factor for cursor movement

    pTime = 0  # Previous time for FPS calculation

    cap = cv2.VideoCapture(0)
    detector = htm.handDetector(maxHands=1)
    wScr, hScr = get_screen_resolution()

    # Configuration for finger gestures
    fingerConfig = {
        "allUp": [1, 1, 1, 1, 1],
        "allDown": [0, 0, 0, 0, 0],
        "move": [0, 1, 0, 0, 0],
        "leftClick":  [0, 1, 0, 0, 0],   #this config is for half - folded fingers
        "rightClick":  [0, 1, 1, 0, 0],
        "drag": [0, 1, 0, 0, 1],
        "scroll": [0, 1, 1, 1, 0]
    }

    mouse_controller = MouseController(smoothening)

    while True:
        success, img = cap.read()
        hCam, wCam, _ = img.shape
        img = cv2.flip(img, 1)
        img = detector.findHands(img)
        lmList, bbox = detector.findPosition(img)
        
        handInCorrectOrientation = False

        if lmList:
            x1, y1, z1 = lmList[8][1:]
            handInCorrectOrientation = not (detector.is_hand_turned() or detector.is_hand_flipped())

        fingers = detector.fingersUp()
        foldedFingers = detector.fingersHalfClosed()
        
        if fingers and -z1 > 0.03 and handInCorrectOrientation:
            cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)

            if fingers == fingerConfig["move"] and not foldedFingers[1]:
                mouse_controller.move(img, x1, y1, frameR, wCam, hCam, wScr, hScr)

            elif  foldedFingers == fingerConfig["leftClick"]:
                # print(x1,y1)
                mouse_controller.left_click(img, x1, y1, frameR, wCam, hCam, wScr, hScr)

            elif fingers == fingerConfig["rightClick"]:
                mouse_controller.right_click(img, detector)

            elif fingers == fingerConfig["drag"]:
                thumbTip = lmList[4][1:]
                mouse_controller.drag(img, detector, thumbTip[0], thumbTip[1], frameR, wCam, hCam, wScr, hScr)

            elif fingers == fingerConfig["scroll"]:
                middle_finger_tip_Y = lmList[12][2]
                mouse_controller.scroll(img, detector, middle_finger_tip_Y, frameR, hCam, hScr)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f"FPS: {int(fps)}", (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 2)

        cv2.imshow("Image", img)
                
        cvWait = cv2.waitKey(1)
        if cvWait & 0xFF == ord('q') or cvWait == 27 :
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
