import os
import shutil
import argparse
import mimetypes


def identify_file_type(file):
    # Identify the file type of a given file
    mime_type, _ = mimetypes.guess_type(file)
    if mime_type:
        return mime_type.split('/')[0]
    return 'unknown'


def create_folders(file_types, target_dir):
    # Create folders based on file types
    for file_type in file_types:
        folder_path = os.path.join(target_dir, file_type)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)


def move_files(files, file_types, target_dir):
    # Move files into corresponding folders
    for file in files:
        file_type = identify_file_type(file)
        if file_type in file_types:
            destination = os.path.join(target_dir, file_type)
            file_name = handle_duplicate_file_names(file, destination)
            shutil.move(file, os.path.join(destination, file_name))


def handle_command_line_options():
    # Parse and handle command-line options
    parser = argparse.ArgumentParser(description='File Organizer')
    parser.add_argument('directory', help='Directory to organize')
    parser.add_argument('--exclude', nargs='*', help='Exclude specific file types')
    args = parser.parse_args()
    return args


def handle_duplicate_file_names(file, destination):
    # Append a number to duplicate file names
    file_name = os.path.basename(file)
    file_base, file_ext = os.path.splitext(file_name)
    counter = 1
    while os.path.exists(os.path.join(destination, file_name)):
        file_name = f'{file_base}_{counter}{file_ext}'
        counter += 1
    return file_name


if __name__ == '__main__':
    args = handle_command_line_options()
    target_dir = args.directory
    exclude_file_types = set(args.exclude) if args.exclude else set()

    all_files = [os.path.join(target_dir, f) for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))]
    file_types = {identify_file_type(f) for f in all_files} - exclude_file_types

    create_folders(file_types, target_dir)
    move_files(all_files, file_types, target_dir)