from django.urls import path


from . import views


urlpatterns = [
    path("home/", views.home, name="home"),
    path("login/", views.custom_login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
]
