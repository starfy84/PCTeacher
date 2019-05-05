from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

# Create your views here.

from website.models import Lesson, SubLesson, SubLessonUserData

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

@login_required
def sublesson(request, id, sub_id):
    lesson = get_object_or_404(Lesson, pk=id)
    sublesson = get_object_or_404(SubLesson, pk=sub_id)

    data, created = SubLessonUserData.objects.get_or_create(sublesson=sublesson, user=request.user)
    
    if data.current_problem is None or data.current_answer is None:
        variables = sublesson.gen_variables()
        data.current_problem = '{} = ?'.format(sublesson.gen_question(variables))
        data.current_answer = sublesson.gen_answer(variables)
        data.save()

    example_vars = sublesson.gen_variables()
    example = '{} = {}'.format(sublesson.gen_question(example_vars), sublesson.gen_answer(example_vars))

    context = {
        'lesson': lesson,
        'sublesson': sublesson,
        'example': example,
        'question': data.current_problem,
        'answer': data.current_answer,
    }
    return render(request, 'sublesson.html', context)
