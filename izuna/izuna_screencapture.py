from PIL import ImageGrab
import win32gui
import os

def update_screen_history():
        if os.path.exists("screen_2.png"):
            os.remove("screen_2.png")
        if os.path.exists("screen_1.png"):
            os.rename("screen_1.png", "screen_2.png")
        if os.path.exists("screen_0.png"):
            os.rename("screen_0.png", "screen_1.png")
        take_screenshot()

def take_screenshot():
    toplist, winlist = [], []
    def enum_cb(hwnd, results):
        winlist.append((hwnd, win32gui.GetWindowText(hwnd)))
    win32gui.EnumWindows(enum_cb, toplist)

    obs_preview = [(hwnd, title) for hwnd, title in winlist if 'projector' in title.lower()]
    # just grab the hwnd for first window matching the OBS preview
    hwnd = obs_preview[0][0]
    orig_window = win32gui.GetForegroundWindow()
    print(obs_preview)
    print("top window: " + str(win32gui.GetTopWindow(hwnd)))
    # if orig_window != hwnd:
    #     win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
    #     win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        # win32gui.SetForegroundWindow(hwnd)
    bbox = win32gui.GetWindowRect(hwnd)
    print(bbox)
    bbox = scale_bbox(bbox)
    img = ImageGrab.grab(bbox, all_screens=True)
    print(bbox)
    img.save("screen_0.png")

def scale_bbox(bbox): #adjusting params to track projection properly across my multiple-monitor setup
    bbox = list(bbox)
    left = bbox[0]
    top = bbox[1]
    right = bbox[2]
    bottom = bbox[3]
    if left >= 1463: 
        right =  left * 1.25 + (right - left) * 1.5
        left *= 1.25
        top *= 1.5
        bottom *= 1.5
    elif top >= 1152:
        left *= 1.25
        top *= 1.25
        right *= 1.25
        bottom *= 1.25
    else:
        left *= 1.75
        top *= 1.75
        right *= 1.75 
        bottom *= 1.75
    bbox = tuple([left, top, right, bottom])
    return bbox