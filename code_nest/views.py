from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import CustomAuthenticationForm, Register
from django.contrib.auth import login,logout
from django.contrib import messages
import uuid

def home(request):
    return render(request,'home.html') 
    
    
def custom_login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST, request=request)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if not form.cleaned_data.get('stay_logged'):
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(2*7*24*60*60)  # 2 săptămâni în secunde            
            return redirect('home')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'login.html', {'form': form})



def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')

def register(request):
    if request.method == 'POST':

        form = Register(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email_confirm = False
            user.cod = str(uuid.uuid4())
            user.save()

            return redirect('login')
        
        else:

            return render(request, 'register.html', {'form' : form})
    else:

        form = Register()
    return render(request, 'register.html', {'form':form})

