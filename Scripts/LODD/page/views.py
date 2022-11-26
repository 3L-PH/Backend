from django.shortcuts import render
from .AI import vision
# Create your views here.

#from rest_framework import generics
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import AllowAny
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_200_OK
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import parser_classes
from django.http import JsonResponse

import os, random
from .voice import speak, recognition
from . import last_word
import numpy as np
import winsound as sd

def beepsound():
    fr = 2000    # range : 37 ~ 32767
    du = 1000     # 1000 ms ==1second
    sd.Beep(fr, du) # winsound.Beep(frequency, duration)

def game_start():
    dir = os.getcwd() + "/mp3/"
    os.mkdir(dir)

    start_word = np.load('word.npy')

    speak('끝말잇기 시작합니다', dir)    
    start = start_word[random.randrange(0, len(start_word))]
    speak(start, dir)

    result = last_word.game_play(dir)
    if result == 'exit':
        speak('게임을 종료합니다', dir)
    elif result == 'win_com':
        beepsound()
        speak('컴퓨터의 승리', dir)
    elif result == 'win_com':
        speak('당신의 승리', dir)
    elif result == 'win_user_black':
        speak('치사하지만 당신의 승리', dir)

    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))
    os.rmdir(dir)
    
@api_view(['POST'])
@permission_classes([AllowAny,])
def sleep_check(request):
    if request.method == 'POST':
        try:
            img = request.data["img"]
            INIT_FLAG = request.data["INIT_FLAG"]
            nose_length = request.data["nose_length"]
            face_length = request.data["face_length"]
            open = request.data["open"]
            close = request.data["close"]
            closed_flag = request.data["closed_flag"]
            game_flag = request.data["game_flag"]
        except:
            message = {"message" : "Not Enough data", "State" : "fail"}
            return JsonResponse(message, status = HTTP_400_BAD_REQUEST)
        result = vision(img, INIT_FLAG, nose_length, face_length, open, close, closed_flag, game_flag)
        print(result)
        if result[-1] == 1:
            message = {"data":"game start", "status":"success"}
                # 여기서 게임 시작하면 될듯
        else:
            message = {"data" : result, "state" : "success"}
        return JsonResponse(message, status = HTTP_200_OK)