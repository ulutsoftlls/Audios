
import os
import os.path
import os
from tqdm import tqdm
from os import path
import shutil
path = '/mnt/ks/Works/site2/kyrgyz_morph_analyzer/two_level_morphanalyzer/media/'
from analyzer.models import Audios
all_files_in_directory = os.listdir(path)
#print(all_files_in_directory)
folder_name = ['003']
def run():
    for i in all_files_in_directory:
    	if i in folder_name:
    	    all_files_in_directory2 = os.listdir(path + str(i))
    	    for j in all_files_in_directory2:
    	    	allroot, created = Audios.objects.get_or_create(audio_file=str(i+"/"+j), super_visor='sup1', admin='admin1')
    	    print(i)
    	    print(created)
