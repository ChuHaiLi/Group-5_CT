import json
import os

def read_places():
    file_path = os.path.join(os.path.dirname(__file__), 'sample_places.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Không tìm thấy file sample_places.json.")
        return []
    except json.JSONDecodeError:
        print("Lỗi định dạng JSON trong sample_places.json.")
        return []

    print("=== Dữ liệu trong sample_places.json ===")
    for i, place in enumerate(data, start=1):
        print(f"{i}. {place['name']} ({place['type']}) - Rating: {place['rating']}")
    print("========================================")
    return data

if __name__ == '__main__':
    read_places()
