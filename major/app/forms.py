from django import forms
from .models import SocialMediaAccount

class SocialMediaAccountForm(forms.ModelForm):
    class Meta:
        model = SocialMediaAccount
        fields = ['username', 'password', 'platform']

class WhatsAppChatForm(forms.Form):
    group_name = forms.CharField(label='Group Name', max_length=255)
    time_from = forms.DateTimeField(label='Time From')
    time_to = forms.DateTimeField(label='Time To')