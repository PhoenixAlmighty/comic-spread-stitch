# About
If you've ever read digital comic books, you've probably come across something that would have been a two-page spread in print, but has been split into two parts, so it's hard to view as the creators intended. Comic Spread Stitch is a collection of Python scripts that partially automates stitching these spreads together into a single image or page so that your reader will show the whole thing at once. It can also rotate pages that are supposed to be in landscape orientation so that you don't have to choose between tilting your monitor and tilting your head, and can delete pages you don't want, such as intrusive ads or accidental page repetitions.
# Limitations
As I only intended this to be used by myself, these scripts lack some of the bells and whistles a project meant for others might have.
- They must be used through the command line
- They assume that each comic book has its own directory (which is the way the ebook management program [Calibre](https://calibre-ebook.com/) organizes book files on disk)
- They only accept CBZ, ePub, or PDF files as input, and will output CBZ files from ePub inputs
# How to install
Before using these scripts, you will need Python 3 installed on your computer, whether [on its own](https://www.python.org/downloads/) or through [Anaconda](https://www.anaconda.com/download/). You will also need [Git](https://git-scm.com/downloads) to clone the repo.

In the command line, navigate to wherever you want the files to live and clone the repo from GitHub.
```
git clone https://github.com/PhoenixAlmighty/comic-spread-stitch.git
```
You will also need to install the OpenCV, PyPDF, and Pillow libraries.
## Using Pip
Run the following commands:
```
pip install opencv-python
pip install pypdf
pip install pillow
```
## Using Anaconda
Make sure the Anaconda environment you want to use is activated, then run the following commands:
```
conda install conda-forge::opencv
conda install conda-forge::pypdf
conda install anaconda::pillow
```
See [here](https://anaconda.org/conda-forge/opencv) for alternate commands you can run to install OpenCV in Anaconda.
# How to use
The repository should include an empty file named `pagesToProcess.txt`. When you run the script, it will look in this file for the list of books to process and the pages in those books to handle. Each book will need to be on its own line. The format of each line is the directory of the book file, followed by a `|`, followed by the list of pages to process. If any other options are needed, these can be appended after the page list, again separated by a `|`. An example is below:
```
D:\Calibre Library\Corinna Bechko\Lords of the Jungle (2839)|2,18,20
D:\Calibre Library\Michal Galek\The Witcher_ Reasons of State (2837)|3d, 40, 57r|pdf
```
There are several things the script can do with each page. Which one it will do depends on the letter after the page number.
- No letter: Stitch this page and the page after it together
- `d`: Delete this page (this can also be used with a range of pages, e.g. `57-60d`)
- `l`: Rotate this page 90 degrees counterclockwise
- `m`: Stitch this page and the page after it together, then rotate the resulting page 90 degrees counterclockwise
- `r`: Rotate this page 90 degrees clockwise
- `s`: Stitch this page and the page after it together, then rotate the resulting page 90 degrees clockwise

There are also several options that can be applied on a per-book basis. These should follow the page list, separated by a `|`.
- `pdf`: Tells the script to look for a PDF file in the specified directory. If a book has neither this option nor the `epub` option specified, the script will look for a CBZ file. Processing PDF files will overwrite any custom pagination with the default of starting at page 1 and counting up from there.
- `epub`: Tells the script to look for an ePub file in the specified directory. If a book has neither this option nor the `pdf` option specified, the script will look for a CBZ file. Books taken as ePub inputs will come out as CBZ. If the book has no pages you wish to alter or remove, but you would like to convert the book to CBZ, simply leave the page list empty, like so:
```
D:\Calibre Library\Jaouen Salaun\Asphalt Blues (2236)||epub
```
- `manga`: Use if the pages are supposed to be read right-to-left, such as if the book is manga. If this option is not specified, the pages will be stitched together as if they're supposed to be read left-to-right, like Western comics.
- `rightlines`: Sometimes a digital comic book will have a line of white pixels running down the right side of each page. If specified, this option will remove the rightmost column of pixels from each page image. This option does nothing on PDF files. When used on CBZ or ePub files, it will significantly increase the time taken to process the book. If the book has no pages you wish to alter or remove, but you would like to remove the right lines, simply leave the page list empty, like so:
```
D:\Calibre Library\Chip Zdarsky\Newburn, Vol. 1 (2910)||rightlines
```
- `backedup`: This script leaves an unaltered backup of each original file it processes, stored with the file extension `.cbz_old` or `.pdf_old`, depending on what the input file type was (since it doesn't output ePub files, ePub inputs are simply left as is). If you try to process a file that has a backup of this kind without specifying this option, the script will skip it. If this option is specified, the script will process the already-processed file, using its page numbers. The backup file will remain unchanged, and a new backup will not be generated.

If more than one option must be applied to the same book, simply separate each option with a `|`, like so:
```
D:\Calibre Library\Dan Goldman\Chasing Echoes (2235)|2,4,6|epub|rightlines
```
The order of the options does not matter.

Once you have as many books as you would like in `pagesToProcess.txt`, open a command prompt, navigate to the directory of the Git repo, and run the following command:
```
python comicSpreadStitch.py
```
The script will run, printing the results of each book in the command prompt window.
- Books that are processed successfully will have a list of pages they were processed on. These will be the new page numbers. I suggest checking in the new file to make sure you didn't accidentally specify a wrong page number or action to take on a page.
- Books that were skipped will say so, usually with a reason.
- Books that encountered a problem the script can't handle will have an error traceback printed. If you are willing and able, you can use this to investigate and find out what the error was and possibly how to fix it.

After all the books have been handled, the number of processed books, skipped books, and errors will be printed.

There are two arguments you can add to the command line, both of which have to do with trying to handle it when the pages you want to stitch together overlap with each other. Neither option does anything when PDF files are processed.

- `-o` or `--overlap`: Specifies the number of columns of pixels to check for overlap. This is done by starting at the right edge of the left image and checking each column to see if it matches the column on the left edge of the right image. Defaults to 50.
- `-c` or `--compression`: If the images are stored in a lossy compression format, such as JPG, checking to see if two columns match perfectly may give false negatives. This argument provides the maximum difference allowed between the same color channel of two pixels for the script to consider it an overlap. Defaults to 75 (out of 255).

If you find that spreads seem to have jumps in the middle where part of the image repeats, try entering different values for these arguments and see if that helps.
# Unit test files
If you decide to make any updates of your own, the files `test_comicSpreadStitch.py` and `test_epubToCbz.py` contain unit tests that can be used to check whether your changes break other functionality. Be warned about relying on them, however; they are not comprehensive, and depending on what changes you make, the tests may break even though your changes are working as intended. To run them, navigate to the project directory in a command prompt and run `python test_comicSpreadStitch.py` or `python test_epubToCbz.py`.
