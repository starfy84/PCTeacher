from django.contrib import admin

# Register your models here.

from website.models import Topic, Lesson, SubLesson

class TopicAdmin(admin.ModelAdmin):
    fields = ('title',)
    list_display = ['title']


class SubLessonAdminInline(admin.TabularInline):
    model = SubLesson
    fields = ('title', 'content', 'example_title')


class LessonAdmin(admin.ModelAdmin):
    fields = ('topic', 'title')
    list_display = ['topic', 'title']
    inlines = [SubLessonAdminInline]

admin.site.register(Topic, TopicAdmin)
admin.site.register(Lesson, LessonAdmin)
