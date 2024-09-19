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

def main():
    window = BookWindow()

    window.root.mainloop()

class BookWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Comic Spread Stitch")
        # list of books with one to start
        self.books = [BookFrame(self)]
        # frame to contain process and add buttons
        self.frm_bottom = tk.Frame(master = self.root)
        # button to process the file(s)
        self.btn_process = ttk.Button(master = self.frm_bottom, text = "Process", command = self.process)
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
        if self.btn_process['state'] == tk.DISABLED:
            self.btn_process.config(state = tk.NORMAL)

    # process the file(s)
    def process(self):
        self.btn_add.config(state = tk.DISABLED)
        self.btn_process.config(state = tk.DISABLED)
        for book in self.books:
            book.lbl_results["text"] = "Working..."
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
            result, reason = comicSpreadStitch.processBook(line, overlap=over, compression=comp)
            book.lbl_results["text"] = reason
        self.btn_add.config(state = tk.NORMAL)
        self.btn_process.config(state = tk.NORMAL)

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
        self.cb_manga.grid(row = 3, column = 0)
        self.cb_rightlines.grid(row = 3, column = 1)
        self.cb_backedup.grid(row = 3, column = 2)
        self.window.root.update()
        self.lbl_results.config(wraplength = self.cb_manga.winfo_width() + self.ent_pages.winfo_width() - 5)
        self.lbl_results.grid(row = 4, column = 0, columnspan = 2)
        self.btn_remove.grid(row = 4, column = 2, sticky = "es")

    # choose file to process
    def browseFiles(self):
        # only CBZ, ePub, and PDF files are supported, so only those are allowable
        filename = filedialog.askopenfilename(initialdir = "/",
                                              title = "Select book",
                                              filetypes = (("Supported files", "*.cbz *.epub *.pdf"),
                                                           ("CBZ files", "*.cbz"),
                                                           ("ePub files", "*.epub"),
                                                           ("PDF files", "*.pdf")))
        # clear entry box
        self.ent_filepath.delete(0, tk.END)
        # insert filename into entry box
        self.ent_filepath.insert(0, filename)

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
    main()
