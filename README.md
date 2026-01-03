# Traccar Data Exporter

A Python script to export position data from Traccar GPS tracking platform to various popular GPS file formats.

## Author

**Prinsessen**  
GitHub: [@Prinsessen](https://github.com/Prinsessen)

## Features

- 🔐 Secure authentication with Traccar server
- 📊 Export to multiple formats: GPX, KML, KMZ, GeoJSON, CSV
- ⏱️ Flexible time range selection (last hour, 24h, 7d, 30d, current year, last year, specific year, or custom)
- 📈 Progress bars for data processing
- ⚠️ Comprehensive error handling
- 🎯 Interactive device selection
- 🌐 Compatible with latest Traccar API
- 🔧 Ghost jump filtering - removes GPS glitches and unrealistic position jumps

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
5. **Ghost Jump Filtering** - Optional: Filter out GPS glitches and unrealistic position jumps

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
5. Current year
6. Last year
7. Specific year
8. Custom range

Select time range (1-8): 7
Enter year (e.g., 2023, 2024): 2024

OUTPUT FORMAT SELECTION
============================================================
1. GPX (GPS Exchange Format)
2. KML (Keyhole Markup Language)
3. KMZ (Compressed KML)
4. GeoJSON
5. CSV

Select output format (1-5): 1

GHOST JUMP FILTERING
============================================================
Filter out erroneous GPS points with unrealistic speeds?
(Useful for removing GPS glitches/jumps)

1. Yes - Filter jumps > 200 km/h (recommended for vehicles)
2. Yes - Filter jumps > 500 km/h (for aircraft/fast vehicles)
3. Yes - Custom speed threshold
4. No - Keep all data points

Select option (1-4): 1

✓ Retrieved 1523 position records
🔧 Applying ghost jump filter (max speed: 200.0 km/h)...
🔧 Filtered out 3 ghost jump(s) (speed > 200.0 km/h)
✓ 1520 position records after filtering
Converting to GPX: 100%|██████████| 1520/1520 [00:02<00:00, 612.45point/s]

============================================================
✓ SUCCESS!
============================================================
File saved: Vehicle_1_20260102_20260103.gpx
Records exported: 1520
============================================================
```

## Ghost Jump Filtering

The script includes a powerful feature to filter out GPS "ghost jumps" - erroneous data points where the device appears to teleport large distances in unrealistic time frames. This is common with:
- Poor GPS signal
- GPS drift
- Sensor errors
- Data transmission issues

**How it works:**
1. Calculates the speed between consecutive GPS points using the Haversine formula
2. Removes points where the calculated speed exceeds your threshold
3. Keeps the previous valid point and continues from there

**Recommended thresholds:**
- **200 km/h** - Good for cars, trucks, and most vehicles
- **500 km/h** - Suitable for aircraft and high-speed vehicles  
- **Custom** - Set your own threshold based on your tracking needs
- **Disabled** - Keep all data points unfiltered

**Example:** If your device jumps from New York to London in 5 minutes (clearly impossible), that point will be filtered out.

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

This script is designed to work with Traccar API (v5.x and above) and has been **tested and verified working** with production Traccar servers. 

It uses the following endpoints:
- `/api/session` - Authentication (POST with form-encoded credentials)
- `/api/devices` - Device list
- `/api/positions` - Position data

**Authentication Method:** The script uses POST requests with **form-encoded credentials** (`application/x-www-form-urlencoded`), not JSON, for compatibility with Traccar's authentication handler. The script automatically tries both `/api/session` and `/api/session/` endpoints for maximum compatibility.

## Security Notes

- Never commit your credentials to version control
- Use environment variables for production deployments
- Consider using Traccar API tokens for enhanced security
- The script does not store credentials; they are only used for the current session

## Troubleshooting

### Connection Issues

**Problem:** `HTTP 415 Unsupported Media Type` or `HTTP 404 Not Found` error

**Solution:** ✅ This has been fixed! The script now:
1. Sends credentials as form-encoded data (required by Traccar)
2. Automatically tries both `/api/session` and `/api/session/` endpoints
3. Shows detailed connection debugging output

**If you still have connection issues:**
1. Verify your server URL format: `https://your-server.com` (without trailing slash)
2. Double-check your email and password
3. Ensure your Traccar server is accessible from your network
4. Check that you're using the latest version of the script

**Example URLs:**
- ✓ Correct: `https://traccar.example.com` or `https://gps.yourdomain.com`
- ✗ Incorrect: `https://traccar.example.com/`

### Common Issues

1. **Invalid Credentials** - Double-check your email and password are correct for your Traccar account
2. **Server Unreachable** - Verify the server URL and network connectivity
3. **SSL Certificate Warnings** - The script includes debug mode with disabled SSL verification. For production use, you can enable SSL verification in the code
4. **No Devices Found** - Ensure you have at least one device configured in your Traccar account
5. **No Position Data** - The selected time range may not contain any tracking data for the chosen device

### Success Indicators

When the connection works correctly, you'll see:
```
Attempting connection to: https://your-server.com/api/session
Sending credentials: email=your@email.com
Response status: 200
✓ Successfully connected to Traccar server
```

## Changelog

### v1.6.0 (2026-01-03) 📅 Specific Year Selection
- **Added:** "Specific year" option - select any year (2000 onwards) for complete annual export
- **Improved:** More flexible time range options for historical data analysis
- **Example:** Export all 2023 data, or 2024 data with a single selection

### v1.5.0 (2026-01-03) 📅 Time Range Update
- **Added:** "Current year" option - exports all data from January 1st to now
- **Added:** "Last year" option - exports complete previous year (Jan 1 - Dec 31)
- **Improved:** More convenient time range selections for annual data exports

### v1.4.0 (2026-01-03) ✨ New Feature
- **Added:** Ghost jump filtering to remove GPS glitches and unrealistic position jumps
- **Added:** Haversine distance calculation for accurate GPS point spacing
- **Added:** Interactive filtering options (200 km/h, 500 km/h, custom, or disabled)
- **Improved:** Better data quality control with configurable speed thresholds

### v1.3.0 (2026-01-03) ✅ Fully Working
- **Fixed:** Authentication now uses form-encoded credentials instead of JSON (resolves HTTP 415 error)
- **Fixed:** Endpoint fallback logic - tries both `/api/session` and `/api/session/` automatically
- **Improved:** Better endpoint discovery with smart retry logic
- **Added:** Detailed debug output showing connection attempts and responses
- **Added:** Response status logging for better troubleshooting
- **Verified:** Tested and working with production Traccar servers

### v1.2.0
- **Fixed:** Authentication method changed from HTTP Basic Auth to POST with credentials
- **Updated:** Documentation and troubleshooting guide

### v1.1.0
- **Fixed:** API endpoint URL for session authentication
- **Improved:** Better error messages for connection troubleshooting

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