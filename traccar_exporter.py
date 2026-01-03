#!/usr/bin/env python3
"""
Traccar Data Exporter
Connects to Traccar server and exports position data in various GPS formats.
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET
from xml.dom import minidom
import zipfile
import io
import sys
from tqdm import tqdm
import getpass
from math import radians, cos, sin, asin, sqrt


class TraccarExporter:
    """Handle Traccar API connections and data export."""
    
    def __init__(self, server_url: str, email: str, password: str):
        """Initialize Traccar connection.
        
        Args:
            server_url: Traccar server URL (e.g., https://demo.traccar.org)
            email: User email for authentication
            password: User password
        """
        self.server_url = server_url.rstrip('/')
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.devices = []
        self.authenticated = False
    def test_connection(self) -> bool:
        """Test connection to Traccar server.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Traccar expects form-encoded credentials
            credentials = {
                'email': self.email,
                'password': self.password
            }
            
            # Try without trailing slash first (standard REST convention)
            url_no_slash = f"{self.server_url}/api/session"
            print(f"Attempting connection to: {url_no_slash}")
            print(f"Sending credentials: email={self.email}")
            
            response = self.session.post(
                url_no_slash,
                data=credentials,  # Use form-encoded data
                verify=False,
                allow_redirects=False,
                timeout=10
            )
            
            print(f"Response status: {response.status_code}")
            
            # If we get 404 or 415, try with trailing slash
            if response.status_code in [404, 415]:
                url_with_slash = f"{self.server_url}/api/session/"
                print(f"First attempt failed, retrying with trailing slash: {url_with_slash}")
                
                response = self.session.post(
                    url_with_slash,
                    data=credentials,  # Use form-encoded data
                    verify=False,
                    allow_redirects=False,
                    timeout=10
                )
                print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                self.authenticated = True
                print("✓ Successfully connected to Traccar server")
                return True
            else:
                print(f"✗ Connection failed: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"✗ Connection error: {e}")
            return False
    
    def get_devices(self) -> List[Dict]:
        """Fetch all devices from Traccar.
        
        Returns:
            List of device dictionaries
        """
        try:
            response = self.session.get(f"{self.server_url}/api/devices")
            response.raise_for_status()
            self.devices = response.json()
            return self.devices
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch devices: {e}")
    
    def get_positions(self, device_id: int, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Fetch positions for a device within a time range.
        
        Args:
            device_id: Device ID
            start_time: Start time for data extraction
            end_time: End time for data extraction
            
        Returns:
            List of position dictionaries
        """
        try:
            params = {
                'deviceId': device_id,
                'from': start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                'to': end_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            }
            
            response = self.session.get(f"{self.server_url}/api/positions", params=params)
            response.raise_for_status()
            positions = response.json()
            return positions
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch positions: {e}")


class DataExporter:
    """Export position data to various GPS formats."""
    
    @staticmethod
    def to_gpx(positions: List[Dict], device_name: str) -> str:
        """Export positions to GPX format.
        
        Args:
            positions: List of position dictionaries
            device_name: Name of the device
            
        Returns:
            GPX XML string
        """
        gpx = ET.Element('gpx', {
            'version': '1.1',
            'creator': 'Traccar Exporter',
            'xmlns': 'http://www.topografix.com/GPX/1/1',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': 'http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd'
        })
        
        metadata = ET.SubElement(gpx, 'metadata')
        ET.SubElement(metadata, 'name').text = f'{device_name} Track'
        ET.SubElement(metadata, 'time').text = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        
        trk = ET.SubElement(gpx, 'trk')
        ET.SubElement(trk, 'name').text = device_name
        trkseg = ET.SubElement(trk, 'trkseg')
        
        for pos in tqdm(positions, desc="Converting to GPX", unit="point"):
            trkpt = ET.SubElement(trkseg, 'trkpt', {
                'lat': str(pos.get('latitude', 0)),
                'lon': str(pos.get('longitude', 0))
            })
            
            if pos.get('altitude'):
                ET.SubElement(trkpt, 'ele').text = str(pos['altitude'])
            
            if pos.get('fixTime'):
                ET.SubElement(trkpt, 'time').text = pos['fixTime']
            
            if pos.get('speed'):
                ET.SubElement(trkpt, 'speed').text = str(pos['speed'])
            
            if pos.get('course'):
                ET.SubElement(trkpt, 'course').text = str(pos['course'])
        
        xml_str = ET.tostring(gpx, encoding='unicode')
        dom = minidom.parseString(xml_str)
        return dom.toprettyxml(indent='  ')
    
    @staticmethod
    def to_kml(positions: List[Dict], device_name: str) -> str:
        """Export positions to KML format.
        
        Args:
            positions: List of position dictionaries
            device_name: Name of the device
            
        Returns:
            KML XML string
        """
        kml = ET.Element('kml', {
            'xmlns': 'http://www.opengis.net/kml/2.2'
        })
        
        document = ET.SubElement(kml, 'Document')
        ET.SubElement(document, 'name').text = f'{device_name} Track'
        
        # Define styles
        style = ET.SubElement(document, 'Style', {'id': 'trackStyle'})
        line_style = ET.SubElement(style, 'LineStyle')
        ET.SubElement(line_style, 'color').text = 'ff0000ff'
        ET.SubElement(line_style, 'width').text = '3'
        
        placemark = ET.SubElement(document, 'Placemark')
        ET.SubElement(placemark, 'name').text = device_name
        ET.SubElement(placemark, 'styleUrl').text = '#trackStyle'
        
        linestring = ET.SubElement(placemark, 'LineString')
        ET.SubElement(linestring, 'tessellate').text = '1'
        ET.SubElement(linestring, 'altitudeMode').text = 'clampToGround'
        
        coordinates = []
        for pos in tqdm(positions, desc="Converting to KML", unit="point"):
            lon = pos.get('longitude', 0)
            lat = pos.get('latitude', 0)
            alt = pos.get('altitude', 0)
            coordinates.append(f'{lon},{lat},{alt}')
        
        ET.SubElement(linestring, 'coordinates').text = '\n' + '\n'.join(coordinates) + '\n'
        
        # Add waypoints
        for i, pos in enumerate(positions):
            if i % max(1, len(positions) // 20) == 0:  # Add waypoints at intervals
                placemark_pt = ET.SubElement(document, 'Placemark')
                ET.SubElement(placemark_pt, 'name').text = f'Point {i+1}'
                
                if pos.get('fixTime'):
                    timestamp = ET.SubElement(placemark_pt, 'TimeStamp')
                    ET.SubElement(timestamp, 'when').text = pos['fixTime']
                
                point = ET.SubElement(placemark_pt, 'Point')
                lon = pos.get('longitude', 0)
                lat = pos.get('latitude', 0)
                alt = pos.get('altitude', 0)
                ET.SubElement(point, 'coordinates').text = f'{lon},{lat},{alt}'
        
        xml_str = ET.tostring(kml, encoding='unicode')
        dom = minidom.parseString(xml_str)
        return dom.toprettyxml(indent='  ')
    
    @staticmethod
    def to_geojson(positions: List[Dict], device_name: str) -> str:
        """Export positions to GeoJSON format.
        
        Args:
            positions: List of position dictionaries
            device_name: Name of the device
            
        Returns:
            GeoJSON string
        """
        features = []
        
        for pos in tqdm(positions, desc="Converting to GeoJSON", unit="point"):
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [
                        pos.get('longitude', 0),
                        pos.get('latitude', 0),
                        pos.get('altitude', 0)
                    ]
                },
                'properties': {
                    'deviceName': device_name,
                    'time': pos.get('fixTime', ''),
                    'speed': pos.get('speed', 0),
                    'course': pos.get('course', 0),
                    'accuracy': pos.get('accuracy', 0)
                }
            }
            features.append(feature)
        
        geojson = {
            'type': 'FeatureCollection',
            'features': features
        }
        
        return json.dumps(geojson, indent=2)
    
    @staticmethod
    def to_csv(positions: List[Dict], device_name: str) -> str:
        """Export positions to CSV format.
        
        Args:
            positions: List of position dictionaries
            device_name: Name of the device
            
        Returns:
            CSV string
        """
        import csv
        from io import StringIO
        
        output = StringIO()
        if not positions:
            return ''
        
        fieldnames = ['time', 'latitude', 'longitude', 'altitude', 'speed', 'course', 'accuracy', 'address']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for pos in tqdm(positions, desc="Converting to CSV", unit="point"):
            writer.writerow({
                'time': pos.get('fixTime', ''),
                'latitude': pos.get('latitude', 0),
                'longitude': pos.get('longitude', 0),
                'altitude': pos.get('altitude', 0),
                'speed': pos.get('speed', 0),
                'course': pos.get('course', 0),
                'accuracy': pos.get('accuracy', 0),
                'address': pos.get('address', '')
            })
        
        return output.getvalue()
    
    @staticmethod
    def to_kmz(positions: List[Dict], device_name: str) -> bytes:
        """Export positions to KMZ format (compressed KML).
        
        Args:
            positions: List of position dictionaries
            device_name: Name of the device
            
        Returns:
            KMZ file as bytes
        """
        kml_content = DataExporter.to_kml(positions, device_name)
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr('doc.kml', kml_content)
        
        return zip_buffer.getvalue()


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points on Earth.
    
    Args:
        lat1, lon1: Coordinates of first point
        lat2, lon2: Coordinates of second point
        
    Returns:
        Distance in kilometers
    """
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Earth radius in kilometers
    r = 6371
    
    return c * r


def filter_ghost_jumps(positions: List[Dict], max_speed_kmh: float = 200.0) -> List[Dict]:
    """Filter out GPS ghost jumps based on unrealistic speeds.
    
    Args:
        positions: List of position dictionaries
        max_speed_kmh: Maximum realistic speed in km/h (default 200 km/h)
        
    Returns:
        Filtered list of positions without ghost jumps
    """
    if len(positions) <= 1:
        return positions
    
    filtered = [positions[0]]  # Always keep the first position
    removed_count = 0
    
    for i in range(1, len(positions)):
        prev_pos = filtered[-1]
        curr_pos = positions[i]
        
        # Get coordinates
        prev_lat = prev_pos.get('latitude')
        prev_lon = prev_pos.get('longitude')
        curr_lat = curr_pos.get('latitude')
        curr_lon = curr_pos.get('longitude')
        
        # Skip if coordinates missing
        if None in [prev_lat, prev_lon, curr_lat, curr_lon]:
            filtered.append(curr_pos)
            continue
        
        # Calculate distance
        distance_km = haversine_distance(prev_lat, prev_lon, curr_lat, curr_lon)
        
        # Calculate time difference
        try:
            prev_time = datetime.fromisoformat(prev_pos.get('fixTime', '').replace('Z', '+00:00'))
            curr_time = datetime.fromisoformat(curr_pos.get('fixTime', '').replace('Z', '+00:00'))
            time_diff_hours = (curr_time - prev_time).total_seconds() / 3600
            
            if time_diff_hours > 0:
                speed_kmh = distance_km / time_diff_hours
                
                # If speed is unrealistic, it's likely a ghost jump
                if speed_kmh <= max_speed_kmh:
                    filtered.append(curr_pos)
                else:
                    removed_count += 1
            else:
                filtered.append(curr_pos)
        except (ValueError, AttributeError):
            # If time parsing fails, keep the point
            filtered.append(curr_pos)
    
    if removed_count > 0:
        print(f"🔧 Filtered out {removed_count} ghost jump(s) (speed > {max_speed_kmh} km/h)")
    
    return filtered


def get_user_input() -> tuple:
    """Get server connection details from user.
    
    Returns:
        Tuple of (server_url, email, password)
    """
    print("\n" + "="*60)
    print("TRACCAR DATA EXPORTER")
    print("="*60 + "\n")
    
    server_url = input("Enter Traccar server URL (e.g., https://demo.traccar.org): ").strip()
    if not server_url:
        server_url = "https://demo.traccar.org"
        print(f"Using default: {server_url}")
    
    email = input("Enter your email: ").strip()
    password = getpass.getpass("Enter your password: ")
    
    return server_url, email, password


def select_device(devices: List[Dict]) -> Optional[Dict]:
    """Let user select a device from the list.
    
    Args:
        devices: List of device dictionaries
        
    Returns:
        Selected device dictionary or None
    """
    if not devices:
        print("No devices found!")
        return None
    
    print("\n" + "="*60)
    print("AVAILABLE DEVICES")
    print("="*60)
    
    for i, device in enumerate(devices, 1):
        status = "Online" if device.get('status') == 'online' else "Offline"
        print(f"{i}. {device.get('name', 'Unknown')} (ID: {device.get('id')}) - {status}")
    
    while True:
        try:
            choice = input(f"\nSelect device (1-{len(devices)}): ").strip()
            index = int(choice) - 1
            if 0 <= index < len(devices):
                return devices[index]
            else:
                print(f"Please enter a number between 1 and {len(devices)}")
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\nOperation cancelled")
            return None


def get_time_range() -> Optional[tuple]:
    """Get time range from user.
    
    Returns:
        Tuple of (start_time, end_time) or None
    """
    print("\n" + "="*60)
    print("TIME RANGE SELECTION")
    print("="*60)
    print("1. Last hour")
    print("2. Last 24 hours")
    print("3. Last 7 days")
    print("4. Last 30 days")
    print("5. Current year")
    print("6. Last year")
    print("7. Specific year")
    print("8. Custom range")
    
    while True:
        try:
            choice = input("\nSelect time range (1-8): ").strip()
            
            end_time = datetime.utcnow()
            
            if choice == '1':
                start_time = end_time - timedelta(hours=1)
                break
            elif choice == '2':
                start_time = end_time - timedelta(days=1)
                break
            elif choice == '3':
                start_time = end_time - timedelta(days=7)
                break
            elif choice == '4':
                start_time = end_time - timedelta(days=30)
                break
            elif choice == '5':
                # Current year from Jan 1 to now
                current_year = end_time.year
                start_time = datetime(current_year, 1, 1, 0, 0, 0)
                break
            elif choice == '6':
                # Last year from Jan 1 to Dec 31
                last_year = end_time.year - 1
                start_time = datetime(last_year, 1, 1, 0, 0, 0)
                end_time = datetime(last_year, 12, 31, 23, 59, 59)
                break
            elif choice == '7':
                # Specific year
                while True:
                    try:
                        year_input = input("Enter year (e.g., 2023, 2024): ").strip()
                        year = int(year_input)
                        if 2000 <= year <= datetime.utcnow().year:
                            start_time = datetime(year, 1, 1, 0, 0, 0)
                            end_time = datetime(year, 12, 31, 23, 59, 59)
                            break
                        else:
                            print(f"Please enter a year between 2000 and {datetime.utcnow().year}")
                    except ValueError:
                        print("Please enter a valid year")
                break
            elif choice == '8':
                print("\nEnter dates in format: YYYY-MM-DD HH:MM")
                start_str = input("Start date and time: ").strip()
                end_str = input("End date and time: ").strip()
                
                try:
                    start_time = datetime.strptime(start_str, '%Y-%m-%d %H:%M')
                    end_time = datetime.strptime(end_str, '%Y-%m-%d %H:%M')
                    
                    if start_time >= end_time:
                        print("Start time must be before end time!")
                        continue
                    break
                except ValueError as e:
                    print(f"Invalid date format: {e}")
                    continue
            else:
                print("Please enter a number between 1 and 8")
        except KeyboardInterrupt:
            print("\nOperation cancelled")
            return None
    
    print(f"\n✓ Selected range: {start_time} to {end_time}")
    return start_time, end_time


def select_format() -> Optional[str]:
    """Let user select output format.
    
    Returns:
        Selected format string or None
    """
    print("\n" + "="*60)
    print("OUTPUT FORMAT SELECTION")
    print("="*60)
    print("1. GPX (GPS Exchange Format)")
    print("2. KML (Keyhole Markup Language)")
    print("3. KMZ (Compressed KML)")
    print("4. GeoJSON")
    print("5. CSV")
    
    formats = {
        '1': 'gpx',
        '2': 'kml',
        '3': 'kmz',
        '4': 'geojson',
        '5': 'csv'
    }
    
    while True:
        try:
            choice = input("\nSelect output format (1-5): ").strip()
            if choice in formats:
                return formats[choice]
            else:
                print("Please enter a number between 1 and 5")
        except KeyboardInterrupt:
            print("\nOperation cancelled")
            return None


def ask_ghost_jump_filter() -> Optional[float]:
    """Ask user if they want to filter ghost jumps.
    
    Returns:
        Max speed in km/h if filtering enabled, None if disabled
    """
    print("\n" + "="*60)
    print("GHOST JUMP FILTERING")
    print("="*60)
    print("Filter out erroneous GPS points with unrealistic speeds?")
    print("(Useful for removing GPS glitches/jumps)")
    print("\n1. Yes - Filter jumps > 200 km/h (recommended for vehicles)")
    print("2. Yes - Filter jumps > 500 km/h (for aircraft/fast vehicles)")
    print("3. Yes - Custom speed threshold")
    print("4. No - Keep all data points")
    
    while True:
        try:
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == '1':
                return 200.0
            elif choice == '2':
                return 500.0
            elif choice == '3':
                while True:
                    try:
                        speed = input("Enter maximum speed in km/h: ").strip()
                        max_speed = float(speed)
                        if max_speed > 0:
                            return max_speed
                        else:
                            print("Speed must be greater than 0")
                    except ValueError:
                        print("Please enter a valid number")
            elif choice == '4':
                return None
            else:
                print("Please enter a number between 1 and 4")
        except KeyboardInterrupt:
            print("\nOperation cancelled")
            return None


def main():
    """Main function to run the exporter."""
    try:
        # Get user input
        server_url, email, password = get_user_input()
        
        # Connect to Traccar
        print("\nConnecting to Traccar server...")
        exporter = TraccarExporter(server_url, email, password)
        
        if not exporter.test_connection():
            print("\nFailed to connect to Traccar server. Please check your credentials.")
            sys.exit(1)
        
        # Get devices
        print("\nFetching devices...")
        devices = exporter.get_devices()
        device = select_device(devices)
        
        if not device:
            print("\nNo device selected.")
            sys.exit(1)
        
        device_name = device.get('name', 'Unknown')
        device_id = device.get('id')
        print(f"\n✓ Selected device: {device_name}")
        
        # Get time range
        time_range = get_time_range()
        if not time_range:
            print("\nNo time range selected.")
            sys.exit(1)
        
        start_time, end_time = time_range
        
        # Get output format
        output_format = select_format()
        if not output_format:
            print("\nNo format selected.")
            sys.exit(1)
        
        print(f"\n✓ Selected format: {output_format.upper()}")
        
        # Fetch positions
        print(f"\nFetching position data from {start_time} to {end_time}...")
        positions = exporter.get_positions(device_id, start_time, end_time)
        
        if not positions:
            print("\n⚠ No position data found for the selected time range.")
            sys.exit(0)
        
        print(f"✓ Retrieved {len(positions)} position records")
        
        # Ask about ghost jump filtering
        max_speed = ask_ghost_jump_filter()
        if max_speed is not None:
            print(f"\n🔧 Applying ghost jump filter (max speed: {max_speed} km/h)...")
            positions = filter_ghost_jumps(positions, max_speed)
            print(f"✓ {len(positions)} position records after filtering")
        
        # Export data
        print(f"\nExporting data to {output_format.upper()} format...")
        
        filename = f"{device_name}_{start_time.strftime('%Y%m%d')}_{end_time.strftime('%Y%m%d')}.{output_format}"
        
        if output_format == 'gpx':
            content = DataExporter.to_gpx(positions, device_name)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
        elif output_format == 'kml':
            content = DataExporter.to_kml(positions, device_name)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
        elif output_format == 'kmz':
            content = DataExporter.to_kmz(positions, device_name)
            with open(filename, 'wb') as f:
                f.write(content)
        elif output_format == 'geojson':
            content = DataExporter.to_geojson(positions, device_name)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
        elif output_format == 'csv':
            content = DataExporter.to_csv(positions, device_name)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print(f"\n{'='*60}")
        print(f"✓ SUCCESS!")
        print(f"{'='*60}")
        print(f"File saved: {filename}")
        print(f"Records exported: {len(positions)}")
        print(f"{'='*60}\n")
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
