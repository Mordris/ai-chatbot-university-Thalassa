import os

def merge_txt_files(input_folder, output_file):
    # Get a list of all txt files in the input folder
    txt_files = [f for f in os.listdir(input_folder) if f.endswith('.txt')]

    # Sort the files (optional, based on naming order)
    txt_files.sort()

    with open(output_file, 'w') as outfile:
        for i, txt_file in enumerate(txt_files):
            file_path = os.path.join(input_folder, txt_file)

            with open(file_path, 'r') as infile:
                # Write the content of the current file
                outfile.write(infile.read())

                # Add a line break after each file's content, except for the last one
                if i < len(txt_files) - 1:
                    outfile.write('\n')  # You can also customize the line break as needed

    print(f"Files merged successfully into {output_file}")

# Usage example:
input_folder = './extracted_texts'  # Replace with the path to the folder containing your txt files
output_file = './extracted_texts/hepsi.txt'  # Replace with the desired output file path

merge_txt_files(input_folder, output_file)
