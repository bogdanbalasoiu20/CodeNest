from django.shortcuts import render
# Create your views here.
from django.http import HttpResponse


def test(request):
    return HttpResponse('server is running...')

def test2(request):
    return HttpResponse('server este ok')


def test3(request):
    return HttpResponse('test3')

def test4(request):
    return HttpResponse('test4')

def test5(request):
    return HttpResponse('test5...')


def home(request):
    return render(request,'home.html') 
    