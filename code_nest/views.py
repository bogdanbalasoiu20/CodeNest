from django.shortcuts import render,redirect, get_object_or_404
from .models import CustomUser, Test, Question, Answer, TestResult
from django.http import HttpResponse
from .forms import CustomAuthenticationForm, Register, ProfileForm, QuestionForm, TestFilterForm
from django.contrib.auth import login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings  
import uuid
from django.http import JsonResponse
from django.views.decorators.http import require_GET
import time
from django.core.cache import cache
from django.utils import timezone
from django.db.models import Prefetch, Q
from . import models


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
    return redirect('home')


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
        
    test_results = user.testresults.select_related("test").order_by("-date_taken")

    return render(request, 'profile.html', {
        'form': form,
        'test_results': test_results
    })


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




def add_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()  # Salvează întrebarea și răspunsurile
            return redirect('some-success-url')  # Redirect după salvare
    else:
        form = QuestionForm()

    return render(request, 'add_question.html', {'form': form})
                                            #----------------------#
                                            #TAKE TEST FUNCTION
                                            #----------------------#

def take_test(request, test_id):
    if not request.user.is_authenticated:
        messages.info(request, "Trebuie să fii autentificat pentru a rezolva teste")
        return redirect('login')
    
    test = get_object_or_404(
        Test.objects.prefetch_related(
            'categories',
            Prefetch('questions', queryset=Question.objects.prefetch_related('answers'))
        ),
        id=test_id
    )

    # Inițializare statistici
    stats = {
        'average_score': test.average_score,
        'completion_rate': test.completion_rate,
        'attempts_count': test.attempts_count,
        'user_score': None,
        'user_rank': None,
        'best_score': None
    }

    if request.user.is_authenticated:
        user_results = TestResult.objects.filter(
            user=request.user,
            test=test
        ).order_by('-percentage')
        
        if user_results.exists():
            stats.update({
                'best_score': user_results.first().percentage,
                'user_rank': TestResult.objects.filter(
                    test=test,
                    percentage__gt=user_results.first().percentage
                ).count() + 1
            })

    if request.method == 'POST':
        # Calcul scor
        score = 0
        total_points = sum(q.points for q in test.questions.all())
        answers = {}

        for question in test.questions.all():
            selected = request.POST.get(f"question_{question.id}")
            answers[f"question_{question.id}"] = selected
            if selected and question.answers.filter(is_correct=True, option_label=selected).exists():
                score += question.points

        percentage = round((score / total_points) * 100, 2) if total_points > 0 else 0

        if request.user.is_authenticated:
            # Actualizare sau creare rezultat
            best_existing = TestResult.objects.filter(
                user=request.user,
                test=test
            ).order_by('-percentage').first()

            # Salvăm doar dacă nu există rezultat sau noul rezultat e mai bun
            if not best_existing or percentage > best_existing.percentage:
                TestResult.objects.update_or_create(
                    user=request.user,
                    test=test,
                    defaults={
                        'score': score,
                        'percentage': percentage,
                        'completed': (percentage == 100),
                        'date_taken': timezone.now(),
                        'cooldown_until': None  # Eliminăm orice cooldown existent
                    }
                )
                
                # Actualizare statistici doar dacă am făcut modificări
                stats.update({
                    'user_score': percentage,
                    'user_rank': TestResult.objects.filter(
                        test=test,
                        percentage__gt=percentage
                    ).count() + 1,
                    'best_score': max(percentage, stats['best_score'] if stats['best_score'] else 0)
                })

                # Invalidate cache
                cache.delete(f'test_stats_{test_id}')

        return render(request, "test_result.html", {
            "test": test,
            "score": score,
            "total": total_points,
            "percentage": percentage,
            "perfect_score": (percentage == 100),
            "stats": stats
        })

    return render(request, "take_test.html", {
        "test": test,
        "questions": test.questions.all(),
        "time_limit": test.time_in_minutes,
        "categories": test.categories.all(),
        "stats": stats,
        "best_score": stats['best_score'],
        "can_retake": True  # Mereu True acum
    })
    
    
def test_404(request):
    return render(request,'404.html',status=404)



                                            #----------------------#
                                            #LEADERBOARD FUNCTION
                                            #----------------------#
def leaderboard(request):
    top_user=list(CustomUser.objects.order_by('-XP'))
    
    
    for index,user in enumerate(top_user):
        new_pos=index+1
        if new_pos != user.ranking_position:
            user.ranking_position=new_pos
            user.save()
            
    
    return render(request,'leaderboard.html',{'top_user':top_user})

from .models import Course, Test
from .forms import TestFilterForm

def course_list(request):
    courses = Course.objects.filter(is_published=True)
    return render(request, 'courses.html', {'courses': courses})

def testsPage(request):
    form = TestFilterForm(request.GET or None)
    tests = Test.objects.all()
    
    if form.is_valid():
        if form.cleaned_data['categories']:
            tests = tests.filter(categories__in=form.cleaned_data['categories'])
        
        if form.cleaned_data['difficulty']:
            tests = tests.filter(difficulty=form.cleaned_data['difficulty'])
    
    return render(request, 'testsPage.html', {
        'form': form,
        'tests': tests
    })

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Course, CourseEnrollment

@login_required
def enroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug)

    # Verifică dacă userul este deja înscris
    enrollment, created = CourseEnrollment.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={
            'status': 'unstarted',
            'payment_method': 'free' if course.is_free else 'card',
        }
    )

    # Dacă era deja înscris, nu face nimic nou
    return redirect('enrollment_confirmation', slug=course.slug)

def enrollment_confirmation(request, slug):
    course = get_object_or_404(Course, slug=slug)
    return render(request, 'course_enrolled.html', {'course': course})

from django.views.decorators.http import require_POST

@login_required
def course_payment(request, slug):
    course = get_object_or_404(Course, slug=slug)

    if request.method == 'POST':
        # aici poți simula că "s-a plătit"
        return redirect('enroll_course', slug=slug)

    return render(request, 'course_payment.html', {'course': course})




                                            #----------------------#
                                            #TEST DETAILS
                                            #----------------------#
   
def testDetails(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    sample_questions = test.questions.all().order_by('?')[:3]
    
    context = {
        'test': test,
        'sample_questions': sample_questions,
        'test_difficulty': test.get_difficulty_display(),
        'can_retake': True  # Mereu True acum
    }
    
    if request.user.is_authenticated:
        # Calculăm progresul general
        completed_count = request.user.testresults.filter(completed=True).count()
        total_tests = Test.objects.count()
        progress = round((completed_count / total_tests) * 100) if total_tests > 0 else 0
        
        # Obținem cel mai bun scor pentru acest test
        best_attempt = TestResult.objects.filter(
            user=request.user,
            test=test
        ).order_by('-percentage').first()
        
        if best_attempt:
            context.update({
                'best_attempt': best_attempt,
                'has_perfect_score': best_attempt.percentage == 100,
            })
        
        context.update({
            'progress': progress,
            'completed_count': completed_count,
            'total_tests': total_tests,
        })

    return render(request, 'test_details.html', context)
    
    
    
    
def get_test_stats(request, test_id):
    """
    Endpoint API pentru statistici cu cache
    """
    cached_stats = cache.get(f'test_stats_{test_id}')
    if cached_stats:
        return JsonResponse(cached_stats)
    
    test = get_object_or_404(Test, id=test_id)
    stats = {
        'average_score': test.average_score,
        'completion_rate': test.completion_rate,
        'attempts_count': test.attempts_count,
        'last_updated': test.updated_at.timestamp() if hasattr(test, 'updated_at') else time.time()
    }
    
    cache.set(f'test_stats_{test_id}', stats, timeout=30)
    return JsonResponse(stats)