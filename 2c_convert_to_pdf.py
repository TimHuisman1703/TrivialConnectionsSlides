import cv2
import os
from PIL import Image

from utils import *

DIRECTORY = os.path.realpath(os.path.dirname(__file__))
OUTPUT_DIRECTORY = f"{DIRECTORY}/output"

videos = read_output_videos()

pages = [Image.fromarray(cv2.cvtColor(video[-1], cv2.COLOR_BGR2RGB)) for video in videos]
pages[0].save(f"{DIRECTORY}/output.pdf", "PDF", resolution=100.0, save_all=True, append_images=pages[1:])

print(f"\033[32;1mDone!\033[0m")
