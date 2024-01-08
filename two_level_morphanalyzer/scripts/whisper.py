
import os
import os.path
import os
from tqdm import tqdm
from os import path
import shutil
import openpyxl
from django.core.management.base import BaseCommand
from analyzer.models import Audios, Users
from datetime import datetime
from scripts.speech2text import WhisperModel
from two_level_morphanalyzer.settings import MEDIA_URL
from pydub import AudioSegment
from two_level_morphanalyzer.settings import MEDIA_ROOT
import random
#print(all_files_in_directory)
path = 'Whisper/'
def run():
	whisper_model = WhisperModel()
	for i in tqdm(range(100)):
        	
		qset = Audios.objects.values('pk').filter(status=False, is_correct=False)
		pk = random.choice(list([i['pk'] for i in list(qset)]))
		qset = Audios.objects.values('audio_file').filter(id=pk).first()
		url = qset['audio_file']
		url = MEDIA_URL + url
		sound = AudioSegment.from_file(url[1:])
		sound = sound.set_frame_rate(16000)
		sound.export(MEDIA_ROOT+path+str(url[11:-4])+'.wav', format="wav")
		text = whisper_model.generate_text_from_audio(MEDIA_ROOT+path+str(url[11:-4])+'.wav')
		#print(str(url[11:-4]))
		os.remove(MEDIA_ROOT+path+str(url[11:-4])+'.wav')
		if len(text) > 300:
			text = text[:300]
		Audios.objects.filter(id=pk).update(text=text, is_correct=False, user_name=2)
		#user_name=2 is Whisper(checkpoint-2000)
		#user_name=5 is Whisper3000(checkpoint-3000)
		sum_n = Users.objects.values('number').filter(id=2).first()
		sum_n = int(sum_n['number']) + 1
		Users.objects.filter(id=2).update(number=sum_n)
	print('successfully ended')
