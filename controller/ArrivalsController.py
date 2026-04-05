from utils import role_required, login_required
from flask import render_template, session

@login_required
@role_required('super_admin')
def arrivals():
    """Render arrivals management page"""
    # Sample data - in real app, this would come from database
    sample_arrivals = [
        {
            'id': 1,
            'municipality': 'Pagsanjan',
            'municipality_code': 'LAG-001',
            'submitted_by': 'Maria Reyes',
            'submitter_role': 'Municipality Admin',
            'date_submitted': 'March 15, 2024',
            'time_submitted': '10:30 AM',
            'status': 'pending',
            'arrival_id': '#ARR-001',
            'notes': 'This arrival submission contains updated visitor statistics for Pagsanjan Falls tourism peak season management.'
        },
        {
            'id': 2,
            'municipality': 'Calamba',
            'municipality_code': 'LAG-002',
            'submitted_by': 'Jose Santos',
            'submitter_role': 'Staff Officer',
            'date_submitted': 'March 14, 2024',
            'time_submitted': '2:45 PM',
            'status': 'active',
            'arrival_id': '#ARR-002',
            'notes': 'Hot spring tourism arrival report with complete visitor data and accommodation statistics for Calamba.'
        },
        {
            'id': 3,
            'municipality': 'Los Baños',
            'municipality_code': 'LAG-003',
            'submitted_by': 'Ana Martinez',
            'submitter_role': 'Data Encoder',
            'date_submitted': 'March 13, 2024',
            'time_submitted': '9:15 AM',
            'status': 'inactive',
            'arrival_id': '#ARR-003',
            'notes': 'Academic tourism arrival data for UPLB and research institutions - incomplete visitor verification.'
        },
        {
            'id': 4,
            'municipality': 'Santa Rosa',
            'municipality_code': 'LAG-004',
            'submitted_by': 'Carlos dela Cruz',
            'submitter_role': 'Municipality Admin',
            'date_submitted': 'March 12, 2024',
            'time_submitted': '4:20 PM',
            'status': 'active',
            'arrival_id': '#ARR-004',
            'notes': 'Shopping and entertainment tourism arrival data with complete visitor demographics from Enchanted Kingdom.'
        }
    ]
    
    active_menu = ['arrivals']
    return render_template('views/dashboard/arrivals.html', 
                        arrivals=sample_arrivals,
                        menu=active_menu)

def get_arrival(arrival_id):
    """Get specific arrival details"""
    # Sample data - in real app, this would query database
    sample_arrivals = {
        1: {
            'municipality': 'Pagsanjan',
            'municipality_code': 'LAG-001',
            'submitted_by': 'Maria Reyes',
            'submitter_role': 'Municipality Admin',
            'date_submitted': 'March 15, 2024',
            'time_submitted': '10:30 AM',
            'status': 'pending',
            'arrival_id': '#ARR-001',
            'notes': 'This arrival submission contains updated visitor statistics for Pagsanjan Falls tourism peak season management.'
        },
        2: {
            'municipality': 'Calamba',
            'municipality_code': 'LAG-002',
            'submitted_by': 'Jose Santos',
            'submitter_role': 'Staff Officer',
            'date_submitted': 'March 14, 2024',
            'time_submitted': '2:45 PM',
            'status': 'active',
            'arrival_id': '#ARR-002',
            'notes': 'Hot spring tourism arrival report with complete visitor data and accommodation statistics for Calamba.'
        },
        3: {
            'municipality': 'Los Baños',
            'municipality_code': 'LAG-003',
            'submitted_by': 'Ana Martinez',
            'submitter_role': 'Data Encoder',
            'date_submitted': 'March 13, 2024',
            'time_submitted': '9:15 AM',
            'status': 'inactive',
            'arrival_id': '#ARR-003',
            'notes': 'Academic tourism arrival data for UPLB and research institutions - incomplete visitor verification.'
        },
        4: {
            'municipality': 'Santa Rosa',
            'municipality_code': 'LAG-004',
            'submitted_by': 'Carlos dela Cruz',
            'submitter_role': 'Municipality Admin',
            'date_submitted': 'March 12, 2024',
            'time_submitted': '4:20 PM',
            'status': 'active',
            'arrival_id': '#ARR-004',
            'notes': 'Shopping and entertainment tourism arrival data with complete visitor demographics from Enchanted Kingdom.'
        }
    }
    
    return sample_arrivals.get(arrival_id, {})

def delete_arrival(arrival_id):
    """Delete an arrival submission"""
    # In real app, this would delete from database
    # For now, just return success
    return True

def create_arrival(data):
    """Create a new arrival submission"""
    # In real app, this would save to database
    # For now, just return success
    return True

def update_arrival(arrival_id, data):
    """Update an existing arrival submission"""
    # In real app, this would update database
    # For now, just return success
    return True
