from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('whatsapp-chat/', views.whatsapp_chat, name='whatsapp_chat'),
    path('success/', views.success, name='success'),
    path('download-pdf/', views.download_pdf, name='download_pdf'),
]