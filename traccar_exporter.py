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
        self.session.auth = (email, password)
        self.devices = []
        
    def test_connection(self) -> bool:
        """Test connection to Traccar server.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.session.get(f"{self.server_url}/api/session")
            if response.status_code == 200:
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
    print("5. Custom range")
    
    while True:
        try:
            choice = input("\nSelect time range (1-5): ").strip()
            
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
                print("Please enter a number between 1 and 5")
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
