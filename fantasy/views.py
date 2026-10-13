from django.shortcuts import render


def home(request):
    return render(request, "fantasy/home.html")