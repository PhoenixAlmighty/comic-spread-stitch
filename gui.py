#	Comic Spread Stitch - for making digital comic books easier to read
#	Copyright (C) 2024 Reed Mauzy
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <https://www.gnu.org/licenses/>.

import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk
import comicSpreadStitch
import os
import logging
import multiprocessing as mp
import time

logger = logging.getLogger(__name__)

class BookWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Comic Spread Stitch")
        # list of books with one to start
        self.books = [BookFrame(self)]
        # frame to contain process and add buttons
        self.frm_bottom = tk.Frame(master = self.root)
        # button to process the file(s)
        self.btn_process = ttk.Button(master = self.frm_bottom, text = "Process", command = self.processAll)
        # button to add another book
        self.btn_add = ttk.Button(master = self.frm_bottom, text = "Add book", command = self.addBook)

        # a progress bar would be nice here

        self.btn_process.grid(row = 0, column = 1, sticky = "e")
        self.btn_add.grid(row = 0, column = 0, sticky = "e")
        for idx, book in enumerate(self.books):
            book.frm.grid(row = idx, column = 0, padx = 3, pady = 3, ipadx = 1, ipady = 1)
        self.frm_bottom.grid(row = len(self.books), column = 0, sticky = "e")

    def addBook(self):
        self.books.append(BookFrame(self))
        self.frm_bottom.grid_forget()
        self.books[-1].frm.grid(row = len(self.books) - 1, column = 0, padx = 3, pady = 3, ipadx = 1, ipady = 1)
        self.frm_bottom.grid(row = len(self.books), column = 0, sticky = "e")
        self.btn_process.config(state = tk.NORMAL)

    # process the file(s)
    def process(self):
        self.btn_add.config(state = tk.DISABLED)
        self.btn_process.config(state = tk.DISABLED)
        for book in self.books:
            book.lbl_results["text"] = "Working..."
            self.root.update_idletasks()
            filepath = book.ent_filepath.get()
            if not filepath:
                book.lbl_results["text"] = "No file entered"
                continue
            name, ext = os.path.splitext(filepath)
            # first part of line needs to be directory the book file is in
            # get this from os.path.split()
            # second part of line needs to be list of pages
            line = f"{os.path.split(name)[0]}|{book.ent_pages.get()}"
            match ext:
                case ".epub":
                    line += "|epub"
                case ".pdf":
                    line += "|pdf"
                case ".cbz":
                    pass
                case _:
                    book.lbl_results["text"] = "Unsupported file type"
                    continue
            if book.manga.get() == "1":
                line += "|manga"
            if book.rightlines.get() == "1":
                line += "|rightlines"
            if book.backedup.get() == "1":
                line += "|backedup"
            if (not book.ent_comp.get().isdigit()) and (not book.ent_comp.get() == ""):
                book.lbl_results["text"] = "Compression fuzz should be a non-negative integer"
                continue
            else:
                if book.ent_comp.get() == "":
                    comp = 75
                else:
                    comp = int(book.ent_comp.get())
            if (not book.ent_overlap.get().isdigit()) and (not book.ent_overlap.get() == ""):
                book.lbl_results["text"] = "Overlap should be a non-negative integer"
                continue
            else:
                if book.ent_overlap.get() == "":
                    over = 50
                else:
                    over = int(book.ent_overlap.get())
            _, reason = comicSpreadStitch.processBook(line, overlap=over, compression=comp)
            book.lbl_results["text"] = reason
        self.btn_add.config(state = tk.NORMAL)
        self.btn_process.config(state = tk.NORMAL)

    # process the file(s) using threads
    def processAll(self):
        # process all books in threads
        self.btn_add.config(state=tk.DISABLED)
        self.btn_process.config(state=tk.DISABLED)
        q = mp.Queue()
        processList = []
        print("Adding processes to list")
        for book in self.books:
            book.lbl_results["text"] = "Working..."
        self.root.update_idletasks()
        for i in range(len(self.books)):
            bi = self.validateBookInput(i)
            if bi:
                processList.append(mp.Process(target = self.processOne, args = (i, q, bi[1], bi[2], bi[3], )))
        print("Starting all processes")
        for p in processList:
            p.start()
        # This for loop still does not update the window when a single book is done
        # Using time.sleep() right after update_idletasks() doesn't help
        for i in range(len(processList)):
            data = q.get(block = True)
            self.books[data[0]].lbl_results["text"] = data[1]
            self.root.update_idletasks()
        # [p.join() for p in processList]
        print("All processes terminated")
        self.btn_add.config(state=tk.NORMAL)
        self.btn_process.config(state=tk.NORMAL)
        # once all books are done, re-enable Add and Process buttons

    # process a single file
    @staticmethod
    def processOne(idx, q, line, over, comp):
        # process a single book, with threading enabled
        print(f"Starting process {idx}")
        _, reason = comicSpreadStitch.processBook(line, overlap=over, compression=comp)
        print(f"Finished with book process {idx}, sending result to queue")
        q.put((idx, reason))

    # process the file(s) using a multiprocessing pool
    def processAllPool(self):
        self.btn_add.config(state=tk.DISABLED)
        self.btn_process.config(state=tk.DISABLED)
        print("Buttons disabled")

        inputList = []
        for i in range(len(self.books)):
            book = self.books[i]
            book.lbl_results["text"] = "Working..."
            self.root.update_idletasks()
            bookInput = self.validateBookInput(i)
            if bookInput:
                inputList.append(bookInput)
            self.root.update_idletasks()

        with mp.Pool(processes = len(inputList)) as pool:
            result = pool.map_async(self.processOnePool, inputList, callback = self.processOnePoolCallback)
            result.wait()

        self.btn_add.config(state=tk.NORMAL)
        self.btn_process.config(state=tk.NORMAL)
        print("Buttons re-enabled")

    # process a single file in the multiprocessing pool
    @staticmethod
    def processOnePool(inputs):
        idx = inputs[0]
        line = inputs[1]
        over = inputs[2]
        comp = inputs[3]
        # [idx, line, over, comp] = inputs
        print(f"Starting process {idx}")
        _, reason = comicSpreadStitch.processBook(line, overlap=over, compression=comp)
        print(f"Finished with book process {idx}, updating GUI")
        return idx, reason

    def processOnePoolCallback(self, outputs):
        print(f"outputs is {outputs}")
        idx = outputs[0]
        print(f"idx is {idx}")
        reason = outputs[1]
        print(f"reason is {reason}")
        self.books[idx].lbl_results.configure(text = reason)
        print("Updated book result label")
        self.root.update_idletasks()
        print("Updated idle tasks")

    def validateBookInput(self, idx):
        book = self.books[idx]
        filepath = book.ent_filepath.get()
        if not filepath:
            print("Didn't find filepath")
            book.lbl_results["text"] = "No file entered"
            return None
        name, ext = os.path.splitext(filepath)
        # first part of line needs to be directory the book file is in
        # get this from os.path.split()
        # second part of line needs to be list of pages
        line = f"{os.path.split(name)[0]}|{book.ent_pages.get()}"
        match ext:
            case ".epub":
                line += "|epub"
            case ".pdf":
                line += "|pdf"
            case ".cbz":
                pass
            case _:
                print("Found bad file")
                book.lbl_results["text"] = "Unsupported file type"
                return None
        if book.manga.get() == "1":
            line += "|manga"
        if book.rightlines.get() == "1":
            line += "|rightlines"
        if book.backedup.get() == "1":
            line += "|backedup"
        if book.leftlines.get() == "1":
            line += "|leftlines"
        if book.toplines.get() == "1":
            line += "|toplines"
        if book.bottomlines.get() == "1":
            line += "|bottomlines"
        if (not book.ent_comp.get().isdigit()) and (not book.ent_comp.get() == ""):
            print("Bad compression fuzz")
            book.lbl_results["text"] = "Compression fuzz should be a non-negative integer"
            return None
        else:
            if book.ent_comp.get() == "":
                comp = 75
            else:
                comp = int(book.ent_comp.get())
        if (not book.ent_overlap.get().isdigit()) and (not book.ent_overlap.get() == ""):
            print("Bad overlap")
            book.lbl_results["text"] = "Overlap should be a non-negative integer"
            return None
        else:
            if book.ent_overlap.get() == "":
                over = 50
            else:
                over = int(book.ent_overlap.get())
        return [idx, line, over, comp]

class BookFrame:
    def __init__(self, window):
        self.window = window
        self.frm = tk.Frame(master = self.window.root, borderwidth = 2, relief = tk.RIDGE)

        # row 0
        # file name and path
        self.lbl_filepath = ttk.Label(master = self.frm, text = "File:")
        self.ent_filepath = ttk.Entry(master = self.frm, width = 50)
        self.btn_filepath = ttk.Button(master = self.frm, text = "Browse...", command = self.browseFiles)

        # row 1
        # pages to process
        self.lbl_pages = ttk.Label(master = self.frm, text = "Pages:")
        self.ent_pages = ttk.Entry(master = self.frm, width = 50)

        #row 2
        # compression entry
        self.lbl_comp = ttk.Label(master = self.frm, text = "Compression Fuzz:")
        self.ent_comp = ttk.Entry(master = self.frm, width = 7)
        # set default
        self.ent_comp.insert(0, "75")
        # overlap entry
        self.lbl_overlap = ttk.Label(master = self.frm, text = "Overlap:")
        self.ent_overlap = ttk.Entry(master = self.frm, width = 7)
        # set default
        self.ent_overlap.insert(0, "50")

        # row 3
        # manga checkbox
        self.manga = tk.StringVar()
        self.cb_manga = ttk.Checkbutton(master = self.frm, text = "Manga", variable = self.manga)
        # rightlines checkbox
        self.rightlines = tk.StringVar()
        self.cb_rightlines = ttk.Checkbutton(master = self.frm, text = "Remove right lines", variable = self.rightlines)
        # backedup checkbox
        self.backedup = tk.StringVar()
        self.cb_backedup = ttk.Checkbutton(master = self.frm, text = "Backed up", variable = self.backedup)

        # row 4
        # leftlines checkbox
        self.leftlines = tk.StringVar()
        self.cb_leftlines = ttk.Checkbutton(master = self.frm, text = "Remove left lines", variable = self.leftlines)
        # toplines checkbox
        self.toplines = tk.StringVar()
        self.cb_toplines = ttk.Checkbutton(master = self.frm, text = "Remove top lines", variable = self.toplines)
        # bottomlines checkbox
        self.bottomlines = tk.StringVar()
        self.cb_bottomlines = ttk.Checkbutton(master = self.frm, text = "Remove bottom lines", variable = self.bottomlines)

        # row 5
        # label to show the results of the processing
        self.lbl_results = ttk.Label(master = self.frm, text = "Click Process button to see results", wraplength = 300, justify = "left")
        # button to remove this book
        self.btn_remove = ttk.Button(master = self.frm, text = "Remove", command = self.removeBook)

        # put widgets into frame
        self.lbl_filepath.grid(row = 0, column = 0, sticky = "e")
        self.ent_filepath.grid(row = 0, column = 1)
        self.btn_filepath.grid(row = 0, column = 2)
        self.lbl_pages.grid(row = 1, column = 0, sticky = "e")
        self.ent_pages.grid(row = 1, column = 1)
        self.lbl_overlap.grid(row = 2, column = 0, sticky = "e")
        self.ent_overlap.grid(row = 2, column = 1, sticky = "w")
        self.lbl_comp.grid(row = 2, column = 1, sticky = "e")
        self.ent_comp.grid(row = 2, column = 2, sticky = "w")
        self.cb_manga.grid(row = 3, column = 0, sticky = "w")
        self.cb_rightlines.grid(row = 3, column = 1, sticky = "w")
        self.cb_backedup.grid(row = 3, column = 2, sticky = "w")
        self.cb_leftlines.grid(row = 4, column = 0, sticky = "w")
        self.cb_toplines.grid(row = 4, column = 1, sticky = "w")
        self.cb_bottomlines.grid(row = 4, column = 2, sticky = "w")
        self.window.root.update()
        self.lbl_results.config(wraplength = self.cb_manga.winfo_width() + self.ent_pages.winfo_width() - 5)
        self.lbl_results.grid(row = 5, column = 0, columnspan = 2)
        self.btn_remove.grid(row = 5, column = 2, sticky = "es")

    # choose file to process
    def browseFiles(self):
        # only CBZ, ePub, and PDF files are supported, so only those are allowable
        filename = filedialog.askopenfilename(initialdir = "/",
                                              title = "Select book",
                                              filetypes = (("Supported files", "*.cbz *.epub *.pdf"),
                                                           ("CBZ files", "*.cbz"),
                                                           ("ePub files", "*.epub"),
                                                           ("PDF files", "*.pdf")))
        if filename:
            # clear entry box
            self.ent_filepath.delete(0, tk.END)
            # insert filename into entry box
            self.ent_filepath.insert(0, filename)
            # clear page number entry box
            self.ent_pages.delete(0, tk.END)
            # reset result label
            self.lbl_results["text"] = "Click Process button to see results"

    def removeBook(self):
        for widget in self.frm.winfo_children():
            widget.grid_forget()
            widget.destroy()
        self.frm.grid_forget()
        self.frm.destroy()
        self.window.books.remove(self)
        if len(self.window.books) == 0:
            self.window.btn_process.config(state = tk.DISABLED)
        del self

if __name__ == "__main__":
    logging.basicConfig(filename="run.log", level=logging.INFO)
    window = BookWindow()

    logger.debug("Running window main loop")
    window.root.mainloop()
    logger.debug("Window loop finished")
