import unittest
import cbzImageConcat
import os
import io
import sys

class TestCbzImageConcat(unittest.TestCase):
	def test_printSuccess(self):
		# Back cover only
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		cbzImageConcat.printSuccess("Test book", [0])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on the back cover.\n", "Console output is wrong for back cover only.")
		
		# Back cover + 1 spread
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		cbzImageConcat.printSuccess("Test book", [0, 2])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on the back cover and page 2.\n", "Console output is wrong for back cover plus 1 spread.")
		
		# Back cover + 2 spreads
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		cbzImageConcat.printSuccess("Test book", [0, 2, 4])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on the back cover and pages 2 and 3.\n", "Console output is wrong for back cover plus 2 spreads.")
		
		# Back cover + 3 or more spreads
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		cbzImageConcat.printSuccess("Test book", [0, 2, 4, 6])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on the back cover and pages 2, 3, and 4.\n", "Console output is wrong for back cover plus 3 spreads.")
		
		# 1 spread
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		cbzImageConcat.printSuccess("Test book", [2])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on page 2.\n", "Console output is wrong for 1 spread.")
		
		# 2 spreads
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		cbzImageConcat.printSuccess("Test book", [2, 4])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on pages 2 and 3.\n", "Console output is wrong for 2 spreads.")
		
		# 3 or more spreads
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		cbzImageConcat.printSuccess("Test book", [2, 4, 6])
		sys.stdout = sys.__stdout__
		self.assertEqual(capturedOutput.getvalue(), "Test book successfully altered on pages 2, 3, and 4.\n", "Console output is wrong for 3 spreads.")
	
	def test_bookDirIsValid(self):
		# No book directory
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		validity = cbzImageConcat.bookDirIsValid("")
		sys.stdout = sys.__stdout__
		self.assertFalse(validity, "Empty string for book directory should return false.")
		self.assertEqual(capturedOutput.getvalue(), "No book directory on this line. Check your input.\n", "Console output is incorrect for empty string input as book directory.")
		
		# Book directory that doesn't exist on my computer
		nonexistentDir = "D:\Calibre Library\Erik Larsen\Savage Dragon #179 (1429)"
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		validity = cbzImageConcat.bookDirIsValid(nonexistentDir)
		sys.stdout = sys.__stdout__
		self.assertFalse(validity, "Book directory that doesn't exist on this computer should return false.")
		self.assertEqual(capturedOutput.getvalue(), "{} does not exist. Check your filepath.\n".format(nonexistentDir), "Console output is incorrect for nonexistent book directory.")
		
		# Book directory that does exist on my computer
		realBookDir = "D:\Calibre Library\Erik Larsen\Savage Dragon #179 (1428)"
		self.assertTrue(cbzImageConcat.bookDirIsValid(realBookDir), "Directory that exists should return true.")
	
	def test_convertPageList(self):
		# No pages
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		pageList = cbzImageConcat.convertPageList("", "Test book directory")
		sys.stdout = sys.__stdout__
		self.assertFalse(pageList, "Should return False if string is empty.")
		self.assertEqual(capturedOutput.getvalue(), "Test book directory has no pages to combine. Check your input.\n", "Console output is incorrect for empty page list.")
		
		# Letters in list
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		pageList = cbzImageConcat.convertPageList("1,2,a", "Test book directory")
		sys.stdout = sys.__stdout__
		self.assertFalse(pageList, "Should return False if string contains letters.")
		self.assertEqual(capturedOutput.getvalue(), "Page list for Test book directory contains at least one thing that's not a number. Check your input.\n", "Console output is incorrect for non-numeric page list.")
		
		# Only numbers in list
		self.assertEqual(cbzImageConcat.convertPageList("5,3,7", "Test book directory"), [3, 5, 7], "Should return a sorted list of integers.")
		
		# Only numbers in list with spaces
		self.assertEqual(cbzImageConcat.convertPageList("5, 3, 7 ", "Test book directory"), [3, 5, 7], "Should return a sorted list of integers without the whitespace triggering a return value of False.")
	
	def test_findCBZFile(self):
		# Directory has no CBZ file
		noCBZ = "D:\Calibre Library\Diane Duane\A Wizard Abroad (686)"
		os.chdir(noCBZ)
		self.assertEqual(cbzImageConcat.findCBZFile(), "", "{} should not have a CBZ file.".format(noCBZ))
		
		# Directory has a CBZ_OLD file
		yesCBZOLD = "D:\Calibre Library\Erik Larsen\Savage Dragon #180 (1427)"
		os.chdir(yesCBZOLD)
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		file = cbzImageConcat.findCBZFile()
		sys.stdout = sys.__stdout__
		self.assertFalse(file, "{} should have a CBZ_OLD file.".format(yesCBZOLD))
		self.assertEqual(capturedOutput.getvalue(),
			"{} contains a CBZ_OLD file like the ones this script leaves behind as backups. As such, this book will be skipped. Try again after moving or deleting the CBZ_OLD file.\n\n".format(yesCBZOLD),
			"Console output is incorrect.")
		
		# Directory has a CBZ file and no CBZ_OLD file
		correctFilesDir = "D:\Calibre Library\Erik Larsen\Savage Dragon #179 (1428)"
		os.chdir(correctFilesDir)
		self.assertEqual(cbzImageConcat.findCBZFile(), "Savage Dragon #179 - Erik Larsen.cbz", "{} should have a CBZ file but not a CBZ_OLD file.".format(correctFilesDir))

if __name__ == "__main__":
	unittest.main()
