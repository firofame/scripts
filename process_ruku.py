import json
import csv

def create_ruku_file(ruku_json_path, verses_csv_path, output_txt_path):
    """
    Reads Ruku data and verse translations to generate a text file
    organized by a continuous, global Ruku count. This version does not
    include the "chapter:verse" prefix on each line.

    Args:
        ruku_json_path (str): The file path for the Ruku.json file.
        verses_csv_path (str): The file path for the amanithafseer.csv file.
        output_txt_path (str): The desired file path for the output text file.
    """
    # Step 1: Load Ruku data
    try:
        with open(ruku_json_path, 'r', encoding='utf-8') as f:
            all_rukus = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{ruku_json_path}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{ruku_json_path}'.")
        return

    # Step 2: Load verse translations
    verses = {}
    try:
        with open(verses_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if len(row) >= 3:
                    chapter, verse, text = int(row[0]), int(row[1]), row[2]
                    if chapter not in verses:
                        verses[chapter] = {}
                    verses[chapter][verse] = text
    except FileNotFoundError:
        print(f"Error: The file '{verses_csv_path}' was not found.")
        return

    # Step 3: Process data with the correct logic
    output_lines = []
    global_ruku_counter = 1

    for i, ruku_info in enumerate(all_rukus):
        if not ruku_info:
            continue

        chapter_num = ruku_info[0]
        start_verse = ruku_info[1]

        # --- Create the Ruku Title (this remains the same) ---
        title = f"--- Ruku {global_ruku_counter} (Chapter {chapter_num}, Verse {start_verse}) ---"
        output_lines.append(title)

        # --- Determine the end verse for this Ruku ---
        end_verse = 0
        is_last_ruku_in_file = (i == len(all_rukus) - 1)

        if is_last_ruku_in_file:
            end_verse = max(verses.get(chapter_num, {0: 0}).keys())
        else:
            next_ruku_info = all_rukus[i + 1]
            if next_ruku_info and next_ruku_info[0] == chapter_num:
                end_verse = next_ruku_info[1] - 1
            else:
                end_verse = max(verses.get(chapter_num, {0: 0}).keys())

        # --- Add all verses belonging to this Ruku ---
        if chapter_num in verses and end_verse > 0:
            for verse_num in range(start_verse, end_verse + 1):
                verse_text = verses[chapter_num].get(verse_num, "Translation not found.")
                
                # --- MODIFIED LINE ---
                # Instead of adding the prefix, just add the translation text.
                output_lines.append(verse_text)
        
        output_lines.append("")
        global_ruku_counter += 1

    # Step 4: Write to output file
    try:
        with open(output_txt_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        total_rukus_processed = global_ruku_counter - 1
        print(f"Successfully created the file: '{output_txt_path}'")
        print(f"Processed {total_rukus_processed} Rukus in total.")
    except IOError as e:
        print(f"Error writing to file '{output_txt_path}': {e}")


if __name__ == "__main__":
    JSON_FILE = 'Ruku.json'
    CSV_FILE = 'amanithafseer.csv'
    OUTPUT_FILE = 'quran_by_ruku.txt'
    
    create_ruku_file(JSON_FILE, CSV_FILE, OUTPUT_FILE)