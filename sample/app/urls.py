from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('login/', views.login_view, name='login'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('signup/', views.signup_view, name='signup'),
    path('home/', views.home, name='home'),
    path('web_scrapping/', views.web_scrapping,name="web_scrapping"),
    path("fetch-whatsapp/", views.fetch_whatsapp_data_view, name="fetch_whatsapp"), 
    path("fetch-result/",views.fetch_result,name="fetch_result"),
    
]
