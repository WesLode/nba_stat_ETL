import json
import os
import argparse
import sys


def combine_json_files(input_folder, output_file, json_structure = 1):
    """
    Combines multiple JSON files from a specified folder into a single JSON file.

    Args:
        input_folder (str): The path to the folder containing the input JSON files.
        output_file (str): The path where the combined JSON file will be saved.
    """
    combined_data = []
    file_count = 0
    error_files = []

    # Check if the input folder exists
    if not os.path.isdir(input_folder):
        print(f"Error: Input folder '{input_folder}' not found or is not a directory.")
        sys.exit(1) # Exit script with an error code

    print(f"Searching for JSON files in: {input_folder}")

    # Iterate through all files in the input folder
    for filename in os.listdir(input_folder):
        # Construct the full file path
        file_path = os.path.join(input_folder, filename)

        # Process only files with the .json extension
        if filename.lower().endswith(".json") and os.path.isfile(file_path):
            file_count += 1
            print(f"  Processing file: {filename}...")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    # Load JSON data from the file
                    data_load = json.load(f)
                    data = single_layer(data_load,filename)
                    # data = record_only(data_load,filename)
                    # data = data_load

                    # Check if the loaded data is a list or a single object
                    if isinstance(data, list):
                        # If it's a list, extend the main list
                        combined_data.extend(data)
                        print(f"    -> Added {len(data)} items (list).")
                    elif isinstance(data, dict):
                        # If it's a dictionary (object), append it to the main list
                        combined_data.append(data)
                        print("    -> Added 1 item (object).")
                    else:
                        print(f"    -> Warning: Content of {filename} is neither a JSON list nor object. Skipping content.")
                        error_files.append(filename + " (invalid root type)")


            except json.JSONDecodeError as e:
                print(f"    -> Error: Could not decode JSON from {filename}. Skipping file. Error: {e}")
                error_files.append(filename + " (JSON decode error)")
            except IOError as e:
                print(f"    -> Error: Could not read file {filename}. Skipping file. Error: {e}")
                error_files.append(filename + " (read error)")
            except Exception as e:
                print(f"    -> Error: An unexpected error occurred processing {filename}. Skipping file. Error: {e}")
                error_files.append(filename + " (unexpected error)")

    if file_count == 0:
        print("No JSON files found in the specified folder.")
        return # Exit the function gracefully

    print(f"\nProcessed {file_count} JSON files.")

    if not combined_data:
        print("Warning: No valid JSON data was successfully combined.")
        if error_files:
             print(f"Files with errors: {', '.join(error_files)}")
        return

    # Write the combined data to the output file
    try:
        print(f"\nWriting combined data to: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            # Use indent for pretty printing, ensure_ascii=False for non-ASCII chars
            json.dump(combined_data, f, indent=4, ensure_ascii=False)
        print("Successfully combined JSON files!")
        if error_files:
            print(f"\nNote: Some files encountered errors during processing: {', '.join(error_files)}")

    except IOError as e:
        print(f"Error: Could not write to output file {output_file}. Error: {e}")
        sys.exit(1) # Exit script with an error code
    except Exception as e:
        print(f"Error: An unexpected error occurred while writing the output file. Error: {e}")
        sys.exit(1) # Exit script with an error code

def single_layer(data_load,filename):
    record = {}
    _id = filename.replace('.json','')
    record['id']= _id
    for i in data_load:
        record[i] = data_load[i]
    
    return record

def record_only(data_load,filename):
    # record = {}
    _id = filename.replace('.json','')
    record = {
        'season': _id,
        'data': data_load
    }

    
    return record

if __name__ == "__main__":
    # Set up argument parser for command-line execution
    parser = argparse.ArgumentParser(
        description="Combine multiple JSON files from a folder into one."
    )
    parser.add_argument(
        "--input_folder", 
        type=str,
        # default="output\\data\\json_export\\gameSummary",
        default="output\\data\\json_export\\player_info",
        # default= "output\\data\\json_export\\boxScore",
        help="Path to the folder containing input JSON files.",
    )
    parser.add_argument(
        "--output_file", 
        type=str,
        default="output\\data\\full_json\\playerInfo.json",
        # default="output\\data\\full_json\\playerBoxscore_update.json",
        help="Path for the combined output JSON file.",

    )

    # Parse arguments from the command line
    args = parser.parse_args(
        
    )

    season_loop = False

    # Call the main function with the provided arguments
    if season_loop == False:
        combine_json_files(args.input_folder, args.output_file)
    else:
        for i in range(1983,2025):
            season = f"{str(i)}_{str(i +1)[-2:]}"
            input_path = "output\\data\\json_export\\boxScoreAdvance"
            output_path = "output\\data\\json_export\\boxScore"
            combine_json_files(f'{input_path}\\{season}', f'{output_path}\\{season}.json')
