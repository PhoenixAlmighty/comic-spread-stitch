import cv2
from zipfile import ZipFile
import os
import shutil

tempPath = "temp"

def main():
	lines = []
	stitcher = cv2.Stitcher_create()
	
	with open("pagesToCombine.txt", "r") as pagesFile:
		lines = pagesFile.readlines()
	
	for line in lines:
		manga = False
		bookFileName = ""
		parts = line.split("|")
		bookDir = parts[0]
	
		# check for errors in input
		if not bookDirIsValid(bookDir):
			continue
		pages = convertPageList(parts[1], bookDir)
		if not pages:
			continue
		
		os.chdir(bookDir)
		
		bookFileName = findCBZFile()
		if bookFileName == "":
			print("{} has no CBZ files in it. Check your input.".format(bookDir))
		if not bookFileName:
			continue
		
		with ZipFile(bookFileName, 'r') as zip:
			zip.extractall(path = tempPath)
		
		os.chdir(tempPath)
		imgList = os.listdir()
		# check to see if the image files are in a subdirectory and bring them out if so
		while os.path.isdir(imgList[0]):
			for file in os.listdir(imgList[0]):
				shutil.move(os.path.join(imgList[0], file), file)
			os.rmdir(imgList[0])
			imgList = os.listdir()
		
		if len(parts) > 2 and parts[2].strip() == "manga":
			manga = True
		stitchPages(stitcher, imgList, pages, manga)
		
		imgList = os.listdir()
		os.chdir("..")
		os.rename(bookFileName, bookFileName + "_old")
		
		# create new CBZ file with the combined pages
		with ZipFile(bookFileName, 'w') as newZip:
			for file in imgList:
				filePath = os.path.join(tempPath, file)
				newZip.write(filePath, arcname = file)
				os.remove(filePath)
		
		os.rmdir(tempPath)
		
		printSuccess(bookFileName, pages)
	
	print("{} books evaluated. See output above for results.\n".format(len(lines)))

def combinePages(imgList, pageList, manga):
	for page in pageList:
		# read in the two pages I want to combine
		# this is page - 1 and page because python lists are 0-indexed and the page numbers are 1-indexed
		# print("{}, {}".format(page - 1, page))
		img1 = cv2.imread(imgList[page - 1])
		img2 = cv2.imread(imgList[page])
		
		# horizontally concatenate the two pages
		if manga:
			combImg = cv2.hconcat([img2, img1])
		else:
			combImg = cv2.hconcat([img1, img2])
		
		# overwrite the first page with the combined pages
		cv2.imwrite(imgList[page - 1], combImg)
		
		# remove the second page so I don't see it again separately from the combined pages
		# unless I'm combining the front and back covers, in which case the front cover gets to stay as it is
		if not page == 0:
			os.remove(imgList[page])

# Note: the below function did not stitch any images together when applied to Big Girls, Vol. 1; it just concatenated all of them

def stitchPages(stitcher, imgList, pageList, manga):
	stitchedPages = []
	concatPages = []
	for page in pageList:
		# read in the two pages I want to combine
		# this is page - 1 and page because python lists are 0-indexed and the page numbers are 1-indexed
		# print("{}, {}".format(page - 1, page))
		img1 = cv2.imread(imgList[page - 1])
		img2 = cv2.imread(imgList[page])
		
		#attempt to stitch the images
		if manga:
			(status, stitched) = stitcher.stitch([img2, img1])
		else:
			(status, stitched) = stitcher.stitch([img2, img1])
		
		# horizontally concatenate the two pages if stitching didn't work
		if status != 0:
			concatPages.append([page, status])
			if manga:
				stitched = cv2.hconcat([img2, img1])
			else:
				stitched = cv2.hconcat([img1, img2])
		else:
			stitchedPages.append(page)
		
		# overwrite the first page with the combined pages
		cv2.imwrite(imgList[page - 1], stitched)
		
		# remove the second page so I don't see it again separately from the combined pages
		# unless I'm combining the front and back covers, in which case the front cover gets to stay as it is
		if not page == 0:
			os.remove(imgList[page])
	
	print("Stitched on pages {}, concatenated on pages {}".format(stitchedPages, concatPages))

def printSuccess(bookFileName, pagesList):
	pagesString = ""
	if pagesList[0] == 0 and len(pagesList) == 1:
		pagesString = "the back cover"
		del pagesList[0]
	elif pagesList[0] == 0 and len(pagesList) > 1:
		pagesString = "the back cover and "
		del pagesList[0]
	numPages = len(pagesList)
	if numPages == 1:
		pagesString += "page {}".format(pagesList[0])
	elif numPages == 2:
		pagesString += "pages {} and {}".format(pagesList[0], pagesList[1] - 1)
	elif numPages > 2:
		pagesString += "pages "
		for i in range(numPages):
			if i == numPages - 1:
				pagesString += "{}".format(pagesList[i] - i)
			elif i == numPages - 2:
				pagesString += "{}, and ".format(pagesList[i] - i)
			else:
				pagesString += "{}, ".format(pagesList[i] - i)
	
	print("{} successfully altered on {}.".format(bookFileName, pagesString))

def bookDirIsValid(bookDir):
	if bookDir == "":
		print("No book directory on this line. Check your input.")
		return False
	elif not os.path.exists(bookDir):
		print(bookDir + " does not exist. Check your filepath.")
		return False
	
	return True

def convertPageList(pageString, bookDir):
	if pageString == "":
		print("{} has no pages to combine. Check your input.".format(bookDir))
		return False
	pageStringList = pageString.split(",")
	pageIntList = []
	for page in pageStringList:
		page = page.strip()
		if not page.isdigit():
			print("Page list for {} contains at least one thing that's not a number. Check your input.".format(bookDir))
			return False
		else:
			pageIntList.append(int(page))
	
	pageIntList.sort()
	
	return pageIntList

def findCBZFile():
	bookFiles = os.listdir()
	bookFileName = ""
	for file in bookFiles:
		filename, extension = os.path.splitext(file)
		if extension == ".cbz":
			bookFileName = file
		if extension == ".cbz_old":
			print("{} contains a CBZ_OLD file like the ones this script leaves behind as backups. As such, this book will be skipped. Try again after moving or deleting the CBZ_OLD file.\n".format(os.getcwd()))
			return False
	
	return bookFileName

if __name__ == "__main__":
	main()
	
# some lines of code that might be useful for debugging at some point

# print(os.getcwd())

# cv2.imshow("Combined image", combImg)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
