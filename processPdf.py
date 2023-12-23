from pypdf import PdfReader, PdfWriter
import argparse
import ast

def main():
	# parse arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("book", help = "The absolute file path of the PDF you want to process")
	parser.add_argument("pageList", help = "The list of pages you want to process and what you want to do with them; should look like a Python list")
	parser.add_argument("-m", "--manga", dest = "manga", action = "store_true", help = "Add this switch if the book is read from right to left")
	args = parser.parse_args()
	pageList = ast.literal_eval(args.pageList)
	processPdf(args.book, pageList, args.manga)

def processPdf(book, pageList, manga):
	# read source PDF
	reader = PdfReader(book)
	
	# create destination PDF
	writer = PdfWriter()
	
	# split pageList into its columns
	pagesList = [item[0] for item in pageList]
	opsList = [item[1] for item in pageList]
	
	# For each page in the source PDF:
	# If neither that page nor the previous one is in the list, add it to the destination PDF
	# If that page is in the list, process it and the next page
	# If the previous page is in the list, the current page would have been processed along with the last one, so leave it alone
	for i in range(len(reader.pages)):
		# no processing needed
		if i + 1 not in pagesList and i not in pagesList:
			writer.add_page(reader.pages[i])
		
		# yes processing needed
		elif i + 1 in pagesList:
			p = pagesList.index(i + 1)
			
			# delete page and add the next one to the destination PDF
			if opsList[p] == 'd' and i < len(reader.pages) - 1:
				writer.add_page(reader.pages[i + 1])
	
	# write file
	with open("C:\\Users\\rmauz\\Desktop\\comic-spread-stitch\\test-resources\\pdf\\test.pdf", "wb") as fp:
		writer.write(fp)

if __name__ == "__main__":
	main()
