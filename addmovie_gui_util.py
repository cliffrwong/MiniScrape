#!/usr/bin/env python
# -*- coding: utf-8 *

from PIL import Image, ImageTk
import tkinter

from addmovie_db_util import insert2DB


def center(master):
    """ Center the window in the middle of the screen

    Parameters
    ----------
    master : the root Tk instance

    """
    master.update_idletasks()
    w = master.winfo_screenwidth()
    h = master.winfo_screenheight()
    size = tuple(int(_) for _ in master.geometry().split('+')[0].split('x'))
    x = w/2 - size[0]/2
    y = h/2 - size[1]/2
    master.geometry("%dx%d+%d+%d" % (size + (x, y)))


def clearApp(addMovGUI):
    """ Clear movieListBox and movie poster image. Change focus to search textbox

    Parameters
    ----------
    addMovieGUI : the instance of AddMovieGUI

    """
    addMovGUI.movieListBox.delete(0, tkinter.END)
    addMovGUI.searchTextBox.focus_set()
    clearImg(addMovGUI)


def clearImg(addMovGUI):
    """ Set the image as the default image.

    Parameters
    ----------
    addMovieGUI : the instance of AddMovieGUI

    """
    pil_image = Image.open("img/default.png")
    img2 = ImageTk.PhotoImage(pil_image)
    addMovGUI.imgPanel.config(image=img2)
    addMovGUI.imgPanel.image = img2
