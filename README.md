# Planet-CLI-Tool
This script outlines a CLI tool that utilizes Planet's Data API and Orders API to search and download ortho-imagery, as part of an interview exercise. It is written in Python and designed to be executable in the command line with a few simple arguments.

Requirements:
- Python version 3.8 or later.
- Python packages: requests (as well as standard Python libraries like os, time, json, and argparse). 
- A GeoJSON of the area of interset (AOI). A simple way to retrieve one would be a tool like this: https://geojson.io/#map=2/0/20\

Steps:
- Excecute the script and enter the arguements including:
- A valid API key from Planet.
- Start time in ISO 8601 format.
- End time in ISO 8601 format.
- Path to area of interest (AOI) GeoJSON.

Example:
python planet_cli.py
  --api-key XXXXXXXXXX 
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-31T23:59:59Z \ 
  --geojson path/to/AOI/aoi.geojson \

Considerations and next steps:

One constraint of the Data API is that it returns a maximum result count of 250 per page, and therefor would require pagination to be able to return the remainder of results over 250. Another constraint would be rate limiting, which is specific to each API. For this constraint, one could code in an exponential backoff to slow down the request volume.
