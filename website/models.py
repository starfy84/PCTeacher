from django.db import models
from django.contrib.auth.models import User
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
    problem = models.IntegerField()
    time = models.DurationField()
    tries = models.IntegerField()
    learn_type = models.CharField(max_length=128)
