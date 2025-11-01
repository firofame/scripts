import os
import glob
import time
from internetarchive import upload

identifier = "BayyinahTVNoumanAliKhanConciseCommentary"
source_directory = "Quran_Audio"

def upload_to_archive():
    metadata = {
        'collection': 'opensource_audio',
        'mediatype': 'audio',
        'creator': 'Nouman Ali Khan',
        'source': 'Bayyinah TV',
        'title': 'Concise Commentary - Nouman Ali Khan (Bayyinah TV)',
        'description': 'Understand the meanings of ayaat beyond the translation. Insights on words, phrases and context - for every ayah.',
        'subject': ['Quran', 'Islam', 'Tafsir', 'Commentary', 'Nouman Ali Khan', 'Bayyinah TV', 'Audio'],
    }

    print(f"\nStarting bulk upload to https://archive.org/details/{identifier}")
    start_time = time.time()
    
    try:
        upload(
            identifier, 
            source_directory,
            metadata=metadata,
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

if __name__ == "__main__":
    upload_to_archive()