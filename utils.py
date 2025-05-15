import cv2
import os
import numpy as np

DIRECTORY = os.path.realpath(os.path.dirname(__file__))
RENDER_DIRECTORY = f"{DIRECTORY}/media/images/1_render"
OUTPUT_DIRECTORY = f"{DIRECTORY}/output"

PAUSE_MARKER_COLOR = [86, 52, 18]
PAUSE_MARKER_COLOR_HEX = "#" + "".join(f"{hex(c)[2:]:02}" for c in PAUSE_MARKER_COLOR[::-1])

BLACK = "#000000"
DARK_GREY = "#3F3F3F"
GREY = "#7F7F7F"
LIGHT_GREY = "#BFBFBF"
WHITE = "#FFFFFF"
RED = "#C3312F"
ORANGE = "#EB7246"
YELLOW = "#F1BE3E"
GREEN = "#00A390"
CYAN = "00A6D6"
BLUE = "#0065A1"
ICO_BLUE = "#41808E"
PURPLE = "#6311B7"

def read_output_videos():
    frame_filenames = sorted(f"{OUTPUT_DIRECTORY}/{filename}" for filename in sorted(os.listdir(OUTPUT_DIRECTORY)))

    videos = [[]]
    for frame_filename in frame_filenames:
        frame = cv2.imread(frame_filename)
        if all(list(frame[np.random.randint(0, frame.shape[0]), np.random.randint(0, frame.shape[1])]) == PAUSE_MARKER_COLOR for _ in range(100)):
            print(f"\033[30;1mLoaded video #{len(videos)} ({len(videos[-1])} frame{'s' * (len(videos[-1]) != 1)})\033[0m")
            videos.append([])
        else:
            videos[-1].append(frame)

    while not videos[-1]:
        videos.pop()
    
    return videos