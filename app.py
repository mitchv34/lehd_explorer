from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
import os
import re
import time


app = Flask(__name__)

# Load the CSV data
# Define the file path
file_path = './lehd_data/label_agg_level.csv'

# Check if file exists and its age
need_download = False
if not os.path.exists(file_path):
    need_download = True
else:
    # Check if file is older than 1 week
    file_age = time.time() - os.path.getmtime(file_path)
    if file_age > 7 * 24 * 60 * 60:  # 7 days in seconds
        need_download = True

if need_download:
    url = "https://lehd.ces.census.gov/data/schema/j2j_latest/label_agg_level.csv"
    df = pd.read_csv(url)
    # Check if the folder exists, if not create it
    os.makedirs('./lehd_data', exist_ok=True)
    # Save the file to the local folder
    df.to_csv(file_path, index=False)

# Load the CSV data
df = pd.read_csv(file_path)

# Extract components from character columns
def extract_components(df):
    # Worker characteristics components
    worker_components = set()
    for val in df['worker_char'].dropna().unique():
        components = val.split(' * ')
        for comp in components:
            worker_components.add(comp)
    
    # Firm characteristics components
    firm_components = set()
    for val in df['firm_char'].dropna().unique():
        components = val.split(' * ')
        for comp in components:
            firm_components.add(comp)
    
    # Firm origin characteristics components
    firm_orig_components = set()
    for val in df['firm_orig_char'].dropna().unique():
        # Remove 'Origin [' prefix and ']' suffix
        val = val.replace('Origin [', '').replace(']', '')
        components = val.split(' * ')
        for comp in components:
            firm_orig_components.add(comp)
    
    return {
        'worker_components': sorted(list(worker_components)),
        'firm_components': sorted(list(set([c.replace('Destination [', '').replace(']', '') for c in firm_components]))),
        'firm_orig_components': sorted(list(firm_orig_components))
    }

@app.route('/')
def index():
    # Get unique values for dropdowns
    geo_levels = ['All'] + sorted(df['geo_level'].unique().tolist())
    ind_levels = ['All'] + sorted(df['ind_level'].unique().tolist())
    
    # Get components for checkbox filtering
    components = extract_components(df)
    
    # Create geo_level and ind_level mappings for display
    geo_mapping = {'N': 'National', 'S': 'State', 'B': 'Metro/Micropolitan'}
    ind_mapping = {'A': 'All Industries', 'S': 'NAICS Sectors', '3': 'NAICS Subsectors'}
    
    return render_template(
                        'index.html', 
                        geo_levels=geo_levels,
                        ind_levels=ind_levels,
                        geo_mapping=geo_mapping,
                        ind_mapping=ind_mapping,
                        worker_components=components['worker_components'],
                        firm_components=components['firm_components'],
                        firm_orig_components=components['firm_orig_components']
                    )

@app.route('/get_data', methods=['POST'])
def get_data():
    # Get filter values from request
    filters = request.json
    
    # Apply filters
    filtered_df = df.copy()
    
    # Data type filters
    data_type_conditions = []
    if filters.get('j2j', False):
        data_type_conditions.append(filtered_df['j2j'] == 1)
    if filters.get('j2jr', False):
        data_type_conditions.append(filtered_df['j2jr'] == 1)
    if filters.get('j2jod', False):
        data_type_conditions.append(filtered_df['j2jod'] == 1)
    if filters.get('qwi', False):
        data_type_conditions.append(filtered_df['qwi'] == 1)
    
    if data_type_conditions:
        combined_condition = data_type_conditions[0]
        for condition in data_type_conditions[1:]:
            combined_condition = combined_condition | condition
        filtered_df = filtered_df[combined_condition]
    
    # Component-based filtering
    # Worker characteristics components
    worker_components = filters.get('worker_components', [])
    if worker_components:
        worker_condition = filtered_df['worker_char'].apply(
            lambda x: pd.notna(x) and all(comp in str(x) for comp in worker_components)
        )
        filtered_df = filtered_df[worker_condition]
    
    # Firm characteristics components
    firm_components = filters.get('firm_components', [])
    if firm_components:
        firm_condition = filtered_df['firm_char'].apply(
            lambda x: pd.notna(x) and all(comp in str(x) for comp in firm_components)
        )
        filtered_df = filtered_df[firm_condition]
    
    # Firm origin characteristics components
    firm_orig_components = filters.get('firm_orig_components', [])
    if firm_orig_components:
        firm_orig_condition = filtered_df['firm_orig_char'].apply(
            lambda x: pd.notna(x) and all(comp in str(x) for comp in firm_orig_components)
        )
        filtered_df = filtered_df[firm_orig_condition]
    
    # Geographic level filter
    if filters.get('geo_level') != 'All':
        filtered_df = filtered_df[filtered_df['geo_level'] == filters.get('geo_level')]
    
    # Industry level filter
    if filters.get('ind_level') != 'All':
        filtered_df = filtered_df[filtered_df['ind_level'] == filters.get('ind_level')]
    
    # Search filter
    if filters.get('search'):
        search_term = filters.get('search').lower()
        # Convert all columns to string and check if search term is in any column
        search_condition = filtered_df.astype(str).apply(
            lambda row: row.str.lower().str.contains(search_term).any(), axis=1
        )
        filtered_df = filtered_df[search_condition]
    
    # Convert to list of dictionaries for JSON response
    result = filtered_df.fillna('').to_dict(orient='records')
    
    return jsonify({
        'data': result,
        'count': len(result)
    })

@app.route('/get_details/<int:agg_level>')
def get_details(agg_level):
    # Find the row with the specified agg_level
    row = df[df['agg_level'] == agg_level]
    
    if row.empty:
        return jsonify({'error': 'Aggregation level not found'})
    
    # Convert to dictionary
    row_dict = row.iloc[0].fillna('').to_dict()
    
    # Create a more detailed response with category groupings
    categories = {
        'Worker Characteristics': ['by_sex', 'by_agegrp', 'by_race', 'by_ethnicity', 'by_education'],
        'Firm Characteristics': ['by_firmage', 'by_firmsize', 'by_ownercode'],
        'Geographic Level': ['geo_level'],
        'Industry Level': ['ind_level'],
        'Data Types': ['j2j', 'j2jr', 'j2jod', 'qwi']
    }
    
    # Create a dictionary to store values for each category
    category_values = {}
    for category, columns in categories.items():
        if category == 'Geographic Level':
            geo_mapping = {'N': 'National', 'S': 'State', 'B': 'Metro/Micropolitan'}
            category_values[category] = geo_mapping.get(row_dict['geo_level'], row_dict['geo_level'])
        elif category == 'Industry Level':
            ind_mapping = {'A': 'All Industries', 'S': 'NAICS Sectors', '3': 'NAICS Subsectors'}
            category_values[category] = ind_mapping.get(row_dict['ind_level'], row_dict['ind_level'])
        elif category == 'Data Types':
            data_types = []
            if row_dict['j2j'] == 1:
                data_types.append('J2J (Job-to-Job)')
            if row_dict['j2jr'] == 1:
                data_types.append('J2JR (Job-to-Job Rates)')
            if row_dict['j2jod'] == 1:
                data_types.append('J2JOD (Origin-Destination)')
            if row_dict['qwi'] == 1:
                data_types.append('QWI (Quarterly Workforce Indicators)')
            category_values[category] = data_types if data_types else ['None']
        else:
            # For worker and firm characteristics, check which ones are enabled (1)
            enabled = [col.replace('by_', '').capitalize() for col in columns if row_dict[col] == 1]
            category_values[category] = enabled if enabled else ['None']
    
    # Add the basic info
    basic_info = {
        'agg_level': int(row_dict['agg_level']),
        'worker_char': row_dict['worker_char'],
        'firm_char': row_dict['firm_char'],
        'firm_orig_char': row_dict['firm_orig_char'],
    }
    
    return jsonify({
        'basic_info': basic_info,
        'categories': category_values
    })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    
    app.run(host='0.0.0.0', port=8080, debug=True)
