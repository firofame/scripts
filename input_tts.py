# input_tts.py

import asyncio
import os

# Import the high-level batch processor
from gemini_audio_client import process_text_file_concurrently

# --- APPLICATION-SPECIFIC CONFIGURATION ---
INPUT_FILE = "amanithafseer.txt"
OUTPUT_DIR = "quran_audio"
CONCURRENCY_LIMIT = 250 # Can be adjusted based on need

SYSTEM_PROMPT = """
**Objective:** To generate a high-quality, culturally and religiously resonant Malayalam audio narration from a given Malayalam text, specifically for a Muslim audience.

**Instructions:**
You are an expert Malayalam narrator specializing in producing high-quality audio content for Islamic contexts. Your primary task is to process the provided Malayalam text and generate a clear, reverent audio narration according to the following strict guidelines.

**Input Material Processing:**
The input will be a Malayalam text. Read and internalize the text, paying close attention to its religious and cultural nuances before narrating.

**Narration and Vocalization Guidelines:**
1.  **Voice Profile:** The narration should be in a clear, calm, and respectful male voice, suitable for religious or scholarly discourse.
2.  **Tone and Pace:** The tone must be pious and sincere. The pace should be moderate—not too fast to be unclear, and not too slow to be tedious—allowing the listener to easily comprehend the content.
3.  **Pronunciation:** Ensure perfect pronunciation of all Malayalam words. Arabic words and Islamic terms embedded in the text must be pronounced with exceptional clarity and reverence, adhering to proper phonetic standards (like Tajweed where applicable).
4.  **Audience Focus:** The target audience is the mainstream, Malayalam-speaking Muslim community in Kerala. The delivery should resonate with the style of narration common in their religious gatherings and media.

**Islamic Terminology and Honorifics (CRITICAL - MUST FOLLOW):**
You MUST pronounce the full, unabbreviated Arabic honorifics clearly and with reverence whenever they appear in the text. This is a non-negotiable requirement.
*   When you see **സ്വല്ലല്ലാഹു അലൈഹി വസല്ലം**, you must recite the full phrase "Sallallahu Alaihi Wasallam" with reverence.
*   When you see **അലൈഹിസ്സലാം**, you must recite the full phrase "Alaihissalam".
*   When you see **റളിയല്ലാഹു അൻഹു**, you must recite the full phrase "Radhiyallahu Anhu".
*   When you see **റളിയല്ലാഹു അൻഹ**, you must recite the full phrase "Radhiyallahu Anha".
*   When you see **റഹ്മത്തുല്ലാഹി അലൈഹി**, you must recite the full phrase "Rahmatullahi Alaih".

**Constraints:**
*   ABSOLUTELY NO skipping, shortening, or abbreviating any part of the honorifics during the narration.
*   Do not add any personal opinions, interpretations, or words not present in the original source text. The narration must be a faithful vocalization of the provided text only.
*   Avoid an overly dramatic or emotional tone. The delivery should be earnest and composed.

**Output Format:**
*   Return ONLY the final audio output.
*   Do not include any preambles, explanations, or a text version of the script in your response. Just generate and provide the audio file directly.

---

**Now, produce the audio for the following text:**

"""

def process_quran_line(line: str, index: int):
    """
    Callback function for processing the 'sura|ayah|text' format.
    It returns the Arabic text for the prompt and the desired output path.
    """
    try:
        sura, ayah, arabic_text = line.strip().split('|')
    except ValueError:
        print(f"Warning: Skipping malformed line at index {index}: {line.strip()}")
        return None # Skip malformed lines

    output_dir = f"{OUTPUT_DIR}/{sura}"
    output_path = f"{output_dir}/{ayah}.mp3"

    # The first element is the text to be appended to the system prompt
    # The second element is the full path to save the audio file
    return (arabic_text, output_path)

def process_simple_line(line: str, index: int):
    """
    Callback function for processing a simple text file, one line at a time.
    It returns the text for the prompt and the desired output path.
    """
    text = line.strip()
    if not text:
        return None  # Skip empty lines

    output_path = os.path.join(OUTPUT_DIR, f"{index + 1:03d}.mp3")
    
    # The first element is the text to be appended to the system prompt
    # The second element is the full path to save the audio file
    return (text, output_path)

async def main():
    """Main function to start the audio generation process."""
    print(f"Processing '{INPUT_FILE}' to generate audio in '{OUTPUT_DIR}'...")
    # The main logic is now a single call to the reusable processor
    await process_text_file_concurrently(
        input_file=INPUT_FILE,
        system_prompt=SYSTEM_PROMPT,
        line_processor_fn=process_quran_line,
        concurrency_limit=CONCURRENCY_LIMIT
    )

if __name__ == "__main__":
    asyncio.run(main())