from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.core.exceptions import ValidationError
import re
import uuid

                                # FORMULAR PENTRU LOGIN
class CustomAuthenticationForm(AuthenticationForm):
    stay_logged=forms.BooleanField(required=False,initial=False,label="Stay logged in")
    
    
    def confirm_login_allowed(self, user):  #login only with email confirmed
        if not user.email_confirm:
            raise forms.ValidationError(
                "You must confirm your email before logging in.",
                code='email_not_confirmed'
            )
    


                                # FORMULAR PENTRU REGISTER

class Register(UserCreationForm):
    age = forms.IntegerField(required=True)

    class Meta:
        model = CustomUser
        fields = (
            'username', 'first_name', 'last_name', 'email', 
            'password1', 'password2', 'age'
        )

    # Validation for username
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[a-zA-Z0-9](?!.*\.\.)[a-zA-Z0-9._]{2,28}[a-zA-Z0-9]$', username):
            raise ValidationError("The username must start and end with a letter or number, "
                                "and can only contain letters, numbers, underscores (_), and dots (.). "
                                "It must be between 3 and 30 characters.")
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken. Choose another one.")
        return username
    
    # Validation for first_name
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not re.match(r'^[a-zA-Z\s-]+$', first_name):
            raise ValidationError("The first name can only contain letters, spaces, and hyphens (-).")
        return first_name
    
    # Validation for last_name
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not re.match(r'^[a-zA-Z\s-]+$', last_name):
            raise ValidationError("The last name can only contain letters, spaces, and hyphens (-).")
        return last_name
    
    # Validation for age
    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age < 13:
            raise ValidationError("You must be at least 13 years old to register.")
        if age > 120:
            raise ValidationError("Invalid age. Please enter a realistic value.")
        return age
    
    def save(self, commit=False):
        user = super().save(commit=False)

        user.code = str(uuid.uuid4())  # Unique code generated with UUID
        user.email_confirm = False  # Initially, the email is not confirmed

        if commit:
            user.save()  # Save the user in the database
            #self.send_confirmation_email(user) # Sending confirmation email
        return user 
    
    
    
                #PROFILE PAGE FORM
                
class ProfileForm(forms.ModelForm):
    class Meta:
        model=CustomUser
        fields=['XP','username','first_name','last_name','email','age']
        
    #these fields can not be modified   
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['XP'].disabled = True
        self.fields['email'].disabled = True