import datetime
import parser

from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Topic(models.Model):
    title = models.CharField(max_length=128)
    
    def __str__(self):
        return'Topic "{}"'.format(self.title)


class Lesson(models.Model):
    title = models.CharField(max_length=128)
    topic = models.ForeignKey('Topic', on_delete=models.CASCADE)

    def __str__(self):
        return 'Lesson "{}"'.format(self.title)


class SubLesson(models.Model):
    title = models.CharField(max_length=128)
    content = models.TextField(null=True, blank=True)
    lesson = models.ForeignKey('Lesson', on_delete=models.CASCADE)

    example_title = models.CharField(max_length=128)
    expression = models.TextField(null=True, blank=True)

    def parse(self, expression, variables={}):
        from random import randint, uniform
        locals().update(variables)
        return eval(parser.expr(expression).compile())

    def gen_variables(self):
        ret = {}
        for var in self.variable_set.all():
            ret[var.name] = self.parse(var.value)
        return ret

    def gen_answer(self, variables):
        return self.parse(self.expression, variables=variables)

    def gen_question(self, variables):
        ret = self.expression
        for var, value in variables.items():
            ret = ret.replace(str(var), str(value))
        return ret

    def __str__(self):
        return 'Sublesson "{}"'.format(self.title)


class Variable(models.Model):
    name = models.CharField(max_length=128)
    order = models.IntegerField()
    value = models.TextField()
    sublesson = models.ForeignKey('SubLesson', on_delete=models.CASCADE) 


class SubLessonUserData(models.Model):
    sublesson = models.ForeignKey('SubLesson', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    current_problem = models.CharField(max_length=128, null=True, blank=True, default=None)
    current_answer = models.CharField(max_length=128, null=True, blank=True, default=None)
    time = models.DurationField(default=datetime.timedelta(seconds=0))
    tries = models.IntegerField(default=1)
    solved = models.BooleanField(default=False)
    learn_type = models.CharField(max_length=128, default='Logical')
