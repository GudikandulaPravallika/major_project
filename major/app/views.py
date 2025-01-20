from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import SocialMediaAccountForm, WhatsAppChatForm
from .models import SocialMediaAccount
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pdfkit
import os
import time

def index(request):
    if request.method == 'POST':
        form = SocialMediaAccountForm(request.POST)
        if form.is_valid():
            account = form.save()
            parse_social_media(account)
            return redirect('success')
    else:
        form = SocialMediaAccountForm()
    return render(request, 'parser/index.html', {'form': form})

def whatsapp_chat(request):
    if request.method == 'POST':
        form = WhatsAppChatForm(request.POST)
        if form.is_valid():
            group_name = form.cleaned_data['group_name']
            time_from = form.cleaned_data['time_from']
            time_to = form.cleaned_data['time_to']
            messages = parse_whatsapp_chat(group_name, time_from, time_to)
            return render(request, 'parser/chat_results.html', {'messages': messages})
    else:
        form = WhatsAppChatForm()
    return render(request, 'parser/whatsapp_chat.html', {'form': form})

def parse_social_media(account):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    if account.platform == 'Instagram':
        parse_instagram(driver, account.username, account.password)
    elif account.platform == 'Facebook':
        parse_facebook(driver, account.username, account.password)
    elif account.platform == 'Twitter':
        parse_twitter(driver, account.username, account.password)
    driver.quit()

def parse_instagram(driver, username, password):
    driver.get('https://www.instagram.com/accounts/login/')
    time.sleep(2)
    driver.find_element(By.NAME, 'username').send_keys(username)
    driver.find_element(By.NAME, 'password').send_keys(password)
    driver.find_element(By.XPATH, '//button[@type="submit"]').click()
    time.sleep(5)
    driver.save_screenshot(os.path.join('media', 'instagram_screenshot.png'))

def parse_facebook(driver, username, password):
    driver.get('https://www.facebook.com/')
    time.sleep(2)
    driver.find_element(By.ID, 'email').send_keys(username)
    driver.find_element(By.ID, 'pass').send_keys(password)
    driver.find_element(By.NAME, 'login').click()
    time.sleep(5)
    driver.save_screenshot(os.path.join('media', 'facebook_screenshot.png'))

def parse_twitter(driver, username, password):
    driver.get('https://twitter.com/login')
    time.sleep(2)
    driver.find_element(By.NAME, 'session[username_or_email]').send_keys(username)
    driver.find_element(By.NAME, 'session[password]').send_keys(password)
    driver.find_element(By.XPATH, '//div[@role="button"]').click()
    time.sleep(5)
    driver.save_screenshot(os.path.join('media', 'twitter_screenshot.png'))

def parse_whatsapp_chat(group_name, time_from, time_to):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get('https://web.whatsapp.com/')
    print("Scan the QR code with your WhatsApp app...")
    time.sleep(15)  # Time to scan QR code
    search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
    search_box.send_keys(group_name)
    time.sleep(2)
    group = driver.find_element(By.XPATH, f"//span[@title='{group_name}']")
    group.click()
    time.sleep(2)
    messages = []
    # Extract messages within the specified time range
    # This is a simplified example and may need adjustments
    message_elements = driver.find_elements(By.XPATH, '//div[@class="_22Msk"]')
    for message_element in message_elements:
        message_text = message_element.text
        messages.append(message_text)
    driver.quit()
    return messages

def success(request):
    return render(request, 'parser/success.html')

def download_pdf(request):
    html_content = """
    <html>
    <head>
        <title>Parsed Data</title>
    </head>
    <body>
        <h1>Parsed Data</h1>
        <img src="/media/instagram_screenshot.png" alt="Instagram Screenshot">
        <img src="/media/facebook_screenshot.png" alt="Facebook Screenshot">
        <img src="/media/twitter_screenshot.png" alt="Twitter Screenshot">
    </body>
    </html>
    """
    pdf = pdfkit.from_string(html_content, False)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="parsed_data.pdf"'
    return response