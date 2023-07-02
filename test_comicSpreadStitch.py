import unittest
import comicSpreadStitch
import os
import io
import sys

class TestComicSpreadStitch(unittest.TestCase):
	def test_printSuccess(self):
		# Back cover only
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		comicSpreadStitch.printSuccess("Test book", [[0, ""]])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on the back cover.\n", "Console output is wrong for back cover only.")
		
		# Back cover + 1 spread
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		comicSpreadStitch.printSuccess("Test book", [[0, ""], [2, ""]])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on the back cover and page 2.\n", "Console output is wrong for back cover plus 1 spread.")
		
		# Back cover + 2 spreads
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		comicSpreadStitch.printSuccess("Test book", [[0, ""], [2, ""], [4, ""]])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on the back cover and pages 2 and 3.\n", "Console output is wrong for back cover plus 2 spreads.")
		
		# Back cover + 3 or more spreads
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		comicSpreadStitch.printSuccess("Test book", [[0, ""], [2, ""], [4, ""], [6, ""]])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on the back cover and pages 2, 3, and 4.\n", "Console output is wrong for back cover plus 3 spreads.")
		
		# 1 spread
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		comicSpreadStitch.printSuccess("Test book", [[2, ""]])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on page 2.\n", "Console output is wrong for 1 spread.")
		
		# 2 spreads
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		comicSpreadStitch.printSuccess("Test book", [[2, ""], [4, ""]])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on pages 2 and 3.\n", "Console output is wrong for 2 spreads.")
		
		# 3 or more spreads
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		comicSpreadStitch.printSuccess("Test book", [[2, ""], [4, ""], [6, ""]])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on pages 2, 3, and 4.\n", "Console output is wrong for 3 spreads.")
		
		### No modifiers above this line
		
		# 1 rotation followed by 1 spread
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		comicSpreadStitch.printSuccess("Test book", [[4, "l"], [6, ""]])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on pages 4 and 6.\n", "Console output is wrong for 2 spreads and 1 rotation.")
		
		# 2 spreads, 1 rotation
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		comicSpreadStitch.printSuccess("Test book", [[2, ""], [4, "l"], [6, ""]])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on pages 2, 3, and 5.\n", "Console output is wrong for 2 spreads and 1 rotation.")
		
		# 3 spreads, 1 of which is rotated
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		comicSpreadStitch.printSuccess("Test book", [[2, ""], [4, "m"], [6, ""]])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on pages 2, 3, and 4.\n", "Console output is wrong for 3 spreads, 1 of which has been rotated.")
		
		# Check that all modifiers are handled correctly
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		comicSpreadStitch.printSuccess("Test book", [[2, ""], [4, "m"], [6, "l"], [8, "r"], [10, "s"], [12, ""]])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on pages 2, 3, 4, 6, 8, and 9.\n", "At least one modifier has been handled incoreectly.")
	
	def test_bookDirIsValid(self):
		# No book directory
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		validity = comicSpreadStitch.bookDirIsValid("")
		sys.stdout = sys.__stdout__
		self.assertFalse(validity, "Empty string for book directory should return false.")
		self.assertEqual(capturedOutput.getvalue(), "No book directory on this line. Check your input.\n", "Console output is incorrect for empty string input as book directory.")
		
		# Book directory that doesn't exist on my computer
		nonexistentDir = "D:\Calibre Library\Erik Larsen\Savage Dragon #179 (1429)"
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		validity = comicSpreadStitch.bookDirIsValid(nonexistentDir)
		sys.stdout = sys.__stdout__
		self.assertFalse(validity, "Book directory that doesn't exist on this computer should return false.")
		self.assertEqual(capturedOutput.getvalue(), "{} does not exist. Check your filepath.\n".format(nonexistentDir), "Console output is incorrect for nonexistent book directory.")
		
		# Book directory that does exist on my computer
		realBookDir = "D:\Calibre Library\Erik Larsen\Savage Dragon #179 (1428)"
		self.assertTrue(comicSpreadStitch.bookDirIsValid(realBookDir), "Directory that exists should return true.")
	
	def test_convertPageList(self):
		# No pages
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		pageList = comicSpreadStitch.convertPageList("", "Test book directory")
		sys.stdout = sys.__stdout__
		self.assertFalse(pageList, "Should return False if string is empty.")
		self.assertEqual(capturedOutput.getvalue(), "Test book directory has no pages to combine. Check your input.\n", "Console output is incorrect for empty page list.")
		
		# Letters in list that aren't attached to numbers
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		pageList = comicSpreadStitch.convertPageList("1,2,a", "Test book directory")
		sys.stdout = sys.__stdout__
		self.assertFalse(pageList, "Should return False if string contains letters that aren't attached to numbers.")
		self.assertEqual(capturedOutput.getvalue(), "Page list for Test book directory contains at least one thing that's not a number and doesn't match any of the available per-page commands. Check your input.\n", "Console output is incorrect for non-numeric page list.")
		
		# Letters in list that don't match the defined modifiers
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		pageList = comicSpreadStitch.convertPageList("1,2,3a", "Test book directory")
		sys.stdout = sys.__stdout__
		self.assertFalse(pageList, "Should return False if string contains letters that aren't attached to numbers.")
		self.assertEqual(capturedOutput.getvalue(), "Page list for Test book directory contains at least one thing that's not a number and doesn't match any of the available per-page commands. Check your input.\n", "Console output is incorrect for non-defined modifiers.")
		
		# Only numbers in list
		self.assertEqual(comicSpreadStitch.convertPageList("5,3,7", "Test book directory"), [[3, ""], [5, ""], [7, ""]], "Should return a sorted list of lists, where each list is an integer followed by an empty string.")
		
		# Only numbers and spaces in list
		self.assertEqual(comicSpreadStitch.convertPageList("5, 3, 7 ", "Test book directory"), [[3, ""], [5, ""], [7, ""]], "Should return a sorted list of lists, where each list is an integer followed by an empty string, without the whitespace triggering a return value of False.")
		
		# Only numbers and modifiers in list
		self.assertEqual(comicSpreadStitch.convertPageList("5l,3r,9s,7m", "Test book directory"), [[3, "r"], [5, "l"], [7, "m"], [9, "s"]], "Should return a sorted list of lists, where each list is an integer followed by one of the following letters: l, m, r, s.")
		
		# Numbers, modifiers, and spaces in list
		self.assertEqual(comicSpreadStitch.convertPageList("5l, 3r, 9s, 7m", "Test book directory"), [[3, "r"], [5, "l"], [7, "m"], [9, "s"]], "Should return a sorted list of lists, where each list is an integer followed by one of the following letters: l, m, r, s, without the whitespace triggering a return value of False.")
	
	def test_findCBZFile(self):
		# Directory has no CBZ file
		noCBZ = "D:\Calibre Library\Diane Duane\A Wizard Abroad (686)"
		os.chdir(noCBZ)
		self.assertEqual(comicSpreadStitch.findCBZFile(), "", "{} should not have a CBZ file.".format(noCBZ))
		
		# Directory has a CBZ_OLD file
		yesCBZOLD = "D:\Calibre Library\Erik Larsen\Savage Dragon #180 (1427)"
		os.chdir(yesCBZOLD)
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		file = comicSpreadStitch.findCBZFile()
		sys.stdout = sys.__stdout__
		self.assertFalse(file, "{} should have a CBZ_OLD file.".format(yesCBZOLD))
		self.assertEqual(capturedOutput.getvalue(),
			"{} contains a CBZ_OLD file like the ones this script leaves behind as backups. As such, this book will be skipped. Try again after moving or deleting the CBZ_OLD file.\n\n".format(yesCBZOLD),
			"Console output is incorrect.")
		
		# Directory has a CBZ file and no CBZ_OLD file
		correctFilesDir = "D:\Calibre Library\Erik Larsen\Savage Dragon #179 (1428)"
		os.chdir(correctFilesDir)
		self.assertEqual(comicSpreadStitch.findCBZFile(), "Savage Dragon #179 - Erik Larsen.cbz", "{} should have a CBZ file but not a CBZ_OLD file.".format(correctFilesDir))

if __name__ == "__main__":
	unittest.main()
