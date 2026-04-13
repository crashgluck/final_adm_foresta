from django.shortcuts import render

def index_start(request):
    return render(request, "index.html")