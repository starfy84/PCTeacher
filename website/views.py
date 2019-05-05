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
    lesson = get_object_or_404(Lesson, pk=id)
    sublesson = get_object_or_404(SubLesson, pk=sub_id)
    example_vars = sublesson.gen_variables()
    example = '{} = {}'.format(sublesson.gen_question(example_vars), sublesson.gen_answer(example_vars))

    variables = sublesson.gen_variables()
    question = sublesson.gen_question(variables)
    answer = sublesson.gen_answer(variables)
    context = {
        'lesson': lesson,
        'sublesson': sublesson,
        'example': example,
        'question': question,
        'answer': answer,
    }
    return render(request, 'sublesson.html', context)
