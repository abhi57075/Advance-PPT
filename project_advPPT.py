import cv2
import os
from cvzone.HandTrackingModule import HandDetector
import numpy as np

# Variables
width, height = 1280, 720 # Frame dimensions
folderPath = "Untitled design"

# Camera Setup
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# Get the list of presentation images
pathImages = sorted(os.listdir(folderPath), key = len)
# print(pathImages)
# We did the sorting because if we have 11 images numbered frim 1 to 11 then
# if we print these images we will get 1, 11, 2, 3 ,.....

# Variables
imgNumber = 0
hs, ws = int(120*1.2), int(213*1.2) # dimension of the small frame which will be there on the image/slide
gestureThreshold = 300 # the line above which our actions will be reognized by the computer

buttonPressed = False
buttonCounter = 0
buttonDelay = 30

annotations = [[]]
annotationNumber = 0 # Index
annotationStart = False

# Hand Detector
detector = HandDetector(detectionCon=0.8, maxHands = 1)

while 1:
    # Import images
    success, img = cap.read()
    img = cv2.flip(img,1) # 1 is for horizontal, 0 is for vertical

    pathFullImage = os.path.join(folderPath,pathImages[imgNumber])
    imgCurrent = cv2.imread(pathFullImage)

    hands, img = detector.findHands(img)

    # We are not writing flip type = False bcoz if we do so our thumb status (if is folded or not) will not be detected
    cv2.line(img, (0,gestureThreshold), (width, gestureThreshold), (0,255,0), thickness = 10)


    if hands and buttonPressed is False:
        hand = hands[0] # since max number of hands is 1 for the program
        # Now we need to check how many fingers are up
        fingers = detector.fingersUp(hand)
        cx,cy = hand['center'] # center x and center y ->{hand center}
        # print(fingers)
        lmlist = hand['lmList'] # lmList stands for landmark list, there are 21 landmarks and this will give us the list of the position of all those landmarks

        # Constraint values for easier drawing {only first finger}
        xVal = int(np.interp(lmlist[8][0], [width//2,width], [0,width]))
        yVal = int(np.interp(lmlist[8][1], [150, height-150], [0,height]))

        indexFinger = xVal, yVal # first finger

        if cy <= gestureThreshold: # if hand is at the height of the face
            annotationStart = False

            # Gesture 1 -> Left
            if fingers == [1,0,0,0,0]:
                annotationStart = False
                #print("Left")
                if imgNumber > 0:
                    buttonPressed = True
                    # to reset the drawings on the ppt
                    annotations = [[]]
                    annotationNumber = 0 
                    imgNumber-=1
            
            # Gesture 2 -> Right
            if fingers == [0,0,0,0,1]:
                annotationStart = False
                #print("Right")
                if imgNumber < len(pathImages)-1:
                    buttonPressed = True
                    annotations = [[]]
                    annotationNumber = 0 
                    imgNumber+=1
            
        # Gesture 3 -> Show Pointer
        if fingers == [0,1,1,0,0]:    
            cv2.circle(imgCurrent, indexFinger, 12, (0,0,255), cv2.FILLED)
            # now to go at the leftmost point in the ppt we dont want to take the hand till there, it will be weird
            # So we will be setting limits
            annotationStart = False

        # Gesture 4 -> Draw Pointer
        if fingers == [0,1,0,0,0]:
            if annotationStart is False:
                annotationStart = True
                annotationNumber += 1
                annotations.append([])
            cv2.circle(imgCurrent, indexFinger, 12, (0,0,255), cv2.FILLED)
            annotations[annotationNumber].append(indexFinger)
        else:
            annotationStart = False
        
        # Gesture 5 -> Erase
        if fingers == [0,1,1,1,0]:
            if annotations: #  means it is not an empty list
                if annotationNumber >= 0 :
                    annotations.pop(-1)
                    annotationNumber -= 1
                    buttonPressed = True
    
    else:
        annotationStart = False
       
    # ButtonPressed Iterations
    if buttonPressed:
        buttonCounter+=1
        if buttonCounter > buttonDelay:
            buttonCounter = 0
            buttonPressed = False
    
    for i in range(len(annotations)):
        for j in range(len(annotations[i])):
            if j!=0:
                cv2.line(imgCurrent, annotations[i][j-1], annotations[i][j] , (0,0,255), thickness = 12)
           

    # Adding Web cam image on the slides
    imgSmall = cv2.resize(img, (ws,hs))
    h,w,c = imgCurrent.shape
    imgCurrent[0:hs,w-ws:w] = imgSmall # imgCurrent is now the matrix

    cv2.imshow("Image",img)
    cv2.imshow("Slides",imgCurrent)
    
    key = cv2.waitKey(1)
    if key == ord('q'):
        break