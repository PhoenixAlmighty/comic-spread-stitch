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
import processPdf
import os
from pypdf import PdfReader

class TestProcessPdf(unittest.TestCase):
	# setup and teardown
	
	def setUp(self):
		pdfPath = os.path.join(os.path.dirname(__file__), "test-resources", "pdf")
		os.chdir(pdfPath)
		self.book = "3page.pdf"
	
	def tearDown(self):
		if os.path.isfile(self.book + "_old"):
			os.remove(self.book)
			os.rename(self.book + "_old", self.book)
	
	# last page tests
	# These tests do not compare the content of the PDFs, since I don't know how to do that; they just compare numbers of pages
	
	# last page left untouched
	def test_processPdf_lastPageUntouched(self):
		processPdf.processPdf(self.book, [[1, ""]], False, False)
		oldRead = PdfReader(self.book + "_old")
		newRead = PdfReader(self.book)
		self.assertEqual(len(oldRead.pages) - 1, len(newRead.pages), "Backup file should have 1 page more than processed file")
	
	# covers stitched together
	def test_processPdf_coversStitched(self):
		processPdf.processPdf(self.book, [[0, ""]], False, False)
		oldRead = PdfReader(self.book + "_old")
		newRead = PdfReader(self.book)
		self.assertEqual(len(oldRead.pages), len(newRead.pages), "Backup file and processed file should have same number of pages")
	
	# last page deleted
	def test_processPdf_lastPageDeleted(self):
		processPdf.processPdf(self.book, [[3, "d"]], False, False)
		oldRead = PdfReader(self.book + "_old")
		newRead = PdfReader(self.book)
		self.assertEqual(len(oldRead.pages) - 1, len(newRead.pages), "Backup file should have 1 page more than processed file")
	
	# last page turned clockwise
	# error not caught: last page not rotated
	def test_processPdf_lastPageCw(self):
		processPdf.processPdf(self.book, [[3, "r"]], False, False)
		oldRead = PdfReader(self.book + "_old")
		newRead = PdfReader(self.book)
		self.assertEqual(len(oldRead.pages), len(newRead.pages), "Backup file and processed file should have same number of pages")
	
	# last page turned counterclockwise
	# error not caught: last page not rotated
	def test_processPdf_lastPageCcw(self):
		processPdf.processPdf(self.book, [[3, "l"]], False, False)
		oldRead = PdfReader(self.book + "_old")
		newRead = PdfReader(self.book)
		self.assertEqual(len(oldRead.pages), len(newRead.pages), "Backup file and processed file should have same number of pages")
	
	# last page stitched to previous
	def test_processPdf_lastPageStitched(self):
		processPdf.processPdf(self.book, [[2, ""]], False, False)
		oldRead = PdfReader(self.book + "_old")
		newRead = PdfReader(self.book)
		self.assertEqual(len(oldRead.pages) - 1, len(newRead.pages), "Backup file should have 1 page more than processed file")

if __name__ == "__main__":
	unittest.main()
