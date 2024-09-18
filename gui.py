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
    # choose file to process
    def browseFiles():
        # only CBZ, ePub, and PDF files are supported, so only those are allowable
        filename = filedialog.askopenfilename(initialdir = "/",
                                              title = "Select book",
                                              filetypes = (("Supported files", "*.cbz *.epub *.pdf"),
                                                           ("CBZ files", "*.cbz"),
                                                           ("ePub files", "*.epub"),
                                                           ("PDF files", "*.pdf")))
        # clear entry box
        ent_filepath.delete(0, tk.END)
        # insert filename into entry box
        ent_filepath.insert(0, filename)

    # process the file
    def process():
        lbl_results["text"] = "Working..."
        filepath = ent_filepath.get()
        if not filepath:
            lbl_results["text"] = "No file entered"
            return
        name, ext = os.path.splitext(filepath)
        # first part of line needs to be directory the book file is in
        # get this from os.path.split()
        # second part of line needs to be list of pages
        line = f"{os.path.split(name)[0]}|{ent_pages.get()}"
        match ext:
            case ".epub":
                line += "|epub"
            case ".pdf":
                line += "|pdf"
            case ".cbz":
                pass
            case _:
                lbl_results["text"] = "Unsupported file type"
                return
        if manga.get() == "1":
            line += "|manga"
        if rightlines.get() == "1":
            line += "|rightlines"
        if backedup.get() == "1":
            line += "|backedup"
        if (not ent_comp.get().isdigit()) and (not ent_comp.get() == ""):
            lbl_results["text"] = "Compression fuzz should be a non-negative integer"
            return
        else:
            if ent_comp.get() == "":
                comp = 75
            else:
                comp = int(ent_comp.get())
        if (not ent_overlap.get().isdigit()) and (not ent_overlap.get() == ""):
            lbl_results["text"] = "Overlap should be a non-negative integer"
            return
        else:
            if ent_overlap.get() == "":
                over = 50
            else:
                over = int(ent_overlap.get())
        result, reason = comicSpreadStitch.processBook(line, overlap = over, compression = comp)
        lbl_results["text"] = reason

    window = tk.Tk()
    window.title("Comic Spread Stitch")

    # file name and path
    lbl_filepath = ttk.Label(text = "File:")
    ent_filepath = ttk.Entry(width = 50)
    btn_filepath = ttk.Button(text = "Browse...", command = browseFiles)
    # pages to process
    lbl_pages = ttk.Label(text = "Pages:")
    ent_pages = ttk.Entry(width = 50)
    # button to process the file
    btn_process = ttk.Button(text = "Process", command = process)
    # label to show the results of the processing
    lbl_results = ttk.Label(text = "Click Process button to see results", wraplength = 300, justify = "left")

    # manga checkbox
    manga = tk.StringVar()
    cb_manga = ttk.Checkbutton(text = "Manga", variable = manga)
    # rightlines checkbox
    rightlines = tk.StringVar()
    cb_rightlines = ttk.Checkbutton(text = "Remove right lines", variable = rightlines)
    # backedup checkbox
    backedup = tk.StringVar()
    cb_backedup = ttk.Checkbutton(text = "Backed up", variable = backedup)

    # compression entry
    lbl_comp = ttk.Label(text = "Compression Fuzz:")
    ent_comp = ttk.Entry(width = 7)
    # set default
    ent_comp.insert(0, "75")
    # overlap entry
    lbl_overlap = ttk.Label(text = "Overlap:")
    ent_overlap = ttk.Entry(width = 7)
    # set default
    ent_overlap.insert(0, "50")

    # a progress bar would be nice, though it might have to wait until I allow multiple books at once in the GUI

    # put widgets into window
    lbl_filepath.grid(row = 0, column = 0, sticky = "e")
    ent_filepath.grid(row = 0, column = 1)
    btn_filepath.grid(row = 0, column = 2)
    lbl_pages.grid(row = 1, column = 0, sticky = "e")
    ent_pages.grid(row = 1, column = 1)
    btn_process.grid(row = 1, column = 2)
    lbl_overlap.grid(row = 2, column = 0, sticky = "e")
    ent_overlap.grid(row = 2, column = 1, sticky = "w")
    lbl_comp.grid(row = 2, column = 1, sticky = "e")
    ent_comp.grid(row = 2, column = 2, sticky = "w")
    cb_manga.grid(row = 3, column = 0)
    cb_rightlines.grid(row = 3, column = 1)
    cb_backedup.grid(row = 3, column = 2)
    lbl_results.grid(row = 4, column = 1)

    window.mainloop()

if __name__ == "__main__":
    main()