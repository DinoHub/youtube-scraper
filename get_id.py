import re


def overwrite_video_ids(file_path):
    try:
        # Open the file in read mode
        with open(file_path, "r+") as file:
            lines = file.readlines()
            file.seek(0)  # Reset file pointer to the beginning

            for line in lines:
                # Use regular expression to extract video ID from the URL
                match = re.search(r"(?<=v=)[a-zA-Z0-9_-]+", line)
                if match:
                    video_id = match.group(0)
                    # Overwrite the line with just the video ID
                    file.write(video_id + "\n")
                else:
                    # If no video ID found, keep the line as it is
                    file.write(line)

            file.truncate()  # Remove any extra content after overwriting

    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage:
file_path = "to_scrape_ids.txt"
overwrite_video_ids(file_path)
