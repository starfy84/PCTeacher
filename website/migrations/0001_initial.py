# Generated by Django 2.2.1 on 2019-05-05 01:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='SubLesson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('content', models.TextField(blank=True, null=True)),
                ('example_title', models.CharField(max_length=128)),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.Lesson')),
            ],
        ),
        migrations.AddField(
            model_name='lesson',
            name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.Topic'),
        ),
    ]