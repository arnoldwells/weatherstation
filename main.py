import signal
import random
import os
from gpiozero import Button
from getimgai import getimg
from time import sleep, ctime
from inkyimage import show_image
from constants import DEBUG
from openweather import get_weather
from datetime import datetime, timedelta                   
from driveapi import get_file_list, upload_image

mode = "weatheram"                                                                              # initial mode
summary = "A day of partly cloudy with clear spells"                                            # default summary
file_list = []
button_a, button_b, button_c, button_d = Button(5), Button(6), Button(16), Button(24)
SLEEP_IMAGE = "images/inky.jpg"

def a_pressed():
    global mode, iterations
    if DEBUG: print("A pressed")
    if mode == "artimage" or mode == "slideshow":
        iterations = 0
        mode = "weatheram"                                                                      # return to weather
    else:
        print("exiting")                                                                        # exit / turn off
        os._exit(os.EX_OK) if DEBUG else os.system('sudo systemctl poweroff')

def b_pressed():
    global mode, iterations
    if DEBUG: print("B pressed")
    iterations = 0
    if mode == "artimage" or mode == "weatheram":
        mode = "slideshow"
    elif mode == "slideshow":
        mode = "artimage"

def c_pressed():
    global mode, iterations, x
    if DEBUG: print("C pressed")
    if mode == "weatheram":
        mode = "artimage"
    elif mode == "artimage" or mode == "slideshow":                                             # pause
        x = 0
        iterations = (seconds_to_midnight() / 2700)

def d_pressed():                                                                                # save art_image
    global mode, art_image
    if DEBUG: print("D pressed")
    if mode != "sleep":
        if DEBUG: print("saving artimage", art_image)
        upload_image(art_image)

button_a.when_pressed = a_pressed
button_b.when_pressed = b_pressed
button_c.when_pressed = c_pressed
button_d.when_pressed = d_pressed

def seconds_to_seven(seven_am, time_now):
    return (seven_am - time_now).total_seconds()

def seconds_to_midnight():
    return (datetime.now().replace(hour=23, minute=59, second=59) - datetime.now()).total_seconds()

def get_latest_file():
    import glob
    files = glob.glob('generated/20?[0-9]-*.jpg')
    if DEBUG: print(f"found [{len(files)}] files")
    if files:
        latest_file = max(files, key=os.path.getctime)
    else:
        latest_file = "images/file-error.png"
    if DEBUG: print(f"latest file: {latest_file}" )
    return latest_file

def int_handler(signum, frame):
    # exit()
    os._exit(os.EX_OK)

signal.signal(signal.SIGINT, int_handler)                                                       # INTERRUPT exit cleanly with CTRL-C

if DEBUG: print("initial delay: 2s")
sleep(2)
x = 0
iterations = 0
art_image = get_latest_file()                                                                   # from "generated/20?[0-9]-*.jpg"

while True:
    time_now = datetime.now()
    seven_am = time_now.replace(hour=7, minute=00, second=00)                                   # 07:00
    nine_am = time_now.replace(hour=9, minute=00, second=00)                                    # 09:00
    nine_sixteen = nine_am + timedelta(minutes = 16)                                            # 09:16
    midnight = time_now.replace(hour=00, minute=00, second=00)                                  # 00:00
    
    if DEBUG: print(f"current mode is <{mode}>, iterations is set to: {iterations}")

    if midnight <= time_now < seven_am:                                                         # sleep:  => 00:00 and < 07:00
        mode = "sleep"
        if DEBUG: print("* * * sleep mode")
        # show_image(SLEEP_IMAGE, background="white")
        exit()
        sleep(seconds_to_seven(seven_am, time_now))                                             # currently bypassed
    elif nine_am <= time_now < nine_sixteen:                                                    # daily artimage:  => 9:00 and < 9:16
        mode = "artimage"
        '''art_image = getimg(summary)                                                          # generate art image
        if DEBUG: print("image generated with filename:", art_image)
        show_image(art_image, background="artimage")'''
        x = 0
        iterations = 2
        while x < iterations:
            if DEBUG: print(f"current mode is <{mode}>, iterations is set to: {iterations} x is: {x}")
            x += 1
            sleep(1800)                                                                         # 30/15 min
        if x == 2:
            mode = "weartheram"
    elif mode == "weatheram":
        summary = get_weather()                                                                 # get and display weather
        if DEBUG: print("sleeping for 900")
        # exit()
        sleep(900)                                                                              # 2700/1800/900 45/30/15 min
    elif mode == "artimage":
        show_image(art_image, background="artimage")
        sleep(3600)
        mode = "weartheram"
    elif mode == "slideshow":
        file_list = get_file_list()                                                             # fetch from google drive
        random.shuffle(file_list)                                                               # randomise list
        del file_list[5:]                                                                       # truncate to first 5
        if DEBUG: print("file_list is now:", *file_list,sep="\n")
        while file_list:                                                                        # list not empty
            x = 1
            iterations = 1
            show_image(file_list.pop(0)["webContentLink"], background="slide")                  # show slide
            sleep(3600)                                                                         # 60/45/30/15 = 3600/2700/1800/900s
            while x < iterations:
                if DEBUG: print(f"current mode is <{mode}>, iterations is set to: {iterations} x is: {x}")
                x += 1
                sleep(3600)
            if iterations == 0: 
                break
        mode = "weatheram"
    else:
        mode = "weatheram"

    if DEBUG: print("sleeping 3s")
    sleep(3)

print("sleep 66 before exit")
sleep(66)
