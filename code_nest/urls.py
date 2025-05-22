from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path("home/", views.home, name="home"),
    path("login/", views.custom_login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    #Register and email confrimation
    path("register/", views.register, name="register"),
    path('confirm_email/<str:code>/', views.confirm_email, name='confirm_email'),

    # Password reset views:
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    
    path('profile/',views.profile,name='profile'),
    path('profile/delete/',views.delete_account,name='delete_account'),
    
    #Change password in profile page
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'), name='password_change_done'),

    #Tests
    path('test/<int:test_id>/', views.take_test, name='take_test'),
    
    #404
    path('page404/',views.test_404,name='page404'),
    
    #leaderboard
    path('leaderboard/',views.leaderboard,name="leaderboard"),
    
    path('courses/', views.course_list, name='course_list'),
    path('tests/', views.testsPage, name='testsPage'),

    
    path('courses/<slug:slug>/enroll/', views.enroll_course, name='enroll_course'),

    path('courses/<slug:slug>/confirmare/', views.enrollment_confirmation, name='enrollment_confirmation'),

    # urls.py
    path('courses/<slug:slug>/payment/', views.course_payment, name='course_payment'),
    
    #test detail
    path('tests/test_details/<int:test_id>/',views.testDetails,name='test_details'),
    
    #test stats
    path('test/<int:test_id>/stats/', views.get_test_stats, name='test-stats'),
    
    #forum
    path('forum/', views.question_list, name='forum_question_list'),
    path('forum/ask/', views.ask_question, name='forum_ask_question'),
    path('forum/<int:pk>/', views.question_detail, name='forum_question_detail'),
    
    #ai
    path('assistant/', views.ai_assistant, name='ai_assistant'),



]
