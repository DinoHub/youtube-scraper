import os
import shutil


def delete_empty_subfolders(folder1, folder1_wav_path, folder2, folder2_wav_path):
    """
    This function deletes empty subfolders from all given folders.

    Args:
        folder1 (str): Path to the first folder.
        folder1_wav_path (str): Path to the first wav folder.
        folder2 (str): Path to the second folder.
        folder2_wav_path (str): Path to the second wav folder

    Returns:
        list: A list of names of subfolders that were deleted as the subfolder was empty.
    """
    # Check for empty subfolders in each of the folders
    empty_subfolders1 = check_empty_subfolders(folder1)
    empty_wav_subfolders1 = check_empty_subfolders(folder1_wav_path)
    empty_subfolders2 = check_empty_subfolders(folder2)
    empty_wav_subfolders2 = check_empty_subfolders(folder2_wav_path)

    # Include all empty subfolder names
    all_empty_subfolders = [
        *empty_subfolders1,
        *empty_wav_subfolders1,
        *empty_subfolders2,
        *empty_wav_subfolders2,
    ]

    # Remove duplicates
    all_empty_subfolders = list(set(all_empty_subfolders))

    # Delete empty subfolders from all folders
    for subfolder in all_empty_subfolders:
        shutil.rmtree(os.path.join(folder1, subfolder))
        shutil.rmtree(os.path.join(folder1_wav_path, subfolder))
        shutil.rmtree(os.path.join(folder2, subfolder))
        shutil.rmtree(os.path.join(folder2_wav_path, subfolder))

    return all_empty_subfolders


def check_empty_subfolders(root_dir):
    """
    This function checks if there are empty subfolders in the given folder.

    Args:
        root_dir (str): Path to the root directory.

    Returns:
        list: A list of names of subfolders that are empty.
    """
    empty_subfolders = []

    for dirpath, dirnames, _ in os.walk(root_dir):
        if not dirnames and not os.listdir(dirpath):
            empty_subfolders.append(os.path.basename(os.path.normpath(dirpath)))

    return empty_subfolders


def compare_folder_text_files(
    folder1, folder1_wav_path, folder2, folder2_wav_path, dry_run=True
):
    """
    This function compares the number of rows in text files for subfolders with the same name between two folders.

    Args:
        folder1 (str): Path to the first folder.
        folder1_wav_path (str): Path to the first wav folder.
        folder2 (str): Path to the second folder.
        folder2_wav_path (str): Path to the second wav folder

    Returns:
        list: A list of subfolder names where the text files have different numbers of rows, or an empty list if all comparisons match.
    """
    mismatches = []
    for subfolder in os.listdir(folder1):
        if os.path.isdir(os.path.join(folder1, subfolder)):
            # Check if subfolder exists in both folders
            if os.path.isdir(os.path.join(folder2, subfolder)):
                subfolder1_path = os.path.join(folder1, subfolder)
                file1_path = os.path.join(
                    subfolder1_path, os.listdir(subfolder1_path)[0]
                )
                subfolder2_path = os.path.join(folder2, subfolder)
                file2_path = os.path.join(
                    subfolder2_path, os.listdir(subfolder1_path)[0]
                )

                # Check if both text files exist
                if os.path.isfile(file1_path) and os.path.isfile(file2_path):
                    try:
                        # Count lines in each file
                        with open(file1_path, "r") as f1, open(file2_path, "r") as f2:
                            num_rows1 = len(f1.readlines())
                            print(num_rows1)
                            num_rows2 = len(f2.readlines())
                            print(num_rows2)
                    except PermissionError:
                        # Handle cases where there might not be permission to read the files
                        print(f"Error: Could not access files in subfolder {subfolder}")
                        continue

                    if num_rows1 != num_rows2:
                        mismatches.append(subfolder)
                        if not dry_run:
                            # Delete the subfolder if not in dry_run mode
                            shutil.rmtree(os.path.join(folder1, subfolder))
                            shutil.rmtree(os.path.join(folder1_wav_path, subfolder))
                            shutil.rmtree(os.path.join(folder2, subfolder))
                            shutil.rmtree(os.path.join(folder2_wav_path, subfolder))
                            print(f"Deleted subfolder {subfolder} due to mismatch.")
                    else:
                        if not dry_run:
                            # Move files to yt-data directory
                            move_file(file1_path, "../yt-data/en/txt")
                            subfolder1_wav_path = os.path.join(
                                folder1_wav_path, subfolder
                            )
                            move_file(
                                os.path.join(
                                    subfolder1_wav_path,
                                    os.listdir(subfolder1_wav_path)[0],
                                ),
                                "../yt-data/en/wav16k",
                            )

                            move_file(file2_path, "../yt-data/vi/txt")
                            subfolder2_wav_path = os.path.join(
                                folder2_wav_path, subfolder
                            )
                            move_file(
                                os.path.join(
                                    subfolder2_wav_path,
                                    os.listdir(subfolder2_wav_path)[0],
                                ),
                                "../yt-data/vi/wav16k",
                            )

    return mismatches


def move_file(source_file, destination_folder):
    """
    Moves a file from the source location to the destination folder.

    Args:
        source_file (str): Path to the file including the subfolder.
        destination_folder (str): Path to the destination folder.
    """
    try:
        shutil.move(source_file, destination_folder)
        print(f"File '{source_file}' moved successfully to '{destination_folder}'.")
    except FileNotFoundError:
        print(f"Error: File '{source_file}' not found.")
    except shutil.Error as e:
        print(f"Error moving file: {e}")


# Example usage
folder1_path = "video/en/txt"
folder1_wav_path = "video/en/wav16k"
folder2_path = "video/vi/txt"
folder2_wav_path = "video/vi/wav16k"

deleted_subfolders = delete_empty_subfolders(
    folder1_path, folder1_wav_path, folder2_path, folder2_wav_path
)
if deleted_subfolders:
    print(f"Deleted subfolders: {', '.join(deleted_subfolders)}")
else:
    print("There are no empty subfolders")

mismatched_subfolders = compare_folder_text_files(
    folder1_path, folder1_wav_path, folder2_path, folder2_wav_path, dry_run=False
)

if mismatched_subfolders:
    print(
        f"Subfolders with mismatched text file row counts: {', '.join(mismatched_subfolders)}"
    )
else:
    print(
        "All text files in subfolders with the same name have the same number of rows."
    )
