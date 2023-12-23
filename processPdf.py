from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import RectangleObject
import argparse
import ast
import os

def main():
	# parse arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("book", help = "The absolute file path of the PDF you want to process")
	parser.add_argument("pageList", help = "The list of pages you want to process and what you want to do with them; should look like a Python list")
	parser.add_argument("-m", "--manga", dest = "manga", action = "store_true", help = "Add this switch if the book is read from right to left")
	parser.add_argument("-b", "--backedup", dest = "backedup", action = "store_true", help = "Add this switch if the book already has a backup")
	args = parser.parse_args()
	pageList = ast.literal_eval(args.pageList)
	processPdf(args.book, pageList, args.manga, args.backedup)

def processPdf(book, pageList, manga, backedup):
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
			# if statement necessary in case i is the last page of the source PDF
			if p + 1 < len(opsList):
				currOp = opsList[p + 1]
			if prevOp in ['d', 'l', 'r']:
				if i + 1 not in pagesList:
					writer.add_page(reader.pages[i])
				else:
					processPage(reader, writer, i, currOp, manga)
		
		# yes processing needed
		else:
			p = pagesList.index(i + 1)
			processPage(reader, writer, i, opsList[p], manga)
	
	# rename old file
	if not backedup:
		os.rename(book, book + "_old")
	
	# write file
	with open(book, "wb") as fp:
		writer.write(fp)

def processPage(reader, writer, pageNum, op, manga):
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
	
	# stitch pages without rotating
	elif op == '':
		stitchPages(reader, writer, pageNum, manga)
	
	# stitch pages and rotate left
	elif op == 'm':
		stitchPages(reader, writer, pageNum, manga)
		writer.pages[-1].rotate(270)
	
	# stitch pages and rotate right
	elif op == 's':
		stitchPages(reader, writer, pageNum, manga)
		writer.pages[-1].rotate(90)

# unlike the function in comicSpreadStitch.py, this one has no overlap detection (not that that worked well anyway...)
def stitchPages(reader, writer, pageNum, manga):
	if manga:
		if pageNum + 1 == len(reader.pages):
			leftPage = reader.pages[0]
		else:
			leftPage = reader.pages[pageNum + 1]
		rightPage = reader.pages[pageNum]
	else:
		leftPage = reader.pages[pageNum]
		if pageNum + 1 == len(reader.pages):
			rightPage = reader.pages[0]
		else:
			rightPage = reader.pages[pageNum + 1]
	
	leftWidth = leftPage.mediabox.right - leftPage.mediabox.left
	rightWidth = rightPage.mediabox.right - rightPage.mediabox.left
	
	# TODO: see about scaling one page to the other in case of size mismatches
	leftPage.mediabox = RectangleObject((leftPage.mediabox.left, leftPage.mediabox.bottom, leftPage.mediabox.right + rightWidth, leftPage.mediabox.top))
	leftPage.cropbox = RectangleObject((leftPage.mediabox.left, leftPage.mediabox.bottom, leftPage.mediabox.right + rightWidth, leftPage.mediabox.top))
	leftPage.trimbox = RectangleObject((leftPage.mediabox.left, leftPage.mediabox.bottom, leftPage.mediabox.right + rightWidth, leftPage.mediabox.top))
	leftPage.bleedbox = RectangleObject((leftPage.mediabox.left, leftPage.mediabox.bottom, leftPage.mediabox.right + rightWidth, leftPage.mediabox.top))
	leftPage.artbox = RectangleObject((leftPage.mediabox.left, leftPage.mediabox.bottom, leftPage.mediabox.right + rightWidth, leftPage.mediabox.top))
	
	rightPage.mediabox = RectangleObject((rightPage.mediabox.left, rightPage.mediabox.bottom, rightPage.mediabox.right + rightWidth, rightPage.mediabox.top))
	rightPage.cropbox = RectangleObject((rightPage.mediabox.left, rightPage.mediabox.bottom, rightPage.mediabox.right + rightWidth, rightPage.mediabox.top))
	rightPage.trimbox = RectangleObject((rightPage.mediabox.left, rightPage.mediabox.bottom, rightPage.mediabox.right + rightWidth, rightPage.mediabox.top))
	rightPage.bleedbox = RectangleObject((rightPage.mediabox.left, rightPage.mediabox.bottom, rightPage.mediabox.right + rightWidth, rightPage.mediabox.top))
	rightPage.artbox = RectangleObject((rightPage.mediabox.left, rightPage.mediabox.bottom, rightPage.mediabox.right + rightWidth, rightPage.mediabox.top))
	
	op = Transformation().translate(tx = leftWidth)
	rightPage.add_transformation(op)
	leftPage.merge_page(rightPage)
	
	writer.add_page(leftPage)

if __name__ == "__main__":
	main()
