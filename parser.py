"""
このコードはmatlab.doubleを解消済みのjsonファイルを、polygon sequenceとadjacency sequenceに変換します
polygon seq = [polygon1, ...]
adjacency seq = [[polygon ID 1, polygon ID 2, 0/1/2, door_x, door_y], ...]
ここで0は連続接続、1はドアを介して接続、2は壁を介して接続を表す。
"""
import sys
from shapely.geometry import Polygon, LineString
import json
import argparse
import os
# from tqdm import tqdm

def main():
    parser = argparse.ArgumentParser(description='Generate room adjacency sequence from a JSON file.')
    parser.add_argument('--json', type=str, required=True, help='Path to the input JSON file.')
    parser.add_argument('--output', type=str, required=True, help='Path to the output directory.')

    args = parser.parse_args()

    # Read the JSON file
    with open(args.json, 'r') as f:
        data = json.load(f)

    room_boundaries = data['room_boundaries']
    doors = data['doors']
    room_types = data['types']
    windows = data['windows']
    boundary = data['boundary']

    # Calculate adjacency
    adjacency_result = determine_adjacency(room_boundaries, doors)

    entrance_door = calculate_entrance_room(boundary)

    # Prepare the output data
    output_data = {
        "room_polygon_seq": room_boundaries,
        "room_adjacency_seq": adjacency_result,
        "types": room_types,
        "windows": windows,
        "entrance_door": entrance_door
    }

    # Write to the output JSON file
    output_file_path = f"{args.output}/{os.path.basename(args.json)}"
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
    
    for i, poly1 in enumerate(room_boundaries):
        for j, poly2 in enumerate(room_boundaries):
            if i >= j:
                continue  # 同じポリゴンまたはすでに比較したポリゴンとは比較しない
            
            polygon1 = Polygon(poly1)
            polygon2 = Polygon(poly2)
            
            connection_flag = 0  # 接続していない場合は0
            
            # 交差する辺があるか調べる
            for idx1, line1 in enumerate(list(polygon1.exterior.coords[:-1])):
                for idx2, line2 in enumerate(list(polygon2.exterior.coords[:-1])):
                    line1_obj = LineString([line1, list(polygon1.exterior.coords)[idx1 + 1]])
                    line2_obj = LineString([line2, list(polygon2.exterior.coords)[idx2 + 1]])
                    
                    if line1_obj.intersects(line2_obj) and not line1_obj.touches(line2_obj):
                        connection_flag = 2  # 接続している場合は2
                        break  # 一つでも交差する辺が見つかれば次のポリゴンへ
                else:
                    continue
                break
            
            if connection_flag == 2:
                adjacency.append([i, j, connection_flag, None, None, None, None])

    door_lines = convert_doors_to_lines(doors)

    for door_line, door in zip(door_lines, doors):
        _, x, y, dx, dy, _ = door
        door_center_x = x + dx / 2
        door_center_y = y + dy / 2
        door_len_x = dx
        door_len_y = dy

        connected_rooms = []
        for i, poly in enumerate(room_boundaries):
            polygon = Polygon(poly)
            if door_line.intersects(polygon):
                connected_rooms.append(i)

        if len(connected_rooms) == 2:
            adjacency.append([connected_rooms[0], connected_rooms[1], 1, door_center_x, door_center_y, door_len_x, door_len_y])

    return adjacency


def convert_doors_to_lines(doors):
    """
    doorsの配列を入力として、それに対応するLineオブジェクトのリストを返す関数。
    
    Parameters:
    - doors: ドア情報のリスト。各ドアは[x, y, dx, dy, _]の形式。
    
    Returns:
    - lines: Lineオブジェクトのリスト
    """

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

def calculate_entrance_room(boundary, target_flag=1, default_distance=6):
    output = []

    for item in boundary:
        if item[3] == 1:
            x, y = item[0], item[1]
            output.append([x, y])
    return output


if __name__ == '__main__':
    main()

