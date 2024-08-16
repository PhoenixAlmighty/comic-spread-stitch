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
	
	# 3 page deletions, no modifications
	def test_printSuccess_threeDeletions(self):
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		comicSpreadStitch.printSuccess("Test book", [[2, "d"], [4, "d"], [6, "d"]])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book has had 3 pages deleted.\n", "Console output is wrong for 3 page deletions and no page modifications.")
		
	# Check that all modifiers are handled correctly
	def test_printSuccess_allModifiers(self):
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		comicSpreadStitch.printSuccess("Test book", [[2, ""], [4, "m"], [6, "l"], [8, "r"], [10, "s"], [12, "d"], [14, ""]])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on pages 2, 3, 4, 6, 8, and 10.\n", "At least one modifier has been handled incorrectly.")
	
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
		self.assertEqual(capturedOutput.getvalue(), "Page list for Test book directory contains at least one thing that's not a number and doesn't match any of the available page modifiers. Check your input.\n", "Console output is incorrect for non-numeric page list.")
		
	# Letters in list that don't match the defined modifiers
	def test_convertPageList_wrongModifiers(self):
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		pageList = comicSpreadStitch.convertPageList("1,2,3a", "Test book directory")
		sys.stdout = sys.__stdout__
		self.assertFalse(pageList, "Should return False if string contains letters that aren't attached to numbers.")
		self.assertEqual(capturedOutput.getvalue(), "Page list for Test book directory contains at least one thing that's not a number and doesn't match any of the available page modifiers. Check your input.\n", "Console output is incorrect for non-defined modifiers.")
		
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
		self.assertEqual(comicSpreadStitch.convertPageList("5l, 3r, 9s, 7m, 10d", "Test book directory"), [[3, "r"], [5, "l"], [7, "m"], [9, "s"], [10, "d"]], "Should return a sorted list of lists, where each list is an integer followed by one of the following letters: l, m, r, s, d, without the whitespace triggering a return value of False.")
	
	# Deletion range
	def test_convertPageList_deletionRange(self):
		self.assertEqual(comicSpreadStitch.convertPageList("4,33-36d", "Test book directory"), [[4, ""], [33, "d"], [34, "d"], [35, "d"], [36, "d"]], "Should return each page from 33 to 36 inclusive for deletion, plus page 4 for stitching.")
	
	# findBookFile tests
	
	# Directory has no CBZ file
	def test_findBookFile_noCBZ(self):
		noCBZ = os.path.join(os.path.dirname(__file__), "test-resources", "no-cbz")
		os.chdir(noCBZ)
		self.assertEqual(comicSpreadStitch.findBookFile(False, False, False), "", "{} should not have a CBZ file.".format(noCBZ))
		
	# Directory has a CBZ_OLD file
	def test_findBookFile_CBZOLD(self):
		yesCBZOLD = os.path.join(os.path.dirname(__file__), "test-resources", "cbz-old")
		os.chdir(yesCBZOLD)
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		file = comicSpreadStitch.findBookFile(False, False, False)
		sys.stdout = sys.__stdout__
		self.assertFalse(file, "{} should have a CBZ_OLD file.".format(yesCBZOLD))
		self.assertEqual(capturedOutput.getvalue(),
			"{} contains a backup from a previous run. As such, this book will be skipped. Try again after either deleting the CBZ_OLD file or adding \"backedup\" as an option on the input.\n\n".format(yesCBZOLD),
			"Console output is incorrect.")
		
	# Directory has a CBZ file and no CBZ_OLD file
	def test_findBookFile_onlyCBZ(self):
		correctFilesDir = os.path.join(os.path.dirname(__file__), "test-resources", "cbz")
		os.chdir(correctFilesDir)
		self.assertEqual(comicSpreadStitch.findBookFile(False, False, False), "dummy.cbz", "{} should have a CBZ file but not a CBZ_OLD file.".format(correctFilesDir))
		
	# Directory has a CBZ_OLD file, but backedup flag is set
	def test_findBookFile_backedupCBZOLD(self):
		yesCBZOLD = os.path.join(os.path.dirname(__file__), "test-resources", "cbz-old")
		os.chdir(yesCBZOLD)
		self.assertEqual(comicSpreadStitch.findBookFile(True, False, False), "dummy.cbz", "The CBZ_OLD file in {} should be ignored because the backedup flag is set.".format(yesCBZOLD))
		
	# Directory has no CBZ_OLD file, but backedup flag is set
	def test_findBookFile_backedupCBZ(self):
		correctFilesDir = os.path.join(os.path.dirname(__file__), "test-resources", "cbz")
		os.chdir(correctFilesDir)
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		file = comicSpreadStitch.findBookFile(True, False, False)
		sys.stdout = sys.__stdout__
		self.assertFalse(file, "{} should not have a CBZ_OLD file.".format(correctFilesDir))
		self.assertEqual(capturedOutput.getvalue(),
			"{} had the backedup flag set, but no backup was found. Remove the backedup flag for this directory to process the book normally.\n\n".format(correctFilesDir),
			"Console output is incorrect.")
	
	# TODO: add tests for ePubs
	
	# TODO: add tests for PDFs
	
	# getBookFlags tests
	
	# No flags
	def test_getBookFlags_noFlags(self):
		self.assertEqual(comicSpreadStitch.getBookFlags([]), (False, False, False, False, False, False), "All flags should be false")
		
	# Manga flag only
	def test_getBookFlags_manga(self):
		self.assertEqual(comicSpreadStitch.getBookFlags(["manga"]), (True, False, False, False, False, False), "Manga flag should be true")
		
	# Backedup flag only
	def test_getBookFlags_backedup(self):
		self.assertEqual(comicSpreadStitch.getBookFlags(["backedup"]), (False, True, False, False, False, False), "Backedup flag should be true")
		
	# Epub flag only
	def test_getBookFlags_epub(self):
		self.assertEqual(comicSpreadStitch.getBookFlags(["epub"]), (False, False, True, False, False, False), "Epub flag should be true")
	
	# PDF flag only
	def test_getBookFlags_pdf(self):
		self.assertEqual(comicSpreadStitch.getBookFlags(["pdf"]), (False, False, False, True, False, False), "PDF flag should be true")
		
	# Rightlines flag only
	def test_getBookFlags_rightlines(self):
		self.assertEqual(comicSpreadStitch.getBookFlags(["rightlines"]), (False, False, False, False, True, False), "Rightlines flag should be true")
		
	# Unknown flag only
	def test_getBookFlags_unknown(self):
		self.assertEqual(comicSpreadStitch.getBookFlags(["blah"]), (False, False, False, False, False, True), "Unknown flag should be true")
		
	# Manga and backedup flags together
	def test_getBookFlags_mangaAndBackedup(self):
		self.assertEqual(comicSpreadStitch.getBookFlags(["backedup", "manga"]), (True, True, False, False, False, False), "Manga and backedup flags should be true")
	
	# processPages tests
	# The images used here are from https://github.com/mohammadimtiazz/standard-test-images-for-Image-Processing
	
	# Stitch only
	def test_processPages_stitchOnly(self):
		testImgDir = os.path.join(os.path.dirname(__file__), "test-resources", "img")
		os.chdir(testImgDir)
		testImg = cv2.imread("baboonboat.png")
		baboon = cv2.imread("baboon.png")
		boat = cv2.imread("boat.png")
		
		comicSpreadStitch.processPages(["baboon.png", "boat.png"], [[1, ""]], False, 50, 75)
		
		# By this point, boat.png should no longer exist and baboon.png should match baboonboat.png
		# Retrieving file list now but checking it later so that the directory will be restored to its original state even if an assertion fails
		imgs = os.listdir()
		processedImg = cv2.imread("baboon.png")
		
		# Restore original directory state
		cv2.imwrite("baboon.png", baboon)
		cv2.imwrite("boat.png", boat)
		
		# Compare output with testImg
		self.assertTrue(processedImg.shape == testImg.shape and not(np.bitwise_xor(processedImg, testImg).any()), "Output image is incorrect")
		
		# Check directory state
		self.assertTrue("baboon.png" in imgs, "baboon.png is missing")
		self.assertFalse("boat.png" in imgs, "boat.png was not deleted")
	
	# Stitch back cover only
	def test_processPages_stitchBackCoverOnly(self):
		testImgDir = os.path.join(os.path.dirname(__file__), "test-resources", "img")
		os.chdir(testImgDir)
		testImg = cv2.imread("boatbaboon.png")
		baboon = cv2.imread("baboon.png")
		boat = cv2.imread("boat.png")
		
		comicSpreadStitch.processPages(["baboon.png", "boat.png"], [[0, ""]], False, 50, 75)
		
		# By this point, baboon.png should still exist and boat.png should match boatbaboon.png
		# Retrieving file list now but checking it later so that the directory will be restored to its original state even if an assertion fails
		imgs = os.listdir()
		processedImg = cv2.imread("boat.png")
		
		# Restore original directory state
		cv2.imwrite("baboon.png", baboon)
		cv2.imwrite("boat.png", boat)
		
		# Compare output with testImg
		self.assertTrue(processedImg.shape == testImg.shape and not(np.bitwise_xor(processedImg, testImg).any()), "Output image is incorrect")
		
		# Check directory state
		self.assertTrue("baboon.png" in imgs, "baboon.png is missing")
		self.assertTrue("boat.png" in imgs, "boat.png is missing")
	
	# Rotate right only
	def test_processPages_rotateRight(self):
		testImgDir = os.path.join(os.path.dirname(__file__), "test-resources", "img")
		os.chdir(testImgDir)
		testImg = cv2.imread("babooncw.png")
		baboon = cv2.imread("baboon.png")
		
		comicSpreadStitch.processPages(["baboon.png", "boat.png"], [[1, "r"]], False, 50, 75)
		
		# By this point, baboon.png should match babooncw.png
		processedImg = cv2.imread("baboon.png")
		
		# Restore original directory state
		cv2.imwrite("baboon.png", baboon)
		
		# Compare output with testImg
		self.assertTrue(processedImg.shape == testImg.shape and not(np.bitwise_xor(processedImg, testImg).any()), "Output image is incorrect")
	
	# Stitch and rotate right
	def test_processPages_stitchRotateRight(self):
		testImgDir = os.path.join(os.path.dirname(__file__), "test-resources", "img")
		os.chdir(testImgDir)
		testImg = cv2.imread("baboonboatcw.png")
		baboon = cv2.imread("baboon.png")
		boat = cv2.imread("boat.png")
		
		comicSpreadStitch.processPages(["baboon.png", "boat.png"], [[1, "s"]], False, 50, 75)
		
		# By this point, boat.png should no longer exist and baboon.png should match baboonboatcw.png
		# Retrieving file list now but checking it later so that the directory will be restored to its original state even if an assertion fails
		imgs = os.listdir()
		processedImg = cv2.imread("baboon.png")
		
		# Restore original directory state
		cv2.imwrite("baboon.png", baboon)
		cv2.imwrite("boat.png", boat)
		
		# Compare output with testImg
		self.assertTrue(processedImg.shape == testImg.shape and not(np.bitwise_xor(processedImg, testImg).any()), "Output image is incorrect")
		
		# Check directory state
		self.assertTrue("baboon.png" in imgs, "baboon.png is missing")
		self.assertFalse("boat.png" in imgs, "boat.png was not deleted")
	
	# Rotate left only
	def test_processPages_rotateLeft(self):
		testImgDir = os.path.join(os.path.dirname(__file__), "test-resources", "img")
		os.chdir(testImgDir)
		testImg = cv2.imread("baboonccw.png")
		baboon = cv2.imread("baboon.png")
		
		comicSpreadStitch.processPages(["baboon.png", "boat.png"], [[1, "l"]], False, 50, 75)
		
		# By this point, baboon.png should match baboonccw.png
		processedImg = cv2.imread("baboon.png")
		
		# Restore original directory state
		cv2.imwrite("baboon.png", baboon)
		
		# Compare output with testImg
		self.assertTrue(processedImg.shape == testImg.shape and not(np.bitwise_xor(processedImg, testImg).any()), "Output image is incorrect")
	
	# Stitch and rotate left
	def test_processPages_stitchRotateLeft(self):
		testImgDir = os.path.join(os.path.dirname(__file__), "test-resources", "img")
		os.chdir(testImgDir)
		testImg = cv2.imread("baboonboatccw.png")
		baboon = cv2.imread("baboon.png")
		boat = cv2.imread("boat.png")
		
		comicSpreadStitch.processPages(["baboon.png", "boat.png"], [[1, "m"]], False, 50, 75)
		
		# By this point, boat.png should no longer exist and baboon.png should match baboonboatccw.png
		# Retrieving file list now but checking it later so that the directory will be restored to its original state even if an assertion fails
		imgs = os.listdir()
		processedImg = cv2.imread("baboon.png")
		
		# Restore original directory state
		cv2.imwrite("baboon.png", baboon)
		cv2.imwrite("boat.png", boat)
		
		# Compare output with testImg
		self.assertTrue(processedImg.shape == testImg.shape and not(np.bitwise_xor(processedImg, testImg).any()), "Output image is incorrect")
		
		# Check directory state
		self.assertTrue("baboon.png" in imgs, "baboon.png is missing")
		self.assertFalse("boat.png" in imgs, "boat.png was not deleted")
	
	# Delete
	def test_processPages_delete(self):
		testImgDir = os.path.join(os.path.dirname(__file__), "test-resources", "img")
		os.chdir(testImgDir)
		boat = cv2.imread("boat.png")
		
		comicSpreadStitch.processPages(["baboon.png", "boat.png"], [[2, "d"]], False, 50, 75)
		
		# By this point, boat.png should no longer exist; nothing else should be changed
		imgs = os.listdir()
		
		# Restore original directory state
		cv2.imwrite("boat.png", boat)
		
		# Check directory state
		self.assertFalse("boat.png" in imgs, "boat.png was not deleted")
	
	# Stitch only in manga mode
	def test_processPages_stitchOnlyManga(self):
		testImgDir = os.path.join(os.path.dirname(__file__), "test-resources", "img")
		os.chdir(testImgDir)
		testImg = cv2.imread("boatbaboon.png")
		baboon = cv2.imread("baboon.png")
		boat = cv2.imread("boat.png")
		
		comicSpreadStitch.processPages(["baboon.png", "boat.png"], [[1, ""]], True, 50, 75)
		
		# By this point, boat.png should no longer exist and baboon.png should match boatbaboon.png
		# Retrieving file list now but checking it later so that the directory will be restored to its original state even if an assertion fails
		imgs = os.listdir()
		processedImg = cv2.imread("baboon.png")
		
		# Restore original directory state
		cv2.imwrite("baboon.png", baboon)
		cv2.imwrite("boat.png", boat)
		
		# Compare output with testImg
		self.assertTrue(processedImg.shape == testImg.shape and not(np.bitwise_xor(processedImg, testImg).any()), "Output image is incorrect")
		
		# Check directory state
		self.assertTrue("baboon.png" in imgs, "baboon.png is missing")
		self.assertFalse("boat.png" in imgs, "boat.png was not deleted")
	
	# Stitch back cover only in manga mode
	def test_processPages_stitchBackCoverOnlyManga(self):
		testImgDir = os.path.join(os.path.dirname(__file__), "test-resources", "img")
		os.chdir(testImgDir)
		testImg = cv2.imread("baboonboat.png")
		baboon = cv2.imread("baboon.png")
		boat = cv2.imread("boat.png")
		
		comicSpreadStitch.processPages(["baboon.png", "boat.png"], [[0, ""]], True, 50, 75)
		
		# By this point, baboon.png should still exist and boat.png should match baboonboat.png
		# Retrieving file list now but checking it later so that the directory will be restored to its original state even if an assertion fails
		imgs = os.listdir()
		processedImg = cv2.imread("boat.png")
		
		# Restore original directory state
		cv2.imwrite("baboon.png", baboon)
		cv2.imwrite("boat.png", boat)
		
		# Compare output with testImg
		self.assertTrue(processedImg.shape == testImg.shape and not(np.bitwise_xor(processedImg, testImg).any()), "Output image is incorrect")
		
		# Check directory state
		self.assertTrue("baboon.png" in imgs, "baboon.png is missing")
		self.assertTrue("boat.png" in imgs, "boat.png is missing")
	
	# Rotate right only in manga mode
	def test_processPages_rotateRightManga(self):
		testImgDir = os.path.join(os.path.dirname(__file__), "test-resources", "img")
		os.chdir(testImgDir)
		testImg = cv2.imread("babooncw.png")
		baboon = cv2.imread("baboon.png")
		
		comicSpreadStitch.processPages(["baboon.png", "boat.png"], [[1, "r"]], True, 50, 75)
		
		# By this point, baboon.png should match babooncw.png
		processedImg = cv2.imread("baboon.png")
		
		# Restore original directory state
		cv2.imwrite("baboon.png", baboon)
		
		# Compare output with testImg
		self.assertTrue(processedImg.shape == testImg.shape and not(np.bitwise_xor(processedImg, testImg).any()), "Output image is incorrect")
	
	# Stitch and rotate right in manga mode
	def test_processPages_stitchRotateRightManga(self):
		testImgDir = os.path.join(os.path.dirname(__file__), "test-resources", "img")
		os.chdir(testImgDir)
		testImg = cv2.imread("boatbabooncw.png")
		baboon = cv2.imread("baboon.png")
		boat = cv2.imread("boat.png")
		
		comicSpreadStitch.processPages(["baboon.png", "boat.png"], [[1, "s"]], True, 50, 75)
		
		# By this point, boat.png should no longer exist and baboon.png should match boatbabooncw.png
		# Retrieving file list now but checking it later so that the directory will be restored to its original state even if an assertion fails
		imgs = os.listdir()
		processedImg = cv2.imread("baboon.png")
		
		# Restore original directory state
		cv2.imwrite("baboon.png", baboon)
		cv2.imwrite("boat.png", boat)
		
		# Compare output with testImg
		self.assertTrue(processedImg.shape == testImg.shape and not(np.bitwise_xor(processedImg, testImg).any()), "Output image is incorrect")
		
		# Check directory state
		self.assertTrue("baboon.png" in imgs, "baboon.png is missing")
		self.assertFalse("boat.png" in imgs, "boat.png was not deleted")
	
	# Rotate left only in manga mode
	def test_processPages_rotateLeftManga(self):
		testImgDir = os.path.join(os.path.dirname(__file__), "test-resources", "img")
		os.chdir(testImgDir)
		testImg = cv2.imread("baboonccw.png")
		baboon = cv2.imread("baboon.png")
		
		comicSpreadStitch.processPages(["baboon.png", "boat.png"], [[1, "l"]], True, 50, 75)
		
		# By this point, baboon.png should match baboonccw.png
		processedImg = cv2.imread("baboon.png")
		
		# Restore original directory state
		cv2.imwrite("baboon.png", baboon)
		
		# Compare output with testImg
		self.assertTrue(processedImg.shape == testImg.shape and not(np.bitwise_xor(processedImg, testImg).any()), "Output image is incorrect")
	
	# Stitch and rotate left in manga mode
	def test_processPages_stitchRotateLeftManga(self):
		testImgDir = os.path.join(os.path.dirname(__file__), "test-resources", "img")
		os.chdir(testImgDir)
		testImg = cv2.imread("boatbaboonccw.png")
		baboon = cv2.imread("baboon.png")
		boat = cv2.imread("boat.png")
		
		comicSpreadStitch.processPages(["baboon.png", "boat.png"], [[1, "m"]], True, 50, 75)
		
		# By this point, boat.png should no longer exist and baboon.png should match boatbaboonccw.png
		# Retrieving file list now but checking it later so that the directory will be restored to its original state even if an assertion fails
		imgs = os.listdir()
		processedImg = cv2.imread("baboon.png")
		
		# Restore original directory state
		cv2.imwrite("baboon.png", baboon)
		cv2.imwrite("boat.png", boat)
		
		# Compare output with testImg
		self.assertTrue(processedImg.shape == testImg.shape and not(np.bitwise_xor(processedImg, testImg).any()), "Output image is incorrect")
		
		# Check directory state
		self.assertTrue("baboon.png" in imgs, "baboon.png is missing")
		self.assertFalse("boat.png" in imgs, "boat.png was not deleted")
	
	# Delete in manga mode
	def test_processPages_deleteManga(self):
		testImgDir = os.path.join(os.path.dirname(__file__), "test-resources", "img")
		os.chdir(testImgDir)
		boat = cv2.imread("boat.png")
		
		comicSpreadStitch.processPages(["baboon.png", "boat.png"], [[2, "d"]], True, 50, 75)
		
		# By this point, boat.png should no longer exist; nothing else should be changed
		imgs = os.listdir()
		
		# Restore original directory state
		cv2.imwrite("boat.png", boat)
		
		# Check directory state
		self.assertFalse("boat.png" in imgs, "boat.png was not deleted")
	
	# stitchPages tests
	
	# Sanity with baboon.png
	def test_stitchPages_baboonSanity(self):
		testImgDir = os.path.join(os.path.dirname(__file__), "test-resources", "img")
		os.chdir(testImgDir)
		baboon = cv2.imread("baboon.png")
		left = cv2.imread("leftbaboon.png")
		right = cv2.imread("rightbaboon.png")
		
		combImg = comicSpreadStitch.stitchPages(left, right, 50, 75)
		
		self.assertTrue(combImg.shape == baboon.shape and not(np.bitwise_xor(combImg, baboon).any()), "Output image is incorrect")

if __name__ == "__main__":
	unittest.main()
