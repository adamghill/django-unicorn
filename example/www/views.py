from django.shortcuts import render


def index(request):
    return render(request, "www/index.html")


def template(request, name):
    return render(request, f"www/{name}.html")
