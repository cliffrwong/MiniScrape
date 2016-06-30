#!/usr/bin/python3

import queue
from io import BytesIO
import urllib.request
from threading import Timer, Thread

from tkinter import Tk, Text, Listbox, Label, Entry, NORMAL, END, DISABLED, SEL, INSERT, DISABLED
from PIL import Image, ImageTk

from addmovie_util import alreadyExist, imdbBingSearch, bsIMDB, insert2DB
from addmovie_gui_util import center, clearApp, clearImg
from replacepopup import ReplaceMoviePopUp


class AddMovieGUI:
    
    def __init__(self, master, queue, endCommand):
        """ initializes the GUI and binds the logic to the GUI elements

        Parameters
        ----------
        master : the root Tk instance
        queue : queue 
            The queue that contain tasks for the GUI to update.
        endCommand : function
            call them to end the main thread calliing periodicCall
        """
        self.queue = queue
        self.master = master
        self.endCommand = endCommand
        master.wm_title("IMDB & Amazon Scraper")
        master.protocol("WM_DELETE_WINDOW", self._quit)

        # Set up the GUI
        window_width = 60
        master.bind('<Control-q>', self._quit)
        
        # Search TextBox
        self.searchTextBox = Text(master, height=1, width=window_width//2)
        self.searchTextBox.bind('<Return>', self.searchPressedEvent)
        self.searchTextBox.bind("<Control-Key-a>", self.select_all)
        self.searchTextBox.pack(pady=5, padx=window_width)
        self.searchTextBox.focus_set()
        self.searchTextBox.bind("<Tab>", self.focus_next_list_window)
        
        # Movie Results List
        self.movieListBox = Listbox(master, width = window_width)       
        self.movieListBox.pack(pady=5, padx = window_width)            
        self.movieListBox.bind("<Return>", self.submitPressedEvent)
        self.movieListBox.bind("<Double-Button-1>", self.submitPressedEvent)
        self.movieListBox.bind("<Tab>", self.focus_next_window)
        self.movieListBox.bind('<<ListboxSelect>>', self.movieListChanged)
        
        # Movie Poster Image
        self.imgPanel = Label(master)
        clearImg(self)
        self.imgPanel.pack()
        
        # Status TextBox
        self.statusTextBox = Entry(master, width=window_width)
        self.statusTextBox.pack(pady=5, padx=window_width)
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
        return('break')

    def searchPressedEvent(self, event):
        """ Function called after user searched a movie name. 
        Initiate search to bing and update movieDict and movie poster
    
        """
        # Disable searchTextBox so users can't input another query
        # while a query is already running
        self.searchTextBox.config(state=DISABLED)
        query = self.searchTextBox.get("1.0",END)
        self.insertStatusText("Searching movie: " + query)
        clearApp(self)
        # Start thread to search movie name.
        Thread(target=self.searchPressed, args=(query,)).start()
        return("break")
    
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
            self.movieListBox.insert(END,"{title} {year} {type}".format(**movie))
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
        # Else, open the ReplaceMoviePopUp box and ask user to replace it or not
        if(alreadyExist(self.movieDict)):
            self.insertStatusText("Movie already in database")
            self.moviePopUp = ReplaceMoviePopUp(self, self.master)
        else:   
            insert2DB(self.movieDict)
        return("break")

    def insertStatusText(self, text):
        """ Insert text in the bottom status bar to inform user.
        
        """
        self.statusTextBox.config(state=NORMAL)
        self.statusTextBox.delete(0, END)
        self.statusTextBox.insert(END, text)
        self.statusTextBox.config(state=DISABLED)
        
    def _quit(self, event = None):
        self.endCommand()
        self.master.destroy()
        return("break")

    def focus_next_window(self, event):
        event.widget.tk_focusNext().focus()
        return("break")

    def focus_next_list_window(self, event):
        event.widget.tk_focusNext().focus()
        event.widget.tk_focusNext().select_set(0)
        return("break")

    
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
        if 'imageURL' in movieDict and movieDict['imageURL'] != "":
            with urllib.request.urlopen("http://ia.media-imdb.com/images/M/{0}._V1_\
                SY150_CR3,0,101,150_AL_.jpg".format(movieDict['imageURL'])) as fd:
                imgData = BytesIO(fd.read())
            pil_image = Image.open(imgData)
            img2 = ImageTk.PhotoImage(image=pil_image)
            self.imgPanel.config(image=img2)
            self.imgPanel.image = img2
        else:
            clearImg(self)
        return("break")


class ThreadedClient:
"""
Launch the main part of the GUI and the worker thread. 

""" 
    def __init__(self, master):
        """ Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI as well. 

        Parameters
        ----------
        master : the root Tk instance

        """
        self.master = master

        # Create the queue
        self.queue = queue.Queue()

        # Set up the GUI part
        self.gui = AddMovieGUI(master, self.queue, self.endApplication)

        # Set up the thread to do asynchronous I/O
        # More threads can also be created and used, if necessary
        self.running = 1
        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.periodicCall()

    def periodicCall(self):
        """ Check every 200 ms if there is something new in the queue.

        """
        self.gui.processIncoming()
        if not self.running:
            import sys
            sys.exit(1)
        self.master.after(100, self.periodicCall)

    def endApplication(self):
        self.running = 0

if __name__ == "__main__":
    root = Tk()
    client = ThreadedClient(root)
    root.mainloop()


