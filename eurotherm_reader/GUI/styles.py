import os.path as path
import os

"""
STYLES SHEET FOR GUI
====================
    The reason this is a py file and not txt,json or any data storing format is because 
    I wanted to have an option to change file/dir paths directly from here.
    TODO- this is better be a type of text file
    TODO2- If not to change into a txt file, enter style and img paths into a class (abstract)
"""


# Styles dict for all of the widgets
style = {
"main_window": ("gridline-color: rgb(166, 166, 166);\n"),
'msg_box_style':("background-color: rgb(62, 252, 255);\n"
        "color: rgb(0, 0, 0);\n"
        "background-color: rgb(170, 255, 0);\n"
        "font: 10pt \"MS Shell Dlg 2\";\n"
        "font: 63 8pt \"Segoe UI Semibold\";\n"
        "background-color: rgb(255, 255, 127);\n"
        "selection-background-color: rgb(255, 255, 255);\n"
        "font: 75 9pt \"MS Shell Dlg 2\";\n"
        "alternate-background-color: rgb(255, 255, 255);"),
'temp_lcd_style' :("background-color: rgb(0, 0, 0);\n"
        "border-bottom-color: rgb(255, 255, 0);\n"
        "border-color: rgb(255, 5, 9);\n"
        "border-color: rgb(162, 162, 0);"),
"about_label":"<html><head/><body><p align=\"center\"><span style=\" "
              "font-size:12pt; font-weight:600;\">About"
              "</span></p></body></html>",
"Help_label": lambda v: "<html><head/><body><p align=\"center\"><span style=\" font-size:12pt; "
              "font-weight:600;\">Help controller version: {}</span></p></body></html>".format(v)
}

# dict containing paths to all the images in the gui applicaiton
img = {
"red_led" : r"images/led-red-on.png",
"green_led" : r"images/green-led-on.png",
"blue led": r"images/blue-led-on.png",
"offline" : r"images/offline.png",
"online": r"images/online.png",
"icon": r"images/CI-SEMI.jpg",
"help_img": r"images/help_img.png"
}

# my current directory TODO- find a way to generalize it for everyone
MyFolder = r"GUI/"
img = {key:path.join(MyFolder, img[key]) for key in img.keys()}
