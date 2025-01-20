# views.py

from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from .models import CustomUser
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.urls import reverse  # Import reverse for URL generation
import random
from django.contrib.auth.decorators import login_required



# Temporary OTP storage
otp_storage = {}

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Corrected redirect URL
        else:
            return render(request, 'signup.html', {'form': form, 'errors': form.errors})
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Generate OTP
            otp = random.randint(100000, 999999)
            otp_storage[user.username] = otp

            # Send OTP via email
            send_mail(
                "Your Login OTP",
                f"Your OTP for login is {otp}.",
                "noreply@example.com",  # Change to your email
                [user.email],
                fail_silently=False,
            )
            request.session['username'] = username
            return redirect('verify_otp')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "login.html")

def verify_otp_view(request):
    if request.method == "POST":
        username = request.session.get('username')
        entered_otp = request.POST.get("otp")

        if username in otp_storage and otp_storage[username] == int(entered_otp):
            user = CustomUser.objects.get(username=username)
            login(request, user)
            del otp_storage[username]  # Clear OTP after successful login
            return redirect('home')
        else:
            messages.error(request, "Invalid OTP")
    return render(request, "verify_otp.html")
@login_required
def home(request):
    return render(request, "home.html")

def index(request):
    return render(request, "index.html")

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = CustomUser.objects.get(email=email)
            # Generate password reset token and URL
            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = request.build_absolute_uri(
                reverse('reset_password', kwargs={'uidb64': uidb64, 'token': token})
            )

            # Send email with reset link
            subject = "Password Reset Request"
            message = render_to_string("password_reset_email.html", {
                "user": user,
                "reset_link": reset_link,
            })
            send_mail(subject, message, "your-email@example.com", [email])

            messages.success(request, "A password reset link has been sent to your email.")
            return redirect("forgot_password")
        except CustomUser.DoesNotExist:
            messages.error(request, "No user found with that email address.")
            return redirect("forgot_password")
    return render(request, "forgot_password.html")

def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (CustomUser.DoesNotExist, ValueError, TypeError, OverflowError):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Your password has been successfully reset.")
                return redirect("login")
            else:
                messages.error(request, "Passwords do not match. Please try again.")
        return render(request, "reset_password.html", {"uidb64": uidb64, "token": token})
    else:
        messages.error(request, "The reset link is invalid or has expired.")
        return redirect("forgot_password")




import os
import time
from django.shortcuts import render
from django.http import HttpResponse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
@login_required
def fetch_whatsapp_data_view(request):
    if request.method == "POST":
        # Get user input from the form
        chat_name = request.POST.get("chat_name")

        # Path to ChromeDriver
        chrome_driver_path = "C://Users//miriy//Projects//whatsapp_parser//chromedriver-win64//chromedriver.exe"
        service = Service(chrome_driver_path)

        # Initialize WebDriver
        driver = webdriver.Chrome(service=service)
        driver.get("https://web.whatsapp.com/")
        print("Please scan the QR code on WhatsApp Web.")
        input("After scanning the QR code, press Enter in the console.")

        try:
            # Search for a chat
            search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"]')
            search_box.send_keys(chat_name)
            search_box.send_keys(Keys.RETURN)

            time.sleep(3)  # Wait for the chat to load

            # Fetch messages
            messages = driver.find_elements(By.XPATH, '//span[contains(@class, "selectable-text")]')
            last_messages = messages[-10:]  # Fetch the last 10 messages

            # Create a PDF document
            pdf_filename = f"{chat_name}_messages.pdf"
            pdf_path = os.path.join("media", pdf_filename)
            c = canvas.Canvas(pdf_path, pagesize=letter)
            width, height = letter

            # Set starting position for text
            y_position = height - 40

            # Write messages to the PDF
            for msg in last_messages:
                message_text = msg.text
                formatted_message = f"{chat_name}: {message_text}  Date: {time.strftime('%Y-%m-%d')}"
                c.drawString(30, y_position, formatted_message)
                y_position -= 20  # Move down for the next message
                
                # Check if we need to create a new page
                if y_position < 40:
                    c.showPage()
                    y_position = height - 40

            c.save()
            driver.quit()

            # Render a template with a link to download/view the PDF
            return render(request, "fetch_result.html", {"pdf_url": f"/media/{pdf_filename}"})

        except Exception as e:
            driver.quit()
            return HttpResponse(f"Error: {e}")

    # Render the form if the request method is GET
    return render(request, "fetch_form.html")
@login_required
def web_scrapping(request):
    return render(request,"web_scrapping.html")

def fetch_result(request):
    return render(request,"fetch_result.html")