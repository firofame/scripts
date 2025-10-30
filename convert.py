import csv

# Define the input and output filenames
input_file_name = 'amanithafseer.csv'
output_file_name = 'amanithafseer.txt'

try:
    # Open the input CSV file for reading and the output TXT file for writing
    # 'encoding="utf-8"' is crucial for handling Malayalam characters correctly.
    # 'newline=""' is recommended when working with the csv module.
    with open(input_file_name, mode='r', encoding='utf-8', newline='') as infile, \
         open(output_file_name, mode='w', encoding='utf-8', newline='') as outfile:

        # Create a reader object to parse the CSV file
        csv_reader = csv.reader(infile)

        # Create a writer object for the output file, specifying '|' as the delimiter
        txt_writer = csv.writer(outfile, delimiter='|')

        # Loop through each row in the input file
        for row in csv_reader:
            # Write the row to the output file with the new delimiter
            txt_writer.writerow(row)

    print(f"Successfully converted '{input_file_name}' to '{output_file_name}'")

except FileNotFoundError:
    print(f"Error: The file '{input_file_name}' was not found.")
except Exception as e:
    print(f"An error occurred: {e}")