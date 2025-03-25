// Global variables
let currentData = [];
let selectedRow = null;

// Document ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the form submission handler
    document.getElementById('filterForm').addEventListener('submit', function(e) {
        e.preventDefault();
        fetchData();
    });
    
    // Initialize the reset button
    document.getElementById('resetBtn').addEventListener('click', resetFilters);
    
    // Load initial data
    fetchData();
});

// Fetch data based on current filters
function fetchData() {
    // Show loading indicator
    document.getElementById('resultsBody').innerHTML = '<tr><td colspan="10"><div class="loading"></div></td></tr>';
    
    // Get form data
    const formData = new FormData(document.getElementById('filterForm'));
    
    // Prepare filters object
    const filters = {
        j2j: formData.get('j2j') === 'on',
        j2jr: formData.get('j2jr') === 'on',
        j2jod: formData.get('j2jod') === 'on',
        qwi: formData.get('qwi') === 'on',
        geo_level: formData.get('geo_level'),
        ind_level: formData.get('ind_level'),
        search: formData.get('search')
    };
    
    // Get component-based filters
    filters.worker_components = [];
    document.querySelectorAll('.worker-component:checked').forEach(cb => {
        filters.worker_components.push(cb.value);
    });
    
    filters.firm_components = [];
    document.querySelectorAll('.firm-component:checked').forEach(cb => {
        filters.firm_components.push(cb.value);
    });
    
    filters.firm_orig_components = [];
    document.querySelectorAll('.firm-orig-component:checked').forEach(cb => {
        filters.firm_orig_components.push(cb.value);
    });
    
    // Send request to server
    fetch('/get_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(filters)
    })
    .then(response => response.json())
    .then(data => {
        // Store the data globally
        currentData = data.data;
        
        // Update the count
        document.getElementById('resultCount').textContent = `Found: ${data.count} records`;
        
        // Clear the table
        document.getElementById('resultsBody').innerHTML = '';
        
        // Hide details panel when new data is loaded
        document.getElementById('detailsCard').style.display = 'none';
        
        // If no data, show message
        if (data.data.length === 0) {
            document.getElementById('resultsBody').innerHTML = '<tr><td colspan="10" class="text-center">No matching records found</td></tr>';
            return;
        }
        
        // Populate the table
        data.data.forEach(row => {
            const tr = document.createElement('tr');
            tr.dataset.aggLevel = row.agg_level;
            
            // Add cells
            tr.innerHTML = `
                <td>${row.agg_level}</td>
                <td>${row.worker_char}</td>
                <td>${row.firm_char}</td>
                <td>${row.firm_orig_char}</td>
                <td>${row.geo_level}</td>
                <td>${row.ind_level}</td>
                <td><span class="status-indicator ${row.j2j == 1 ? 'status-yes' : 'status-no'}">${row.j2j == 1 ? '✓' : '✗'}</span></td>
                <td><span class="status-indicator ${row.j2jr == 1 ? 'status-yes' : 'status-no'}">${row.j2jr == 1 ? '✓' : '✗'}</span></td>
                <td><span class="status-indicator ${row.j2jod == 1 ? 'status-yes' : 'status-no'}">${row.j2jod == 1 ? '✓' : '✗'}</span></td>
                <td><span class="status-indicator ${row.qwi == 1 ? 'status-yes' : 'status-no'}">${row.qwi == 1 ? '✓' : '✗'}</span></td>
            `;
            
            // Add click event
            tr.addEventListener('click', function() {
                // Remove selected class from all rows
                document.querySelectorAll('#resultsBody tr').forEach(row => {
                    row.classList.remove('selected');
                });
                
                // Add selected class to clicked row
                this.classList.add('selected');
                
                // Store selected row
                selectedRow = this;
                
                // Fetch and display details
                fetchDetails(row.agg_level);
            });
            
            // Add to table
            document.getElementById('resultsBody').appendChild(tr);
        });
    })
    .catch(error => {
        console.error('Error fetching data:', error);
        document.getElementById('resultsBody').innerHTML = '<tr><td colspan="10" class="text-center text-danger">Error loading data. Please try again.</td></tr>';
    });
}

// Fetch details for a specific aggregation level
function fetchDetails(aggLevel) {
    // Show loading in details panel
    document.getElementById('detailsCard').style.display = 'block';
    document.getElementById('detailsContent').innerHTML = '<div class="loading"></div>';
    
    // Fetch details from server
    fetch(`/get_details/${aggLevel}`)
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById('detailsContent').innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
            return;
        }
        
        // Update title
        let title = `Aggregation Level ${data.basic_info.agg_level}`;
        if (data.basic_info.worker_char) {
            title += ` - Worker: ${data.basic_info.worker_char}`;
        }
        if (data.basic_info.firm_char) {
            title += ` - Firm: ${data.basic_info.firm_char}`;
        }
        if (data.basic_info.firm_orig_char) {
            title += ` - Origin: ${data.basic_info.firm_orig_char}`;
        }
        document.getElementById('detailsTitle').textContent = title;
        
        // Build details content
        let html = '<div class="row">';
        
        // Left column
        html += '<div class="col-md-6">';
        
        // Worker Characteristics
        html += '<div class="detail-category">Worker Characteristics</div>';
        data.categories['Worker Characteristics'].forEach(item => {
            html += `<div class="detail-item"><span class="detail-badge bg-primary text-white">${item}</span></div>`;
        });
        
        // Firm Characteristics
        html += '<div class="detail-category">Firm Characteristics</div>';
        data.categories['Firm Characteristics'].forEach(item => {
            html += `<div class="detail-item"><span class="detail-badge bg-success text-white">${item}</span></div>`;
        });
        
        html += '</div>'; // End left column
        
        // Right column
        html += '<div class="col-md-6">';
        
        // Geographic Level
        html += '<div class="detail-category">Geographic Level</div>';
        html += `<div class="detail-item"><span class="detail-badge bg-info text-white">${data.categories['Geographic Level']}</span></div>`;
        
        // Industry Level
        html += '<div class="detail-category">Industry Level</div>';
        html += `<div class="detail-item"><span class="detail-badge bg-warning text-dark">${data.categories['Industry Level']}</span></div>`;
        
        // Data Types
        html += '<div class="detail-category">Data Types</div>';
        data.categories['Data Types'].forEach(item => {
            html += `<div class="detail-item"><span class="detail-badge bg-secondary text-white">${item}</span></div>`;
        });
        
        html += '</div>'; // End right column
        html += '</div>'; // End row
        
        // Add explanation
        html += `
        <div class="mt-4 p-3 bg-light rounded">
            <h6 class="mb-2">What does this mean?</h6>
            <p>This aggregation level (${data.basic_info.agg_level}) represents a specific way to group and analyze LEHD data.</p>
            <p>When using this aggregation level, you can analyze data with the characteristics shown above.</p>
            <p>This level is available for the data types listed and with the geographic and industry detail specified.</p>
        </div>`;
        
        // Update details content
        document.getElementById('detailsContent').innerHTML = html;
    })
    .catch(error => {
        console.error('Error fetching details:', error);
        document.getElementById('detailsContent').innerHTML = '<div class="alert alert-danger">Error loading details. Please try again.</div>';
    });
}

// Reset all filters to default values
function resetFilters() {
    // Reset checkboxes
    document.getElementById('j2j').checked = true;
    document.getElementById('j2jr').checked = true;
    document.getElementById('j2jod').checked = true;
    document.getElementById('qwi').checked = true;
    
    // Reset component checkboxes
    document.querySelectorAll('.worker-component, .firm-component, .firm-orig-component').forEach(checkbox => {
        checkbox.checked = false;
    });
    
    // Reset dropdowns
    document.getElementById('geoLevel').value = 'All';
    document.getElementById('indLevel').value = 'All';
    
    // Reset search
    document.getElementById('search').value = '';
    
    // Fetch data with reset filters
    fetchData();
}
