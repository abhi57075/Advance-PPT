import cv2
import os
import numpy as np
from cvzone.HandTrackingModule import HandDetector

width, height = 1280, 720
gestureThreshold = 300

folderPath = "PBL HANDSIGNS/"

cap = cv2.VideoCapture(0)
cap.set(3,width)
cap.set(4,height)

detectorHand = HandDetector(detectionCon=0.8, maxHands=1)

imgList = []
delay = 20
buttonPressed = False
counter = 0
drawMode = False
imgNumber = 1
delayCounter = 0
annotations = [[]]
annotationNumber = -1
annotationStart = False
hs,ws = 120, 213 # dimensions of the small frame which will be displayed on the slide screen

# pathImages = os.listdir(folderPath) By just writing this the images will not be displayed in a correct Order
pathImages = sorted(os.listdir(folderPath), key = len)
print(pathImages)

while 1:
    success,img = cap.read()
    img = cv2.flip(img,1)

    image_name = str(pathImages[imgNumber])
    print(image_name)
    pathFullImage = folderPath + image_name
    imgCurrent = cv2.imread(pathFullImage)
    imgCurrent = cv2.resize(imgCurrent, (width,height))

    hands,img = detectorHand.findHands(img)
    # print(hands) # hands will contain lmList, bbox, center, type

    cv2.line(img, (0,gestureThreshold),(width,gestureThreshold), (0,255,0), 10)

    






    if hands and buttonPressed is False:
        
        hand = hands[0]
        cx,cy = hand['center']
        lmList = hand['lmList']
        fingers = detectorHand.fingersUp(hand)

        xVal = int(np.interp(lmList[8][0], [width//2, width],[0,width]))
        yVal = int(np.interp(lmList[8][1], [150, height-150],[0,height]))
        indexFinger = xVal,yVal

        if cy<=gestureThreshold : # If hand is at the height of the face
            
            if fingers == [0,1,0,0,1]: # Gesture 1
                print("Left")
                buttonPressed = True
                if imgNumber>0:
                    imgNumber-=1
                    annotations = [[]]
                    annotationNumber = -1
                    annotationStart = False
                
            if fingers == [0,0,0,0,0]: # Gesture 2
                print("Right")
                buttonPressed = True
                if imgNumber<len(pathImages)-1:
                    imgNumber+=1
                    annotations = [[]]
                    annotationNumber = -1
                    annotationStart = False
        
        if fingers == [0,1,1,0,0]: # Gesture 3
            cv2.circle(imgCurrent, indexFinger, 12, (255,0,0), -1)

        if fingers == [0,1,0,0,0]: # Gesture 4
            if annotationStart is False:
                annotationStart = True
                annotationNumber+=1
                annotations.append([])
            # print(annotationNumber)
            annotations[annotationNumber].append(indexFinger)
            cv2.circle(imgCurrent, indexFinger, 12, (0,0,255), -1)
        else:
            annotationStart = False
        
        if fingers == [0,1,1,1,0]: # Gesture 5
            if annotations:
                annotations.pop(-1)
                annotationNumber-=1
                buttonPressed = True
        
        if fingers == [1,0,0,0,0]:
            cv2.destroyAllWindows()
            break
    else:
        annotationStart == False
    
    if buttonPressed:
        counter+=1
        if counter > delay: 
            counter = 0
            buttonPressed = False
    
    for i in range(len(annotations)):
        for j in range(len(annotations[i])):
            if j!=0:
                cv2.line(imgCurrent, annotations[i][j-1], annotations[i][j] , (0,0,255), 7)





    imgSmall = cv2.resize(img, (ws,hs))
    h,w,c = imgCurrent.shape
    imgCurrent[0:hs, w-ws:w] = imgSmall

    cv2.imshow("SLIDES",imgCurrent)
    cv2.imshow("Image",img)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break