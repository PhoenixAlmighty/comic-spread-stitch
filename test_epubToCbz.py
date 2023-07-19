import unittest
import epubToCbz
import os
import shutil
import io
import sys

class TestEpubToCbz(unittest.TestCase):
	# getDocDir tests
	
	# no document directory
	def test_getDocDir_noDocDir(self):
		yesCBZOLD = os.path.join(os.path.dirname(__file__), "test-resources", "cbz-old")
		os.chdir(yesCBZOLD)
		self.assertFalse(epubToCbz.getDocDir(), "cbz-old should not contain a document directory.")
	
	# yes document directory
	def test_getDocDir_yesDocDir(self):
		extEpub = os.path.join(os.path.dirname(__file__), "test-resources", "extracted-epub")
		os.chdir(extEpub)
		self.assertEqual(epubToCbz.getDocDir(), "OEBPS", "extracted-epub should contain a document directory called OEBPS.")
	
	# findOpfFile tests
	
	# no OPF file
	def test_findOpfFile_noOpfFile(self):
		imageDir = os.path.join(os.path.dirname(__file__), "test-resources", "extracted-epub", "OEBPS", "images")
		os.chdir(imageDir)
		self.assertFalse(epubToCbz.findOpfFile(), "images should not contain an OPF file.")
	
	# yes OPF file
	def test_findOpfFile_yesOpfFile(self):
		docDir = os.path.join(os.path.dirname(__file__), "test-resources", "extracted-epub", "OEBPS")
		os.chdir(docDir)
		self.assertEqual(epubToCbz.findOpfFile(), "content.opf", "OEBPS should contain an OPF file called content.opf.")
	
	# getManifestAndSpine tests
	
	# basic sanity test
	def test_getManifestAndSpine_sanity(self):
		docDir = os.path.join(os.path.dirname(__file__), "test-resources", "extracted-epub", "OEBPS")
		os.chdir(docDir)
		opfFile = "content.opf"
		manifest, spine = epubToCbz.getManifestAndSpine(opfFile)
		expectedManifest = {'cover': 'cover.xhtml', 'cover-image': 'images/cover.jpg', 'ncx': 'toc.ncx', 'style': 'stylesheet.css', 'pagetemplate': 'page-template.xpgt', 'page_002': 'p002.xhtml', 'image_002': 'images/i002.jpg', 'page_003': 'p003.xhtml', 'image_003': 'images/i003.jpg', 'page_004': 'p004.xhtml', 'image_004': 'images/i004.jpg', 'page_005': 'p005.xhtml', 'image_005': 'images/i005.jpg', 'page_006': 'p006.xhtml', 'image_006': 'images/i006.jpg', 'page_007': 'p007.xhtml', 'image_007': 'images/i007.jpg', 'page_008': 'p008.xhtml', 'image_008': 'images/i008.jpg', 'page_009': 'p009.xhtml', 'image_009': 'images/i009.jpg', 'page_010': 'p010.xhtml', 'image_010': 'images/i010.jpg', 'page_011': 'p011.xhtml', 'image_011': 'images/i011.jpg', 'page_012': 'p012.xhtml', 'image_012': 'images/i012.jpg', 'page_013': 'p013.xhtml', 'image_013': 'images/i013.jpg', 'page_014': 'p014.xhtml', 'image_014': 'images/i014.jpg', 'page_015': 'p015.xhtml', 'image_015': 'images/i015.jpg', 'page_016': 'p016.xhtml', 'image_016': 'images/i016.jpg', 'page_017': 'p017.xhtml', 'image_017': 'images/i017.jpg', 'page_018': 'p018.xhtml', 'image_018': 'images/i018.jpg'}
		expectedSpine = ['cover', 'page_002', 'page_003', 'page_004', 'page_005', 'page_006', 'page_007', 'page_008', 'page_009', 'page_010', 'page_011', 'page_012', 'page_013', 'page_014', 'page_015', 'page_016', 'page_017', 'page_018']
		self.assertEqual(manifest, expectedManifest, "Manifest is not what was expected")
		self.assertEqual(spine, expectedSpine, "Spine is not what was expected")
	
	# getImageFilenames tests
	
	# basic sanity test
	def test_getImageFilenames_sanity(self):
		docDir = os.path.join(os.path.dirname(__file__), "test-resources", "extracted-epub", "OEBPS")
		os.chdir(docDir)
		opfFile = "content.opf"
		manifest, spine = epubToCbz.getManifestAndSpine(opfFile)
		imgs = epubToCbz.getImageFilenames(manifest, spine)
		expectedImgs = ['images/cover.jpg', 'images/i002.jpg', 'images/i003.jpg', 'images/i004.jpg', 'images/i005.jpg', 'images/i006.jpg', 'images/i007.jpg', 'images/i008.jpg', 'images/i009.jpg', 'images/i010.jpg', 'images/i011.jpg', 'images/i012.jpg', 'images/i013.jpg', 'images/i014.jpg', 'images/i015.jpg', 'images/i016.jpg', 'images/i017.jpg', 'images/i018.jpg']
		self.assertEqual(imgs, expectedImgs, "Image list is not what was expected.")
	
	# not going to bother testing buildCbzFile, I already know it works and I'm not sure how to compare the content of 2 files in an assertion
	
	# getHtmlAttributeValue tests
	# no negative tests, since I didn't put in any validation for this function
	
	# double quotes
	def test_getHtmlAttributeValue_doubleQuotes(self):
		tag = '<img src="images/cover.jpg" alt="image"/>'
		attr = 'src'
		self.assertEqual(epubToCbz.getHtmlAttributeValue(tag, attr), 'images/cover.jpg', 'Return value should be "images/cover.jpg".')
	
	# single quotes
	def test_getHtmlAttributeValue_singleQuotes(self):
		tag = "<img src='images/cover.jpg' alt='image'/>"
		attr = "src"
		self.assertEqual(epubToCbz.getHtmlAttributeValue(tag, attr), "images/cover.jpg", 'Return value should be "images/cover.jpg".')
	
	# findOpfEnterDoc tests
	
	# no document directory
	def test_findOpfEnterDoc_noDocDir(self):
		bookDir = os.path.join(os.path.dirname(__file__), "test-resources")
		tempPath = "temp"
		os.chdir(bookDir)
		if not os.path.exists(tempPath):
			os.mkdir(tempPath)
		os.chdir(os.path.join(os.path.dirname(__file__), "test-resources", "cbz"))
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		docDir, opfFile = epubToCbz.findOpfEnterDoc(bookDir, tempPath)
		sys.stdout = sys.__stdout__
		self.assertFalse(docDir, "docDir should be False.")
		self.assertFalse(opfFile, "opfFile should be False.")
		self.assertEqual(capturedOutput.getvalue(), "Provided ePub has no document directory.\n", "Console output is incorrect for no document directory.")
		self.assertFalse(tempPath in os.listdir(), "test-resources should no longer contain the temp directory.")
	
	# no OPF file
	def test_findOpfEnterDoc_noOpfFile(self):
		bookDir = os.path.join(os.path.dirname(__file__), "test-resources")
		tempPath = "temp"
		os.chdir(bookDir)
		if not os.path.exists(tempPath):
			os.mkdir(tempPath)
		capturedOutput = io.StringIO()
		sys.stdout = capturedOutput
		docDir, opfFile = epubToCbz.findOpfEnterDoc(bookDir, tempPath)
		sys.stdout = sys.__stdout__
		self.assertFalse(docDir, "docDir should be False.")
		self.assertFalse(opfFile, "opfFile should be False.")
		self.assertEqual(capturedOutput.getvalue(), "Provided ePub has no OPF file.\n", "Console output is incorrect for no document directory.")
		self.assertFalse(tempPath in os.listdir(), "test-resources should no longer contain the temp directory.")
	
	# OPF file in top-level directory
	def test_findOpfEnterDoc_opfFileInTop(self):
		bookDir = os.path.join(os.path.dirname(__file__), "test-resources")
		tempPath = "temp"
		os.chdir(bookDir)
		os.chdir(os.path.join(os.path.dirname(__file__), "test-resources", "extracted-epub", "OEBPS"))
		docDir, opfFile = epubToCbz.findOpfEnterDoc(bookDir, tempPath)
		self.assertEqual(docDir, "", "docDir should be an empty string.")
		self.assertEqual(opfFile, "content.opf", "opfFile should be content.opf.")
	
	# OPF file one level down from top-level directory
	def test_findOpfEnterDoc_opfFileOneDown(self):
		bookDir = os.path.join(os.path.dirname(__file__), "test-resources")
		tempPath = "temp"
		os.chdir(bookDir)
		os.chdir(os.path.join(os.path.dirname(__file__), "test-resources", "extracted-epub"))
		docDir, opfFile = epubToCbz.findOpfEnterDoc(bookDir, tempPath)
		self.assertEqual(docDir, "OEBPS", "docDir should be OEBPS.")
		self.assertEqual(opfFile, "content.opf", "opfFile should be content.opf.")

if __name__ == "__main__":
	unittest.main()
