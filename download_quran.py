import requests
import os
import concurrent.futures
from tqdm import tqdm

# --- Configuration ---
MAX_WORKERS = 8
OUTPUT_DIR = "Quran_Audio"
CHUNK_SIZE = 8192  # Download in chunks to save memory

BASE_URL = "https://d36m9bni5rssex.cloudfront.net/ayah-by-ayah/"
QUERY_PARAMS = os.environ.get("QUERY_PARAMS")
AYAH_COUNTS = [0, 7, 286, 200, 176, 120, 165, 206, 75, 129, 109, 123, 111, 43, 52, 99, 128, 111, 110, 98, 135, 112, 78, 118, 64, 77, 227, 93, 88, 69, 60, 34, 30, 73, 54, 45, 83, 182, 88, 75, 85, 54, 53, 89, 59, 37, 35, 38, 29, 18, 45, 60, 49, 62, 55, 78, 96, 29, 22, 24, 13, 14, 11, 11, 18, 12, 12, 30, 52, 52, 44, 28, 28, 20, 56, 40, 31, 50, 40, 46, 42, 29, 19, 36, 25, 22, 17, 19, 26, 30, 20, 15, 21, 11, 8, 8, 19, 5, 8, 8, 11, 11, 8, 3, 9, 5, 4, 7, 3, 6, 3, 5, 4, 5, 6]


def download_ayah_once(task_info):
    """
    Downloads a file to a temporary .part location in a single attempt.
    Renames the file on success. Cleans up partial files on failure.
    """
    url = task_info['url']
    final_filepath = task_info['filepath']
    temp_filepath = final_filepath + ".part"
    filename = task_info['filename']

    try:
        response = requests.get(url, stream=True, timeout=30)
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        with open(temp_filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                f.write(chunk)
        
        # Verify the downloaded file is not empty before renaming
        if os.path.getsize(temp_filepath) > 0:
            os.rename(temp_filepath, final_filepath)
            return None  # Return None on success
        else:
            return f"Failed {filename} (Downloaded file is empty)"

    except requests.exceptions.RequestException as e:
        return f"Failed {filename} (Error: {e})"
    finally:
        # This block ensures the temporary file is removed after the try/except
        if os.path.exists(temp_filepath):
            try:
                os.remove(temp_filepath)
            except OSError:
                pass


def download_quran_audio():
    """Main function to scan for missing files and download them."""
    print("Scanning for missing audio files...")
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    tasks_to_run = []
    for surah_number in range(1, 115):
        surah_dir = os.path.join(OUTPUT_DIR, f"Surah_{surah_number:03d}")
        if not os.path.exists(surah_dir):
            os.makedirs(surah_dir)
            
        num_ayahs = AYAH_COUNTS[surah_number]
        for ayah_number in range(1, num_ayahs + 1):
            local_filename = f"{surah_number:03d}_{ayah_number:03d}.mp3"
            local_filepath = os.path.join(surah_dir, local_filename)
            
            if os.path.exists(local_filepath) and os.path.getsize(local_filepath) > 0:
                continue
                
            remote_filename = f"{surah_number:03d}{ayah_number:03d}.mp3"
            url = f"{BASE_URL}{remote_filename}{QUERY_PARAMS}"
            tasks_to_run.append({
                "url": url,
                "filepath": local_filepath,
                "filename": local_filename
            })

    if not tasks_to_run:
        print("✓ All Quran audio files are already downloaded.")
        return

    print(f"Found {len(tasks_to_run)} files to download. Starting...\n")

    failed_downloads = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks to the executor
        future_to_task = {executor.submit(download_ayah_once, task): task for task in tasks_to_run}
        
        # Process results as they complete with a progress bar
        with tqdm(total=len(tasks_to_run), desc="Downloading", unit="file") as pbar:
            for future in concurrent.futures.as_completed(future_to_task):
                error = future.result()
                
                if error:
                    failed_downloads.append(error)
                    tqdm.write(f"✗ {error}") # Print errors without disturbing the bar
                
                pbar.update(1)

    # Final summary report
    print(f"\n{'='*60}")
    print("Download process completed.")
    print(f"Successfully downloaded: {len(tasks_to_run) - len(failed_downloads)}/{len(tasks_to_run)}")
    
    if failed_downloads:
        print(f"\n⚠ Failed downloads ({len(failed_downloads)}):")
        for error in failed_downloads:
            print(f"  - {error}")
    else:
        print("✓ All files downloaded successfully!")
    print(f"{'='*60}")


if __name__ == "__main__":
    download_quran_audio()