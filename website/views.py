from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Sum
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.safestring import mark_safe

import re
import json
from operator import itemgetter

from num2words import num2words


# Create your views here.

from .forms import UserRegisterForm
from website.models import Lesson, SubLesson, SubLessonUserData, LEARNING_TYPES


chart_colors = [0x3366CC, 0xDC3912, 0xFF9900, 0x109618, 0x990099, 0x3B3EAC, 0x0099C6, 0xDD4477, 0x66AA00, 0xB82E2E,
                0x316395, 0x994499, 0x22AA99, 0xAAAA11, 0x6633CC, 0xE67300, 0x8B0707, 0x329262, 0x5574A6, 0x3B3EAC]
highlight_colors = []


def _highlight_colors():
    for color in chart_colors:
        r, g, b = color >> 16, (color >> 8) & 0xFF, color & 0xFF
        highlight_colors.append('#%02X%02X%02X' % (min(int(r * 1.2), 255),
                                                   min(int(g * 1.2), 255),
                                                   min(int(b * 1.2), 255)))


_highlight_colors()
del _highlight_colors

chart_colors = list(map('#%06X'.__mod__, chart_colors))


def home(request):
    context = {
        'lessons': Lesson.objects.order_by('id'),
    }
    if request.user.is_authenticated:
        objs = sorted(SubLessonUserData.objects.filter(user=request.user).values('learn_type') \
                                               .annotate(sum=Sum('tries')).values_list('learn_type', 'sum'))
        total = sum(map(itemgetter(1), objs))
        context['chart_data'] = mark_safe(json.dumps({
            'labels': [x[1].title() for x in LEARNING_TYPES],
            'datasets': [{
                'backgroundColor': chart_colors,
                'highlightBackgroundColor': highlight_colors,
                'data': [round(x[1] / total * 100, 2) for x in objs]
            }]
        }))
    return render(request, 'home.html', context)


def done_sublessons(user):
    return SubLessonUserData.objects.filter(user=user, solved=settings.PROBLEM_SOLVE_COUNT).values_list('sublesson_id', flat=True)


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
        try:
            correct = (user_answer == int(data.current_answer))
        except Exception:
            pass
        else:
            data.solved += correct
            if not correct:
                data.current_tries += 1
                data.tries += 1
            else:
                context['user_answer'] = ''
                data.current_problem = None
                data.current_answer = None
                data.current_tries = 1

            data.save()
        context['next_sublesson'] = lesson.sublesson_set.exclude(id__in=done_sublessons(request.user)).order_by('id').first()
    else:
        data = SubLessonUserData.objects.get_or_create(sublesson=sublesson, user=request.user)[0]

    if (data.current_problem is None or data.current_answer is None) and data.solved < settings.PROBLEM_SOLVE_COUNT:
        variables = sublesson.gen_variables()

        objs = SubLessonUserData.objects.filter(user=request.user).values('learn_type').annotate(sum=Sum('tries')).values_list('learn_type', 'sum')
        learn_type_cnt = sorted(objs, key=lambda x: x[1])
        for i in LEARNING_TYPES:
            if i[0] not in list(map(lambda x: x[0], learn_type_cnt)):
                typ = i[0]
                break
        else:
            typ = learn_type_cnt[0][0]

        data.learn_type = typ

        data.current_problem = sublesson.gen_question(variables, markdown=sublesson.markdown_expression)
        data.current_answer = sublesson.gen_answer(variables)

        data.save()

    example_vars = sublesson.gen_variables()
    example_question = sublesson.gen_question(example_vars)
    example_answer = sublesson.gen_question(example_vars)
    example = '{} = {}'.format(example_question, str(eval(example_answer)))
    if data.learn_type == 0:   #VISUAL
        image = '<img src="/static/apple.png" class="apple"></img>'
        match = re.search('\d+', example_question)
        while match is not None:
            l, r = match.span()
            example_question = example_question[:l] + image*int(example_question[l:r]) + example_question[r:]
            match = re.search('\d+', example_question)
        example = '{} = {}'.format(example_question, image*(eval(example_answer)))
    elif data.learn_type == 1: #VERBAL / text
        operator_format = {
            '+': '{} objects added to {} objects results in {} objects.',
            '-': '{} objects with {} objects taken away results in {} objects.',
            '*': '{} objects repeated {} times results in {} objects.',
            '//': '{} split into groups of {} creates {} groups.',
            '**': '{} multipled {} times is {}.',
        }
        example = operator_format[re.search('(\\+)|(-)|(\\/\\/)|(\\*\\*)|(\\*)', example_question).group(0)].format(*re.findall('\d+', example_question), str(eval(example_answer)))
        match = re.search('\d+', example)
        while match is not None:
            l, r = match.span()
            example = example[:l] + num2words(int(example[l:r])) + example[r:]
            match = re.search('\d+', example)
        example = example.capitalize()

    num_lessons = lesson.sublesson_set.count()
    done_lessons = lesson.sublesson_set.filter(id__in=done_sublessons(request.user)).count()

    context.update({
        'example': example,
        'question': data.current_problem,
        'learn_type': data.learn_type,
        'problems': {
            'correct': data.solved,
            'total': settings.PROBLEM_SOLVE_COUNT,
            'attempted': data.current_tries > 1,
        },
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
