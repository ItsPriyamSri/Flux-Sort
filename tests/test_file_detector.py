"""Tests for file detector module."""

import unittest
from pathlib import Path
import tempfile
import os

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.file_detector import FileTypeDetector, FileCategory


class TestFileTypeDetector(unittest.TestCase):
    """Test cases for FileTypeDetector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = FileTypeDetector()
    
    def test_image_detection(self):
        """Test image file detection."""
        test_cases = [
            ('photo.jpg', FileCategory.IMAGES),
            ('image.png', FileCategory.IMAGES),
            ('animation.gif', FileCategory.IMAGES),
            ('vector.svg', FileCategory.IMAGES),
            ('raw_photo.cr2', FileCategory.IMAGES),
            ('modern_image.webp', FileCategory.IMAGES),
        ]
        
        for filename, expected_category in test_cases:
            with self.subTest(filename=filename):
                file_path = Path(filename)
                category = self.detector.detect_file_category(file_path)
                self.assertEqual(category, expected_category)
    
    def test_video_detection(self):
        """Test video file detection."""
        test_cases = [
            ('movie.mp4', FileCategory.VIDEOS),
            ('clip.avi', FileCategory.VIDEOS),
            ('presentation.mkv', FileCategory.VIDEOS),
            ('mobile_video.mov', FileCategory.VIDEOS),
            ('streaming.webm', FileCategory.VIDEOS),
        ]
        
        for filename, expected_category in test_cases:
            with self.subTest(filename=filename):
                file_path = Path(filename)
                category = self.detector.detect_file_category(file_path)
                self.assertEqual(category, expected_category)
    
    def test_document_detection(self):
        """Test document file detection."""
        test_cases = [
            ('document.pdf', FileCategory.DOCUMENTS),
            ('report.doc', FileCategory.DOCUMENTS),
            ('spreadsheet.xlsx', FileCategory.DOCUMENTS),
            ('notes.txt', FileCategory.DOCUMENTS),
            ('readme.md', FileCategory.DOCUMENTS),
            ('data.csv', FileCategory.DOCUMENTS),
        ]
        
        for filename, expected_category in test_cases:
            with self.subTest(filename=filename):
                file_path = Path(filename)
                category = self.detector.detect_file_category(file_path)
                self.assertEqual(category, expected_category)
    
    def test_audio_detection(self):
        """Test audio file detection."""
        test_cases = [
            ('song.mp3', FileCategory.AUDIO),
            ('podcast.wav', FileCategory.AUDIO),
            ('music.flac', FileCategory.AUDIO),
            ('audio.aac', FileCategory.AUDIO),
            ('sound.ogg', FileCategory.AUDIO),
        ]
        
        for filename, expected_category in test_cases:
            with self.subTest(filename=filename):
                file_path = Path(filename)
                category = self.detector.detect_file_category(file_path)
                self.assertEqual(category, expected_category)
    
    def test_archive_detection(self):
        """Test archive file detection."""
        test_cases = [
            ('archive.zip', FileCategory.ARCHIVES),
            ('backup.rar', FileCategory.ARCHIVES),
            ('compressed.7z', FileCategory.ARCHIVES),
            ('source.tar.gz', FileCategory.ARCHIVES),
            ('package.tar.bz2', FileCategory.ARCHIVES),
        ]
        
        for filename, expected_category in test_cases:
            with self.subTest(filename=filename):
                file_path = Path(filename)
                category = self.detector.detect_file_category(file_path)
                self.assertEqual(category, expected_category)
    
    def test_code_detection(self):
        """Test code file detection."""
        test_cases = [
            ('script.py', FileCategory.CODE),
            ('app.js', FileCategory.CODE),
            ('component.tsx', FileCategory.CODE),
            ('main.cpp', FileCategory.CODE),
            ('style.css', FileCategory.WEB),  # CSS is web category
            ('config.json', FileCategory.DATA),  # JSON is data category
        ]
        
        for filename, expected_category in test_cases:
            with self.subTest(filename=filename):
                file_path = Path(filename)
                category = self.detector.detect_file_category(file_path)
                self.assertEqual(category, expected_category)
    
    def test_unknown_extension(self):
        """Test unknown file extensions."""
        unknown_files = [
            'file.unknown',
            'document.xyz',
            'data.custom',
            'no_extension'
        ]
        
        for filename in unknown_files:
            with self.subTest(filename=filename):
                file_path = Path(filename)
                category = self.detector.detect_file_category(file_path)
                self.assertEqual(category, FileCategory.MISCELLANEOUS)
    
    def test_case_insensitive_detection(self):
        """Test that file detection is case insensitive."""
        test_cases = [
            ('Photo.JPG', FileCategory.IMAGES),
            ('Video.MP4', FileCategory.VIDEOS),
            ('Document.PDF', FileCategory.DOCUMENTS),
            ('MUSIC.MP3', FileCategory.AUDIO),
        ]
        
        for filename, expected_category in test_cases:
            with self.subTest(filename=filename):
                file_path = Path(filename)
                category = self.detector.detect_file_category(file_path)
                self.assertEqual(category, expected_category)
    
    def test_compound_extensions(self):
        """Test compound extensions like .tar.gz."""
        test_cases = [
            ('archive.tar.gz', FileCategory.ARCHIVES),
            ('backup.tar.bz2', FileCategory.ARCHIVES),
            ('package.tar.xz', FileCategory.ARCHIVES),
        ]
        
        for filename, expected_category in test_cases:
            with self.subTest(filename=filename):
                file_path = Path(filename)
                category = self.detector.detect_file_category(file_path)
                self.assertEqual(category, expected_category)
    
    def test_get_category_extensions(self):
        """Test getting extensions for a category."""
        image_extensions = self.detector.get_category_extensions(FileCategory.IMAGES)
        
        # Check that common image extensions are included
        expected_extensions = {'.jpg', '.png', '.gif', '.svg', '.webp'}
        self.assertTrue(expected_extensions.issubset(image_extensions))
    
    def test_get_all_categories(self):
        """Test getting all available categories."""
        categories = self.detector.get_all_categories()
        
        # Check that we have the expected number of categories
        self.assertGreater(len(categories), 10)
        
        # Check that specific categories are included
        expected_categories = {
            FileCategory.IMAGES,
            FileCategory.VIDEOS,
            FileCategory.DOCUMENTS,
            FileCategory.AUDIO,
            FileCategory.ARCHIVES
        }
        self.assertTrue(expected_categories.issubset(set(categories)))
    
    def test_hidden_file_detection(self):
        """Test hidden file detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create a hidden file (starts with dot)
            hidden_file = temp_path / '.hidden_file.txt'
            hidden_file.touch()
            
            # Create a normal file
            normal_file = temp_path / 'normal_file.txt'
            normal_file.touch()
            
            # Test detection
            self.assertTrue(self.detector.is_hidden_file(hidden_file))
            self.assertFalse(self.detector.is_hidden_file(normal_file))
    
    def test_get_file_info(self):
        """Test getting file information."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / 'test_image.jpg'
            
            # Create a test file with some content
            test_content = b'fake image data'
            with open(test_file, 'wb') as f:
                f.write(test_content)
            
            # Get file info
            file_info = self.detector.get_file_info(test_file)
            
            # Verify file info
            self.assertIsNotNone(file_info)
            self.assertEqual(file_info.name, 'test_image.jpg')
            self.assertEqual(file_info.extension, '.jpg')
            self.assertEqual(file_info.category, FileCategory.IMAGES)
            self.assertEqual(file_info.size, len(test_content))
            self.assertEqual(file_info.path, test_file)
    
    def test_get_file_info_nonexistent(self):
        """Test getting file info for non-existent file."""
        nonexistent_file = Path('/nonexistent/file.txt')
        file_info = self.detector.get_file_info(nonexistent_file)
        self.assertIsNone(file_info)


if __name__ == '__main__':
    unittest.main()