import os

# --- Configuration ---
input_filename = 'quran.txt'
number_of_parts = 240
output_folder = 'quran_parts'  # <<< NEW: The name of the folder for the output files
# ---------------------

# Check if the input file exists
if not os.path.exists(input_filename):
    print(f"Error: The file '{input_filename}' was not found.")
    exit()

# <<< NEW: Create the output directory if it doesn't already exist
# The exist_ok=True argument prevents an error if the folder is already there.
os.makedirs(output_folder, exist_ok=True)
print(f"Output will be saved in the '{output_folder}' directory.")

# 1. Get the total file size in bytes
total_size = os.path.getsize(input_filename)
# 2. Calculate the target size for each part
target_part_size = total_size / number_of_parts

print(f"Total file size: {total_size} bytes.")
print(f"Dividing into {number_of_parts} parts, aiming for ~{int(target_part_size)} bytes each.")
print("-" * 30)

try:
    # Open the source file for reading
    with open(input_filename, 'r', encoding='utf-8') as f_in:
        part_number = 1
        current_lines = []
        current_size = 0

        # Read the source file line by line
        for line in f_in:
            current_lines.append(line)
            current_size += len(line.encode('utf-8'))

            # If the current part size has reached the target, write the file
            if current_size >= target_part_size and part_number < number_of_parts:
                
                # <<< CHANGED: Construct the full path for the output file
                file_name = f"{part_number:02d}.txt"
                output_filepath = os.path.join(output_folder, file_name)
                
                with open(output_filepath, 'w', encoding='utf-8') as f_out:
                    f_out.writelines(current_lines)
                
                print(f"Created {output_filepath} with {len(current_lines)} lines ({current_size} bytes).")
                
                # Reset for the next part
                part_number += 1
                current_lines = []
                current_size = 0

        # After the loop, write any remaining lines to the final part
        if current_lines:
            # <<< CHANGED: Construct the full path for the final output file
            file_name = f"{part_number:02d}.txt"
            output_filepath = os.path.join(output_folder, file_name)

            with open(output_filepath, 'w', encoding='utf-8') as f_out:
                f_out.writelines(current_lines)
            print(f"Created {output_filepath} with {len(current_lines)} lines ({current_size} bytes).")

    print("\nDone! All parts have been created.")

except Exception as e:
    print(f"An error occurred: {e}")