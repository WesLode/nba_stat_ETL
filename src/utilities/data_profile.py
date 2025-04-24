import json
import argparse
from collections import defaultdict, Counter
import statistics
import math
import sys
import os # For seeding hash functions

# --- Dependency Check and Import for Count-Min Sketch ---
try:
    from probables import CountMinSketch
except ImportError:
    print("Error: 'probables' library not found. Please install it: pip install probables", file=sys.stderr)
    sys.exit(1)

# --- Configuration ---
MAX_UNIQUE_STRINGS_TO_STORE = 1000 # Limit memory usage for unique string tracking

# --- Helper Function to Safely Calculate Welford-based Stats ---
def calculate_welford_stats(n, mean, s, min_val, max_val, numeric_counter): # Added numeric_counter
    """Calculates final stats from Welford accumulators and finds mode from counter."""
    stats = {
        'min': min_val,
        'max': max_val,
        'mean': None,
        'mode': None, # <-- ADDED
        'mode_count': 0, # <-- ADDED
        'stdev': None,
        'variance_sample': None,
        'variance_population': None
    }
    if n > 0:
        stats['mean'] = mean
        if n > 1:
            try:
                variance_sample = s / (n - 1)
                stats['variance_sample'] = variance_sample
                stats['stdev'] = math.sqrt(variance_sample)
            except ValueError: # Handle potential negative s due to floating point issues
                 stats['variance_sample'] = 0.0
                 stats['stdev'] = 0.0

        try:
             stats['variance_population'] = s / n
        except ValueError:
             stats['variance_population'] = 0.0


        # Calculate Mode from counter
        if numeric_counter:
            # Find the highest frequency
            most_common_items = numeric_counter.most_common() # Returns list of (value, count) sorted by count desc
            if most_common_items:
                max_freq = most_common_items[0][1]
                # Get all items with the max frequency (handles ties)
                modes = [item[0] for item in most_common_items if item[1] == max_freq]
                stats['mode'] = modes[0] if len(modes) == 1 else modes # Store single mode or list of modes
                stats['mode_count'] = max_freq


    return stats

# --- Modified Helper for String Stats ---
def calculate_string_stats_cms(cms, string_lengths, empty_count, examples, unique_strings, unique_strings_limited): # Added unique tracking params
    """Calculates stats for strings using CMS, length info, examples, and unique count."""
    stats = {
        'min_length': None, 'max_length': None, 'avg_length': None,
        'empty_count': empty_count,
        'unique_count': len(unique_strings), # <-- ADDED
        'unique_count_limited': unique_strings_limited, # <-- ADDED flag
        'estimated_total_items': cms.elements_added,
        'cms_width': cms.width,
        'cms_depth': cms.depth,
        'cms_error_rate': cms.error_rate,
        'cms_confidence': cms.confidence,
        'examples': examples
    }
    if not string_lengths:
        return stats

    try:
        stats['min_length'] = min(string_lengths)
        stats['max_length'] = max(string_lengths)
        stats['avg_length'] = statistics.mean(string_lengths)
    except ValueError: # Handle empty list edge case if necessary
        pass

    return stats


def calculate_list_stats(lengths):
    """Calculates stats for list lengths."""
    stats = {'min_length': None, 'max_length': None, 'avg_length': None}
    if not lengths:
        return stats
    try:
        stats['min_length'] = min(lengths)
        stats['max_length'] = max(lengths)
        stats['avg_length'] = statistics.mean(lengths)
    except ValueError: # Handle empty list edge case
        pass
    return stats

# --- Core Traversal and Collection Logic (Modified) ---
def traverse_and_collect(data, path, collected_data, cms_width, cms_depth, cms_error_rate, cms_confidence):
    """
    Recursively traverses the data structure and collects information using
    Welford+Counter for numbers and Count-Min Sketch+LimitedSet for strings.
    """
    # Initialize node info if path is new
    if path not in collected_data:
         seeds = [int.from_bytes(os.urandom(8), byteorder='big') for _ in range(cms_depth)]
         collected_data[path] = {
            'count': 0,
            'types': Counter(),
            'null_count': 0,
            'empty_count': 0,
            'list_lengths': [],
            'string_lengths': [],
            'string_examples': [],
            'unique_strings': set(), # <-- ADDED: Set for unique strings
            'unique_strings_limited': False, # <-- ADDED: Flag if set limit reached
            # Welford accumulators
            'welford_n': 0,
            'welford_mean': 0.0,
            'welford_s': 0.0,
            'numeric_min': float('inf'),
            'numeric_max': float('-inf'),
            'numeric_counter': Counter(), # <-- ADDED: Counter for numeric mode
            # Count-Min Sketch
            'cms': CountMinSketch(width=cms_width, 
                                  depth=cms_depth, 
                                  error_rate=cms_error_rate, 
                                  confidence=cms_confidence, 
                                #   seeds=seeds
                                  )
        }

    current_node_info = collected_data[path]
    current_node_info['count'] += 1
    data_type = type(data).__name__
    current_node_info['types'][data_type] += 1

    if data is None:
        current_node_info['null_count'] += 1
    elif isinstance(data, bool):
        pass
    elif isinstance(data, (int, float)) and not math.isnan(data): # Welford update + Counter Update
        current_node_info['numeric_min'] = min(current_node_info['numeric_min'], data)
        current_node_info['numeric_max'] = max(current_node_info['numeric_max'], data)

        # --- ADDED: Update Numeric Counter for Mode ---
        current_node_info['numeric_counter'][data] += 1
        # ---------------------------------------------

        # --- Welford's Algorithm Step ---
        n = current_node_info['welford_n'] + 1
        old_mean = current_node_info['welford_mean']
        new_mean = old_mean + (data - old_mean) / n
        new_s = current_node_info['welford_s'] + (data - new_mean) * (data - old_mean)
        current_node_info['welford_n'] = n
        current_node_info['welford_mean'] = new_mean
        current_node_info['welford_s'] = new_s
        # --------------------------------

    elif isinstance(data, str): # Count-Min Sketch update + Example Collection + Unique Set Update
        current_node_info['string_lengths'].append(len(data))
        current_node_info['cms'].add(data)
        if data == "":
             current_node_info['empty_count'] += 1

        # Collect up to 2 string examples
        if len(current_node_info['string_examples']) < 2:
            if data not in current_node_info['string_examples']:
                 current_node_info['string_examples'].append(data)

        # --- ADDED: Update unique string set (up to limit) ---
        if not current_node_info['unique_strings_limited']:
            if len(current_node_info['unique_strings']) < MAX_UNIQUE_STRINGS_TO_STORE:
                current_node_info['unique_strings'].add(data)
            else:
                # Limit reached, stop adding and set flag
                current_node_info['unique_strings_limited'] = True
        # ----------------------------------------------------

    elif isinstance(data, list):
        current_node_info['list_lengths'].append(len(data))
        if len(data) == 0:
            current_node_info['empty_count'] += 1
        list_element_path = f"{path}[*]"
        for item in data:
            traverse_and_collect(item, list_element_path, collected_data, cms_width, cms_depth, cms_error_rate, cms_confidence)
    elif isinstance(data, dict):
        if len(data) == 0:
             current_node_info['empty_count'] += 1
        for key, value in data.items():
            sanitized_key = str(key).replace('.', '_')
            child_path = f"{path}.{sanitized_key}"
            traverse_and_collect(value, child_path, collected_data, cms_width, cms_depth, cms_error_rate, cms_confidence)
    else:
        current_node_info['types']['unknown'] += 1


# --- Main Profiling Function (Modified calls to stats functions) ---
def profile_json_data(data, cms_width, cms_depth, cms_error_rate, cms_confidence):
    """Profiles the loaded JSON data (Python object) using memory-efficient techniques."""
    collected_data = {}

    print("Starting data traversal and collection...")
    traverse_and_collect(data, '$', collected_data, cms_width, cms_depth, cms_error_rate, cms_confidence)
    print("Traversal complete. Calculating final statistics...")

    profile_results = {}
    for path, info in collected_data.items():
        result = {
            'count': info['count'],
            'types': dict(info['types']),
            'null_percentage': (info['null_count'] / info['count'] * 100) if info['count'] else 0,
            'empty_percentage': (info['empty_count'] / info['count'] * 100) if info['count'] else 0,
        }

        dominant_type = None
        filtered_types = {t: c for t, c in info['types'].items() if t != 'NoneType'}
        if filtered_types:
             dominant_type = max(filtered_types, key=filtered_types.get)
        elif 'NoneType' in info['types']:
             dominant_type = 'NoneType'

        # --- Numeric Stats ---
        if info['welford_n'] > 0:
             min_val = info['numeric_min'] if info['numeric_min'] != float('inf') else None
             max_val = info['numeric_max'] if info['numeric_max'] != float('-inf') else None
             result['numeric_stats'] = calculate_welford_stats(
                 info['welford_n'], info['welford_mean'], info['welford_s'], min_val, max_val,
                 info['numeric_counter'] # Pass counter for mode
             )
             result['numeric_stats']['note'] = "Mean/Stdev via Welford. Mode via Counter. Float mode depends on exact precision."

        # --- String Stats ---
        if info['cms'].elements_added > 0 or info['string_examples'] or info['unique_strings']:
             result['string_stats'] = calculate_string_stats_cms(
                 info['cms'], info['string_lengths'], info['empty_count'],
                 info['string_examples'], # Pass examples
                 info['unique_strings'], info['unique_strings_limited'] # Pass unique info
             )
             result['string_stats']['note'] = f"Unique count tracked up to {MAX_UNIQUE_STRINGS_TO_STORE} items. Freq estimates via CMS."

        # --- List Stats ---
        if info['list_lengths']:
            result['list_stats'] = calculate_list_stats(info['list_lengths'])

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

# --- Modified Formatting Function ---
def format_and_print_profile(profile):
    """Formats the profile dictionary for printing."""
    if not profile:
        print("No profile data generated.")
        return

    print("\n--- JSON Data Profile ---")
    for path, stats in sorted(profile.items()):
        print(f"\nPath: {path}")
        print(f"  Count: {stats['count']}")
        print(f"  Data Types: {stats['types']}")
        print(f"  Null %: {stats['null_percentage']:.2f}%")
        print(f"  Empty %: {stats['empty_percentage']:.2f}%")

        if 'numeric_stats' in stats:
            n_stats = stats['numeric_stats']
            # Format numeric stats for printing, handling None values gracefully
            stat_parts = []
            for k, v in n_stats.items():
                if k == 'note' or v is None: continue
                if isinstance(v, float):
                    stat_parts.append(f"{k}={v:.4f}")
                else:
                    stat_parts.append(f"{k}={v}") # Includes mode which could be list
            print(f"  Numeric Stats: {{{', '.join(stat_parts)}}}")
            if 'note' in n_stats: print(f"    Note: {n_stats['note']}")

        if 'string_stats' in stats:
            s_stats = stats['string_stats']
            unique_limit_note = "(Limit Reached)" if s_stats.get('unique_count_limited') else ""
            # Print basic string stats first
            print(f"  String Stats: Unique={s_stats.get('unique_count', 'N/A')}{unique_limit_note}, "
                  f"AvgLen={s_stats.get('avg_length', 'N/A'):.2f}, "
                  f"MinLen={s_stats.get('min_length', 'N/A')}, MaxLen={s_stats.get('max_length', 'N/A')}, "
                  f"EmptyCnt={s_stats.get('empty_count', 'N/A')}")
            # Print examples if they exist
            if s_stats.get('examples'):
                 print(f"    Examples: {s_stats['examples']}")
             # Print CMS specific info
            print(f"    CMS Info: ItemsAdded={s_stats.get('estimated_total_items', 'N/A')}, "
                  f"Width={s_stats.get('cms_width', 'N/A')}, Depth={s_stats.get('cms_depth', 'N/A')}")
            # Print note about CMS/Uniques
            if 'note' in s_stats: print(f"    Note: {s_stats['note']}")

        if 'list_stats' in stats:
            l_stats = stats['list_stats']
            stat_strs = [f"{k}={v:.2f}" if isinstance(v, float) and v is not None else f"{k}={v}"
                         for k, v in l_stats.items() if v is not None]
            print(f"  List Stats (length): {{{', '.join(stat_strs)}}}")

    print("\n--- End Profile ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Profile a JSON file using Welford's algorithm and Counter for numeric stats, "
                    "and Count-Min Sketch + Limited Set for string frequency/uniqueness estimation.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
    parser.add_argument("json_file", help="Path to the input JSON file.")
    parser.add_argument("-o", "--output", help="Path to save the profile results (JSON format).")
    parser.add_argument("--cms_error_rate", type=float, default=0.001, help="Target error rate for Count-Min Sketch (adjusts width/depth).")
    parser.add_argument("--cms_confidence", type=float, default=0.99, help="Target confidence for Count-Min Sketch estimates (adjusts depth/width).")
    # Removed MAX_UNIQUE_STRINGS_TO_STORE from args for now, using constant

    args = parser.parse_args()

    temp_cms = CountMinSketch(error_rate=args.cms_error_rate, confidence=args.cms_confidence)
    cms_width = temp_cms.width
    cms_depth = temp_cms.depth
    print(f"Using Count-Min Sketch with calculated params: width={cms_width}, depth={cms_depth} (for error_rate={args.cms_error_rate}, confidence={args.cms_confidence})")
    print(f"Tracking exact unique strings up to a limit of: {MAX_UNIQUE_STRINGS_TO_STORE}")


    print(f"Loading JSON file: {args.json_file}")
    json_data = load_json_file(args.json_file)

    if json_data is not None:
        print("Profiling data...")
        profile = profile_json_data(json_data, cms_width, cms_depth, args.cms_error_rate, args.cms_confidence)
        print("Profiling complete.")

        format_and_print_profile(profile)

        if args.output:
            print(f"Saving profile results to: {args.output}")
            try:
                class ProfileEncoder(json.JSONEncoder):
                    def default(self, obj):
                        if isinstance(obj, CountMinSketch):
                            return f"<CountMinSketch width={obj.width} depth={obj.depth} elements={obj.elements_added}>"
                        if isinstance(obj, set): # Handle sets (like unique_strings if kept in output)
                            return list(obj) # Convert set to list for JSON
                        if obj == float('inf') or obj == float('-inf'):
                            return str(obj)
                        # Let the base class default method raise the TypeError
                        return json.JSONEncoder.default(self, obj)

                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(profile, f, indent=2, cls=ProfileEncoder)
                print("Profile saved successfully.")
            except Exception as e:
                print(f"Error saving profile to {args.output}: {e}", file=sys.stderr)
    else:
        print("Exiting due to loading errors.", file=sys.stderr)
        sys.exit(1)