from pynput import keyboard, mouse
import win32gui
import win32api
import win32con
import unicodedata

screen_width  = win32api.GetSystemMetrics(0)  # SM_CXSCREEN
screen_height = win32api.GetSystemMetrics(1)  # SM_CYSCREEN
ctrl_pressed = False

WINDOW_TITLE = "War"
click_x = screen_width//2  
click_y = screen_height//2

# Remove bad unicode from screen name
def normalize(s):
    return "".join(
        c for c in unicodedata.normalize("NFKC", s)
        if not unicodedata.category(c).startswith("Z")
    ).strip()

def find_window_partial(name):
    result = []
    def enum(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title and name in normalize(title):
                result.append(hwnd)
    win32gui.EnumWindows(enum, None)
    return result[0] if result else None

#2d coords into 'lparam' which is what PostMessage needs
def make_lparam(x, y):
    return (y << 16) | x


hwnd = find_window_partial(WINDOW_TITLE)
if not hwnd:
    print(f'Window containing "{WINDOW_TITLE}" not found')
    exit()

print("Foxhole Automator\n"+
      "\tInstructions:\n"
      "\t1) Face your soldier and camera in the direction of the screen you are alt-tabbing\n"+
      "\t3) Alt-tab\n"+
      "\t4) Hold Left ctrl + left click to start autoclicking in Foxhole\n"+
      "\t5) When done, return to foxhole and click to stop the autoclicker\n"
      "\n"+
      "I'm still plugging away at this, it would be nice to also use it while the window is in focus, but getting it to work while alt-tabbed was the goal\n"+
      "\n"+
      "Enjoy\n"
      "- Auklin")

def send_left_click(hwnd, x, y):
    lparam = make_lparam(x, y)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)

def unsend_left_click(hwnd, x, y):
    lparam = make_lparam(x, y)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lparam)

# Detects keyboard clicks   
def on_press(key):
    global ctrl_pressed
    # if key == keyboard.Key.alt_gr:
    #     send_left_click(hwnd, click_x, click_y)
    if key == keyboard.Key.ctrl_l:
        ctrl_pressed = True


def on_release(key):
    global ctrl_pressed
    if key == keyboard.Key.ctrl_l:
        ctrl_pressed = False


# Detects mouse clicks    
def on_click(x, y, button, pressed):
    global ctrl_pressed
    print("click")
    if pressed:
        if button == mouse.Button.left and ctrl_pressed:        
            send_left_click(hwnd, click_x, click_y)
    else:
        global releasedCords
        releasedCords = (x,y)

# Keyboard and Mouse listener handling
mlistener = mouse.Listener(
    on_click=on_click)
mlistener.start()

klistener = keyboard.Listener(
    on_press=on_press, on_release=on_release)
klistener.start()

klistener.join() 
mlistener.join()