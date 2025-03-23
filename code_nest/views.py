from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import CustomAuthenticationForm, Register, ProfileForm
from django.contrib.auth import login,logout
from django.contrib import messages
import uuid
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request,'home.html') 
    
#LOGIN FUNCTION    
def custom_login_view(request):
    if request.user.is_authenticated:   #if user is already logged in then he is redirected to home page
        return redirect('home')

    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST, request=request)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if not form.cleaned_data.get('stay_logged'):
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(2*7*24*60*60)              
            
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'login.html', {'form': form})



#LOGOUT FUNCTION
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')



#REGISTER FUNCTION
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



#PROFILE FUNCTION
@login_required
def profile(request):
    user=request.user
    if request.method=='POST':
        form=ProfileForm(request.POST,instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form=ProfileForm(instance=user)
        
    return render(request,'profile.html',{'form':form})


#DELETE ACCOUNT FUNCTION
def delete_account(request):
    if request.method=='POST':
        user=request.user
        user.delete()
        messages.success(request,f"Your account ({user.username}) has been successfully deleted")
        logout(request)
        return redirect('home')
    return render(request,"delete_account_confirm.html")