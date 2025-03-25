# LEHD Aggregation Level Explorer - Documentation

## Overview
The LEHD Aggregation Level Explorer is a web-based application designed to help users explore and understand the aggregation levels in the Census Bureau's LEHD (Longitudinal Employer-Household Dynamics) program. This tool allows you to filter, search, and visualize different aggregation levels based on various characteristics such as worker demographics, firm attributes, geographic levels, and industry classifications.

## Features
- **Interactive Filtering**: Filter aggregation levels by data type, worker characteristics, firm characteristics, geographic level, and industry level
- **Search Functionality**: Search across all fields to quickly find specific aggregation levels
- **Detailed Visualization**: View comprehensive details about each aggregation level, including which characteristics are included
- **Responsive Design**: Works on desktop and mobile devices

## Installation

### Prerequisites
- Python 3.6 or higher
- Flask
- Pandas
- Internet connection (to access the CSV file)

### Setup Instructions
1. Clone or download the application files to your local machine
2. Install the required dependencies:
   ```
   pip install flask pandas
   ```
3. Ensure the CSV file is downloaded:
   ```
   mkdir -p lehd_data
   cd lehd_data
   wget https://lehd.ces.census.gov/data/schema/j2j_latest/label_agg_level.csv
   ```
4. Run the application:
   ```
   python app.py
   ```
5. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

## Using the Application

### Filter Panel
The left side of the application contains filters to narrow down the aggregation levels:

1. **Data Type Filters**:
   - J2J (Job-to-Job): Job-to-Job Flows
   - J2JR (Job-to-Job Rates): Job-to-Job Flow Rates
   - J2JOD (Origin-Destination): Origin-Destination Job-to-Job Flows
   - QWI (Quarterly Workforce Indicators): Quarterly Workforce Indicators

2. **Worker Characteristics**: Filter by worker demographic attributes like Sex, Age, Race, Ethnicity, or Education

3. **Firm Characteristics**: Filter by firm attributes like Firm Age, Firm Size, or NAICS Sector

4. **Geographic Level**:
   - N: National level
   - S: State level
   - B: Metro/Micropolitan level

5. **Industry Level**:
   - A: All Industries
   - S: NAICS Sectors
   - 3: NAICS Subsectors

6. **Search**: Enter text to search across all fields

7. **Reset Filters**: Reset all filters to their default values

### Results Panel
The main panel displays a table of aggregation levels matching your filter criteria:

- Each row represents a unique aggregation level
- Columns show the key attributes of each level
- Checkmarks (✓) indicate which data types are available for each level
- Click on any row to view detailed information about that aggregation level

### Details Panel
When you select an aggregation level, the details panel shows:

- Comprehensive information about the selected aggregation level
- Worker characteristics included in this level
- Firm characteristics included in this level
- Geographic and industry detail
- Available data types
- An explanation of what this aggregation level represents

## Understanding LEHD Aggregation Levels

### Key Concepts

1. **Aggregation Level**: A specific way to group and analyze LEHD data, represented by a numeric code

2. **Worker Characteristics**: Demographic attributes of workers, such as:
   - Sex
   - Age
   - Race
   - Ethnicity
   - Education

3. **Firm Characteristics**: Attributes of firms/employers, such as:
   - Firm Age
   - Firm Size
   - Industry (NAICS codes)

4. **Geographic Levels**:
   - N (National): Country-wide data
   - S (State): State-level data
   - B (Metro/Micropolitan): Metropolitan and Micropolitan Statistical Area data

5. **Industry Levels**:
   - A (All Industries): Data aggregated across all industries
   - S (NAICS Sectors): Data broken down by NAICS Sector (2-digit)
   - 3 (NAICS Subsectors): Data broken down by NAICS Subsector (3-digit)

6. **Data Types**:
   - J2J: Job-to-Job Flows, measuring worker movements between jobs
   - J2JR: Job-to-Job Flow Rates, providing rates of worker movements
   - J2JOD: Origin-Destination Job-to-Job Flows, tracking where workers move from and to
   - QWI: Quarterly Workforce Indicators, providing employment statistics

## Troubleshooting

### Common Issues

1. **Application doesn't start**:
   - Ensure Python and required packages are installed
   - Check if port 5000 is already in use by another application
   - Verify the CSV file has been downloaded correctly

2. **No data appears**:
   - Check if the CSV file path in app.py is correct
   - Ensure the CSV file has been downloaded successfully
   - Try resetting all filters

3. **Slow performance**:
   - The application processes a large CSV file with many rows
   - More specific filters will improve performance

## Technical Details

### File Structure
- `app.py`: Flask application backend
- `templates/index.html`: HTML template for the web interface
- `static/style.css`: CSS styles for the application
- `static/script.js`: JavaScript for interactive functionality
- `lehd_data/label_agg_level.csv`: Data file containing aggregation levels

### Data Processing
The application uses pandas to process the CSV data and applies filters based on user selections. The filtered data is then converted to JSON and sent to the frontend for display.

### Customization
You can customize the application by:
- Modifying the CSS in `static/style.css` to change the appearance
- Updating the HTML in `templates/index.html` to alter the layout
- Enhancing the JavaScript in `static/script.js` to add new features
- Extending the Flask backend in `app.py` to add new functionality

## Conclusion
The LEHD Aggregation Level Explorer provides an intuitive interface for understanding and selecting the appropriate aggregation levels for LEHD data analysis. By using this tool, you can quickly identify which aggregation levels contain the specific characteristics and data types you need for your analysis.
