from django.contrib import admin
from django.urls import path
import views
urlpatterns = [
    #path('',)
    path('vision',views.sleep_check),
    
]