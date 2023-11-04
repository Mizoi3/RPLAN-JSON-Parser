# RPLAN-JSON-Parser

## Usage

### Command Line Arguments
`parser.py` accepts the following command-line arguments:

- `--json`: The path to the input JSON file containing room boundaries and doors data.
- `--dir`: The path to the directory containing multiple JSON files to be processed. Cannot be used with `--json` simultaneously.
- `--output`: The path to the output directory where the results will be saved.

### Modes
- Single File Mode: When using `--json`, the script will process a single JSON file and output the adjacency data.
- Directory Mode: When using `--dir`, the script will process all JSON files within the specified directory and output adjacency data for each file.

### Output File Format
The output will be in JSON format, containing the following information:
- `polygons`: A list of polygons representing room boundaries.
- `adjacency`: A list representing the adjacency relationships between rooms, with connection flags.
- `types`: Room types, if available in the input data.
- `windows`: Window positions and sizes, if available in the input data.
- `entrance`: The calculated position and size of the entrance door.

Each adjacency entry will contain indices of two adjacent rooms followed by a connection flag (0 for no connection, 1 for connection via door, 2 for direct edge connection).
