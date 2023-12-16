from pypdf import PdfReader
from zipfile import ZipFile
import argparse
import os
import math

tempPath = "temp"
newPath = "new"

def main():
	# parse arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("book", help = "The absolute file path of the PDF you want to convert to CBZ")
	args = parser.parse_args()
	convertPdfToCbz(args.book)

# currently only extracts images from the PDF and puts them in the temp path
def convertPdfToCbz(book):
	[root, ext] = os.path.splitext(book)
	if ext.lower() != ".pdf":
		sys.exit("Provided file is not a PDF.")
	
	bookDir = os.path.dirname(book)
	bookPdf = os.path.basename(book)
	os.chdir(bookDir)
	
	reader = PdfReader(bookPdf)
	count = 0
	numDigits = math.ceil(math.log(len(reader.pages), 10))
	
	for page in reader.pages:
		for image_file_object in page.images:
			with open(os.path.join(tempPath, ("{:0" + str(numDigits) + "d}").format(count) + os.path.splitext(image_file_object.name)[1]), "wb") as fp:
				fp.write(image_file_object.data)
				count += 1

if __name__ == "__main__":
	main()
