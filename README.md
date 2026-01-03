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
- 💾 Optional saved credentials for faster reruns
- 📡 GPS accuracy filtering - removes points with poor satellite fix quality
- 🧹 Drift noise filtering - removes low-speed jitter during GPS fix acquisition
- 🪶 Small-jitter filtering - removes tiny stop/start wiggles near the last point
- 🎯 Stationary point removal - eliminates noise from stationary or barely moving devices
- ⏱️ Time interval filtering - reduces data density by enforcing minimum time gaps
- 🎯 Trajectory outlier detection - removes 20-100m jumps that don't match the path
- ⚡ Quick presets - Ultra Clean, Clean, or Light filtering modes for instant setup

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
git clone https://github.com/Prinsessen/Traccar-Data-Exporter.git
cd Traccar-Data-Exporter
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
	- If credentials are saved locally, you can reuse them or delete/re-enter
2. **Device Selection** - Choose which device to export data from
3. **Time Range** - Select the time period for data extraction
4. **Output Format** - Choose your desired output format
5. **Filter Preset** - Choose quick preset or configure filters manually:
   - **Ultra Clean** - Maximum noise removal (20m accuracy, 30m outliers, 10m stationary)
   - **Clean (Balanced)** - Good for most cases (30m accuracy, 50m outliers, 5m stationary)
   - **Light** - Minimal filtering (50m accuracy, 200 km/h jumps only)
   - **Custom** - Configure each filter individually
   - **No filtering** - Keep all data

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

✓ Selected format: GPX

Fetching position data from 2024-01-01 00:00:00 to 2024-12-31 23:59:59...
✓ Retrieved 1523 position records

FILTER PRESET
============================================================
Choose a filtering preset or configure manually:

1. Ultra Clean (Aggressive) - Maximum noise removal for very noisy data
   • GPS Accuracy: 20m | Ghost Jumps: 100 km/h
   • Trajectory Outliers: 30m | Stationary: 10m | Time: 15s

2. Clean (Balanced) - Good balance for most use cases
   • GPS Accuracy: 30m | Ghost Jumps: 150 km/h
   • Trajectory Outliers: 50m | Stationary: 5m | Time: 10s

3. Light - Minimal filtering, keeps most data
   • GPS Accuracy: 50m | Ghost Jumps: 200 km/h
   • No trajectory/stationary/time filtering

4. Custom - Configure each filter individually

5. No filtering - Keep all data (not recommended)

Select option (1-5): 2

⚖️ Applying CLEAN preset (balanced filtering)...
✓ 1511 records after GPS accuracy filter (30m)
✓ 1508 records after ghost jump filter (150 km/h)
✓ 1498 records after trajectory outlier filter (50m)
✓ 1492 records after stationary removal (5m)
✓ 1487 records after time interval filter (10s)

Exporting data to GPX format...
Converting to GPX: 100%|██████████| 1487/1487 [00:02<00:00, 612.45point/s]

============================================================
✓ SUCCESS!
============================================================
File saved: Vehicle_1_20240101_20241231.gpx
Records exported: 1487
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

## GPS Accuracy Filtering

Many GPS receivers report an "accuracy" value representing the estimated error radius in meters. Points with high accuracy values indicate poor satellite visibility, weak signal, or unreliable positioning - often the root cause of jitter and noise.

**How it works:**
1. Checks the `accuracy` field reported by the GPS receiver
2. Removes points where accuracy exceeds your threshold
3. Keeps points without accuracy data (assumes valid)
4. Always retains at least one point even if all are filtered

**Recommended thresholds:**
- **50m** - Good balance for most use cases (recommended)
- **30m** - Stricter filtering for cleaner tracks
- **20m** - Very strict, best for areas with good GPS coverage
- **Custom** - Set your own threshold based on requirements
- **Disabled** - Keep all points regardless of accuracy

**Why filter by accuracy?** Poor GPS fixes (accuracy > 50m) often indicate:
- Weak satellite signal (urban canyons, indoors, tunnels)
- Cold start or GPS reacquisition
- Device hardware limitations
- Atmospheric interference

Filtering these points removes the primary source of jitter and noise in your tracks.

## Quick Filter Presets ⚡

For faster setup, the script offers three pre-configured filter combinations:

### Ultra Clean (Aggressive)
**Best for very noisy GPS data with frequent jumps**
- GPS Accuracy: 20m
- Ghost Jumps: 100 km/h
- Trajectory Outliers: 30m
- Stationary Points: 10m minimum movement
- Time Interval: 15 seconds

**Use when:** You have extremely noisy data and need maximum cleanup, even if it means losing some legitimate points.

### Clean (Balanced) ✅ Recommended
**Best for most use cases**
- GPS Accuracy: 30m
- Ghost Jumps: 150 km/h
- Trajectory Outliers: 50m
- Stationary Points: 5m minimum movement
- Time Interval: 10 seconds

**Use when:** You want clean tracks without being too aggressive. Good default for typical GPS tracking.

### Light
**Best for high-quality GPS data**
- GPS Accuracy: 50m
- Ghost Jumps: 200 km/h
- No trajectory/stationary/time filtering

**Use when:** Your GPS data is already fairly clean and you just want to remove obvious glitches.

## Trajectory Outlier Detection

This powerful filter detects and removes GPS points that deviate significantly from the expected path - perfect for catching those 20-100m jumps that don't match your actual movement.

**How it works:**
1. Uses a sliding window to analyze the trajectory
2. Calculates the expected position based on neighboring points
3. Removes points that deviate too far from the expected path
4. Preserves the overall track shape while removing outliers

**Recommended thresholds:**
- **30m** - Aggressive, recommended for very noisy data
- **50m** - Balanced, good for most cases
- **75m** - Light filtering for cleaner data
- **Custom** - Set your own deviation threshold
- **Disabled** - Keep all points

**Use case:** If your track shows you walking straight but one point jumps 50m to the side (while your speed and direction suggest you kept walking), that outlier is removed while the smooth path is preserved.

**Why it works:** Unlike simple distance filters, this looks at trajectory consistency - a 50m movement is normal if you're actually moving that direction, but abnormal if it's perpendicular to your path.

## Drift Noise Filtering

The script can remove low-speed GPS drift that happens while a device is stationary and acquiring a fix. It drops points where both:
- Speed is below a small threshold (e.g., 8–10 km/h)
- Displacement from the previous kept point is tiny (e.g., 30–50 m)

**Presets:**
- 10 km/h & 50 m (recommended default)
- 8 km/h & 30 m (stricter)
- Custom thresholds
- Disabled

**Example:** At startup, GPS may report a few wandering points within 30 m while stopped; these are removed so tracks start cleanly from the true location.

## Small-Jitter Filtering

Targets tiny stop/start wiggles near the last known point (often when pulling away or coming to a stop). It drops points where:
- Speed is below a modest threshold (e.g., 12–15 km/h)
- Displacement from the last kept point is tiny (e.g., 10–15 m)

**Presets:**
- 15 km/h & 15 m (recommended)
- 12 km/h & 10 m (stricter)
- Custom thresholds
- Disabled

**Tip:** Use this after drift filtering to keep starts/stops clean without harming normal low-speed movement.

## Stationary Point Removal

This powerful filter removes consecutive points where the device hasn't moved significantly, which is especially effective at eliminating GPS noise when stationary or nearly stationary.

**How it works:**
1. Compares each point to the last kept point
2. Only keeps points that have moved at least the minimum distance
3. Aggressively removes jitter/noise from stationary periods

**Recommended thresholds:**
- **5m** - Recommended for cleaner tracks, removes most stationary noise
- **10m** - Moderate filtering, keeps more data
- **3m** - Very aggressive, best for high-precision tracks
- **Custom** - Set your own minimum movement distance
- **Disabled** - Keep all points

**Use case:** If your GPS reports 20 points within a 3-meter radius while parked, this filter keeps only the first point, eliminating the noise cloud.

## Time Interval Filtering

Enforces a minimum time gap between consecutive points, reducing data density and file size while maintaining track shape. Particularly useful for high-frequency GPS loggers.

**How it works:**
1. Keeps the first point always
2. For subsequent points, only keeps if enough time has passed since the last kept point
3. Temporal downsampling without losing track quality

**Recommended intervals:**
- **10 seconds** - Good balance between detail and noise reduction
- **30 seconds** - Aggressive filtering for long trips, smaller files
- **5 seconds** - Light filtering for detailed tracks
- **Custom** - Set your own interval
- **Disabled** - Keep all points

**Use case:** If your device logs every second but you only need one point every 10 seconds, this drastically reduces noise and file size while preserving the overall track shape.

**Tip:** Combine with stationary point removal for maximum noise reduction - first remove stationary points, then apply time interval filtering to reduce data density during movement.

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
- By default credentials are not stored; they are only used for the current session
- Optional local credential storage uses `~/.traccar_exporter/credentials.json` with file mode 600 (user-only)

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

### v1.9.0 (2026-01-03) 🪶 Small-Jitter Filtering
- **Added:** Tiny stop/start jitter filter (distance & speed thresholds)
- **Presets:** 15 km/h & 15 m; 12 km/h & 10 m; custom or disabled
- **Flow:** Runs after drift filtering; reports removed points

### v1.8.0 (2026-01-03) 🧹 Drift Noise Filtering
- **Added:** Low-speed drift filter (distance & speed thresholds) for GPS fix jitter
- **Presets:** 10 km/h & 50 m; 8 km/h & 30 m; custom or disabled
- **Flow:** Prompted after ghost jump filtering, with summary of removed points

### v1.7.0 (2026-01-03) 🔒 Credential Convenience
- **Added:** Optional local credential storage in `~/.traccar_exporter/credentials.json`
- **Added:** Reuse/delete prompts for saved credentials
- **Security:** File permissions set to 600; best-effort warnings on failures

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