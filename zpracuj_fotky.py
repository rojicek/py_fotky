# py 3.10

import imageio
import numpy as np
import os
from PIL import Image
import matplotlib.pyplot as plt
import re
import shutil
import PIL
#from PIL.ExifTags import TAGS
import datetime
import exifread



def set_file_timestamp_from_exif(heic_path):
    with open(heic_path, 'rb') as f:
        # Read EXIF data using exifread
        tags = exifread.process_file(f)

        # Extract the DateTimeOriginal tag
        datetime_original = tags.get('EXIF DateTimeOriginal')

        if datetime_original:
            # Convert the DateTimeOriginal value to a datetime object
            dt_object = datetime.strptime(str(datetime_original), "%Y:%m:%d %H:%M:%S")

            # Get the timestamp from the datetime object
            timestamp = dt_object.timestamp()

            # Set the file timestamp using os.utime
            os.utime(heic_path, (timestamp, timestamp))
            print(f"File timestamp set based on EXIF data: {dt_object}")
        else:
            print("No DateTimeOriginal tag found in EXIF data.")

def delete_all_subfolders(folder_path):
    # Iterate over all subfolders in the specified directory
    for subfolder in os.listdir(folder_path):
        subfolder_path = os.path.join(folder_path, subfolder)

        # Check if the subfolder is a directory
        if os.path.isdir(subfolder_path):
            shutil.rmtree(subfolder_path)


def get_files_in_folder(folder_path):
    files_list = []
    for root, dirs, files in os.walk(folder_path):
        for f in files:
            files_list.append(f)
    return files_list


folder = r'c:\Users\jiri\Documents\multimedia\zpracovat\_nove-ala\test_folder'

delete_all_subfolders(folder)

folder_keep = os.path.join(folder, 'keep')
folder_check = os.path.join(folder, 'kontrola')
folder_remove = os.path.join(folder, 'smazat')
folder_jpg = os.path.join(folder, 'jpg')
folder_mov = os.path.join(folder, 'mov')

os.makedirs(folder_keep)
os.makedirs(folder_check)
os.makedirs(folder_remove)
os.makedirs(folder_jpg)
os.makedirs(folder_mov)

# videa kratsi nez X jsou smazana (protoze live photo)
max_delka = 5  # sec


all_files = get_files_in_folder(folder)

# projdi vsechny heic a prepis casovou znacku z EXIF
for file in all_files:

    file_path = os.path.join(folder, file)
    if file.lower().endswith('.heic'):
        if os.path.isfile(file_path):
            set_file_timestamp_from_exif(file_path)



for file in all_files:
    file_path = os.path.join(folder, file)
    # .AAE suffix -> smazat (ani nedavam ke kontrole)
    if file.lower().endswith('.aae'):
        os.remove(file_path)

    # .jpg or png
    if file.lower().endswith('.jpg') or file.lower().endswith('.png'):
        shutil.move(file_path, os.path.join(folder_jpg, file))

    # mov - smaz kratsi nez 5s
    if file.lower().endswith('.mp4') or file.lower().endswith('.mov'):
        vid = imageio.get_reader(file_path)
        delka = vid.get_meta_data()['duration']
        vid.close()

        if delka < max_delka:
            # move to "remove"
            shutil.move(file_path, folder_remove)
        else:
            # ostatni mov do keep
            print(file_path)
            print('---------')
            shutil.move(file_path, folder_mov)

    # heic
    pattern1 = re.compile('^img_[0-9]{4}.heic')
    if pattern1.match(file.lower()) and False:
        e_name = file[0:4] + 'E' + file[4:]
        if os.path.isfile(os.path.join(folder, e_name)):
            # existuji oba dva
            one_pic_folder = os.path.join(folder, 'dir-'+file[:-5])
            os.makedirs(one_pic_folder)
            shutil.move(file_path,one_pic_folder)
            shutil.move(os.path.join(folder, e_name), one_pic_folder)

    pattern2 = re.compile('^img_e[0-9]{4}.heic')
    if pattern2.match(file.lower()):
        h_name = file[0:4] + file[5:]
        if os.path.isfile(os.path.join(folder, h_name)):
            # existuji oba dva
            one_pic_folder = os.path.join(folder, 'dir-'+file[:-5])
            os.makedirs(one_pic_folder)
            shutil.move(file_path,one_pic_folder)
            shutil.move(os.path.join(folder, h_name), one_pic_folder)

# zkopiruj jen ty heic co zbudou
for file in all_files:
    # ostatni heic do keep

    file_path = os.path.join(folder, file)
    if file.lower().endswith('.heic'):
        if os.path.isfile(file_path):
            shutil.move(file_path, os.path.join(folder_keep, file))



print('konec')

