#!/usr/bin/env python
# -*- coding: utf-8 *
""" The GUI and main logic for the program

The AddMovieGUI program's init builds the GUI and binds actions on the
components to different functions also in the AddMovieGUI class. We also
included lots of keyboard shortcuts to make usage more efficient. 

AddMovieGUI has a textbox (searchTextBox) for the user to query a movie name.
Pressing enter starts a thread executing searchPressed(), which retrieves the
IMDB ID's from Bing and then scrapes data from each of the corresponding IMDB
pages. The data includes the IMDB image URL, title, year, and (importantly)
the Amazon ASIN. It stores the data in the instance variable movieList, then
pushes the string message "movie searched" to the queue. Messages are popped
from the queue regularly in the processIncoming method by the worker thread
created in class ThreadedClient. The worker thread reads the message "movie
searched" and calls searchPressed2() to update the GUI with the new movies
in the listbox. 

The movie poster for the selected movie will also be displayed in imgPanel.
The logic for that is in movieListChanged(). If no image is available,
clearImg() is called to display the default image in the img subdirectory.

When a movie in the listbox is selected, pressing enter or double clicking on
the movie will print the selected movie's dictonary info in stdout. 

"""


import queue
from io import BytesIO
from threading import Thread

from tkinter import Text, Listbox, Label, Entry, NORMAL, END, DISABLED, \
    SEL, INSERT, DISABLED
from PIL import Image, ImageTk

from addmovie_web_util import imdbBingSearch, bsIMDB, getContent
from addmovie_db_util import insert2DB, alreadyExist
from addmovie_gui_util import center, clearApp, clearImg
from replacepopup import ReplaceMoviePopUp


class AddMovieGUI:

    def __init__(self, master, queue, end_app):
        """ initializes the GUI and binds the logic to the GUI elements

        Parameters
        ----------
        master : the root Tk instance
        queue : queue
            The queue that contain tasks for the GUI to update.
        end_app : function
            call them to end the main thread calliing periodicCall
        """
        self.queue = queue
        self.master = master
        self.end_app = end_app
        master.wm_title("IMDB & Amazon Scraper")
        master.protocol("WM_DELETE_WINDOW", self._quit)

        # Set up the GUI
        WINDOW_WIDTH = 60
        master.bind('<Control-q>', self._quit)

        # Search TextBox
        self.searchTextBox = Text(master, height=1, width=WINDOW_WIDTH//2)
        self.searchTextBox.bind('<Return>', self.searchPressedEvent)
        self.searchTextBox.bind("<Control-Key-a>", self.select_all)
        self.searchTextBox.pack(pady=5, padx=WINDOW_WIDTH)
        self.searchTextBox.focus_set()
        self.searchTextBox.bind("<Tab>", self.focus_next_list_window)

        # Movie Results List
        self.movieListBox = Listbox(master, width=WINDOW_WIDTH)
        self.movieListBox.pack(pady=5, padx=WINDOW_WIDTH)
        self.movieListBox.bind("<Return>", self.submitPressedEvent)
        self.movieListBox.bind("<Double-Button-1>", self.submitPressedEvent)
        self.movieListBox.bind("<Tab>", self.focus_next_window)
        self.movieListBox.bind('<<ListboxSelect>>', self.movieListChanged)

        # Movie Poster Image
        self.imgPanel = Label(master)
        clearImg(self)
        self.imgPanel.pack()

        # Status TextBox
        self.statusTextBox = Entry(master, width=WINDOW_WIDTH)
        self.statusTextBox.pack(pady=5, padx=WINDOW_WIDTH)
        self.insertStatusText("")

        # Center the window in the middle of the screen
        center(master)

    def processIncoming(self):
        """ Handle all messages currently in the queue, if any.

        """
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                # after querying movie and getting results. Update GUI
                if msg == "movie searched":
                    self.searchPressed2()
                else:
                    raise Exception('unknown message in queue!')
            except queue.Empty:
                # just on general principles, although we don't
                # expect this branch to be taken in this case
                pass

    def select_all(self, event):
        """ Select all text in SearchTextBox. Bound to Ctrl-a

        """
        event.widget.tag_add(SEL, "1.0", END)
        event.widget.mark_set(INSERT, "1.0")
        event.widget.see(INSERT)
        return 'break'

    def searchPressedEvent(self, event):
        """ Function called after user searched a movie name.
        Initiate search to bing and update movieDict and movie poster

        """
        # Disable searchTextBox so users can't input another query
        # while a query is already running
        self.searchTextBox.config(state=DISABLED)
        query = self.searchTextBox.get("1.0", END)
        self.insertStatusText("Searching movie: " + query)
        clearApp(self)
        # Start thread to search movie name.
        Thread(target=self.searchPressed, args=(query,)).start()
        return "break"

    def searchPressed(self, query):
        """ Queries movie name and stores returned imdb ID's in self.movieList

        Parameters
        ----------
        query : the query string

        """
        # Get list of imdb IDs for a input query string
        imdbIDs = imdbBingSearch(query)
        self.movieList = []
        # Extract movie info for each imdbID and store in movieList dict.
        for imdbID in imdbIDs:
            imdbDict = bsIMDB(imdbID)
            if imdbDict:
                self.movieList.append(imdbDict)
        # Put message into queue to update GUI with new movie list.
        msg = "movie searched"
        self.queue.put(msg)

    def searchPressed2(self):
        """ Update GUI after getting the movieList.
        Put movie string (title, year, type) into movieListBox
        Change focus to movieListBox
        Update movie image
        re-enable searchTextBox

        """
        # Insert movies found from bing into movieListBox
        for movie in self.movieList:
            self.movieListBox.insert(END, "{title} {year} {type}"
                                     .format(**movie))
        self.insertStatusText("")
        # Update movieListBox focus and movie image
        self.movieListBox.select_set(0)
        self.movieListBox.focus()
        self.movieListChanged(None)
        self.searchTextBox.config(state=NORMAL)

    def submitPressedEvent(self, event):
        """ User chooses a movie from movieListBox.

        """
        if self.movieListBox.size() == 0:
            return

        # Get selected movie in movieListBox
        selection = self.movieListBox.curselection()[0]
        self.movieDict = self.movieList[selection]

        # Form another query. Not used here. But this is used for further
        # web scraping on other sites (not shown).
        self.movieDict['queryStr'] = "{title} {year}".format(**self.movieDict)

        # Check if selected movie is already in DB. if not, then insert it
        # Else, open ReplaceMoviePopUp and ask user to replace it or not
        if(alreadyExist(self.movieDict)):
            self.insertStatusText("Movie already in database")
            self.moviePopUp = ReplaceMoviePopUp(self, self.master)
        else:
            insert2DB(self.movieDict)
        return "break"

    def insertStatusText(self, text):
        """ Insert text in the bottom status bar to inform user.

        """
        self.statusTextBox.config(state=NORMAL)
        self.statusTextBox.delete(0, END)
        self.statusTextBox.insert(END, text)
        self.statusTextBox.config(state=DISABLED)

    def _quit(self, event=None):
        self.end_app()
        self.master.destroy()
        return "break"

    def focus_next_window(self, event):
        event.widget.tk_focusNext().focus()
        return "break"

    def focus_next_list_window(self, event):
        event.widget.tk_focusNext().focus()
        event.widget.tk_focusNext().select_set(0)
        return "break"

    def movieListChanged(self, event):
        """ Update image when movieList selection changes.
        In the original version, this instigates more events downstream.

        """
        if self.movieListBox.size() == 0:
            return

        # store the current selection in curMovie for subsequent processing
        self.curMovie = self.movieListBox.curselection()[0]
        movieDict = self.movieList[self.curMovie]

        # Take image URL and store image in imgData. Then set it in imgPanel
        gotImage = False
        if 'imageURL' in movieDict and movieDict['imageURL'] != "":
            url = "http://ia.media-imdb.com/images/M/{0}._V1_"\
                "SY150_CR3,0,101,150_AL_.jpg".format(movieDict['imageURL'])
            resp = getContent(url)
            if resp:
                imgData = BytesIO(resp.read())
                pil_image = Image.open(imgData)
                img2 = ImageTk.PhotoImage(image=pil_image)
                self.imgPanel.config(image=img2)
                self.imgPanel.image = img2
                gotImage = True

        # If we couldn't load movie image, set default image instead
        if not gotImage:
            clearImg(self)
        return "break"
