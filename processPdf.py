from pypdf import PdfReader, PdfWriter
import argparse

def main():
	# parse arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("book", help = "The absolute file path of the PDF you want to process")
	args = parser.parse_args()
	processPdf(args.book)

def processPdf(book):
	# read source PDF
	reader = PdfReader(book)
	
	# create destination PDF and add pages 1 and 3 of the source to it
	writer = PdfWriter()
	writer.add_page(reader.pages[0])
	writer.add_page(reader.pages[2])
	
	# write file
	with open("C:\\Users\\rmauz\\Desktop\\comic-spread-stitch\\test-resources\\pdf\\1and3page.pdf", "wb") as fp:
		writer.write(fp)

if __name__ == "__main__":
	main()
