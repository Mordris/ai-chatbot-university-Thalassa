import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get paths from environment variables or use defaults
TEXT_FOLDER = os.getenv("TEXT_FOLDER", './extracted_texts')
OUTPUT_FILE_NAME = 'hepsi.txt' # Keep merged file within the text folder
OUTPUT_FILE_PATH = os.path.join(TEXT_FOLDER, OUTPUT_FILE_NAME)

def merge_txt_files(input_folder, output_file):
    """Merges all .txt files in the input folder into a single output file."""
    logging.info(f"Starting merge process for folder: {input_folder}")
    logging.info(f"Output file: {output_file}")

    if not os.path.isdir(input_folder):
        logging.error(f"Input folder not found: {input_folder}")
        return

    # Get a list of all txt files, excluding the potential output file itself
    try:
        txt_files = [f for f in os.listdir(input_folder)
                     if f.endswith('.txt') and os.path.join(input_folder, f) != output_file]
    except FileNotFoundError:
        logging.error(f"Cannot access input folder: {input_folder}")
        return
    except Exception as e:
        logging.error(f"Error listing files in {input_folder}: {e}")
        return


    if not txt_files:
        logging.warning(f"No .txt files found to merge in {input_folder} (excluding {os.path.basename(output_file)}).")
        # Optionally create an empty output file or just exit
        # with open(output_file, 'w', encoding='utf-8') as outfile:
        #     outfile.write('') # Create empty file
        return

    # Sort the files alphabetically for consistent merging order
    txt_files.sort()
    logging.info(f"Found {len(txt_files)} files to merge: {txt_files}")

    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            for i, txt_file in enumerate(txt_files):
                file_path = os.path.join(input_folder, txt_file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                        outfile.write(content)
                        # Add a clear separator between files for potential debugging
                        # Add two newlines for better separation
                        if i < len(txt_files) - 1:
                            outfile.write('\n\n') # Separator between files
                    logging.debug(f"Successfully merged: {txt_file}")
                except Exception as e:
                    logging.error(f"Error reading file {txt_file}: {e}. Skipping.")

        logging.info(f"Files merged successfully into {output_file}")

    except IOError as e:
        logging.error(f"Error writing to output file {output_file}: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred during merging: {e}")

if __name__ == "__main__":
    # Ensure the data directory exists
    os.makedirs(TEXT_FOLDER, exist_ok=True)
    merge_txt_files(TEXT_FOLDER, OUTPUT_FILE_PATH)