import cv2
import mediapipe as mp
import time
import math
# import numpy as np

class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=self.mode, 
                                        max_num_hands=self.maxHands,
                                        min_detection_confidence=self.detectionCon, 
                                        min_tracking_confidence=self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)

        return img

    def findPosition(self, img, handNo=0, draw=True):
        xList = []
        yList = []
        # zList = []
        bbox = []
        self.lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy, cz = int(lm.x * w), int(lm.y * h), lm.z
                xList.append(cx)
                yList.append(cy)
                # zList.append(cz)
                self.lmList.append([id, cx, cy, cz])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            bbox = xmin, ymin, xmax, ymax

            if draw:
                cv2.rectangle(img, (xmin - 20, ymin - 20), (xmax + 20, ymax + 20),
                              (0, 255, 0), 2)

        return self.lmList, bbox

    def fingersUp(self):
        fingers = []
        # Thumb
        if len(self.lmList) == 0:
            return []
        # print(self.lmList[self.tipIds[0]])
        
        handType = self.results.multi_handedness[0].classification[0].label
        
        if self.lmList[self.tipIds[0]][1]  > self.lmList[self.tipIds[0] - 1][1] and handType == 'Left':
            fingers.append(1)

        elif self.lmList[self.tipIds[0]][1]  < self.lmList[self.tipIds[0] - 1][1] and handType == 'Right':
            fingers.append(1)
            
        else:
            fingers.append(0)

        # Fingers
        for id in range(1, 5):
            if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers
    
    def fingersHalfClosed(self):
        fingers = []
        if len(self.lmList) == 0:
            return []

        handType = self.results.multi_handedness[0].classification[0].label

        # Thumb
        if self.lmList[self.tipIds[0]][1] < self.lmList[self.tipIds[0] - 1][1] and \
            self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0] - 2][1] and handType == 'Left':
                
            fingers.append(1)
        elif self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0] - 1][1] and \
            self.lmList[self.tipIds[0]][1] < self.lmList[self.tipIds[0] - 2][1] and handType == 'Right':
            fingers.append(1)
        else:
            fingers.append(0)

        # Fingers
        for id in range(1, 5):
            tipY = self.lmList[self.tipIds[id]][2]
            dipY = self.lmList[self.tipIds[id] - 3][2]
            pipY = self.lmList[self.tipIds[id] - 1][2]

            # Check if the fingertip is roughly in the middle position between DIP and PIP
            if (dipY <= tipY <= pipY) or (pipY <= tipY <= dipY):
            # if tipY - pipY <= 0 :
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers
    
    def is_hand_flipped(self):
        # Assuming a right hand, check if the palm is facing up or down
        # Compare the Z coordinates of the middle finger tip and wrist
        landmarks = self.results.multi_hand_landmarks[0].landmark
        wrist = landmarks[0]
        middle_finger_tip = landmarks[12]

        if middle_finger_tip.y > wrist.y:
            return True  # Palm up
        else:
            return False  # Palm down
        
    def is_hand_turned(self):
        
        landmarks = self.results.multi_hand_landmarks[0].landmark
        
        index_bottom = landmarks[5]
        pinky_bottom = landmarks[17]
        
        
        # flipped = self.is_hand_flipped()
        turned = False
        
        handType = self.results.multi_handedness[0].classification[0].label
        
        # print(f"index: {index_bottom}")
        # print(f"pinky: {pinky_bottom}")
        # print(f"Hand: {handType}")
        # print(f"Condition 1: {(index_bottom.x > pinky_bottom.x) and handType == 'Right'}")
        # print(f"Condition 2: {(index_bottom.x < pinky_bottom.x) and handType == 'Left'}")
        
        if (index_bottom.x > pinky_bottom.x) and handType == 'Right':
            turned = True
            
        elif (index_bottom.x < pinky_bottom.x) and handType == 'Left':
            turned = True
            
        # print(turned, flipped, turned ^ flipped)
        
        # return turned ^ flipped
        return turned 

    def findDistance(self, p1, p2, img, draw=True, r=10, t=3):
        x1, y1, z1 = self.lmList[p1][1:]
        x2, y2, z2 = self.lmList[p2][1:]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
            cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)
        length = math.hypot(x2 - x1, y2 - y1)

        return length, img, [x1, y1, x2, y2, cx, cy]


def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector()
    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        img = detector.findHands(img)
        lmList, bbox = detector.findPosition(img)
        detector.fingersUp()
        if len(lmList) != 0:
            print(lmList[4])

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)

        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xff == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
