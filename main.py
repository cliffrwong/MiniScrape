#!/usr/bin/env python
# -*- coding: utf-8 *

import queue
from tkinter import Tk

from addmovie_gui import AddMovieGUI

class ThreadedClient:
    """ Launch the main part of the GUI and the worker thread.

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
