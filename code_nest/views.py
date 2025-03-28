from django.shortcuts import render,redirect, get_object_or_404
from .models import CustomUser, Test, Question, Answer
from django.http import HttpResponse
from .forms import CustomAuthenticationForm, Register, ProfileForm
from django.contrib.auth import login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings  
import uuid

def home(request):
    return render(request,'home.html') 


                                                #-------------#
                                                #LOGIN FUNCTION
                                                #-------------#
def custom_login_view(request):
    if request.user.is_authenticated:   #if user is already logged in then he is redirected to home page
        return redirect('home')

    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST, request=request)
        if form.is_valid():
            user = form.get_user()

            if not user.email_confirm:
                messages.error(request, "Please confirm your email first.")
                return redirect('login')
            
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


                                                #--------------#
                                                #LOGOUT FUNCTION
                                                #--------------#
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')


                                                #----------------#
                                                #REGISTER FUNCTION
                                                #----------------#
def register(request):
    if request.method == 'POST':

        form = Register(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email_confirm = False
            user.save()

            send_confirmation_email(user)

            messages.success(request, "Please confirm your email first.")
            return redirect('login')
        else:
            return render(request, 'register.html', {'form' : form})
    else:

        form = Register()
    return render(request, 'register.html', {'form':form})


                                                #-------------------------#
                                                #SENDING CONFIRMATION EMAIL
                                                #-------------------------#
def send_confirmation_email(user):

    if user.email_confirm: 
        print(f"User {user.username} has already confirm his email.")
        return 
    
    confirmation_link = f"http://127.0.0.1:8000/code_nest/confirm_email/{user.code}/"

    context = {
        'first_name' : user.first_name,
        'last_name' : user.last_name,
        'username' : user.username,
        'confirmation_link' : confirmation_link,
    }

    email_html = render_to_string('confirmation_email.html', context)

    email = EmailMessage(
        subject = 'Confirm your email Address',
        body = email_html,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    email.content_subtype = "html"
    email.send()
    print(f"Confirmation link: {confirmation_link}")


                                                #------------#
                                                #EMAIL CONFIRM
                                                #------------#
def confirm_email(request, code):
    try:
        user = CustomUser.objects.get(code=code)
        if user.email_confirm:
            messages.info(request, "Your email is already confirmed.")
        else:
            user.email_confirm = True
            user.save()
            messages.success(request, "Your email has been successfully confirmed!")

        return redirect('login')

    except CustomUser.DoesNotExist:
        messages.error(request, "Invalid confirmation link.")
        return redirect('register')



                                                #---------------#
                                                #PROFILE FUNCTION
                                                #---------------#
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


                                            #----------------------#
                                            #DELETE ACCOUNT FUNCTION
                                            #----------------------#
def delete_account(request):
    if request.method=='POST':
        user=request.user
        user.delete()
        messages.success(request,f"Your account ({user.username}) has been successfully deleted")
        logout(request)
        return redirect('home')
    return render(request,"delete_account_confirm.html")

                                            #----------------------#
                                            #TAKE TEST FUNCTION
                                            #----------------------#

def take_test(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    questions = test.questions.all().prefetch_related("answers")

    if request.method == 'POST':
        score = 0
        total = questions.count()

        for question in questions:
            selected = request.POST.get(f"question_{question.id}")
            if selected:
                correct_answer = question.answers.filter(is_correct=True, option_label=selected).exists()
                if correct_answer:
                    score += question.points

        return render(request, "test_result.html", {
            "test": test,
            "score": score,
            "total": total
        })

    return render(request, "take_test.html", {
        "test": test,
        "questions": questions,
    })
    
    
    
def test_404(request):
    return render(request,'404.html',status=404)