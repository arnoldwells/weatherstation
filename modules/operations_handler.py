import os
import logging
from data.env import DEBUG
from datetime import datetime
from modules.drive_api import get_file_list, upload_image

logger = logging.getLogger(__name__)
    
class OperationsHandler:
    def __init__(self):
        self.mode = "weather"
        self.art_images = []
        self.iterations = 0
        self.latest_file = ""
    
    def seconds_to_midnight():
        now = datetime.now()
        return (now.replace(hour=23, minute=59, second=59, microsecond=0) - now).total_seconds()

    def a_pressed(self):
        logger.info("A pressed")
        if self.mode == "weather":                                                      # exit
            if DEBUG: os._exit(os.EX_OK)
            else: os.system('sudo systemctl poweroff')
        self.mode = "weather"
        self.art_images = []                                                            # clear art_images list
        self.iterations = 0
        logger.info(f"mode: {self.mode} images: {len(self.art_images)} iterations: {self.iterations}")

    def b_pressed(self):
        logger.info("B pressed")
        if self.mode == "slideshow":                                                    # switch to artimage
            self.mode = "artimage"
            self.art_images = [(self.latest_file, "artimage")]
        else:                                                                           # switch to slideshow
            self.mode = "slideshow"
            self.art_images = get_file_list()                                           # retrieve list from google drive
        self.iterations = 0
        logger.info(f"mode: {self.mode} images: {len(self.art_images)} iterations: {self.iterations}")

    def c_pressed(self):
        logger.info("C pressed")
        if self.mode == "weather":                                                      # switch to artimage
            self.mode = "artimage"
            self.art_images = [(self.latest_file, "artimage")]
        else:
            self.iterations = (self.seconds_to_midnight() / 1800)                       # pause
        logger.info(f"mode: {self.mode} images: {len(self.art_images)} iterations: {self.iterations}")

    def d_pressed(self):                                                                # save artimage to google drive
        logger.info("D pressed")
        upload_image(self.latest_file)  

    def int_handler(self, signum, frame):
        logger.warning(f"exit from script")
        os._exit(os.EX_OK)

    def get_latest_file(self):
        from glob import glob
        files = glob("generated/20?[0-9]-*.jpg")
        logger.info(f"found [{len(files)}] files")
        if files:
            self.latest_file = max(files, key=os.path.getctime)
        else:
            self.latest_file = "images/file-error.png"
        logger.info(f"latest file: {self.latest_file}" )        