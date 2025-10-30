import os
import subprocess

# --- Configuration ---
INPUT_FOLDER = "output_audio"
OUTPUT_FILENAME = "concatenated_ffmpeg.wav"
TEMP_LIST_FILENAME = "ffmpeg_file_list.txt"
# ---------------------

def concatenate_audio_with_ffmpeg():
    """
    Finds all .wav files in the input folder, creates a list for ffmpeg,
    and uses the 'concat' demuxer to losslessly join them.
    """
    # Check if the input folder exists
    if not os.path.isdir(INPUT_FOLDER):
        print(f"Error: Input folder '{INPUT_FOLDER}' not found.")
        return

    # Get a sorted list of absolute paths to the .wav files
    try:
        files_to_concat = sorted(
            [f for f in os.listdir(INPUT_FOLDER) if f.endswith('.wav')]
        )
    except FileNotFoundError:
        print(f"Error: Could not read from folder '{INPUT_FOLDER}'.")
        return

    if not files_to_concat:
        print(f"No .wav files found in '{INPUT_FOLDER}'.")
        return

    print(f"Found {len(files_to_concat)} files to concatenate:")
    for f in files_to_concat:
        print(f"  - {f}")

    # Create the temporary list file for ffmpeg's concat demuxer
    print(f"\nGenerating temporary file list: '{TEMP_LIST_FILENAME}'...")
    with open(TEMP_LIST_FILENAME, 'w') as f:
        for wav_file in files_to_concat:
            # Important: Use single quotes for ffmpeg if paths have spaces
            # The format is: file '/path/to/your/file.wav'
            file_path = os.path.join(INPUT_FOLDER, wav_file)
            f.write(f"file '{os.path.abspath(file_path)}'\n")

    # Construct the ffmpeg command
    # -f concat: Use the concat demuxer
    # -safe 0: Necessary for using absolute or relative paths in the list file
    # -i ...:   Specifies the input file list
    # -c copy:  Copies the stream without re-encoding (fast and lossless)
    command = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', TEMP_LIST_FILENAME,
        '-c', 'copy',
        OUTPUT_FILENAME
    ]
    
    # Overwrite the output file if it already exists
    command.append('-y')

    print("\nRunning ffmpeg command:")
    print(" ".join(command))

    # Execute the command
    try:
        process = subprocess.run(
            command,
            check=True,          # Raise an exception for non-zero exit codes
            capture_output=True, # Capture stdout and stderr
            text=True            # Decode stdout/stderr as text
        )
        print("\n--- ffmpeg output ---")
        print(process.stderr) # ffmpeg prints progress to stderr
        print("---------------------\n")
        print(f"✅ Success! Audio concatenated to '{OUTPUT_FILENAME}'")

    except FileNotFoundError:
        print("\n❌ Error: 'ffmpeg' command not found.")
        print("Please make sure FFmpeg is installed and in your system's PATH.")
    except subprocess.CalledProcessError as e:
        print("\n❌ Error during ffmpeg execution.")
        print("--- ffmpeg error output ---")
        print(e.stderr)
        print("---------------------------")
    finally:
        # Clean up the temporary file list
        if os.path.exists(TEMP_LIST_FILENAME):
            os.remove(TEMP_LIST_FILENAME)
            print(f"Cleaned up temporary file: '{TEMP_LIST_FILENAME}'")

if __name__ == "__main__":
    concatenate_audio_with_ffmpeg()