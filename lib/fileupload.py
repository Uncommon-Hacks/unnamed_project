import os
import random
import shutil
from urllib.parse import urljoin
from urllib.request import pathname2url

class LocalImageManager:
    """
    Manages image uploads and retrieval from a local directory, simulating S3 behavior.
    """

    def __init__(self, base_directory='local_images', url_prefix='http://localhost:8000/'):
        """
        Initializes the LocalImageManager.

        Args:
            base_directory (str): The base directory for storing images.
            url_prefix (str): The URL prefix for generated image URLs.
        """
        self.base_directory = base_directory
        self.url_prefix = url_prefix
        os.makedirs(self.base_directory, exist_ok=True)

    def upload_file(self, file_path, object_name=None):
        """
        Uploads a file to the local directory.

        Args:
            file_path (str): The local path to the file to upload.
            object_name (str, optional): The object name (path) within the local directory. If None, the basename of file_path is used.

        Returns:
            bool: True if upload was successful, False otherwise.
        """
        try:
            object_name = object_name or os.path.basename(file_path)
            destination_path = os.path.join(self.base_directory, object_name)
            os.makedirs(os.path.dirname(destination_path), exist_ok=True) #create subdirectories if needed.
            shutil.copy2(file_path, destination_path)  # copy2 preserves metadata
            print(f"Uploaded {file_path} to {destination_path}")
            return True
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
            return False
        except Exception as e:
            print(f"Error uploading file: {e}")
            return False

    def get_random_files(self, user_name, num_files=9):
        """
        Retrieves a random set of files from the local directory, including one file associated with the given user.

        Args:
            user_name (str): The username used to filter and include one of the user's files in the result.
            num_files (int, optional): The number of random files to retrieve. Defaults to 9.

        Returns:
            list[str] or None: A list of local file URLs, or None if an error occurs or not enough files are found.
        """
        try:
            all_files = []
            for root, _, files in os.walk(self.base_directory):
                for file in files:
                    all_files.append(os.path.join(root, file))

            user_files = [f for f in all_files if user_name in f]

            if not user_files:
                print(f"Warning: No files found for user '{user_name}'.")
                return None

            selected_user_file = random.choice(user_files)
            other_files = [f for f in all_files if f != selected_user_file and user_name not in f]

            if len(other_files) < num_files - 1:
                print("Warning: Not enough other files to fulfill the request.")
                return None

            selected_files = [selected_user_file] + random.sample(other_files, num_files - 1)
            random.shuffle(selected_files)

            local_urls = []
            for file_path in selected_files:
                relative_path = os.path.relpath(file_path, self.base_directory)
                local_url = urljoin(self.url_prefix, pathname2url(relative_path)) #pathname2url creates a valid url.
                local_urls.append(local_url)

            return local_urls

        except Exception as e:
            print(f"Error retrieving files: {e}")
            return None

# Example Usage:


if __name__ == '__main__':
    
    image_manager = LocalImageManager()  # Uses default base directory and URL prefix

    # Uploading a file
    local_file_path = 'path/to/your/image.jpg' #replace with your image path
    object_name = 'user1/my_image.jpg'
    upload_success = image_manager.upload_file(local_file_path, object_name)

    if upload_success:
        print("Upload successful!")
    else:
        print("Upload failed.")

    # Getting random files for a user
    user_name = 'user1'
    random_urls = image_manager.get_random_files(user_name)

    if random_urls:
        print("\nRandom Image URLs:")
        for url in random_urls:
            print(url)
    else:
        print("\nFailed to retrieve random image URLs.")