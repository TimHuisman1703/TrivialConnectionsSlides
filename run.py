import cv2
import os
import screeninfo
import time

WINDOW_NAME = "Trivial Connections on Discrete Surfaces"
FULLSCREEN = True
MOUSE_CONTROLLED = True

DIRECTORY = os.path.realpath(os.path.dirname(__file__))
OUTPUT_DIRECTORY = f"{DIRECTORY}/output"

f = open(f"{OUTPUT_DIRECTORY}/halt_frames.txt")
halt_frames = {int(j) for j in f.read().split()}
f.close()

cap_filenames = ["output/" + filename for filename in sorted(os.listdir(OUTPUT_DIRECTORY)) if filename.endswith(".mp4")]

frames = []
framerate = None
for cap_filename in cap_filenames:
    cap = cv2.VideoCapture(cap_filename)

    if framerate == None:
        framerate = cap.get(cv2.CAP_PROP_FPS)

    curr_frames = []
    while cap.isOpened():
        ret, frame = cap.read()
        if ret == False:
            break
        curr_frames.append(frame)

    frames.append(curr_frames)

    print(f"\033[30;1mLoaded {cap_filename} ({len(curr_frames)} frames)\033[0m")
print(f"\033[32;1mRunning!\033[0m")

merged_frames = [[]]
for idx, curr_frames in enumerate(frames):
    merged_frames[-1].extend(curr_frames)
    if idx in halt_frames:
        merged_frames.append([])
while not merged_frames[-1]:
    merged_frames.pop()
frames = merged_frames

if FULLSCREEN:
    screen = screeninfo.get_monitors()[0]
    cv2.namedWindow(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN)
    cv2.moveWindow(WINDOW_NAME, screen.x - 1, screen.y - 1)
    cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
else:
    screen = screeninfo.get_monitors()[0]
    cv2.namedWindow(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN)
    cv2.moveWindow(WINDOW_NAME, screen.x - 1, screen.y - 1)
    cv2.resizeWindow(WINDOW_NAME, screen.width // 2, screen.height // 2)

action = -1
def click(event, x, y, flags, param):
    global action

    if event == cv2.EVENT_LBUTTONDOWN:
        action = 0
    elif event == cv2.EVENT_RBUTTONDOWN:
        action = 2

if MOUSE_CONTROLLED:
    cv2.setMouseCallback(WINDOW_NAME, click)

video_nr = 0
time_since_last_click = time.time()

while True:
    frame_nr = max(0, min(int((time.time() - time_since_last_click) * framerate), len(frames[video_nr]) - 1))
    cv2.imshow(WINDOW_NAME, frames[video_nr][frame_nr])
    key = cv2.waitKey(1)

    if key in [32, 13]:
        action = 0
    elif key in [100]:
        action = 1
    elif key in [2162688, 2490368, 2424832, 97]:
        action = 2
    elif key in [27]:
        action = 3

    if action == 0:
        if video_nr < len(frames) - 1:
            video_nr += 1
            time_since_last_click = time.time()
        action = -1
    elif action == 1:
        if video_nr < len(frames) - 1:
            video_nr += 1
            time_since_last_click = 0
        action = -1
    elif action == 2:
        if video_nr > 0:
            video_nr -= 1
            time_since_last_click = 0
        action = -1
    elif action == 3:
        break

cv2.destroyAllWindows()
