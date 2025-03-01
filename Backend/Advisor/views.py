from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import ScraperModels
from . import Analyser

import time
import random

Current_URL = ""


# @csrf_exempt # For GET this is not needed
@api_view(['GET'])
def ApiHome(request):

    print("Received data:", request.GET.get("URL"))
    # Run the code
    url = Current_URL # The GET method will not pass URL, just a hello message

    # res = Analyser.Validation(ScraperModels.GetInstaPost(url)) # xd xd
    res = url
    time.sleep(3)

    print("Data sent: ", res_temp)
    
    return Response(res_temp)

@api_view(["POST"])
@csrf_exempt
def input(request):
    if request.method == 'POST':
        Current_URL = request.data['request']['URL']
        print("Received URL:", Current_URL)
        return Response({"message": "Data received", "data": request.data})
    else:
        return Response({"message": "This page only supports POST"})
