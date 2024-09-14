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
        pages = ent_pages.get()
        lbl_results["text"] = pages

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
    lbl_results = ttk.Label(text = "Click Process button to see results")

    # would be nice:
        # progress bar

    # put widgets into window
    lbl_filepath.grid(row = 0, column = 0, sticky = "e")
    ent_filepath.grid(row = 0, column = 1)
    btn_filepath.grid(row = 0, column = 2)
    lbl_pages.grid(row = 1, column = 0, sticky = "e")
    ent_pages.grid(row = 1, column = 1)
    btn_process.grid(row = 1, column = 2)
    lbl_results.grid(row = 2, column = 1)

    window.mainloop()

if __name__ == "__main__":
    main()