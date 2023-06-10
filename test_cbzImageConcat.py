import unittest
import cbzImageConcat

class TestCbzImageConcat(unittest.TestCase):
	def test_printSuccess:
		# test printSuccess:
		# Back cover only
		# Back cover + 1 spread
		# Back cover + 2 spreads
		# Back cover + 3 or more spreads
		# 1 spread
		# 2 spreads
		# 3 or more spreads
	
	def test_bookDirIsValid:
		# test bookDirIsValid:
		# No book directory
		# Book directory that doesn't exist on my computer
		# Book directory that does exist on my computer
	
	def test_convertPageList:
		# test convertPageList:
		# No pages
		# Letters in list
		# Only numbers in list
	
	def test_findCBZFile:
		# test findCBZFile:
		# Directory has no CBZ file
		# Directory has a CBZ_OLD file
		# Directory has a CBZ file and no CBZ_OLD file

if __name__ == "__main__":
	unittest.main()
