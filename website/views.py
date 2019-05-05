from django.shortcuts import render, get_object_or_404

# Create your views here.

from website.models import Lesson, SubLesson

def home(request):
    context = {
        'lessons': Lesson.objects.all(),
    }
    return render(request, 'home.html', context)

def lesson(request, id):
    lesson = get_object_or_404(Lesson, pk=id)

    context = {
        'lesson': lesson,
        'sublesson_begin': lesson.sublesson_set.order_by('id').first()
    }
    return render(request, 'lesson.html', context)

def sublesson(request, id, sub_id):
    context = {
        'lesson': get_object_or_404(Lesson, pk=id),
        'sublesson': get_object_or_404(SubLesson, pk=sub_id),
    }
    return render(request, 'sublesson.html', context)
