from django.shortcuts import render
from AI import vision
from tasks import add
# Create your views here.

#from rest_framework import generics
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import AllowAny
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_200_OK
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import parser_classes
from django.http import JsonResponse

import base64


@api_view(['POST'])
@permission_classes([AllowAny,])
def sleep_check(request):
    if request.method == 'POST':
        if "image" in request.data:
            img = vision()#(request.data["image"])
            message = {"data" : img, "state" : "success"}
            return JsonResponse(message, status = HTTP_200_OK)
        else:
            message = {"message" : "Data does not include image", "State" : "fail"}
            return JsonResponse(message, status = HTTP_400_BAD_REQUEST)
