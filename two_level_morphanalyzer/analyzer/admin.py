from django.contrib import admin
from django.forms import TextInput
from django.utils.safestring import mark_safe

from . import models

from django.contrib import admin
from django.shortcuts import render
from django.urls import path
from django import forms
from .models import Audios, Users, Univers
from django.utils.html import format_html






class AudiosAdmin(admin.ModelAdmin):
    #form = MyModel
    list_display = ('id', 'get_audio', 'get_text', 'super_visor', 'get_user_name', 'status', 'is_correct', 'sound_display')
    list_display_links = ('id', 'get_audio')
    search_fields = ('get_audio','super_visor', 'user_name', 'status')
    list_filter = ('status','is_correct','super_visor', 'user_name')
    list_editable = ('status', 'is_correct')
    fields = ('audio_file','text','super_visor', 'user_name', 'status', 'is_correct')
    #prepopulated_fields = {"slug": ("audio_file",)}
    class Media:
        css = {
            'all': ('analyzer/css/fancy.css',)
        }

    def get_audio(self, object):
        if object.audio_file:
            wav_name = str(object.audio_file)
            wav_name = wav_name[:8] + '...'
            return mark_safe(f"<div style='max-width: 20px table-layout:fixed' >{wav_name}</div>")
    def get_text(self, object):
        if object.text:
            return mark_safe(f"<p style='width: 180px; word-wrap: break-word;'>{object.text}</p>")
    def get_user_name(self, object):
        if object.user_name:
            return mark_safe(f"<p style='width: 50px; word-wrap: break-word;'>{object.user_name}</p>")
    def check_box(self, object):
        if object.text:
            return mark_safe(f"<p style='width: 180px; word-wrap: break-word;'>{object.text}</p>")
    def sound_display(self, item):
        return item.sound_display
    def save_model(self, request, obj, form, change):
        print(obj.status)
        print(obj.is_correct)
        if not obj.is_correct and change and 'is_correct' in form.changed_data:
            #if sound must be overwritten
            user_name = str(obj.user_name)
            user_name =user_name[1:]
            qset = Users.objects.values('pk').filter(user_name=user_name).first()
            written_s_num = Users.objects.values('written_s_num').filter(id=qset['pk']).first()

            incorrect_s_num = Users.objects.values('incorrect_s_num').filter(id=qset['pk']).first()
            incorrect_s_num = int(incorrect_s_num['incorrect_s_num']) + 1
            Users.objects.filter(id=qset['pk']).update(incorrect_s_num=incorrect_s_num)

            #fin_s_num = Users.objects.values('finished_s_num').filter(id=qset['pk']).first()
            fin_s_num = int(written_s_num['written_s_num']) - incorrect_s_num
            Users.objects.filter(id=qset['pk']).update(finished_s_num=fin_s_num)



            qset = Users.objects.values('univer_name').filter(id=qset['pk']).first()
            written_s_num = Univers.objects.values('written_s_num').filter(id=qset['univer_name']).first()

            incorrect_s_num = Univers.objects.values('incorrect_s_num').filter(id=str(qset['univer_name'])).first()
            incorrect_s_num = int(incorrect_s_num['incorrect_s_num']) + 1
            Univers.objects.filter(id=qset['univer_name']).update(incorrect_s_num=incorrect_s_num)

            fin_s_num = int(written_s_num['written_s_num']) - incorrect_s_num
            Univers.objects.filter(id=qset['univer_name']).update(finished_s_num=fin_s_num)
        elif obj.status and change and 'status' in form.changed_data:
            # if sound totally correct
            user_name = str(obj.user_name)
            user_name =user_name[1:]
            qset = Users.objects.values('pk').filter(user_name=user_name).first()

            correct_s_num = Users.objects.values('correct_s_num').filter(id=qset['pk']).first()
            correct_s_num = int(correct_s_num['correct_s_num']) + 1
            Users.objects.filter(id=qset['pk']).update(correct_s_num=correct_s_num)

            qset = Users.objects.values('univer_name').filter(id=qset['pk']).first()
            correct_s_num = Univers.objects.values('correct_s_num').filter(id=str(qset['univer_name'])).first()
            correct_s_num = int(correct_s_num['correct_s_num']) + 1
            Univers.objects.filter(id=qset['univer_name']).update(correct_s_num=correct_s_num)
        elif not obj.status and change and 'status' in form.changed_data:
            # if incorrect
            user_name = str(obj.user_name)
            user_name = user_name[1:]
            qset = Users.objects.values('pk').filter(user_name=user_name).first()

            correct_s_num = Users.objects.values('correct_s_num').filter(id=qset['pk']).first()
            correct_s_num = int(correct_s_num['correct_s_num']) - 1
            Users.objects.filter(id=qset['pk']).update(correct_s_num=correct_s_num)

            qset = Users.objects.values('univer_name').filter(id=qset['pk']).first()

            correct_s_num = Univers.objects.values('correct_s_num').filter(id=str(qset['univer_name'])).first()
            correct_s_num = int(correct_s_num['correct_s_num']) - 1
            Univers.objects.filter(id=qset['univer_name']).update(correct_s_num=correct_s_num)

            # Сохраняем модель
        super().save_model(request, obj, form, change)

    sound_display.short_description = 'sound'
    sound_display.allow_tags = True
    get_text.short_description = 'Text'
    get_user_name.short_description = 'User name'
    get_audio.short_description = 'Audio'

class UsersAdmin(admin.ModelAdmin):
    # form = MyModel
    list_display = (
    'id', 'univer_name', 'user_name', 'written_s_num', 'incorrect_s_num', 'finished_s_num', 'correct_s_num')
    list_display_links = ('id',)
    search_fields = ('univer_name', 'user_name',)
    list_filter = ('univer_name', 'user_name',)
    list_editable = ('written_s_num', 'incorrect_s_num', 'finished_s_num', 'correct_s_num')
    fields = ('univer_name', 'user_name', 'written_s_num', 'incorrect_s_num', 'finished_s_num', 'correct_s_num')

        # def save_model(self, request, obj, form, change):
        #     # Проверяем, изменилось ли поле 'number'
        #     if change and 'number' in form.changed_data:
        #         print(2142352)
        #         # Выполняем необходимое действие
        #         # Например, вы можете добавить свой код здесь
        #         print(f'Поле "number" изменилось для пользователя с ID {obj.id}')
        #
        #     # Сохраняем модель
        #     super().save_model(request, obj, form, change)

class UniversAdmin(admin.ModelAdmin):
    # form = MyModel
    list_display = ('id', 'univer_name', 'written_s_num', 'incorrect_s_num', 'finished_s_num', 'correct_s_num')
    list_display_links = ('id',)
    search_fields = ('univer_name',)
    list_filter = ('univer_name',)
    list_editable = ('written_s_num', 'incorrect_s_num', 'finished_s_num', 'correct_s_num')
    fields = ('univer_name', 'written_s_num', 'incorrect_s_num', 'finished_s_num', 'correct_s_num')

admin.site.register(Audios, AudiosAdmin)
admin.site.register(Users, UsersAdmin)
admin.site.register(Univers, UniversAdmin)
