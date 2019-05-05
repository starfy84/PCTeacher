from django.contrib import admin

# Register your models here.

from website.models import Topic, Lesson, SubLesson, SubLessonUserData, Variable

class TopicAdmin(admin.ModelAdmin):
    fields = ('title',)
    list_display = ['title']


class VariableInline(admin.TabularInline):
    model = Variable
    fields = ('name', 'value', 'order')


class SubLessonAdmin(admin.ModelAdmin):
    fields = ('lesson', 'title', 'content', 'example_title', 'expression')
    inlines = [VariableInline]
    list_display = ('lesson', 'title')


class SubLessonUserDataAdmin(admin.ModelAdmin):
    fields = ('sublesson', 'user', 'current_problem', 'current_answer', 'time', 'learn_type')
    list_display = ('sublesson', 'user', 'current_problem')


class LessonAdmin(admin.ModelAdmin):
    fields = ('topic', 'title')
    list_display = ['topic', 'title']


admin.site.register(Topic, TopicAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(SubLesson, SubLessonAdmin)
admin.site.register(SubLessonUserData, SubLessonUserDataAdmin)
