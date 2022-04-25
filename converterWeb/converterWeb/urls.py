"""converterWeb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from converter.views import index
from converter.views import audio_converter
from converter.views import audio_convert
from converter.views import video_converter
from converter.views import video_convert

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    path('audioConverter/', audio_converter),
    path('audioConverter/convert', audio_convert),
    path('videoConverter/', video_converter),
    path('videoConverter/convert', video_convert)
]
