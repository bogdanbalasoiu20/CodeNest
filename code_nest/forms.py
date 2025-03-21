from django import forms
from django.contrib.auth.forms import AuthenticationForm


class CustomAuthenticationForm(AuthenticationForm):
    stay_logged=forms.BooleanField(required=False,initial=False,label="Stay logged in")
    
    def clean(self):
        cleaned_data=super().clean()
        stay_logged=self.cleaned_data.get('stay_logged')
        return cleaned_data