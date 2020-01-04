from django.shortcuts import render
from .models import Week

# Create your views here.

def post_list(request):
    return render(request, 'appmain/post_list.html', {})

#def home_frame(request):
#    return render(request, 'appmain/home_frame.html', {})

def home(request):
   weeks = Week.objects.filter(id=1)
   return render(request, 'appmain/home.html', {'weeks': weeks})

def picks_view(request):
    return render(request, 'appmain/picks_view.html', {})

def picks_make(request):
    return render(request, 'appmain/picks_make.html', {})

def picks_revisions(request):
    return render(request, 'appmain/picks_revisions.html', {})