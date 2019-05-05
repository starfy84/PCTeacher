from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserRegisterForm

import re
from num2words import num2words
# Create your views here.

from website.models import Lesson, SubLesson, SubLessonUserData, LEARNING_TYPES


def home(request):
    context = {
        'lessons': Lesson.objects.order_by('id'),
    }
    return render(request, 'home.html', context)


def done_sublessons(user):
    return SubLessonUserData.objects.filter(user=user, solved=True).values_list('sublesson_id', flat=True)


@login_required
def lesson(request, id):
    lesson = get_object_or_404(Lesson, pk=id)

    first_sublesson = lesson.sublesson_set.order_by('id').first()
    current_sublesson = lesson.sublesson_set.exclude(id__in=done_sublessons(request.user)).order_by('id').first()

    context = {
        'lesson': lesson,
        'sublesson_begin': current_sublesson,
        'start': first_sublesson == current_sublesson,
        'title': lesson.title,
    }
    return render(request, 'lesson.html', context)


@login_required
def sublesson(request, id, sub_id):
    lesson = get_object_or_404(Lesson, pk=id)
    sublesson = get_object_or_404(SubLesson, pk=sub_id)

    context = {
        'lesson': lesson,
        'sublesson': sublesson,
        'title': sublesson.title,
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
        context['next_sublesson'] = lesson.sublesson_set.exclude(id__in=done_sublessons(request.user)).order_by('id').first()
    else:
        data, created = SubLessonUserData.objects.get_or_create(sublesson=sublesson, user=request.user)

        if data.current_problem is None or data.current_answer is None:
            variables = sublesson.gen_variables()
            data.current_problem = sublesson.gen_question(variables)
            data.current_answer = sublesson.gen_answer(variables)

            objs = SubLessonUserData.objects.filter(user=request.user).values('learn_type').annotate(sum=Sum('tries')).values_list('learn_type', 'sum')
            learn_type_cnt = sorted(objs, key=lambda x: x[1])
            for i in LEARNING_TYPES:
                if i[0] not in list(map(lambda x: x[0], learn_type_cnt)):
                    typ = i[0]
                    break
            else:
                typ = learn_type_cnt[0][0]

            data.learn_type = typ
            data.save()

    context['correct'] = data.solved
    context['attempted'] = (data.tries > 1)

    example_vars = sublesson.gen_variables()
    example_question = sublesson.gen_question(example_vars)
    example_answer = sublesson.gen_question(example_vars)
    example = None
    if data.learn_type == 0:   #VISUAL
        image = '<img src="/static/apple.png" class="apple"></img>'
        match = re.search('\d+', example_question)
        while match is not None:
            l, r = match.span()
            example_question = example_question[:l] + image*int(example_question[l:r]) + example_question[r:]
            match = re.search('\d+', example_question)
        example_answer = image*eval(example_answer)
        l,r = re.match('[+*/-]', example_question)
        example_question = example_question[:l] + '<span font-size="3em">' + example_question[l:r] + '</span>' + example_question[r:]
        example = '{} <span font-size="3em">=</span> {}'.format(example_question, example_answer)
    elif data.learn_type == 1: #VERBAL / text
        operator_format = {
            '+': '{} objects added to {} objects results in {} objects.',
            '-': '{} objects with {} objects taken away results in {} objects.',
            '*': '{} objects repeated {} times results in {} objects.',
            '/': '{} split into groups of {} creates {} groups.'
        }
        example = operator_format[re.search('[+*/-]', example_question).group(0)].format(*re.findall('\d+', example_question), str(eval(example_answer)))
        match = re.search('\d+', example)
        while match is not None:
            l, r = match.span()
            example = example[:l] + num2words(int(example[l:r])) + example[r:]
            match = re.search('\d+', example)

    num_lessons = lesson.sublesson_set.count()
    done_lessons = lesson.sublesson_set.filter(id__in=done_sublessons(request.user)).count()

    context.update({
        'example': example,
        'question': data.current_problem,
        'learn_type': data.learn_type,
        'sublessons': {
            'done': done_lessons,
            'total': num_lessons,
            'percentage': done_lessons / num_lessons * 100,
        }
    })
    return render(request, 'sublesson.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, 'Your account has been created!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form':form})
