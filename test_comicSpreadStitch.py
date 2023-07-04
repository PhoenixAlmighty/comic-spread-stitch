import unittest
import comicSpreadStitch
import os
import io
import sys
import numpy as np
import cv2

class TestComicSpreadStitch(unittest.TestCase):
	# printSuccess tests
	
	# Back cover only
	def test_printSuccess_backCoverOnly(self):
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		comicSpreadStitch.printSuccess("Test book", [[0, ""]])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on the back cover.\n", "Console output is wrong for back cover only.")
		
	# Back cover + 1 spread
	def test_printSuccess_backCoverOneSpread(self):
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		comicSpreadStitch.printSuccess("Test book", [[0, ""], [2, ""]])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on the back cover and page 2.\n", "Console output is wrong for back cover plus 1 spread.")
		
	# Back cover + 2 spreads
	def test_printSuccess_backCoverTwoSpreads(self):
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		comicSpreadStitch.printSuccess("Test book", [[0, ""], [2, ""], [4, ""]])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on the back cover and pages 2 and 3.\n", "Console output is wrong for back cover plus 2 spreads.")
		
	# Back cover + 3 or more spreads
	def test_printSuccess_backCoverThreeSpreads(self):
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		comicSpreadStitch.printSuccess("Test book", [[0, ""], [2, ""], [4, ""], [6, ""]])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on the back cover and pages 2, 3, and 4.\n", "Console output is wrong for back cover plus 3 spreads.")
		
	# 1 spread
	def test_printSuccess_oneSpread(self):
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		comicSpreadStitch.printSuccess("Test book", [[2, ""]])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on page 2.\n", "Console output is wrong for 1 spread.")
		
	# 2 spreads
	def test_printSuccess_twoSpreads(self):
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		comicSpreadStitch.printSuccess("Test book", [[2, ""], [4, ""]])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on pages 2 and 3.\n", "Console output is wrong for 2 spreads.")
		
	# 3 or more spreads
	def test_printSuccess_threeSpreads(self):
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		comicSpreadStitch.printSuccess("Test book", [[2, ""], [4, ""], [6, ""]])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on pages 2, 3, and 4.\n", "Console output is wrong for 3 spreads.")
		
	# 1 rotation followed by 1 spread
	def test_printSuccess_rotationThenSpread(self):
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		comicSpreadStitch.printSuccess("Test book", [[4, "l"], [6, ""]])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on pages 4 and 6.\n", "Console output is wrong for 2 spreads and 1 rotation.")
		
	# 2 spreads, 1 rotation
	def test_printSuccess_twoSpreadsOneRotation(self):
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		comicSpreadStitch.printSuccess("Test book", [[2, ""], [4, "l"], [6, ""]])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on pages 2, 3, and 5.\n", "Console output is wrong for 2 spreads and 1 rotation.")
		
	# 3 spreads, 1 of which is rotated
	def test_printSuccess_threeSpreadsOneRotated(self):
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		comicSpreadStitch.printSuccess("Test book", [[2, ""], [4, "m"], [6, ""]])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on pages 2, 3, and 4.\n", "Console output is wrong for 3 spreads, 1 of which has been rotated.")
		
	# Check that all modifiers are handled correctly
	def test_printSuccess_allModifiers(self):
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		comicSpreadStitch.printSuccess("Test book", [[2, ""], [4, "m"], [6, "l"], [8, "r"], [10, "s"], [12, ""]])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on pages 2, 3, 4, 6, 8, and 9.\n", "At least one modifier has been handled incoreectly.")
	
	# bookDirIsValid tests
	
	# No book directory
	def test_bookDirIsValid_noDirectory(self):
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		validity = comicSpreadStitch.bookDirIsValid("")
		sys.stdout = sys.__stdout__
		self.assertFalse(validity, "Empty string for book directory should return false.")
		self.assertEqual(capturedOutput.getvalue(), "No book directory on this line. Check your input.\n", "Console output is incorrect for empty string input as book directory.")
		
	# Book directory that doesn't exist on my computer
	def test_bookDirIsValid_nonexistentDirectory(self):
		nonexistentDir = "D:\Calibre Library\Erik Larsen\Savage Dragon #179 (1429)"
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		validity = comicSpreadStitch.bookDirIsValid(nonexistentDir)
		sys.stdout = sys.__stdout__
		self.assertFalse(validity, "Book directory that doesn't exist on this computer should return false.")
		self.assertEqual(capturedOutput.getvalue(), "{} does not exist. Check your filepath.\n".format(nonexistentDir), "Console output is incorrect for nonexistent book directory.")
		
	# Book directory that does exist on my computer
	def test_bookDirIsValid_realDirectory(self):
		realBookDir = "D:\Calibre Library\Erik Larsen\Savage Dragon #179 (1428)"
		self.assertTrue(comicSpreadStitch.bookDirIsValid(realBookDir), "Directory that exists should return true.")
	
	# convertPageList tests
	
	# No pages
	def test_convertPageList_noPages(self):
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		pageList = comicSpreadStitch.convertPageList("", "Test book directory")
		sys.stdout = sys.__stdout__
		self.assertFalse(pageList, "Should return False if string is empty.")
		self.assertEqual(capturedOutput.getvalue(), "Test book directory has no pages to combine. Check your input.\n", "Console output is incorrect for empty page list.")
		
	# Letters in list that aren't attached to numbers
	def test_convertPageList_lonelyLetters(self):
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		pageList = comicSpreadStitch.convertPageList("1,2,a", "Test book directory")
		sys.stdout = sys.__stdout__
		self.assertFalse(pageList, "Should return False if string contains letters that aren't attached to numbers.")
		self.assertEqual(capturedOutput.getvalue(), "Page list for Test book directory contains at least one thing that's not a number and doesn't match any of the available per-page commands. Check your input.\n", "Console output is incorrect for non-numeric page list.")
		
	# Letters in list that don't match the defined modifiers
	def test_convertPageList_wrongModifiers(self):
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		pageList = comicSpreadStitch.convertPageList("1,2,3a", "Test book directory")
		sys.stdout = sys.__stdout__
		self.assertFalse(pageList, "Should return False if string contains letters that aren't attached to numbers.")
		self.assertEqual(capturedOutput.getvalue(), "Page list for Test book directory contains at least one thing that's not a number and doesn't match any of the available per-page commands. Check your input.\n", "Console output is incorrect for non-defined modifiers.")
		
	# Only numbers in list
	def test_convertPageList_numbersOnly(self):
		self.assertEqual(comicSpreadStitch.convertPageList("5,3,7", "Test book directory"), [[3, ""], [5, ""], [7, ""]], "Should return a sorted list of lists, where each list is an integer followed by an empty string.")
		
	# Only numbers and spaces in list
	def test_convertPageList_numbersAndSpaces(self):
		self.assertEqual(comicSpreadStitch.convertPageList("5, 3, 7 ", "Test book directory"), [[3, ""], [5, ""], [7, ""]], "Should return a sorted list of lists, where each list is an integer followed by an empty string, without the whitespace triggering a return value of False.")
		
	# Only numbers and modifiers in list
	def test_convertPageList_numbersAndModifiers(self):
		self.assertEqual(comicSpreadStitch.convertPageList("5l,3r,9s,7m", "Test book directory"), [[3, "r"], [5, "l"], [7, "m"], [9, "s"]], "Should return a sorted list of lists, where each list is an integer followed by one of the following letters: l, m, r, s.")
		
	# Numbers, modifiers, and spaces in list
	def test_convertPageList_numbersModifiersAndSpaces(self):
		self.assertEqual(comicSpreadStitch.convertPageList("5l, 3r, 9s, 7m", "Test book directory"), [[3, "r"], [5, "l"], [7, "m"], [9, "s"]], "Should return a sorted list of lists, where each list is an integer followed by one of the following letters: l, m, r, s, without the whitespace triggering a return value of False.")
	
	# findCBZFile tests
	
	# Directory has no CBZ file
	def test_findCBZFile_noCBZ(self):
		noCBZ = os.path.join(os.path.dirname(__file__), "test-resources", "no-cbz")
		os.chdir(noCBZ)
		self.assertEqual(comicSpreadStitch.findCBZFile(False), "", "{} should not have a CBZ file.".format(noCBZ))
		
	# Directory has a CBZ_OLD file
	def test_findCBZFile_CBZOLD(self):
		yesCBZOLD = os.path.join(os.path.dirname(__file__), "test-resources", "cbz-old")
		os.chdir(yesCBZOLD)
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		file = comicSpreadStitch.findCBZFile(False)
		sys.stdout = sys.__stdout__
		self.assertFalse(file, "{} should have a CBZ_OLD file.".format(yesCBZOLD))
		self.assertEqual(capturedOutput.getvalue(),
			"{} contains a CBZ_OLD file like the ones this script leaves behind as backups. As such, this book will be skipped. Try again after either deleting the CBZ_OLD file or adding \"backedup\" as a flag on the input.\n\n".format(yesCBZOLD),
			"Console output is incorrect.")
		
	# Directory has a CBZ file and no CBZ_OLD file
	def test_findCBZFile_onlyCBZ(self):
		correctFilesDir = os.path.join(os.path.dirname(__file__), "test-resources", "cbz")
		os.chdir(correctFilesDir)
		self.assertEqual(comicSpreadStitch.findCBZFile(False), "dummy.cbz", "{} should have a CBZ file but not a CBZ_OLD file.".format(correctFilesDir))
		
	# Directory has a CBZ_OLD file, but backedup flag is set
	def test_findCBZFile_backedupCBZOLD(self):
		yesCBZOLD = os.path.join(os.path.dirname(__file__), "test-resources", "cbz-old")
		os.chdir(yesCBZOLD)
		self.assertEqual(comicSpreadStitch.findCBZFile(True), "dummy.cbz", "The CBZ_OLD file in {} should be ignored because the backedup flag is set.".format(yesCBZOLD))
		
	# Directory has no CBZ_OLD file, but backedup flag is set
	def test_findCBZFile_backedupCBZ(self):
		correctFilesDir = os.path.join(os.path.dirname(__file__), "test-resources", "cbz")
		os.chdir(correctFilesDir)
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		file = comicSpreadStitch.findCBZFile(True)
		sys.stdout = sys.__stdout__
		self.assertFalse(file, "{} should not have a CBZ_OLD file.".format(correctFilesDir))
		self.assertEqual(capturedOutput.getvalue(),
			"{} had the backedup flag set, but no backup was found. Remove the backedup flag for this directory to process the book normally.\n\n".format(correctFilesDir),
			"Console output is incorrect.")
	
	# getBookFlags tests
	
	# No flags
	def test_getBookFlags_noFlags(self):
		self.assertEqual(comicSpreadStitch.getBookFlags([]), (False, False, False), "All flags should be false")
		
	# Manga flag only
	def test_getBookFlags_manga(self):
		self.assertEqual(comicSpreadStitch.getBookFlags(["manga"]), (True, False, False), "Manga flag should be true")
		
	# Backedup flag only
	def test_getBookFlags_backedup(self):
		self.assertEqual(comicSpreadStitch.getBookFlags(["backedup"]), (False, True, False), "Backedup flag should be true")
		
	# Unknown flag only
	def test_getBookFlags_unknown(self):
		self.assertEqual(comicSpreadStitch.getBookFlags(["blah"]), (False, False, True), "Unknown flag should be true")
		
	# Manga and backedup flags together
	def test_getBookFlags_mangaAndBackedup(self):
		self.assertEqual(comicSpreadStitch.getBookFlags(["backedup", "manga"]), (True, True, False), "Manga and backedup flags should be true")
	
	# processPages tests — these will probably require some test images to be stored in a subdirectory
	
	# The line of code that tells me whether two images are identical or not:
	# self.assertTrue(processedImg.shape == testImg.shape and not(np.bitwise_xor(processedImg, testImg).any()))
	# This may require some testing to be sure it behaves as expected
	
	# Stitch only
	# def test_processPages_stitchOnly(self):
		# testImgDir = os.path.join(os.path.dirname(__file__), "test-resources", "img")
		# os.chdir(testImgDir)
		# testImg = cv2.imread("baboonboat.png")
		# baboon = cv2.imread("baboon.png")
		# boat = cv2.imread("boat.png")
		# Call processPages with proper parameters
		# Retrieve current directory state
		# Restore original directory state
		# Compare output with testImg
		# Check directory state
	
	# Stitch back cover only
	
	# Rotate right only
	
	# Stitch and rotate right
	
	# Rotate left only
	
	# Stitch and rotate left
	
	# Stitch only in manga mode
	
	# Stitch back cover only in manga mode
	
	# Rotate right only in manga mode
	
	# Stitch and rotate right in manga mode
	
	# Rotate left only in manga mode
	
	# Stitch and rotate left in manga mode

if __name__ == "__main__":
	unittest.main()
