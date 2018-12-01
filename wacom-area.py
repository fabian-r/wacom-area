import tkinter as tk

import subprocess


def run_cmd(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    out, err = p.communicate()
    p.wait()
    retval = p.returncode
    if retval != 0:
        print("An error occured when executing `{}`:".format(cmd))
        print(err.decode("utf-8"))
        return (False, None)
    return (True, out.decode("utf-8").splitlines())


# Find STYLUS device TODO add cli option for this
success, lines = run_cmd("xsetwacom list")

if not success:
    print("Failed to call xsetwacom!")
    exit(1)

dev_id = -1

for l in lines:
    li = l.split()
    if li[-1] == 'STYLUS':
        dev_id = int(li[-3])
        print("Found STYLUS device with id {}".format(dev_id))

if dev_id == -1:
    print("Failed to find device!")
    exit(1)

print("Using STYLUS device with id {}".format(dev_id))

if not run_cmd("xsetwacom set {} ResetArea".format(dev_id))[0]:
    print("Failed to reset area!")
    exit(1)

success, lines = run_cmd("xsetwacom get {} Area".format(dev_id))
if not success or len(lines) != 1:
    print("Failed to get area!")
    exit(1)

l = lines[0].split()

if len(l) != 4:
    print("Failed to get area!")
    exit(1)

dev_width = int(l[2])
dev_height = int(l[3])

print("Reset STYLUS to native device area of {}x{}".format(dev_width, dev_height))


root = tk.Tk()

root.overrideredirect(True)
root.wait_visibility(root)
root.wm_attributes("-alpha", 0.5)
root.wm_attributes("-topmost", True)
root.title("wacom-size")
root.configure(background='red')

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

run_cmd("xsetwacom set {} MapToOutput {}x{}+{}+{}".format(dev_id, screen_width, screen_height, 0, 0))


win_width = 400
win_height = 300
win_xpos = 0
win_ypos = 0


ratio_min = 10
ratio_max = 100
ratio_step = 2

ratio = ratio_max

def updateWinSize():
    global win_width
    global win_height
    global ratio
    if ratio < ratio_min:
        ratio = ratio_min
    if ratio > ratio_max:
        ratio = ratio_max
    win_width = int((ratio / 100) * screen_height * (dev_width / dev_height))
    win_height = int((ratio / 100) * screen_height)

updateWinSize()

def getPosStr():
    xpos = win_xpos - win_width//2
    ypos = win_ypos - win_height//2
    if xpos + win_width > screen_width:
        xpos = screen_width - win_width
    if xpos < 0:
        xpos = 0
    if ypos + win_height > screen_height:
        ypos = screen_height - win_height
    if ypos < 0:
        ypos = 0
    return "{width}x{height}+{xpos}+{ypos}".format(width=win_width, height=win_height, xpos=xpos, ypos=ypos)

def setPos():
    global win_xpos
    global win_ypos
    win_xpos, win_ypos = root.winfo_pointerxy()
    root.geometry(getPosStr())

setPos()

def motion(event):
    setPos()

def click(event):
    pos_str = root.winfo_geometry()
    if not run_cmd("xsetwacom set {} MapToOutput {}".format(dev_id, pos_str))[0]:
        print("Failed to map to output!")
        exit(1)
    print("Mapped STYLUS to area {}".format(pos_str))
    exit(0)

def mouse_wheel(event):
    global ratio
    if event.num == 5:
        ratio -= ratio_step
    if event.num == 4:
        ratio += ratio_step
    updateWinSize()
    setPos()

prev_y = None

def mouse_hold_motion(event):
    global prev_y
    global ratio
    setPos()
    curr_y = win_ypos
    if prev_y == None:
        prev_y = curr_y
        return

    if curr_y > prev_y:
        ratio -= ratio_step
    elif curr_y < prev_y:
        ratio += ratio_step

    prev_y = curr_y
    updateWinSize()
    setPos()

def mouse_hold_release(event):
    global prev_y
    prev_y = None



root.bind('<Motion>', motion)
root.bind('<Button-1>', click)

root.bind("<Button-4>", mouse_wheel)
root.bind("<Button-5>", mouse_wheel)

root.bind("<B3-Motion>", mouse_hold_motion)
root.bind("<ButtonRelease-3>", mouse_hold_release)

print("Usage:")
print("  Move mouse to move mapped area.")
print("  Scroll or move mouse with right button pressed to adjust the size of the mapped area.")
print("  Click to set size of the mapped area and exit.")

root.mainloop()

