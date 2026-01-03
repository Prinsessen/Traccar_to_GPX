# Traccar Data Exporter

A Python script to export position data from Traccar GPS tracking platform to various popular GPS file formats.

## Author

**Prinsessen**  
GitHub: [@Prinsessen](https://github.com/Prinsessen)

## Features

- 🔐 Secure authentication with Traccar server
- 📊 Export to multiple formats: GPX, KML, KMZ, GeoJSON, CSV
- ⏱️ Flexible time range selection (last hour, 24h, 7d, 30d, or custom)
- 📈 Progress bars for data processing
- ⚠️ Comprehensive error handling
- 🎯 Interactive device selection
- 🌐 Compatible with latest Traccar API

## Supported Output Formats

1. **GPX** - GPS Exchange Format (XML-based, widely supported)
2. **KML** - Keyhole Markup Language (Google Earth compatible)
3. **KMZ** - Compressed KML format
4. **GeoJSON** - JSON-based geographic data format
5. **CSV** - Comma-separated values (spreadsheet compatible)

## Requirements

- Python 3.7 or higher
- Traccar server access (credentials required)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/Prinsessen/Traccar_to_GPX.git
cd Traccar_to_GPX
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the script:
```bash
python traccar_exporter.py
```

The script will guide you through:
1. **Server Connection** - Enter your Traccar server URL and credentials
2. **Device Selection** - Choose which device to export data from
3. **Time Range** - Select the time period for data extraction
4. **Output Format** - Choose your desired output format

### Example

```
TRACCAR DATA EXPORTER
============================================================

Enter Traccar server URL (e.g., https://demo.traccar.org): https://your-server.com
Enter your email: user@example.com
Enter your password: ********

✓ Successfully connected to Traccar server

AVAILABLE DEVICES
============================================================
1. Vehicle 1 (ID: 1) - Online
2. Vehicle 2 (ID: 2) - Offline

Select device (1-2): 1

TIME RANGE SELECTION
============================================================
1. Last hour
2. Last 24 hours
3. Last 7 days
4. Last 30 days
5. Custom range

Select time range (1-5): 2

OUTPUT FORMAT SELECTION
============================================================
1. GPX (GPS Exchange Format)
2. KML (Keyhole Markup Language)
3. KMZ (Compressed KML)
4. GeoJSON
5. CSV

Select output format (1-5): 1

✓ Retrieved 1523 position records
Converting to GPX: 100%|██████████| 1523/1523 [00:02<00:00, 612.45point/s]

============================================================
✓ SUCCESS!
============================================================
File saved: Vehicle_1_20260102_20260103.gpx
Records exported: 1523
============================================================
```

## Output File Naming

Files are automatically named using the pattern:
```
{DeviceName}_{StartDate}_{EndDate}.{extension}
```

Example: `Vehicle_1_20260102_20260103.gpx`

## Error Handling

The script includes comprehensive error handling for:
- Network connection issues
- Invalid credentials
- No data available for selected time range
- API request failures
- File write errors
- User input validation

## Traccar API Compatibility

This script is designed to work with Traccar API (v5.x and above). It uses the following endpoints:
- `/api/session` - Authentication (POST with form-encoded credentials)
- `/api/devices` - Device list
- `/api/positions` - Position data

**Authentication Method:** The script uses POST requests with form-encoded credentials (not JSON) for compatibility with Traccar's authentication handler.

## Security Notes

- Never commit your credentials to version control
- Use environment variables for production deployments
- Consider using Traccar API tokens for enhanced security
- The script does not store credentials; they are only used for the current session

## Troubleshooting

### Connection Issues

**Problem:** `HTTP 415 Unsupported Media Type` error

**Solution:** The script now correctly sends credentials as form-encoded data. Ensure:
1. Your server URL is correct: `https://your-server.com` (without trailing slash)
2. Your email and password are correct
3. Your Traccar server is accessible from your network

**Problem:** `HTTP 404 Not Found` error

**Solution:** The script tries both `/api/session/` and `/api/session` endpoints automatically.

**Example URLs:**
- ✓ Correct: `https://traccar.example.com`
- ✗ Incorrect: `https://traccar.example.com/`

### Common Issues

1. **Invalid Credentials** - Double-check your email and password are correct for your Traccar account
2. **Server Unreachable** - Verify the server URL and network connectivity
3. **SSL Certificate Warnings** - The script temporarily disables SSL verification for troubleshooting. For production, enable it in the code
4. **No Devices Found** - Ensure you have at least one device configured in Traccar
5. **No Position Data** - The selected time range may not contain any tracking data

## Changelog

### v1.3.0 (2026-01-03)
- **Fixed:** Authentication now uses form-encoded credentials instead of JSON
- **Improved:** Better endpoint discovery with fallback logic
- **Added:** Debug output to show connection attempts
- **Fixed:** HTTP 415 error by using correct content-type for credentials

### v1.2.0
- **Fixed:** Authentication method changed from HTTP Basic Auth to POST with credentials

### v1.1.0
- **Fixed:** API endpoint URL for session authentication

### v1.0.0
- Initial release with GPX, KML, KMZ, GeoJSON, and CSV export support

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues related to:
- **This script**: Open an issue on GitHub
- **Traccar server**: Visit [Traccar documentation](https://www.traccar.org/documentation/)

## Acknowledgments

- Built for [Traccar GPS tracking platform](https://www.traccar.org/)
- Uses standard GPS data formats for maximum compatibility