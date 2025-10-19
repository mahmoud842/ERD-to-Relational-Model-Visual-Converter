import sys
import json
import os
import build_table
import render

def load_json(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <file.json>")
        sys.exit(1)

    json_data = load_json(sys.argv[1])
    if not json_data:
        sys.exit(1)

    filename, _ = os.path.splitext(sys.argv[1])
    t = build_table.generate_tables(json_data)
    render.tables_to_graph(t, filename)
