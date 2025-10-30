import os
import glob
import time
from internetarchive import upload

identifier = "QuranTranslationAmaniMoulaviMalayalam"
source_directory = "quran_audio"

def upload_to_archive():
    metadata = {
        'collection': 'opensource_audio',
        'mediatype': 'audio',
        'title': 'Quran Malayalam Only Audio',
        'subject': ['Quran', 'Islam', 'Malayalam', 'Recitation', 'Audio'],
    }

    print(f"\nStarting bulk upload to https://archive.org/details/{identifier}")
    start_time = time.time()
    
    try:
        upload(
            identifier, 
            "quran_audio/2/1.mp3",
            verbose=True,
            checksum=True,  # Skip already uploaded files
            verify=True,    # Ensure data integrity
            delete=False,    # Safe cleanup
            retries=5       # Make it robust
        )
        
        print("\n" + "="*50)
        print(f"✓ UPLOAD PROCESS COMPLETED SUCCESSFULLY!")
        print(f"  Total time: {(time.time() - start_time)/60:.1f} minutes")
        print("="*50)

    except Exception as e:
        print(f"\n✗ AN ERROR OCCURRED: {e}")

upload_to_archive()