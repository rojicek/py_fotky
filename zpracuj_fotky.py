# py 3.10

import imageio
import numpy as np
import os

folder = r'c:\Users\jiri\Documents\multimedia\zpracovat\_nove-ala\test_folder'

# videa kratsi nez X jsou smazana (protoze live photo)
max_delka = 5

for root, _, files in os.walk(folder):
    for file in files:
        file_path = os.path.join(root, file)

        # .AAE suffix -> smazat
        if file.lower().endswith('.aae'):
            os.remove(file_path)

        # mov - smaz kratsi nez 5s
        if file.lower().endswith('.mov'):
            vid = imageio.get_reader(file_path, 'ffmpeg')
            delka = vid.get_meta_data()['duration']
            vid.close()

            if delka < max_delka:
                os.remove(file_path)

        # heic

print('konec')

