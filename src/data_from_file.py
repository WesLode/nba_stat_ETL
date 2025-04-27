import requests
import re # For extracting the file ID using regex

def download_gdrive_file(share_link, output_filename):
    """
    Downloads a publicly accessible file from Google Drive using its share link.

    Args:
        share_link (str): The Google Drive sharing link
                          (e.g., 'https://drive.google.com/file/d/FILE_ID/view?usp=sharing').
        output_filename (str): The path and name to save the downloaded file as.

    Returns:
        bool: True if download was successful, False otherwise.
    """
    # --- 1. Extract File ID ---
    # Use regex to find the file ID between /d/ and /view or the end of the string
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', share_link)
    if not match:
        print(f"Error: Could not extract file ID from link: {share_link}")
        return False
    file_id = match.group(1)
    print(f"Extracted File ID: {file_id}")

    # --- 2. Construct Direct Download URL ---
    direct_download_url = f'https://drive.google.com/uc?export=download&id={file_id}'
    print(f"Constructed download URL: {direct_download_url}")

    # --- 3. Download using requests ---
    try:
        print(f"Attempting to download to: {output_filename}...")
        # Use a session object for potential cookie handling (good practice)
        session = requests.Session()
        # Make the request, allow redirects as Drive might redirect
        response = session.get(direct_download_url, stream=True, timeout=30) # stream=True is important for large files
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # Check if Google requires confirmation for large files
        # Sometimes Google Drive shows a warning page for large files.
        # We might need to grab a confirmation token and make a second request.
        # This part can be complex and might need adjustments based on Google's changes.
        # A simpler check might be based on content type or initial response size.
        # For this example, we'll assume direct download works for moderately sized files.
        # A more robust solution might check response headers or content.

        # --- 4. Save the file ---
        with open(output_filename, 'wb') as f:
            # Download in chunks to handle large files efficiently
            chunk_size = 8192 # 8 KB
            downloaded_size = 0
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    # Optional: print progress
                    # print(f"Downloaded {downloaded_size / (1024*1024):.2f} MB", end='\r')

        print(f"\nSuccessfully downloaded file to {output_filename}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"Error during download: {e}")
        # Check specifically for 403 Forbidden, often indicating permission issues
        if response is not None and response.status_code == 403:
             print("Received 403 Forbidden. Check if the file is shared correctly ('Anyone with the link').")
        return False
    except IOError as e:
        print(f"Error writing file {output_filename}: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

# --- Example Usage ---
if __name__ == "__main__":
    # Replace with your actual share link and desired output path
    # IMPORTANT: The file MUST be shared with "Anyone with the link" can view
    example_share_link = "https://drive.google.com/file/d/1DO_KlpyGl0_XaeKmoYHRq0jbnVXlk0s/view?usp=sharing" # Example: A small public PDF
    output_path = "./downloaded_google_doc.pdf"

    if download_gdrive_file(example_share_link, output_path):
        print("Download process completed successfully.")
    else:
        print("Download process failed.")

    # Example with a file ID known to require confirmation (might not work reliably without handling confirmation step)
    # large_file_link = "https://drive.google.com/file/d/LARGE_FILE_ID/view?usp=sharing"
    # large_output_path = "./large_downloaded_file.zip"
    # download_gdrive_file(large_file_link, large_output_path)
