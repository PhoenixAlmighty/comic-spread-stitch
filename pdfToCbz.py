from pypdf import PdfReader
from zipfile import ZipFile
import argparse
import os
import math
import shutil

tempPath = "temp"
newPath = "new"

def main():
	# parse arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("book", help = "The absolute file path of the PDF you want to convert to CBZ")
	args = parser.parse_args()
	convertPdfToCbz(args.book)

# As PDFs are black magic, this may not get the desired result
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
	cbzFileName = os.path.basename(root) + ".cbz"
	
	try:
		os.mkdir(tempPath)
	except FileExistsError as err:
		print(tempPath + " directory already exists")
	
	# The reason for the line image_file_object = page.images[count] is that
	# the PDF I first tried this on seemed to have all the images repeated in each page
	for page in reader.pages:
		# for image_file_object in page.images:
		image_file_object = page.images[count]
		with open(os.path.join(tempPath, ("{:0" + str(numDigits) + "d}").format(count) + os.path.splitext(image_file_object.name)[1]), "wb") as fp:
			fp.write(image_file_object.data)
			count += 1
	
	imgs = os.listdir(tempPath)
	with ZipFile(cbzFileName, "w") as cbz:
		for img in imgs:
			cbz.write(os.path.join(tempPath, img), arcname = img)
	
	# clean up
	shutil.rmtree(tempPath)
	
	print("{} converted to CBZ.".format(bookPdf))

if __name__ == "__main__":
	main()
