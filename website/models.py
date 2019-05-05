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

