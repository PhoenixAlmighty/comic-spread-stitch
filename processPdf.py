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
	# If the previous page is in the list, check how it was transformed to see whether anything should be done with this one
	for i in range(len(reader.pages)):
		# no processing needed
		if i + 1 not in pagesList and i not in pagesList:
			writer.add_page(reader.pages[i])
		
		# maybe processing needed
		elif i in pagesList:
			p = pagesList.index(i)
			prevOp = opsList[p]
			currOp = opsList[p + 1]
			if prevOp in ['d', 'l', 'r']:
				if i + 1 not in pagesList:
					writer.add_page(reader.pages[i])
				else:
					processPage(reader, writer, i, currOp)
		
		# yes processing needed
		else:
			p = pagesList.index(i + 1)
			processPage(reader, writer, i, opsList[p])
	
	# write file
	with open("C:\\Users\\rmauz\\Desktop\\comic-spread-stitch\\test-resources\\pdf\\test.pdf", "wb") as fp:
		writer.write(fp)

def processPage(reader, writer, pageNum, op):
	# delete page by not adding it to the destination PDF
	if op == 'd':
		return
	
	# rotate page 90 degrees left and add it to the destination PDF
	elif op == 'l':
		writer.add_page(reader.pages[pageNum])
		writer.pages[-1].rotate(270)
	
	# rotate page 90 degrees right and add it to the destination PDF
	elif op == 'r':
		writer.add_page(reader.pages[pageNum])
		writer.pages[-1].rotate(90)

if __name__ == "__main__":
	main()
