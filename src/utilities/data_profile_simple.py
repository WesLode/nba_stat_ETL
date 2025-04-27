import json
import argparse
from collections import defaultdict, Counter
import statistics
import math
import sys

# --- Helper Function to Safely Calculate Stats ---
def calculate_numeric_stats(values):
    """Calculates stats for a list of numeric values, handling errors."""
    stats = {
        'min': None, 'max': None, 'mean': None,
        'median': None, 'stdev': None
    }
    numeric_values = [v for v in values if isinstance(v, (int, float)) and not math.isnan(v)]
    if not numeric_values:
        return stats

    try:
        stats['min'] = min(numeric_values)
        stats['max'] = max(numeric_values)
        stats['mean'] = statistics.mean(numeric_values)
        stats['median'] = statistics.median(numeric_values)
        if len(numeric_values) > 1:
            stats['stdev'] = statistics.stdev(numeric_values)
    except statistics.StatisticsError as e:
        print(f"Warning: Could not calculate some stats: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Warning: Unexpected error calculating stats: {e}", file=sys.stderr)

    return stats

def calculate_string_stats(values, top_n=5):
    """Calculates stats for a list of string values."""
    stats = {
        'min_length': None, 'max_length': None, 'avg_length': None,
        'empty_count': 0, 'unique_count': 0, 'most_common': []
    }
    string_values = [v for v in values if isinstance(v, str)]
    if not string_values:
        return stats

    lengths = [len(s) for s in string_values]
    stats['min_length'] = min(lengths)
    stats['max_length'] = max(lengths)
    stats['avg_length'] = statistics.mean(lengths) if lengths else 0
    stats['empty_count'] = sum(1 for s in string_values if s == "")

    try:
        counter = Counter(string_values)
        stats['unique_count'] = len(counter)
        stats['most_common'] = counter.most_common(top_n)
    except TypeError as e:
        # Handle cases where unhashable types might have slipped through (shouldn't happen with check)
        print(f"Warning: Could not count frequencies due to unhashable type: {e}", file=sys.stderr)
        stats['unique_count'] = "Error calculating"
        stats['most_common'] = ["Error calculating"]


    return stats

def calculate_list_stats(lengths):
    """Calculates stats for list lengths."""
    stats = {'min_length': None, 'max_length': None, 'avg_length': None}
    if not lengths:
        return stats
    stats['min_length'] = min(lengths)
    stats['max_length'] = max(lengths)
    stats['avg_length'] = statistics.mean(lengths)
    return stats

# --- Core Traversal and Collection Logic ---
def traverse_and_collect(data, path, collected_data):
    """
    Recursively traverses the data structure and collects information.
    `collected_data` is a dict mapping path -> stats_dict.
    """
    current_node_info = collected_data[path]
    current_node_info['count'] += 1
    data_type = type(data).__name__
    current_node_info['types'][data_type] += 1

    if data is None:
        current_node_info['null_count'] += 1
        current_node_info['values'].append(data)
    elif isinstance(data, bool):
         current_node_info['values'].append(data) # Can count True/False later if needed
    elif isinstance(data, (int, float)):
        current_node_info['values'].append(data)
    elif isinstance(data, str):
        current_node_info['values'].append(data)
        current_node_info['string_lengths'].append(len(data))
        if data == "":
             current_node_info['empty_count'] += 1
    elif isinstance(data, list):
        current_node_info['list_lengths'].append(len(data))
        if len(data) == 0:
            current_node_info['empty_count'] += 1
        # Use [*] to represent "any element" in the list for profiling list contents
        list_element_path = f"{path}[*]"
        for item in data:
            traverse_and_collect(item, list_element_path, collected_data)
    elif isinstance(data, dict):
        if len(data) == 0:
             current_node_info['empty_count'] += 1
        for key, value in data.items():
            # Ensure keys are valid strings for paths
            sanitized_key = str(key).replace('.', '_') # Basic sanitization
            child_path = f"{path}.{sanitized_key}"
            traverse_and_collect(value, child_path, collected_data)
    else:
        # Handle other potential JSON-like types if necessary
        current_node_info['types']['unknown'] += 1


# --- Main Profiling Function ---
def profile_json_data(data):
    """Profiles the loaded JSON data (Python object)."""
    # Use defaultdict for easier aggregation during traversal
    collected_data = defaultdict(lambda: {
        'count': 0,
        'types': Counter(),
        'values': [], # Store raw values for stats (can be memory intensive!)
        'null_count': 0,
        'empty_count': 0, # Count "" for strings, [] for lists, {} for dicts
        'list_lengths': [],
        'string_lengths': []
    })

    # Start traversal from the root '$'
    traverse_and_collect(data, '$', collected_data)

    # --- Post-traversal: Calculate final statistics ---
    profile_results = {}
    for path, info in collected_data.items():
        result = {
            'count': info['count'],
            'types': dict(info['types']),
            'null_percentage': (info['null_count'] / info['count'] * 100) if info['count'] else 0,
            'empty_percentage': (info['empty_count'] / info['count'] * 100) if info['count'] else 0,
        }

        # Determine dominant type (excluding NoneType if other types exist)
        dominant_type = None
        filtered_types = {t: c for t, c in info['types'].items() if t != 'NoneType'}
        if filtered_types:
             dominant_type = max(filtered_types, key=filtered_types.get)
        elif 'NoneType' in info['types']:
             dominant_type = 'NoneType'


        # Add stats based on dominant type
        if dominant_type in ('int', 'float'):
            result['numeric_stats'] = calculate_numeric_stats(info['values'])
        elif dominant_type == 'str':
            result['string_stats'] = calculate_string_stats(info['values'])
        elif dominant_type == 'list':
            result['list_stats'] = calculate_list_stats(info['list_lengths'])
            # Note: Stats for list *contents* are under the path[*] key

        # Cleanup - don't need raw values in final report (unless explicitly desired)
        # Be mindful of memory if keeping large lists of values
        # del info['values']

        profile_results[path] = result

    return profile_results

# --- File Loading and Execution ---
def load_json_file(file_path):
    """Loads JSON data from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Could not decode JSON from {file_path}. Invalid JSON format: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"An unexpected error occurred while reading {file_path}: {e}", file=sys.stderr)
        return None

def format_and_print_profile(profile):
    """Formats the profile dictionary for printing."""
    if not profile:
        print("No profile data generated.")
        return

    print("--- JSON Data Profile ---")
    for path, stats in sorted(profile.items()): # Sort paths for readability
        print(f"\nPath: {path}")
        print(f"  Count: {stats['count']}")
        print(f"  Data Types: {stats['types']}")
        print(f"  Null %: {stats['null_percentage']:.2f}%")
        print(f"  Empty %: {stats['empty_percentage']:.2f}%") # (Empty string, list, or dict)

        if 'numeric_stats' in stats:
            print(f"  Numeric Stats: {stats['numeric_stats']}")
        if 'string_stats' in stats:
            print(f"  String Stats: {stats['string_stats']}")
        if 'list_stats' in stats:
            print(f"  List Stats (length): {stats['list_stats']}")
    print("\n--- End Profile ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Profile a JSON file to understand its structure and data types.")
    parser.add_argument("-f","--json_file", help="Path to the input JSON file.")
    parser.add_argument("-o", "--output", help="Path to save the profile results (JSON format).")

    args = parser.parse_args()

    print(f"Loading JSON file: {args.json_file}")
    json_data = load_json_file(args.json_file)

    if json_data is not None:
        print("Profiling data...")
        profile = profile_json_data(json_data)
        print("Profiling complete.")

        format_and_print_profile(profile)

        if args.output:
            print(f"Saving profile results to: {args.output}")
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    # Use default=str to handle potential non-serializable types like float('nan') if they creep in
                    json.dump(profile, f, indent=2, default=str)
                print("Profile saved successfully.")
            except Exception as e:
                print(f"Error saving profile to {args.output}: {e}", file=sys.stderr)
    else:
        print("Exiting due to loading errors.", file=sys.stderr)
        sys.exit(1)