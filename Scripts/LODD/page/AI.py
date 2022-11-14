import numpy as np
import imutils
import time
import timeit
import dlib
import cv2
import matplotlib.pyplot as plt
from scipy.spatial import distance as dist
from imutils import face_utils
from threading import Thread
from threading import Timer
#from threading import Thread
#from threading import Timer
#from .check_cam_fps import check_fps

from PIL import Image

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

OPEN_EAR = 0 #For init_open_ear()
EAR_THRESH = 0 #Threashold value

def eye_aspect_ratio(eye) :
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

#캠 인식하고 5초 동안 눈 ear 값과 코 길이 측정
def init_open_ear(landmarks, both_ear, nose_length, face_length) :
    ear_list = []
    nose_list = []
    face_list = []
    print("눈과 코 인식을 시작합니다")
    for i in range(100) :
        face = landmarks.part(8).y - landmarks.part(27).y
        nose = landmarks.part(30).y - landmarks.part(27).y
        ear_list.append(both_ear)
        face_list.append(face)
        nose_list.append(nose)
    OPEN_EAR = 0
    CLOSE_EAR = 0
    ear_list.sort(reverse=True)
    face_list.sort(reverse=True)
    nose_list.sort(reverse=True)
    for i in range(10):
        OPEN_EAR += ear_list[i]
        face_length += face_list[i]
        nose_length += nose_list[i]
    for i in range(7):
        CLOSE_EAR += ear_list[99 - i]
    OPEN_EAR /= 10
    CLOSE_EAR /= 10
    face_length /= 10
    nose_length /= 10
    EAR_THRESH = (((OPEN_EAR - CLOSE_EAR) * 0.6) + CLOSE_EAR) #EAR_THRESH means 50% of the being opened eyes state
    print("OPEN_EAR : ", OPEN_EAR, "\nCLOSE_EAR : ", CLOSE_EAR, "\nEAR_THRESH : ", EAR_THRESH, "\nNOSE_LENGTH : ", nose_length, "\nFACE_LENGTH : ", face_length)


def init_message() :
    print("init_message")
    #alarm.sound_alarm("init_sound.mp3")

def light_removing(frame) :
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    L = lab[:,:,0]
    med_L = cv2.medianBlur(L,99) #median filter
    invert_L = cv2.bitwise_not(med_L) #invert lightness
    composed = cv2.addWeighted(gray, 0.75, invert_L, 0.25, 0)
    return L, composed

def get_head_angle_ratio(head_points, facial_landmarks, _frame):
    # 코의 가로선 표시
    nose_region1 = np.array([(facial_landmarks.part(head_points[0]).x, facial_landmarks.part(head_points[0]).y),
                             (facial_landmarks.part(head_points[1]).x, facial_landmarks.part(head_points[1]).y),
                             (facial_landmarks.part(head_points[2]).x, facial_landmarks.part(head_points[2]).y),
                             (facial_landmarks.part(head_points[3]).x, facial_landmarks.part(head_points[3]).y)],
                            np.int32)
    cv2.polylines(_frame, [nose_region1], True, (0, 255, 255), 1)

#####################################################################################################################
#1. Variables for checking EAR.
#2. Variables for detecting if user is asleep.
#3. When the alarm rings, measure the time eyes are being closed.
#4. When the alarm is rang, count the number of times it is rang, and prevent the alarm from ringing continuously.
#5. We should count the time eyes are being opened for data labeling.
#6. Variables for trained data generation and calculation fps.
#7. Detect face & eyes.
#8. Run the cam.
#9. Threads to run the functions in which determine the EAR_THRESH.

def vision(img, INIT_FLAG, nose_length, face_length, open, close, closed_flag, game_flag):
    #1.
    #9.
    """if init_flag < 10:
        th_open = Thread(target = init_open_ear, args=(landmarks, both_ear, nose_length, face_length))
        th_open.deamon = True
        th_open.start()"""

    #####################################################################################################################
    INIT_FLAG = int(INIT_FLAG)
    nose_length = int(nose_length)
    face_length = int(face_length)
    open = float(open)
    close = float(close)
    closed_flag = int(closed_flag)
    game_flag = int(game_flag)

    img0 = img.read()
    img_enc = np.frombuffer(img0 , np.uint8)
    frame = cv2.imdecode(img_enc, cv2.IMREAD_UNCHANGED)
    #frame = image
    frame = imutils.resize(frame, width = 400)
    
    L, gray = light_removing(frame)
    rects = detector(gray,0)
    
    #prev_time, fps = check_fps(prev_time)

    #checking fps. If you want to check fps, just uncomment below two lines.
    #prev_time, fps = check_fps(prev_time)
    #cv2.putText(frame, "fps : {:.2f}".format(fps), (10,130), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200,30,20), 2)

    for rect in rects:
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)

        both_ear = (leftEAR + rightEAR) * 500  #I multiplied by 1000 to enlarge the scope.

        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [leftEyeHull], -1, (0,255,0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0,255,0), 1)
        
        faces = detector(gray)


        for face in faces:
            landmarks = predictor(gray, face)
            get_head_angle_ratio([27, 28, 29, 30, 31, 32, 33, 34, 35], landmarks, frame)
        
        if INIT_FLAG <= 100:
            print("start thread")
            init_open_ear(landmarks, both_ear, nose_length, face_length)
            INIT_FLAG += 1
        else:
            print("EAR_THRESH : {}".format(EAR_THRESH))
            #face = landmarks.part(8).y - landmarks.part(27).y
            #nose = landmarks.part(30).y - landmarks.part(27).y
            #print(nose, face, face - nose)
            #if nose - nose_length > 3 and nose_length > 0:
            #    print("고개를 숙였습니다 : ") 
            print("both_ear : {}".format(both_ear))
            
            if both_ear < EAR_THRESH and closed_flag == 0:
                print("now close")

                close = time.time()
                closed_flag = 1
            if both_ear > EAR_THRESH and closed_flag == 1:
                print("now open")

                open = time.time()
                closed_flag = 0
            closed = open - close
            if closed >= 0.5 and game_flag == 0:
                game_flag = 1
                print("끝말잇기 게임이 실행됩니다")
                return [game_flag]
        
    return [INIT_FLAG, nose_length, face_length, open, close, closed_flag, game_flag]
