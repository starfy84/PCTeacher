from django.shortcuts import render

# Create your views here.

from website.models import Lesson

def home(request):
    context = {
        'lessons': Lesson.objects.all(),
    }
    return render(request, 'home.html', context)
