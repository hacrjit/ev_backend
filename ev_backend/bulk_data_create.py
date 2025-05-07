import json
import random
import os

def convert_charging_stations(input_file_path, output_file_path):
    """
    Convert charging stations data from the original format to the desired format.
    
    Args:
        input_file_path (str): Path to the input JSON file
        output_file_path (str): Path where the converted JSON will be saved
    """
    print(f"Opening file: {input_file_path}")
    
    try:
        # Read the input file
        with open(input_file_path, 'r', encoding='utf-8') as file:
            # Try to load as single JSON array first
            try:
                data = json.load(file)
                # If this succeeds, data should be a list or object
                if not isinstance(data, list):
                    data = [data]  # Convert single object to list
            except json.JSONDecodeError:
                # If it's not a valid single JSON, try reading as multiple JSON objects
                file.seek(0)  # Reset file pointer to beginning
                content = file.read()
                # Find all JSON objects (objects that start with { and end with })
                data = []
                import re
                json_objects = re.findall(r'{\s*"_id".*?}(?=\s*{|\s*$)', content, re.DOTALL)
                
                for json_str in json_objects:
                    try:
                        obj = json.loads(json_str)
                        data.append(obj)
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON object: {e}")
                        continue
    except Exception as e:
        print(f"Error reading input file: {e}")
        return None
    
    print(f"Successfully loaded {len(data)} charging stations from file")
    
    # Convert the data to the desired format
    converted_data = []
    for station in data:
        # Skip if no address info or missing coordinates
        if not station.get("AddressInfo") or "Latitude" not in station.get("AddressInfo", {}) or "Longitude" not in station.get("AddressInfo", {}):
            continue
        
        address_info = station["AddressInfo"]
        
        # Extract plug types from connections
        plug_types = []
        if "Connections" in station and station["Connections"]:
            for connection in station["Connections"]:
                if connection.get("ConnectionType") and connection["ConnectionType"].get("Title"):
                    plug_type = connection["ConnectionType"]["Title"]
                    if plug_type != "Unknown" and plug_type not in plug_types:
                        plug_types.append(plug_type)
        
        # Build address string
        address_components = []
        if address_info.get("AddressLine1"):
            address_components.append(address_info["AddressLine1"])
        if address_info.get("Town"):
            address_components.append(address_info["Town"])
        if address_info.get("StateOrProvince"):
            address_components.append(address_info["StateOrProvince"])
        
        address = ", ".join(address_components)
        
        # Generate random price between 8 and 15
        price_per_kwh = round(random.uniform(8.0, 15.0), 2)
        
        # Generate random availability
        is_available = random.choice([True, False])
        
        # Generate random hours (realistic for charging stations)
        open_hour = random.randint(6, 9)
        close_hour = random.randint(20, 23)
        
        converted_station = {
            "name": address_info.get("Title", "Unknown Charging Station"),
            "address": address,
            "pin_code": address_info.get("Postcode", ""),
            "latitude": address_info["Latitude"],
            "longitude": address_info["Longitude"],
            "plug_types": plug_types,
            "price_per_kwh": price_per_kwh,
            "is_available": is_available,
            "open_time": f"{open_hour:02d}:00:00",
            "close_time": f"{close_hour:02d}:00:00"
        }
        
        converted_data.append(converted_station)
    
    print(f"Converted {len(converted_data)} charging stations")
    
    # Write the converted data to the output file
    try:
        with open(output_file_path, 'w', encoding='utf-8') as file:
            json.dump(converted_data, file, indent=2)
        print(f"Successfully wrote converted data to {output_file_path}")
        return converted_data
    except Exception as e:
        print(f"Error writing output file: {e}")
        return None

if __name__ == "__main__":
    # Define file paths
    input_file = "charging_stations.json"
    output_file = "converted_charging_stations.json"
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
    else:
        # Convert the data
        convert_charging_stations(input_file, output_file)