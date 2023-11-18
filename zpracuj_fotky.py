# py 3.10

import imageio
import numpy as np
import os
from PIL import Image
import matplotlib.pyplot as plt
import re
import shutil
import datetime
import exifread
import PIL
import pillow_heif
# from PIL import Image
# from pillow_heif import register_heif_opener

pillow_heif.register_heif_opener()


def reset_filestamp(heic_path):
    image = PIL.Image.open(heic_path)

    exif_data = image.getexif()
    original_date_str = exif_data[306]

    # Parse the string into a datetime object
    datetime_obj = datetime.datetime.strptime(original_date_str, '%Y:%m:%d %H:%M:%S').timestamp()
    os.utime(heic_path, times=(datetime_obj, datetime_obj))

    return


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


folder = r'c:\Users\jiri\Documents\multimedia\zpracovat\work_photos'

delete_all_subfolders(folder)

folder_keep = os.path.join(folder, 'keep')
folder_remove = os.path.join(folder, 'smazat')
folder_edited_remove = os.path.join(folder, 'e-smazat')
folder_jpg = os.path.join(folder, 'jpg')
folder_mov = os.path.join(folder, 'mov')

os.makedirs(folder_keep)
os.makedirs(folder_remove)
os.makedirs(folder_edited_remove)
os.makedirs(folder_jpg)
os.makedirs(folder_mov)

# videa kratsi nez X jsou smazana (protoze live photo)
max_delka = 5  # sec


all_files = get_files_in_folder(folder)

# projdi vsechny heic a prepis casovou znacku z EXIF
# i kdyz vetsinu potom smazu
for file in all_files:
    file_path = os.path.join(folder, file)
    if file.lower().endswith('.heic'):
        if os.path.isfile(file_path):
            reset_filestamp(file_path)


cnt = len(all_files)

for file in all_files:
    print(f'zbyva {cnt}')
    cnt = cnt - 1

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
            shutil.move(file_path, folder_mov)

    pattern_e = re.compile('^img_e[0-9]{4}.heic')
    if pattern_e.match(file.lower()):
        e_name = file
        h_name = file[0:4] + file[5:]

        # keep e_name
        shutil.move(os.path.join(folder, e_name), folder_keep)
        # delete h_name
        shutil.move(os.path.join(folder, h_name), folder_edited_remove)


# zkopiruj jen ty heic co zbudou
for file in all_files:
    # ostatni heic do keep

    file_path = os.path.join(folder, file)
    if file.lower().endswith('.heic'):
        if os.path.isfile(file_path):
            shutil.move(file_path, os.path.join(folder_keep, file))

print('konec')
