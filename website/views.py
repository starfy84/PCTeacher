from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, get_object_or_404

# Create your views here.

from website.models import Lesson, SubLesson, SubLessonUserData


def home(request):
    context = {
        'lessons': Lesson.objects.order_by('id'),
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

    context = {
        'lesson': lesson,
        'sublesson': sublesson,
        'user_answer': '',
    }

    if request.method == 'POST':
        data = get_object_or_404(SubLessonUserData, sublesson=sublesson, user=request.user)
        try:
            user_answer = int(request.POST['answer'])
        except Exception:
            raise Http404()
        context['user_answer'] = user_answer
        correct = (user_answer == int(data.current_answer))
        data.solved = correct
        if not correct:
            data.tries += 1
        data.save()
    else:
        data, created = SubLessonUserData.objects.get_or_create(sublesson=sublesson, user=request.user)

        if data.current_problem is None or data.current_answer is None:
            variables = sublesson.gen_variables()
            data.current_problem = '{} = ?'.format(sublesson.gen_question(variables))
            data.current_answer = sublesson.gen_answer(variables)
            data.save()

    context['correct'] = data.solved
    context['attempted'] = (data.tries > 1)

    example_vars = sublesson.gen_variables()
    example = '{} = {}'.format(sublesson.gen_question(example_vars), sublesson.gen_answer(example_vars))

    context.update({
        'example': example,
        'question': data.current_problem,
    })
    return render(request, 'sublesson.html', context)
