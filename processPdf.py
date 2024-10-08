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

from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import RectangleObject
import argparse
import ast
import os
import logging
import traceback
import datetime

logger = logging.getLogger(__name__)

def main():
	# parse arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("book", help = "The absolute file path of the PDF you want to process")
	parser.add_argument("pageList", help = "The list of pages you want to process and what you want to do with them; should look like a Python list")
	parser.add_argument("-m", "--manga", dest = "manga", action = "store_true", help = "Add this switch if the book is read from right to left")
	parser.add_argument("-b", "--backedup", dest = "backedup", action = "store_true", help = "Add this switch if the book already has a backup")
	args = parser.parse_args()
	logging.basicConfig(filename = "run.log", level = logging.INFO)
	logger.info(f"Running at {datetime.datetime.now()}")
	pageList = ast.literal_eval(args.pageList)
	logger.info(f"Page list is {pageList}")
	logger.info(f"manga = {args.manga}")
	logger.info(f"backedup = {args.backedup}")
	try:
		status, reason = processPdf(args.book, pageList, args.manga, args.backedup)
		if not status:
			logger.info("Processing complete")
			print(f"{args.book} successfully processed.")
		else:
			logger.warning(reason)
			print(reason)
	except Exception as err:
		out = f"Error occurred while processing\n{traceback.format_exc()}"
		logger.error(out)
		print(out)

def processPdf(book, pageList, manga, backedup):
	# read source PDF
	reader = PdfReader(book)
	logger.info("Opened PDF file")
	
	# check whether reader.pages is long enough to cover the last page in pagesList
	if (pageList[-1][1] in ["l", "r", "d"] and len(reader.pages) < pageList[-1][0]) or (not (pageList[-1][1] in ["l", "r", "d"]) and len(reader.pages) < pageList[-1][0] + 1):
		return 1, f"{book} skipped because the last page to process is past the end of the book."
	
	#check whether back cover needs to be altered
	backcover = False
	if pageList[0][0] == 0:
		backcover = True
		del pageList[0]
	logger.debug(f"backcover = {backcover}")
	
	# create destination PDF
	writer = PdfWriter()
	logger.info("Created PDF writer")
	
	# split pageList into its columns
	pagesList = [item[0] for item in pageList]
	opsList = [item[1] for item in pageList]
	logger.debug(f"pagesList = {pagesList}")
	logger.debug(f"opsList = {opsList}")
	
	# For each page in the source PDF except the back cover:
	# If neither that page nor the previous one is in the list, add it to the destination PDF
	# If that page is in the list, process it and the next page
	# If the previous page is in the list, check how it was transformed to see whether anything should be done with this one
	for i in range(len(reader.pages) - 1):
		# no processing needed
		if i + 1 not in pagesList and i not in pagesList:
			writer.add_page(reader.pages[i])
			logger.debug(f"Added page {i + 1} unaltered")
		
		# maybe processing needed because previous page was processed
		elif i in pagesList:
			p = pagesList.index(i)
			prevOp = opsList[p]
			# if statement necessary in case i is the last page of the source PDF
			if p + 1 < len(opsList):
				currOp = opsList[p + 1]
			if prevOp in ['d', 'l', 'r']:
				if i + 1 not in pagesList:
					writer.add_page(reader.pages[i])
					logger.debug(f"Added page {i + 1} unaltered")
				else:
					processPage(reader, writer, i, currOp, manga)
		
		# yes processing needed
		else:
			p = pagesList.index(i + 1)
			processPage(reader, writer, i, opsList[p], manga)
	
	# handle back cover
	if backcover:
		stitchPages(reader, writer, -1, manga)
		logger.info("Stitched back cover to front cover")
	# don't add back cover if it was supposed to be deleted or stitched to the previous page
	elif len(reader.pages) - 1 in pagesList and opsList[pagesList.index(len(reader.pages) - 1)] in ["", "m", "s"]:
		logger.debug("Did not add back cover because it was stitched to the previous page")
	elif len(reader.pages) in pagesList and opsList[pagesList.index(len(reader.pages))] == "d":
		logger.info("Deleted back cover")
	# rotate back cover if needed
	elif len(reader.pages) in pagesList and opsList[pagesList.index(len(reader.pages))] in ["l", "r"]:
		processPage(reader, writer, len(reader.pages) - 1, opsList[pagesList.index(len(reader.pages))], manga)
	# add back cover unchanged if no other operations on it
	else:
		writer.add_page(reader.pages[-1])
		logger.debug("Added back cover unaltered")
	
	# set right-to-left reading direction if manga
	if manga:
		writer.create_viewer_preferences()
		writer.viewer_preferences.direction = "/R2L"
		logger.debug("Set view direction to right-to-left")
	
	# rename old file
	if not backedup:
		try:
			os.rename(book, book + "_old")
			logger.debug("Backup created")
		except PermissionError as permErr:
			logger.error("Backup not created because source file could not be renamed")
			return 1, f"{book} is open in another program. Close it and run the script again."
	else:
		logger.debug("Backup not created because a backup already exists")
	
	# write file
	with open(book, "wb") as fp:
		writer.write(fp)
	logger.info("PDF written to disk")
	
	return 0, ""

def processPage(reader, writer, pageNum, op, manga):
	# delete page by not adding it to the destination PDF
	if op == 'd':
		logger.info(f"Deleted page {pageNum + 1}")
	
	# rotate page 90 degrees left and add it to the destination PDF
	elif op == 'l':
		writer.add_page(reader.pages[pageNum])
		writer.pages[-1].rotate(270)
		logger.info(f"Rotated {pageNum + 1} counterclockwise")
	
	# rotate page 90 degrees right and add it to the destination PDF
	elif op == 'r':
		writer.add_page(reader.pages[pageNum])
		writer.pages[-1].rotate(90)
		logger.info(f"Rotated {pageNum + 1} clockwise")
	
	# stitch pages without rotating
	elif op == '':
		stitchPages(reader, writer, pageNum, manga)
		logger.info(f"Stitched pages {pageNum + 1} and {pageNum + 2}")
	
	# stitch pages and rotate left
	elif op == 'm':
		stitchPages(reader, writer, pageNum, manga)
		writer.pages[-1].rotate(270)
		logger.info(f"Stitched pages {pageNum + 1} and {pageNum + 2} and rotated them counterclockwise")
	
	# stitch pages and rotate right
	elif op == 's':
		stitchPages(reader, writer, pageNum, manga)
		writer.pages[-1].rotate(90)
		logger.info(f"Stitched pages {pageNum + 1} and {pageNum + 2} and rotated them clockwise")

# unlike the function in comicSpreadStitch.py, this one has no overlap detection (not that that worked well anyway...)
# if pageNum is -1, that represents the back cover
def stitchPages(reader, writer, pageNum, manga):
	if pageNum == -1:
		if manga:
			leftPage = reader.pages[0]
			rightPage = reader.pages[-1]
		else:
			leftPage = reader.pages[-1]
			rightPage = reader.pages[0]
	else:
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
