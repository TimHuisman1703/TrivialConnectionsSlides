import cv2
import os
from PIL import Image

DIRECTORY = os.path.realpath(os.path.dirname(__file__))
OUTPUT_DIRECTORY = f"{DIRECTORY}/output"

cap_filenames = ["output/" + filename for filename in sorted(os.listdir(OUTPUT_DIRECTORY)) if filename.endswith(".mp4")]

pages = []
for cap_filename in cap_filenames:
    cap = cv2.VideoCapture(cap_filename)

    frames = []
    while cap.isOpened():
        ret, frame = cap.read()
        if ret == False:
            break
        frames.append(frame)
    pages.append(frames[-1])

    cap.release()

    print(f"\033[30;1mLoaded {cap_filename}\033[0m")

pages = [Image.fromarray(cv2.cvtColor(page, cv2.COLOR_BGR2RGB)) for page in pages]
pages[0].save(f"{DIRECTORY}/output.pdf", "PDF", resolution=100.0, save_all=True, append_images=pages[1:])

print(f"\033[32;1mDone!\033[0m")
