import time
import os
import logging
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from PIL import Image

gauth = GoogleAuth()
drive = GoogleDrive(gauth)

input_folder = '1ewG7eCcYQpoUD9VsfTBeDtCWbfUgcWNb'

logging.basicConfig(filename='logfile.log', level=logging.DEBUG)

class FileProcess:

    def __init__(self, home_dir='.'):
        self.home_dir = home_dir
        self.input_dir = self.home_dir + os.path.sep + 'input'
        self.output_dir = self.home_dir + os.path.sep + 'output'

    def download_from_drive(self, img_drive_link):

        if not img_drive_link:
            print('Google drive input link not provided')

        os.makedirs(self.input_dir, exist_ok=True)

        logging.info("Image download from drive started / in progress")

        file_list = drive.ListFile({'q': f"'{input_folder}' in parents and trashed=false"}).GetList()

        start = time.perf_counter()
        for index, file in enumerate(file_list):
            print(index + 1, 'file downloaded : ', file['title'])
            file.GetContentFile(f"./input/{file['title']}")
        stop = time.perf_counter()

        logging.info(f"A total of {len(file_list)} images have been downloaded from Drive in {stop-start} seconds")

    def perform_resizing(self):
        # validate inputs
        if not os.listdir(self.input_dir):
            return
        os.makedirs(self.output_dir, exist_ok=True)

        logging.info("Image processing has started...")
        target_sizes = [32, 64, 128, 256, 512]
        num_images = len(os.listdir(self.input_dir))

        start = time.perf_counter()
        for filename in os.listdir(self.input_dir):
            orig_img = Image.open(self.input_dir + os.path.sep + filename)
            for bw in target_sizes:
                img = orig_img

                wp = (bw / float(img.size[0]))
                hsize = int((float(img.size[1]) * float(wp)))

                img = img.resize((bw, hsize))

                new_filename = os.path.splitext(filename)[0] + \
                               '_' + str(bw) + os.path.splitext(filename)[1]
                img.save(self.output_dir + os.path.sep + new_filename)

            os.remove(self.input_dir + os.path.sep + filename)
        end = time.perf_counter()

        logging.info("Processed {} images in {} seconds".format(num_images, end - start))

    def file_process(self, img_drive_link):
        self.download_from_drive(img_drive_link)
        self.perform_resizing()


file_proc = FileProcess()
file_proc.file_process(img_drive_link=input_folder)




