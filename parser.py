import json
import argparse
import os
import sys
sys.path.append("../")

from shapely.geometry import Polygon, LineString

# optional (if you need to change category dummy as string)
# from config import category

def main():
    parser = argparse.ArgumentParser(description='Generate room adjacency sequence from JSON files.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--json', type=str, help='Path to the input JSON file.')
    group.add_argument('--dir', type=str, help='Directory path to process all JSON files within it.')
    parser.add_argument('--output', type=str, required=True, help='Path to the output directory.')

    args = parser.parse_args()

    if args.json:
        json_files = [args.json]
    else:
        json_files = [os.path.join(args.dir, file) for file in os.listdir(args.dir) if file.endswith('.json')]

    for json_file in json_files:
        with open(json_file, 'r') as f:
            data = json.load(f)

        room_boundaries = data['room_boundaries']
        doors = make_doors_easy(data['doors']) # remove direction
        types = [category[type_] for type_ in data['types']]
        windows = data['windows']
        boundary = data['boundary']

        # Calculate adjacency
        adjacency, doors = determine_adjacency(room_boundaries, doors)

        entrance_door = calculate_entrance_room(boundary)

        # Prepare the output data
        output_data = {
            "polygons": room_boundaries,
            "adjacency": adjacency,
            "types": types,
            "doors": doors,
            "windows": windows,
            "entrance": entrance_door
        }

        # Write to the output JSON file
        output_file_name = os.path.basename(json_file)
        output_file_path = os.path.join(args.output, output_file_name)
        with open(output_file_path, 'w') as f:
            json.dump(output_data, f)

def is_overlapping(edge1, edge2):
    """Check if two edges overlap and are not just touching at a vertex."""
    line1 = LineString(edge1)
    line2 = LineString(edge2)
    overlap = line1.intersection(line2)
    
    # Check if they are not just touching at a vertex
    return overlap.length > 0

def determine_adjacency(room_boundaries, doors):
    """Determine the adjacency between room polygons."""
    adjacency = []
    door_data = []

    for i, poly1 in enumerate(room_boundaries):
        for j, poly2 in enumerate(room_boundaries):
            if i >= j:
                continue

            polygon1 = Polygon(poly1)
            polygon2 = Polygon(poly2)

            connection_flag = 0

            for idx1, point1 in enumerate(polygon1.exterior.coords[:-1]):
                for idx2, point2 in enumerate(polygon2.exterior.coords[:-1]):
                    line1 = LineString([point1, polygon1.exterior.coords[idx1 + 1]])
                    line2 = LineString([point2, polygon2.exterior.coords[idx2 + 1]])

                    if line1.intersects(line2) and not line1.touches(line2):
                        connection_flag = 2
                        break
                if connection_flag:
                    break

            if connection_flag:
                adjacency.append([i, j, connection_flag])

    for door in doors:
        x, y, dx, dy = door  # 更新されたフォーマットに基づいて変更
        door_line = LineString([(x, y), (x + dx, y + dy)])
        
        connected_rooms = []
        for i, poly in enumerate(room_boundaries):
            if door_line.intersects(Polygon(poly)):
                connected_rooms.append(i)

        if len(connected_rooms) == 2:
            adjacency.append([connected_rooms[0], connected_rooms[1], 1])
            door_center_x = x + dx / 2
            door_center_y = y + dy / 2
            door_data.append([door_center_x, door_center_y, abs(dx), abs(dy)])

    return adjacency, door_data



def convert_doors_to_lines(doors):
    output_doors = []
    for idx, x, y, dx, dy, direction in doors:
        # Adjust the direction of the vector according to the dir value
        if direction == 3:  # Right
            dx, dy = dx, 0
        elif direction == 0:  # Up
            dx, dy = 0, dy
        elif direction == 1:  # Left
            dx, dy = -dx, 0
        elif direction == 2:  # Down
            dx, dy = 0, -dy
        start_x, end_x = x, x + dx
        start_y, end_y = y, y + dy
        # Lineオブジェクトの作成
        door = LineString([(start_x, start_y), (end_x, end_y)])
        output_doors.append(door)

    return output_doors

def make_doors_easy(doors):
    output_doors = []
    for idx, x, y, dx, dy, direction in doors:
        # Adjust the direction of the vector according to the dir value
        if direction == 3:  # Right
            dx, dy = dx, 0
        elif direction == 0:  # Up
            dx, dy = 0, dy
        elif direction == 1:  # Left
            dx, dy = -dx, 0
        elif direction == 2:  # Down
            dx, dy = 0, -dy
        # Lineオブジェクトの作成
        output_doors.append([x, y, dx, dy])

    return output_doors

def calculate_entrance_room(boundary):
    output = []

    for item in boundary:
        if item[3] == 1:
            x, y = item[0], item[1]
            output.append([x, y])
    return output


if __name__ == '__main__':
    main()
