import os
import glob
import time
from internetarchive import upload, delete

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
    try:
        upload(identifier, source_directory, metadata=metadata, verbose=True)
        # delete(identifier, verbose=True)
    except Exception as e:
        print(f"\n✗ AN ERROR OCCURRED: {e}")

if __name__ == "__main__":
    upload_to_archive()