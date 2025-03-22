from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import CustomAuthenticationForm
from django.contrib.auth import login,logout
from django.contrib import messages

def test(request):
    return HttpResponse('server is running...')

def test2(request):
    return HttpResponse('server este ok')


def test3(request):
    return HttpResponse('test3')

def test4(request):
    return HttpResponse('test4')



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
