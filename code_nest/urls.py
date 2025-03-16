from django.urls import path


from . import views


urlpatterns = [
    path("test/", views.test, name="test"),
    path("test2/", views.test2, name="test2"),
    path("test3/", views.test3, name="test3"),
    path("test4/", views.test4, name="test4"),

]
