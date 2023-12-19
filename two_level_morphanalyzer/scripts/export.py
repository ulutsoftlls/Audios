
import os
import os.path
import os
from tqdm import tqdm
from os import path
import shutil
import openpyxl
from django.core.management.base import BaseCommand
from analyzer.models import Audios
from datetime import datetime


#print(all_files_in_directory)

def run():
        data = Audios.objects.values_list('audio_file', 'text').filter(status=False, is_correct=True)

        # Create a new Excel workbook
        wb = openpyxl.Workbook()
        ws = wb.active

        # Add headers to the worksheet
        ws.append(['audio_file', 'text'])  # Replace with your field names
        #print(data)
        # Add data to the worksheet
        for item in data:
                encoded_item = [str(field).encode('utf-8').decode() for field in item]
                ws.append(encoded_item)
                #ws.append(item)



        # Save the workbook to a file
        base_file_name = 'exported_'  # Set your desired base file name
        timestamp = datetime.now().strftime('%d%H%M%S')  # Add a timestamp
        file_path = f'{base_file_name}_{timestamp}.xlsx'  # Create a unique filename


        wb.save(file_path)


        print('successfully export')
