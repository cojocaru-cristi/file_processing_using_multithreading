import time
import os
import logging
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import threading

from PIL import Image

gauth = GoogleAuth()
drive = GoogleDrive(gauth)

input_folder = '1ewG7eCcYQpoUD9VsfTBeDtCWbfUgcWNb'
output_folder = '1My1BIwpXigJOgDif7a-c3BYyG8929tdL'

FORMAT = "[%(threadName)s, %(asctime)s, %(levelname)s] %(message)s"

logging.basicConfig(filename='logfile.log', level=logging.DEBUG, format=FORMAT)


class FileProcessing:

    def download_image(self, index, file):

        with self.max_download_semaphore:
            logging.info(f"download image {file['title']}")
            print(index + 1, 'file downloaded : ', file['title'])
            dest_path= self.input_dir + os.path.sep + file['title']

            file.GetContentFile(dest_path)
            file_size = os.path.getsize(dest_path)
            with self.size_lock:
                self.downloaded_bytes += file_size
            logging.info(f'file of size {file_size} bytes was stored ')

    def upload_to_drive(self, up_drive_link):

        if not up_drive_link:
            return False

        start = time.perf_counter()
        for i in os.listdir(self.output_dir):
            filename = os.path.join(self.output_dir, i)
            gfile = drive.CreateFile({'parents' : [{'id' : output_folder}], 'title': i})
            gfile.SetContentFile(filename)
            gfile.Upload()
            #os.remove(self.input_dir + os.path.sep + filename)
        stop = time.perf_counter()
        print(stop-start)

    def download_from_drive(self, img_drive_link):

        if not img_drive_link:
            return False

        os.makedirs(self.input_dir, exist_ok=True)

        logging.info("Image download from drive started / in progress")

        file_list = drive.ListFile({'q': f"'{input_folder}' in parents and trashed=false"}).GetList()

        start = time.perf_counter()
        threads = []
        for index, file in enumerate(file_list):
            t = threading.Thread(target=self.download_image, args=(index,file,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        stop = time.perf_counter()

        logging.info(f"A total of {len(file_list)} images have been downloaded from Drive in {stop-start} seconds")

    def perform_resizing(self):
        # validate inputs
        if not os.listdir(self.input_dir):
            return
        os.makedirs(self.output_dir, exist_ok=True)

        logging.info("Started the processing parte of the files")
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

        logging.info("created {} thumbnails in {} seconds".format(num_images, end - start))

    def process_files(self, img_drive_link, up_drive_link):
        self.download_from_drive(img_drive_link)
        self.perform_resizing()
        #self.upload_to_drive(up_drive_link)

    def __init__(self, home_dir='.'):
        self.home_dir = home_dir
        self.input_dir = self.home_dir + os.path.sep + 'input'
        self.output_dir = self.home_dir + os.path.sep + 'output'
        self.downloaded_bytes = 0
        self.size_lock = threading.Lock()
        max_file_download = 20
        self.max_download_semaphore = threading.Semaphore(max_file_download)


file_process = FileProcessing()
file_process.process_files(img_drive_link=input_folder, up_drive_link=output_folder)