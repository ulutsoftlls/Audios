import random

import markdown, sys, os
import markdown
import time
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.core.cache import cache
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.views.generic import ListView, DetailView, CreateView
from django.shortcuts import render, redirect, get_object_or_404
from analyzer.forms import *
from two_level_morphanalyzer.settings import MEDIA_URL
from .models import *
from .forms import *
from django.urls import reverse_lazy
from django.db import connection
from django.http import JsonResponse

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
import mimetypes
from django.http.response import HttpResponse, HttpResponseNotFound, Http404
from django.views.decorators.cache import cache_page
from django.contrib.sessions.backends.db import SessionStore
from django.db.models import Max


navbar = [
          {'title': 'Кирүү', 'url': 'login'},
          ]
user_names = ['user01','user02','user03','user04','user05']

context = {}

file_result = ''
class AudiosHome(ListView):
    model = Audios
    template_name = 'analyzer/index.html'
    context_object_name = 'audios'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Башкы бет'
        context['navbar'] = navbar
        context['cat_selected'] = 0
        return context

    def get_queryset(self):
        return Audios.objects.filter(status=False)

class ShowAudio(DetailView):
    model = Audios
    context_object_name = 'audio'
    template_name = 'analyzer/audio.html'
    pk_url_kwarg = 'audio_id'
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        form = TextForm()
        context['title'] = 'Угуп жазуу'
        context['navbar'] = navbar
        context['form'] = form
        return context
    def get_queryset(self):
        return Audios.objects.filter(status=False)
def text_reader(context, text):
    context['text'] = text
    return context


def home(request):
    form = TextForm()
    title = 'Башкы бет'
    context = {
        'form': form,
        'title': title,
        'navbar': navbar,
        'cat_selected': 0,
    }
    return render(request, 'analyzer/index.html', context=context)


def about(request):
    title = 'Биз жөнүндө'

    with open("analyzer/about.md", "r", encoding="utf-8") as md_file:
        html = markdown.markdown(md_file.read(), extensions=["fenced_code"])
    context = {
        'title': title,
        'navbar': navbar,
        'html': html,
    }
    return render(request, 'analyzer/about.html', context=context)







@cache_page(60 * 1)
@csrf_protect
@csrf_exempt
def text(request):

    context = {}
    if request.method == 'POST':
        text = request.POST['text']
        audio_id = request.POST['audio_id']
        audio_file_url = request.POST['audio_file']
        if not audio_id:
            redirect('home')
        form = TextForm(request.POST)
        if 'main_sumbit' in request.POST:
            if form.is_valid() and not form.cleaned_data['text']:
                #the form is empty
                context = {
                    'title': 'Угуп жазуу',
                    'navbar': navbar,
                    'form': form,
                    'audio_id': audio_id,
                    'audio_file_url': audio_file_url,
                    'finished_sound_number': request.session['s_num'],
                    'form_empty': True
                }
                # return redirect("audio", audio_id=audio_id[0])
                return render(request, "analyzer/audio.html", context=context)
            if form.is_valid():
                #print(request.session['user_id'])
                #print(user_name_id)
                qset = Audios.objects.values('is_correct').filter(id=audio_id,status=False).first()
                if not qset['is_correct']:
                    Audios.objects.filter(id=audio_id).update(text=text, is_correct=True, user_name=request.session['user_id'])

                    #print(request.session['s_num'])
                    request.session['s_num'] = Users.objects.values('written_s_num').filter(
                        id=request.session['user_id']).first()
                    request.session['s_num'] = int(request.session['s_num']['written_s_num'])+ 1
                    Users.objects.filter(id=request.session['user_id']).update(written_s_num=request.session['s_num'])

                    request.session['fin_num'] = Users.objects.values('finished_s_num').filter(
                        id=request.session['user_id']).first()
                    request.session['fin_num'] = int(request.session['fin_num']['finished_s_num']) + 1
                    Users.objects.filter(id=request.session['user_id']).update(finished_s_num=request.session['fin_num'])

                    request.session['univ_num'] = Univers.objects.values('written_s_num').filter(id=request.session['univer_id']).first()
                    request.session['univ_num'] = int(request.session['univ_num']['written_s_num']) + 1
                    Univers.objects.filter(id=request.session['univer_id']).update(written_s_num=request.session['univ_num'])

                    request.session['finished_s_num'] = Univers.objects.values('finished_s_num').filter(
                        id=request.session['univer_id']).first()
                    request.session['finished_s_num'] = int(request.session['finished_s_num']['finished_s_num']) + 1
                    Univers.objects.filter(id=request.session['univer_id']).update(finished_s_num=request.session['finished_s_num'])
                qset = Audios.objects.values('pk').filter(status=False, is_correct=False)
                # request.session['s_id_list'] = list(qset)
                # #print(request.session['s_id_list'])
                if not qset:
                    context = {
                        'no_audio': True,
                        'title': 'Башкы бет',
                        'navbar': navbar,
                        'user_name': request.session['name']
                    }
                    return render(request, "analyzer/index.html", context=context)
                request.session['audios_id'] = random.choice(list([i['pk'] for i in list(qset)]))
                qset2 = Audios.objects.values('audio_file', 'text').filter(id=request.session['audios_id']).first()
                request.session['audio_url'] = qset2['audio_file']
                request.session['audio_url'] = MEDIA_URL + request.session['audio_url']
                if qset2['text']:
                    form = TextForm(initial={'text': str(qset2['text'])})
                    #form = TextForm()
                    context = {
                        'title': 'Угуп жазуу',
                        'navbar': navbar,
                        'form': form,
                        'audio_id': request.session['audios_id'],
                        'audio_file_url': request.session['audio_url'],
                        'is_not_valid': False,
                        'finished_sound_number': request.session['s_num'],
                        'text': qset2['text']
                    }
                    # return redirect("audio", audio_id=audio_id[0])
                    return render(request, "analyzer/audio.html", context=context)
                else:

                    form = TextForm()
                    context = {
                        'title': 'Угуп жазуу',
                        'navbar': navbar,
                        'form': form,
                        'audio_id': request.session['audios_id'],
                        'audio_file_url': request.session['audio_url'],
                        'is_not_valid': False,
                        'finished_sound_number': request.session['s_num'],
                        'text': False
                    }
                    # return redirect("audio", audio_id=audio_id[0])
                    return render(request, "analyzer/audio.html", context=context)
                # return redirect("audio", audio_id=request.session['audios_id'])
            else:
                # print('form is not valid')
                context = {
                    'title': 'Угуп жазуу',
                    'navbar': navbar,
                    'form': form,
                    'audio_id': audio_id,
                    'audio_file_url': audio_file_url,
                    'is_not_valid': True
                }
                # return redirect("audio", audio_id=audio_id[0])
                return render(request, "analyzer/audio.html", context=context)
        elif 'not_understand' in request.POST:
            text = '*'
            qset = Audios.objects.values('is_correct').filter(id=audio_id, status=False).first()
            if not qset['is_correct']:
                Audios.objects.filter(id=audio_id).update(text=text, is_correct=True,
                                                          user_name=request.session['user_id'])

            qset = Audios.objects.values('pk').filter(status=False, is_correct=False)
            if not qset:
                context = {
                    'no_audio': True,
                    'title': 'Башкы бет',
                    'navbar': navbar,
                    'user_name': request.session['name']
                }
                return render(request, "analyzer/index.html", context=context)
            request.session['audios_id'] = random.choice(list([i['pk'] for i in list(qset)]))
            qset = Audios.objects.values('audio_file', 'text').filter(id=request.session['audios_id']).first()
            request.session['audio_url'] = qset['audio_file']
            request.session['audio_url'] = MEDIA_URL + request.session['audio_url']
            if qset['text']:
                form = TextForm()
                context = {
                    'title': 'Угуп жазуу',
                    'navbar': navbar,
                    'form': form,
                    'audio_id': request.session['audios_id'],
                    'audio_file_url': request.session['audio_url'],
                    'is_not_valid': False,
                    'finished_sound_number': request.session['s_num'],
                    'text': qset['text']
                }
                # return redirect("audio", audio_id=audio_id[0])
                return render(request, "analyzer/audio.html", context=context)
            else:
                form = TextForm()
                context = {
                    'title': 'Угуп жазуу',
                    'navbar': navbar,
                    'form': form,
                    'audio_id': request.session['audios_id'],
                    'audio_file_url': request.session['audio_url'],
                    'is_not_valid': False,
                    'finished_sound_number': request.session['s_num'],
                    'text': False
                }
                # return redirect("audio", audio_id=audio_id[0])
                return render(request, "analyzer/audio.html", context=context)

    else:
        form = TextForm(request.POST)
        context = {
        'title': 'Угуп жазуу',
        'navbar': navbar,
        'form': form,
        }
    return redirect("audio", audio_id=request.session['audios_id'][0])


def pageNotFound(request, exception):
    #return redirect('home', permanent=False)
    return HttpResponseNotFound('<h1>Page not found</h1>')

# class RegisterUser(CreateView):
#     form_class = UserCreationForm
#     template_name = 'analyzer/register.html'
#     success_url = reverse_lazy('login')
#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super().get_context_data(**kwargs)
#         return context

#@cache_page(60 * 5)
@csrf_protect
@csrf_exempt
def login(request):
    if request.method == 'POST':
        form = User_nameForm(request.POST)
        form2 = TextForm(request.POST)
        if form.is_valid():
            request.session['univer_name'] = request.POST["univer_name"]
            request.session['name'] = str(request.session["univer_name"])+'_'+str(request.POST['user_name'])

            qset = Users.objects.values('pk').filter(user_name=request.session['name']).first()
            qset2 = Univers.objects.values('pk').filter(univer_name=request.session['univer_name']).first()
            request.session['univer_id'] = qset2['pk']
            
            # qset = Univers.objects.values('pk').filter(univer_name=univer_name).first()

            if qset:

                # if 'name' in request.session and request.session['name']==user_name:

                qset = Users.objects.values('pk').filter(user_name=request.session['name']).first()
                # print(qset)
                request.session['user_id'] = qset['pk']
                request.session['s_num'] = Users.objects.values('written_s_num').filter(
                    id=request.session['user_id']).first()
                request.session['s_num'] = request.session['s_num']['written_s_num']
                # print('name is exist')
                qset = Audios.objects.values('pk').filter(status=False, is_correct=False)
                # request.session['s_id_list'] = list(qset)
                # print(request.session['s_id_list'])
                if not qset:
                    context = {
                        'no_audio': True,
                        'title': 'Башкы бет',
                        'navbar': navbar,
                        'user_name': request.session['name']
                    }
                    return render(request, "analyzer/index.html", context=context)
                request.session['audios_id'] = random.choice(list([i['pk'] for i in list(qset)]))
                qset = Audios.objects.values('audio_file', 'text').filter(id=request.session['audios_id']).first()

                request.session['audio_url'] = qset['audio_file']
                request.session['audio_url'] = MEDIA_URL + request.session['audio_url']
                if qset['text']:
                    context = {
                        'title': 'Угуп жазуу',
                        'navbar': navbar,
                        'form': form2,
                        'audio_id': request.session['audios_id'],
                        'audio_file_url': request.session['audio_url'],
                        'is_not_valid': False,
                        'finished_sound_number': request.session['s_num'],
                        'text': qset['text']
                    }
                else:
                    context = {
                        'title': 'Угуп жазуу',
                        'navbar': navbar,
                        'form': form2,
                        'audio_id': request.session['audios_id'],
                        'audio_file_url': request.session['audio_url'],
                        'is_not_valid': False,
                        'finished_sound_number': request.session['s_num'],
                        'text': False
                    }
                return render(request, "analyzer/audio.html", context=context)

            else:
                # print('not found')
                # print(request.session['name'])
                created = Users.objects.create(user_name=request.session['name'])
                created.save()
                Users.objects.filter(user_name=request.session['name']).update(univer_name=request.session['univer_id'])
                qset = Users.objects.values('pk').filter(user_name=request.session['name']).first()
                # print(qset)
                request.session['user_id'] = qset['pk']
                request.session['s_num'] = Users.objects.values('written_s_num').filter(
                    id=request.session['user_id']).first()
                request.session['s_num'] = request.session['s_num']['written_s_num']
                # print('name is not exist')
                qset = Audios.objects.values('pk').filter(status=False, is_correct=False)
                # request.session['s_id_list'] = list(qset)
                # print(request.session['s_id_list'])
                if not qset:
                    context = {
                        'no_audio': True,
                        'title': 'Башкы бет',
                        'navbar': navbar,
                        'user_name': request.session['name']
                    }
                    return render(request, "analyzer/index.html", context=context)
                request.session['audios_id'] = random.choice(list([i['pk'] for i in list(qset)]))
                qset = Audios.objects.values('audio_file', 'text').filter(id=request.session['audios_id']).first()

                request.session['audio_url'] = qset['audio_file']
                request.session['audio_url'] = MEDIA_URL + request.session['audio_url']
                if qset['text']:
                    context = {
                        'title': 'Угуп жазуу',
                        'navbar': navbar,
                        'form': form2,
                        'audio_id': request.session['audios_id'],
                        'audio_file_url': request.session['audio_url'],
                        'is_not_valid': False,
                        'finished_sound_number': request.session['s_num'],
                        'text': qset['text']
                    }
                else:
                    context = {
                        'title': 'Угуп жазуу',
                        'navbar': navbar,
                        'form': form2,
                        'audio_id': request.session['audios_id'],
                        'audio_file_url': request.session['audio_url'],
                        'is_not_valid': False,
                        'finished_sound_number': request.session['s_num'],
                        'text': False
                    }
                return render(request, "analyzer/audio.html", context=context)
        form = User_nameForm(request.POST)
        # user_not_found = True
        context = {
            'title': "Кирүү",
            'navbar': navbar,
            'form': form,
            'form_error': True
            # 'user_name': user_name,
            # 'user_not_found': user_not_found
        }
        return render(request, 'analyzer/login.html', context=context)
    else:
        form = User_nameForm(request.POST)
    context = {
        'title': 'Кирүү',
        'navbar': navbar,
        'form': form,
    }
    return render(request, 'analyzer/login.html', context=context)




