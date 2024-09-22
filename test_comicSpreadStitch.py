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

import unittest
import comicSpreadStitch
import os
import io
import sys
import numpy as np
import cv2

class TestGetResultString(unittest.TestCase):
	# Back cover only
	def test_getResultString_backCoverOnly(self):
		resultString = comicSpreadStitch.getResultString("Test book", [[0, ""]])
		self.assertEqual(resultString,
						 "Test book successfully altered on the back cover.",
						 "Console output is wrong for back cover only.")
		
	# Back cover + 1 spread
	def test_getResultString_backCoverOneSpread(self):
		resultString = comicSpreadStitch.getResultString("Test book", [[0, ""], [2, ""]])
		self.assertEqual(resultString,
						 "Test book successfully altered on the back cover and page 2.",
						 "Console output is wrong for back cover plus 1 spread.")
		
	# Back cover + 2 spreads
	def test_getResultString_backCoverTwoSpreads(self):
		resultString = comicSpreadStitch.getResultString("Test book", [[0, ""], [2, ""], [4, ""]])
		self.assertEqual(resultString,
						 "Test book successfully altered on the back cover and pages 2 and 3.",
						 "Console output is wrong for back cover plus 2 spreads.")
		
	# Back cover + 3 or more spreads
	def test_getResultString_backCoverThreeSpreads(self):
		resultString = comicSpreadStitch.getResultString("Test book", [[0, ""], [2, ""], [4, ""], [6, ""]])
		self.assertEqual(resultString,
						 "Test book successfully altered on the back cover and pages 2, 3, and 4.",
						 "Console output is wrong for back cover plus 3 spreads.")
		
	# 1 spread
	def test_getResultString_oneSpread(self):
		resultString = comicSpreadStitch.getResultString("Test book", [[2, ""]])
		self.assertEqual(resultString,
						 "Test book successfully altered on page 2.",
						 "Console output is wrong for 1 spread.")
		
	# 2 spreads
	def test_getResultString_twoSpreads(self):
		resultString = comicSpreadStitch.getResultString("Test book", [[2, ""], [4, ""]])
		self.assertEqual(resultString,
						 "Test book successfully altered on pages 2 and 3.",
						 "Console output is wrong for 2 spreads.")
		
	# 3 or more spreads
	def test_getResultString_threeSpreads(self):
		resultString = comicSpreadStitch.getResultString("Test book", [[2, ""], [4, ""], [6, ""]])
		self.assertEqual(resultString,
						 "Test book successfully altered on pages 2, 3, and 4.",
						 "Console output is wrong for 3 spreads.")
		
	# 1 rotation followed by 1 spread
	def test_getResultString_rotationThenSpread(self):
		resultString = comicSpreadStitch.getResultString("Test book", [[4, "l"], [6, ""]])
		self.assertEqual(resultString,
						 "Test book successfully altered on pages 4 and 6.",
						 "Console output is wrong for 2 spreads and 1 rotation.")
		
	# 2 spreads, 1 rotation
	def test_getResultString_twoSpreadsOneRotation(self):
		resultString = comicSpreadStitch.getResultString("Test book", [[2, ""], [4, "l"], [6, ""]])
		self.assertEqual(resultString,
						 "Test book successfully altered on pages 2, 3, and 5.",
						 "Console output is wrong for 2 spreads and 1 rotation.")
		
	# 3 spreads, 1 of which is rotated
	def test_getResultString_threeSpreadsOneRotated(self):
		resultString = comicSpreadStitch.getResultString("Test book", [[2, ""], [4, "m"], [6, ""]])
		self.assertEqual(resultString,
						 "Test book successfully altered on pages 2, 3, and 4.",
						 "Console output is wrong for 3 spreads, 1 of which has been rotated.")
	
	# 3 page deletions, no modifications
	def test_getResultString_threeDeletions(self):
		resultString = comicSpreadStitch.getResultString("Test book", [[2, "d"], [4, "d"], [6, "d"]])
		self.assertEqual(resultString,
						 "Test book has had 3 pages deleted.",
						 "Console output is wrong for 3 page deletions and no page modifications.")
		
	# Check that all modifiers are handled correctly
	def test_getResultString_allModifiers(self):
		resultString = comicSpreadStitch.getResultString("Test book", [[2, ""], [4, "m"], [6, "l"], [8, "r"], [10, "s"], [12, "d"], [14, ""]])
		self.assertEqual(resultString,
						 "Test book successfully altered on pages 2, 3, 4, 6, 8, and 10.",
						 "At least one modifier has been handled incorrectly.")
	

class TestBookDirIsValid(unittest.TestCase):
	# No book directory
	def test_bookDirIsValid_noDirectory(self):
		validity, reason = comicSpreadStitch.bookDirIsValid("")
		self.assertFalse(validity, "Empty string for book directory should return false.")
		self.assertEqual(reason,
						 "No book directory on this line. Check your input.",
						 "Console output is incorrect for empty string input as book directory.")
		
	# Book directory that doesn't exist on my computer
	def test_bookDirIsValid_nonexistentDirectory(self):
		nonexistentDir = "D:\Calibre Library\Erik Larsen\Savage Dragon #179 (1429)"
		validity, reason = comicSpreadStitch.bookDirIsValid(nonexistentDir)
		self.assertFalse(validity, "Book directory that doesn't exist on this computer should return false.")
		self.assertEqual(reason,
						 f"{nonexistentDir} does not exist. Check your filepath.",
						 "Console output is incorrect for nonexistent book directory.")
		
	# Book directory that does exist on my computer
	def test_bookDirIsValid_realDirectory(self):
		realBookDir = "D:\Calibre Library\Erik Larsen\Savage Dragon #179 (1428)"
		self.assertEqual(comicSpreadStitch.bookDirIsValid(realBookDir), (True, ""), "Directory that exists should return true.")
	

class TestConvertPageList(unittest.TestCase):
	# No pages
	def test_convertPageList_noPages(self):
		pageList, reason = comicSpreadStitch.convertPageList("", "Test book directory")
		self.assertFalse(pageList, "Should return False if string is empty.")
		self.assertEqual(reason,
						 "Test book directory has no pages to combine. Check your input.",
						 "Reason is incorrect for empty page list.")
		
	# Letters in list that aren't attached to numbers
	def test_convertPageList_lonelyLetters(self):
		pageList, reason = comicSpreadStitch.convertPageList("1,2,a", "Test book directory")
		self.assertFalse(pageList, "Should return False if string contains letters that aren't attached to numbers.")
		self.assertEqual(reason,
						 "Page list for Test book directory contains at least one thing that's not a number and doesn't match any of the available page modifiers. Check your input.",
						 "Reason is incorrect for non-numeric page list.")
		
	# Letters in list that don't match the defined modifiers
	def test_convertPageList_wrongModifiers(self):
		pageList, reason = comicSpreadStitch.convertPageList("1,2,3a", "Test book directory")
		self.assertFalse(pageList, "Should return False if string contains letters that aren't attached to numbers.")
		self.assertEqual(reason,
						 "Page list for Test book directory contains at least one thing that's not a number and doesn't match any of the available page modifiers. Check your input.",
						 "Console output is incorrect for non-defined modifiers.")
		
	# Only numbers in list
	def test_convertPageList_numbersOnly(self):
		self.assertEqual(comicSpreadStitch.convertPageList("5,3,7", "Test book directory"),
						 ([[3, ""], [5, ""], [7, ""]], "",),
						 "Should return a tuple where the first element is a sorted list of lists, where each list is an integer followed by an empty string, and the second tuple element is an empty string.")
		
	# Only numbers and spaces in list
	def test_convertPageList_numbersAndSpaces(self):
		self.assertEqual(comicSpreadStitch.convertPageList("5, 3, 7 ", "Test book directory"),
						 ([[3, ""], [5, ""], [7, ""]], ""),
						 "Should return a tuple where the first element is a sorted list of lists, where each list is an integer followed by an empty string, and the second tuple element is an empty string, without the whitespace triggering a return value of False.")
		
	# Only numbers and modifiers in list
	def test_convertPageList_numbersAndModifiers(self):
		self.assertEqual(comicSpreadStitch.convertPageList("5l,3r,9s,7m", "Test book directory"),
						 ([[3, "r"], [5, "l"], [7, "m"], [9, "s"]], ""),
						 "Should return a tuple where the first element is a sorted list of lists, where each list is an integer followed by one of the following letters: l, m, r, s, and the second tuple element is an empty string.")
		
	# Numbers, modifiers, and spaces in list
	def test_convertPageList_numbersModifiersAndSpaces(self):
		self.assertEqual(comicSpreadStitch.convertPageList("5l, 3r, 9s, 7m, 10d", "Test book directory"),
						 ([[3, "r"], [5, "l"], [7, "m"], [9, "s"], [10, "d"]], ""),
						 "Should return a tuple where the first element is a sorted list of lists, where each list is an integer followed by one of the following letters: l, m, r, s, d, and the second tuple element is an empty string, without the whitespace triggering a return value of False.")
	
	# Deletion range
	def test_convertPageList_deletionRange(self):
		self.assertEqual(comicSpreadStitch.convertPageList("4,33-36d", "Test book directory"),
						 ([[4, ""], [33, "d"], [34, "d"], [35, "d"], [36, "d"]], ""),
						 "Should return a tuple where the first element is a list containing each page from 33 to 36 inclusive for deletion, plus page 4 for stitching, and the second tuple element is an empty string.")


class TestFindBookFile(unittest.TestCase):
	# Directory has no CBZ file
	def test_findBookFile_noCBZ(self):
		noCBZ = os.path.join(os.path.dirname(__file__), "test-resources", "no-cbz")
		os.chdir(noCBZ)
		self.assertEqual(comicSpreadStitch.findBookFile(False, False, False),
						 (False, f"{noCBZ} has no CBZ files in it. Check your input."),
						 f"{noCBZ} should not have a CBZ file.")
		
	# Directory has a CBZ_OLD file
	def test_findBookFile_CBZOLD(self):
		yesCBZOLD = os.path.join(os.path.dirname(__file__), "test-resources", "cbz-old")
		os.chdir(yesCBZOLD)
		valid, file = comicSpreadStitch.findBookFile(False, False, False)
		self.assertFalse(valid, f"{yesCBZOLD} should have a CBZ_OLD file.")
		self.assertEqual(file,
			f"{yesCBZOLD} contains a backup from a previous run. As such, this book will be skipped. Try again after either deleting the CBZ_OLD file or adding \"backedup\" as an option on the input.\n",
			"Console output is incorrect.")
		
	# Directory has a CBZ file and no CBZ_OLD file
	def test_findBookFile_onlyCBZ(self):
		correctFilesDir = os.path.join(os.path.dirname(__file__), "test-resources", "cbz")
		os.chdir(correctFilesDir)
		self.assertEqual(comicSpreadStitch.findBookFile(False, False, False), (True, "Test.cbz"), f"{correctFilesDir} should have a CBZ file but not a CBZ_OLD file.")
		
	# Directory has a CBZ_OLD file and backedup flag is set
	def test_findBookFile_backedupCBZOLD(self):
		yesCBZOLD = os.path.join(os.path.dirname(__file__), "test-resources", "cbz-old")
		os.chdir(yesCBZOLD)
		self.assertEqual(comicSpreadStitch.findBookFile(True, False, False), (True, "Test.cbz"), f"The CBZ_OLD file in {yesCBZOLD} should be ignored because the backedup flag is set.")
		
	# Directory has no CBZ_OLD file, but backedup flag is set
	def test_findBookFile_backedupCBZ(self):
		correctFilesDir = os.path.join(os.path.dirname(__file__), "test-resources", "cbz")
		os.chdir(correctFilesDir)
		valid, file = comicSpreadStitch.findBookFile(True, False, False)
		self.assertFalse(valid, f"{correctFilesDir} should not have a CBZ_OLD file.")
		self.assertEqual(file,
			f"{correctFilesDir} had the backedup flag set, but no backup was found. Remove the backedup flag for this directory to process the book normally.\n",
			"Console output is incorrect.")

	# Directory has no ePub file
	def test_findBookFile_noEpub(self):
		noCBZ = os.path.join(os.path.dirname(__file__), "test-resources", "no-cbz")
		os.chdir(noCBZ)
		self.assertEqual(comicSpreadStitch.findBookFile(False, True, False),
						 (False, f"{noCBZ} has no EPUB files in it. Check your input."),
						 f"{noCBZ} should not have an ePub file.")

	# TODO: add more tests for ePubs

	# Directory has no PDF file
	def test_findBookFile_noPdf(self):
		noCBZ = os.path.join(os.path.dirname(__file__), "test-resources", "no-cbz")
		os.chdir(noCBZ)
		self.assertEqual(comicSpreadStitch.findBookFile(False, False, True),
						 (False, f"{noCBZ} has no PDF files in it. Check your input."),
						 f"{noCBZ} should not have a PDF file.")
	
	# TODO: add more tests for PDFs
	

class TestGetBookFlags(unittest.TestCase):
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
	

class TestProcessPages(unittest.TestCase):
	# The images used here are from https://github.com/mohammadimtiazz/standard-test-images-for-Image-Processing
	
	def setUp(self):
		testImgDir = os.path.join(os.path.dirname(__file__), "test-resources", "img")
		os.chdir(testImgDir)
		self.baboon = cv2.imread("baboon.png")
		self.boat = cv2.imread("boat.png")
	
	def tearDown(self):
		# Restore original directory state
		cv2.imwrite("baboon.png", self.baboon)
		cv2.imwrite("boat.png", self.boat)
	
	# Stitch only
	def test_processPages_stitchOnly(self):
		testImg = cv2.imread("baboonboat.png")
		
		comicSpreadStitch.processPages(["baboon.png", "boat.png"], [[1, ""]], False, 50, 75)
		
		# By this point, boat.png should no longer exist and baboon.png should match baboonboat.png
		imgs = os.listdir()
		processedImg = cv2.imread("baboon.png")
		
		# Compare output with testImg
		self.assertTrue(processedImg.shape == testImg.shape and not(np.bitwise_xor(processedImg, testImg).any()), "Output image is incorrect")
		
		# Check directory state
		self.assertTrue("baboon.png" in imgs, "baboon.png is missing")
		self.assertFalse("boat.png" in imgs, "boat.png was not deleted")
	
	# Stitch back cover only
	def test_processPages_stitchBackCoverOnly(self):
		testImg = cv2.imread("boatbaboon.png")
		
		comicSpreadStitch.processPages(["baboon.png", "boat.png"], [[0, ""]], False, 50, 75)
		
		# By this point, baboon.png should still exist and boat.png should match boatbaboon.png
		imgs = os.listdir()
		processedImg = cv2.imread("boat.png")
		
		# Compare output with testImg
		self.assertTrue(processedImg.shape == testImg.shape and not(np.bitwise_xor(processedImg, testImg).any()), "Output image is incorrect")
		
		# Check directory state
		self.assertTrue("baboon.png" in imgs, "baboon.png is missing")
		self.assertTrue("boat.png" in imgs, "boat.png is missing")
	
	# Rotate right only
	def test_processPages_rotateRight(self):
		testImg = cv2.imread("babooncw.png")
		
		comicSpreadStitch.processPages(["baboon.png", "boat.png"], [[1, "r"]], False, 50, 75)
		
		# By this point, baboon.png should match babooncw.png
		processedImg = cv2.imread("baboon.png")
		
		# Compare output with testImg
		self.assertTrue(processedImg.shape == testImg.shape and not(np.bitwise_xor(processedImg, testImg).any()), "Output image is incorrect")
	
	# Stitch and rotate right
	def test_processPages_stitchRotateRight(self):
		testImg = cv2.imread("baboonboatcw.png")
		
		comicSpreadStitch.processPages(["baboon.png", "boat.png"], [[1, "s"]], False, 50, 75)
		
		# By this point, boat.png should no longer exist and baboon.png should match baboonboatcw.png
		imgs = os.listdir()
		processedImg = cv2.imread("baboon.png")
		
		# Compare output with testImg
		self.assertTrue(processedImg.shape == testImg.shape and not(np.bitwise_xor(processedImg, testImg).any()), "Output image is incorrect")
		
		# Check directory state
		self.assertTrue("baboon.png" in imgs, "baboon.png is missing")
		self.assertFalse("boat.png" in imgs, "boat.png was not deleted")
	
	# Rotate left only
	def test_processPages_rotateLeft(self):
		testImg = cv2.imread("baboonccw.png")
		
		comicSpreadStitch.processPages(["baboon.png", "boat.png"], [[1, "l"]], False, 50, 75)
		
		# By this point, baboon.png should match baboonccw.png
		processedImg = cv2.imread("baboon.png")
		
		# Compare output with testImg
		self.assertTrue(processedImg.shape == testImg.shape and not(np.bitwise_xor(processedImg, testImg).any()), "Output image is incorrect")
	
	# Stitch and rotate left
	def test_processPages_stitchRotateLeft(self):
		testImg = cv2.imread("baboonboatccw.png")
		
		comicSpreadStitch.processPages(["baboon.png", "boat.png"], [[1, "m"]], False, 50, 75)
		
		# By this point, boat.png should no longer exist and baboon.png should match baboonboatccw.png
		imgs = os.listdir()
		processedImg = cv2.imread("baboon.png")
		
		# Compare output with testImg
		self.assertTrue(processedImg.shape == testImg.shape and not(np.bitwise_xor(processedImg, testImg).any()), "Output image is incorrect")
		
		# Check directory state
		self.assertTrue("baboon.png" in imgs, "baboon.png is missing")
		self.assertFalse("boat.png" in imgs, "boat.png was not deleted")
	
	# Delete
	def test_processPages_delete(self):
		comicSpreadStitch.processPages(["baboon.png", "boat.png"], [[2, "d"]], False, 50, 75)
		
		# By this point, boat.png should no longer exist; nothing else should be changed
		imgs = os.listdir()
		
		# Check directory state
		self.assertFalse("boat.png" in imgs, "boat.png was not deleted")
	
	# Stitch only in manga mode
	def test_processPages_stitchOnlyManga(self):
		testImg = cv2.imread("boatbaboon.png")
		
		comicSpreadStitch.processPages(["baboon.png", "boat.png"], [[1, ""]], True, 50, 75)
		
		# By this point, boat.png should no longer exist and baboon.png should match boatbaboon.png
		imgs = os.listdir()
		processedImg = cv2.imread("baboon.png")
		
		# Compare output with testImg
		self.assertTrue(processedImg.shape == testImg.shape and not(np.bitwise_xor(processedImg, testImg).any()), "Output image is incorrect")
		
		# Check directory state
		self.assertTrue("baboon.png" in imgs, "baboon.png is missing")
		self.assertFalse("boat.png" in imgs, "boat.png was not deleted")
	
	# Stitch back cover only in manga mode
	def test_processPages_stitchBackCoverOnlyManga(self):
		testImg = cv2.imread("baboonboat.png")
		
		comicSpreadStitch.processPages(["baboon.png", "boat.png"], [[0, ""]], True, 50, 75)
		
		# By this point, baboon.png should still exist and boat.png should match baboonboat.png
		imgs = os.listdir()
		processedImg = cv2.imread("boat.png")
		
		# Compare output with testImg
		self.assertTrue(processedImg.shape == testImg.shape and not(np.bitwise_xor(processedImg, testImg).any()), "Output image is incorrect")
		
		# Check directory state
		self.assertTrue("baboon.png" in imgs, "baboon.png is missing")
		self.assertTrue("boat.png" in imgs, "boat.png is missing")
	
	# Rotate right only in manga mode
	def test_processPages_rotateRightManga(self):
		testImg = cv2.imread("babooncw.png")
		
		comicSpreadStitch.processPages(["baboon.png", "boat.png"], [[1, "r"]], True, 50, 75)
		
		# By this point, baboon.png should match babooncw.png
		processedImg = cv2.imread("baboon.png")
		
		# Compare output with testImg
		self.assertTrue(processedImg.shape == testImg.shape and not(np.bitwise_xor(processedImg, testImg).any()), "Output image is incorrect")
	
	# Stitch and rotate right in manga mode
	def test_processPages_stitchRotateRightManga(self):
		testImg = cv2.imread("boatbabooncw.png")
		
		comicSpreadStitch.processPages(["baboon.png", "boat.png"], [[1, "s"]], True, 50, 75)
		
		# By this point, boat.png should no longer exist and baboon.png should match boatbabooncw.png
		imgs = os.listdir()
		processedImg = cv2.imread("baboon.png")
		
		# Compare output with testImg
		self.assertTrue(processedImg.shape == testImg.shape and not(np.bitwise_xor(processedImg, testImg).any()), "Output image is incorrect")
		
		# Check directory state
		self.assertTrue("baboon.png" in imgs, "baboon.png is missing")
		self.assertFalse("boat.png" in imgs, "boat.png was not deleted")
	
	# Rotate left only in manga mode
	def test_processPages_rotateLeftManga(self):
		testImg = cv2.imread("baboonccw.png")
		
		comicSpreadStitch.processPages(["baboon.png", "boat.png"], [[1, "l"]], True, 50, 75)
		
		# By this point, baboon.png should match baboonccw.png
		processedImg = cv2.imread("baboon.png")
		
		# Compare output with testImg
		self.assertTrue(processedImg.shape == testImg.shape and not(np.bitwise_xor(processedImg, testImg).any()), "Output image is incorrect")
	
	# Stitch and rotate left in manga mode
	def test_processPages_stitchRotateLeftManga(self):
		testImg = cv2.imread("boatbaboonccw.png")
		
		comicSpreadStitch.processPages(["baboon.png", "boat.png"], [[1, "m"]], True, 50, 75)
		
		# By this point, boat.png should no longer exist and baboon.png should match boatbaboonccw.png
		imgs = os.listdir()
		processedImg = cv2.imread("baboon.png")
		
		# Compare output with testImg
		self.assertTrue(processedImg.shape == testImg.shape and not(np.bitwise_xor(processedImg, testImg).any()), "Output image is incorrect")
		
		# Check directory state
		self.assertTrue("baboon.png" in imgs, "baboon.png is missing")
		self.assertFalse("boat.png" in imgs, "boat.png was not deleted")
	
	# Delete in manga mode
	def test_processPages_deleteManga(self):
		
		comicSpreadStitch.processPages(["baboon.png", "boat.png"], [[2, "d"]], True, 50, 75)
		
		# By this point, boat.png should no longer exist; nothing else should be changed
		imgs = os.listdir()
		
		# Check directory state
		self.assertFalse("boat.png" in imgs, "boat.png was not deleted")
	

class TestStitchPages(unittest.TestCase):
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
