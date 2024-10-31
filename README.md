# STAAR Data Collection and Processing Tool

This tool automates the collection and processing of STAAR test data from the Texas Research Portal. It uses Selenium WebDriver for web automation and Pandas for data processing.

## Prerequisites

### 1. Python Requirements
- Python 3.7 or higher
- pip (Python package installer)

### 2. Chrome Browser
- Install Google Chrome browser if you haven't already
- Verify your Chrome version:
  1. Open Chrome
  2. Click the three dots in the top-right corner
  3. Go to Help > About Google Chrome
  4. Note your Chrome version number

### 3. ChromeDriver Installation
The ChromeDriver version must match your Chrome browser version. Follow these steps:

1. Visit the [Chrome for Testing Downloads](https://googlechromelabs.github.io/chrome-for-testing/#stable) page

2. Find your Chrome version in the "Stable" section

3. Download the appropriate ChromeDriver:
   - For Windows: Download the `chromedriver-win64.zip`
   - For Mac: Download the `chromedriver-mac-x64.zip` (Intel) or `chromedriver-mac-arm64.zip` (Apple Silicon)
   - For Linux: Download the `chromedriver-linux64.zip`

4. Extract the downloaded zip file

5. Add ChromeDriver to your system PATH:
   - **Windows**:
     1. Copy the extracted `chromedriver.exe` to `C:\Windows\System32`
     OR
     1. Create a folder (e.g., `C:\WebDrivers`)
     2. Copy chromedriver.exe there
     3. Add the folder to your System PATH:
        - Right-click Computer > Properties > Advanced System Settings
        - Click Environment Variables
        - Under System Variables, find PATH
        - Click Edit > New
        - Add your ChromeDriver folder path
   
   - **Mac/Linux**:
     1. Move the chromedriver to `/usr/local/bin`:
     ```bash
     sudo mv chromedriver /usr/local/bin
     sudo chmod +x /usr/local/bin/chromedriver
     ```

## Configuration

1. Create a CSV file named `my3.csv` with the following columns:
```
District,Program,Report,Administration,Subject,Grade,Version,Cluster
```

2. Fill in the CSV with your desired queries. Example row:
```
El Paso ISD,B,STAAR 3-8,Group Summary: Performance Levels & Reporting Categories,March 2021;April 2021,Mathematics;Reading,3;4;5
```

Note: Use semicolons (;) to separate multiple values within a single field.

## Usage

1. Ensure your ChromeDriver is properly installed and in your PATH

2. Run the main script:
```bash
python Script.py
```

The script will:
1. Read queries from `my3.csv`
2. Download reports from the Texas Research Portal
3. Process and clean the downloaded data
4. Save processed files in the `downloads/clean` directory

## Project Structure

```
project/
│
├── main.py              # Main script containing web automation logic
├── Processing.py        # Data processing and cleaning script
├── my3.csv             # Input file containing queries
├── requirements.txt     # Python dependencies
│
├── downloads/          # Raw downloaded files
│   └── clean/         # Processed output files
│
└── README.md           # This documentation
```

## Troubleshooting

### Common Issues:

1. **ChromeDriver Version Mismatch**
   - Error: `SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version XX`
   - Solution: Download the matching ChromeDriver version for your Chrome browser

2. **ChromeDriver Not Found**
   - Error: `WebDriverException: Message: 'chromedriver' executable needs to be in PATH`
   - Solution: Verify ChromeDriver is properly installed and added to your system PATH

3. **Download Directory Issues**
   - Error: Permission denied when creating downloads directory
   - Solution: Ensure you have write permissions in the script's directory

## License

Copyright © 2024 Guillermo Jimenez
