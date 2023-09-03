import os
import shutil
import tempfile
import unittest
from file_organizer import identify_file_type, create_folders, move_files, handle_duplicate_file_names


class TestFileOrganizer(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_identify_file_type(self):
        self.assertEqual(identify_file_type('test.jpg'), 'image')
        self.assertEqual(identify_file_type('test.pdf'), 'application')
        self.assertEqual(identify_file_type('test.mp3'), 'audio')
        self.assertEqual(identify_file_type('unknown.xyz'), 'unknown')

    def test_create_folders(self):
        file_types = {'image', 'audio', 'application'}
        create_folders(file_types, self.test_dir)
        for file_type in file_types:
            self.assertTrue(os.path.exists(os.path.join(self.test_dir, file_type)))

    def test_move_files(self):
        file_types = {'image', 'audio', 'application'}
        create_folders(file_types, self.test_dir)
        test_files = ['test.jpg', 'test.pdf', 'test.mp3']
        for file in test_files:
            open(os.path.join(self.test_dir, file), 'w').close()
        move_files([os.path.join(self.test_dir, f) for f in test_files], file_types, self.test_dir)
        for file_type, file in zip(file_types, test_files):
            self.assertTrue(os.path.exists(os.path.join(self.test_dir, file_type, file)))

    def test_handle_duplicate_file_names(self):
        file_name = 'test.jpg'
        destination = os.path.join(self.test_dir, 'image')
        os.makedirs(destination)
        open(os.path.join(destination, file_name), 'w').close()
        new_file_name = handle_duplicate_file_names(file_name, destination)
        self.assertEqual(new_file_name, 'test_1.jpg')


if __name__ == '__main__':
    unittest.main()