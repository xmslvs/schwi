import ctypes
from PIL import ImageGrab
import win32gui
import win32con
import os

# 1. Tell Windows this process is DPI Aware (High DPI). 
# This makes GetWindowRect return actual physical pixels, removing the need for manual scaling.
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2) # 2 = Process_Per_Monitor_DPI_Aware
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

def update_screen_history():
    if os.path.exists("screen_context\\screen_2.png"):
        os.remove("screen_context\\screen_2.png")
    if os.path.exists("screen_context\\screen_1.png"):
        os.rename("screen_context\\screen_1.png", "screen_context\\screen_2.png")
    if os.path.exists("screen_context\\screen_0.png"):
        os.rename("screen_context\\screen_0.png", "screen_context\\screen_1.png")
    take_screenshot()

def take_screenshot():
    toplist, winlist = [], []
    def enum_cb(hwnd, results):
        winlist.append((hwnd, win32gui.GetWindowText(hwnd)))
    win32gui.EnumWindows(enum_cb, toplist)

    # Find the OBS projector window
    obs_preview = [(hwnd, title) for hwnd, title in winlist if 'projector' in title.lower()]
    
    if not obs_preview:
        print("OBS Projector window not found.")
        return

    hwnd = obs_preview[0][0]
    warned = False
    try:
        # Restore if minimized
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        
        # Attempt to set foreground
       #win32gui.SetForegroundWindow(hwnd)
    except Exception as e:
        if not warned:
            warned = True
            print(f"Warning: Could not force focus to OBS (Windows restriction). capturing anyway... Error: {e}")
        # OPTIONAL: If you REALLY need to force it, uncomment the 2 lines below:
        # shell = win32com.client.Dispatch("WScript.Shell")
        # shell.SendKeys('%') # Press Alt to trick Windows into allowing focus switch
        # win32gui.SetForegroundWindow(hwnd)

    # Get the bounding box. Because of the DPI fix above, these are now correct physical pixels.
    bbox = win32gui.GetWindowRect(hwnd)
    
    # Optional: Small trim to remove window borders (OBS projectors often have thin borders)
    # rect = list(bbox)
    # rect[0] += 8
    # rect[1] += 31 # Title bar
    # rect[2] -= 8
    # rect[3] -= 8
    # bbox = tuple(rect)

    # Capture
    img = ImageGrab.grab(bbox, all_screens=True)
    img.save("screen_context\\screen_0.png")

if __name__ == "__main__":
    update_screen_history()