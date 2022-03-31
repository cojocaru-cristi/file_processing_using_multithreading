import logging
import multiprocessing
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from queue import Queue
from threading import Thread
import time
import zipfile

from PIL import Image

drive = GoogleDrive(GoogleAuth())

# Unique IDs of Google drive folders which are used in the download and upload process

input_folder = '1ewG7eCcYQpoUD9VsfTBeDtCWbfUgcWNb'
output_folder = '1My1BIwpXigJOgDif7a-c3BYyG8929tdL'

# File types that will be included into a compressed folder

ext = [".txt", ".docs", ".ppt", ".xlsx", ".pdf", ".docx", ".ods"]

# Format of the log messages which will be written into the logfile

FORMAT = "[%(threadName)s, %(asctime)s, %(levelname)s] %(message)s"
logging.basicConfig(filename='logfile.log', level=logging.DEBUG, format=FORMAT)


class FileProcess:

    def __init__(self, home_dir='.'):
        self.home_dir = home_dir
        self.input_dir = self.home_dir + os.path.sep + 'input'
        self.output_dir = self.home_dir + os.path.sep + 'output'
        self.img_list = []
        self.compress_list = []

    # Download method implemented with the queue mechanism
    def download_file(self, download_queue):
        while not download_queue.empty():
            try:
                file = download_queue.get(block=False)
                print("Downloading file: {}".format(file['originalFilename']))
                file.GetContentFile(f"./input/{file['title']}")

                if file['originalFilename'].endswith(tuple(ext)):
                    self.compress_list.append(file['title'])
                else:
                    self.img_list.append(file['title'])

                download_queue.task_done()
            except Queue.Empty:
                logging.info("Queue empty")

    # Upload method
    def upload_to_drive(self, up_drive_link):

        if not up_drive_link:
            return False

        start = time.perf_counter()

        for i in os.listdir(self.output_dir):

            filename = os.path.join(self.output_dir, i)
            gfile = drive.CreateFile({'parents': [{'id': output_folder}], 'title': i})
            gfile.SetContentFile(filename)
            gfile.Upload()

        stop = time.perf_counter()

        print("Files uploaded to drive in {}".format(stop-start))

    # Image processing method
    def resize_image(self, filename):

        target_sizes = [32, 64, 128, 256, 512]

        if filename.endswith(".jpg"):
            logging.info("Resizing image {}".format(filename))
            orig_img = Image.open(self.input_dir + os.path.sep + filename)
            for w in target_sizes:
                img = orig_img

                ratio = (w / float(img.size[0]))
                h = int((float(img.size[1]) * float(ratio)))

                img = img.resize((w, h))

                new_filename = os.path.splitext(filename)[0] + '_' + str(w) + os.path.splitext(filename)[1]
                img.save(self.output_dir + os.path.sep + new_filename)

            os.remove(self.input_dir + os.path.sep + filename)
            logging.info("Done resizing image {}".format(filename))
        else:
            logging.info("File {} is not an image".format(filename))

    # File compression method
    def compress_file(self, filename):

        arch_zip = zipfile.ZipFile(self.output_dir + os.path.sep + "files.zip", 'w')

        for folder, subfolder, files in os.walk(self.input_dir + os.path.sep):

            for filename in files:
                if filename.endswith(tuple(ext)):
                    logging.info("Compressing file {}".format(filename))
                    arch_zip.write(os.path.join(folder, filename), os.path.relpath(os.path.join(folder, filename),
                                   self.output_dir + os.path.sep), compress_type=zipfile.ZIP_LZMA)
                    #os.remove(self.input_dir + os.path.sep + filename)

        arch_zip.close()

    def process_files(self, download_drive_link, upload_drive_link):

        logging.info("Start processing files:")
        image_pool = multiprocessing.Pool()
        file_pool = multiprocessing.Pool()
        start = time.perf_counter()

        start_download = time.perf_counter()
        download_queue = Queue()

        file_list_in = drive.ListFile({'q': f"'{input_folder}' in parents and trashed=false"}).GetList()
        for link in file_list_in:
            download_queue.put(link)

        num_threads = 4
        for _ in range(num_threads):
            t = Thread(target = self.download_file, args=(download_queue,))
            t.start()

        download_queue.join()

        stop_download = time.perf_counter()

        start_process = time.perf_counter()
        image_pool.map(self.resize_image, self.img_list)
        stop_process = time.perf_counter()

        start_process1 = time.perf_counter()
        file_pool.map(self.compress_file, self.compress_list)
        stop_process1 = time.perf_counter()

        end = time.perf_counter()

        image_pool.close()
        image_pool.join()
        file_pool.close()
        file_pool.join()

        logging.info("Download time for the files is {}.".format(stop_download-start_download))
        logging.info("Processed {} images in {} seconds".format(len(self.img_list), stop_process-start_process))
        logging.info("Compressed {} files in {} seconds".format(len(self.compress_list), stop_process1 - start_process1))
        logging.info(f'End of all tasks in {end-start} seconds')

        self.upload_to_drive(up_drive_link=output_folder)


if __name__ == '__main__':

    file_list = FileProcess()
    file_list.process_files(download_drive_link=input_folder, upload_drive_link=output_folder)