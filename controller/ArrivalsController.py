from flask import render_template, request, jsonify, session
from functools import wraps
import os
from dotenv import load_dotenv

load_dotenv()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def arrivals():
    """Render arrivals management page"""
    # Sample data - in real app, this would come from database
    sample_arrivals = [
        {
            'id': 1,
            'municipality': 'Quezon City',
            'municipality_code': 'QC-001',
            'submitted_by': 'Juan Dela Cruz',
            'submitter_role': 'Municipality Admin',
            'date_submitted': 'March 15, 2024',
            'time_submitted': '10:30 AM',
            'status': 'pending',
            'arrival_id': '#ARR-001',
            'notes': 'This arrival submission contains updated demographic data and visitor statistics for current reporting period.'
        },
        {
            'id': 2,
            'municipality': 'Manila City',
            'municipality_code': 'MNL-002',
            'submitted_by': 'Maria Santos',
            'submitter_role': 'Staff Officer',
            'date_submitted': 'March 14, 2024',
            'time_submitted': '2:45 PM',
            'status': 'active',
            'arrival_id': '#ARR-002',
            'notes': 'Monthly arrival report with complete visitor logs and accommodation data.'
        },
        {
            'id': 3,
            'municipality': 'Caloocan City',
            'municipality_code': 'CAL-003',
            'submitted_by': 'Roberto Jose',
            'submitter_role': 'Data Encoder',
            'date_submitted': 'March 13, 2024',
            'time_submitted': '9:15 AM',
            'status': 'inactive',
            'arrival_id': '#ARR-003',
            'notes': 'Incomplete submission - missing visitor count verification.'
        },
        {
            'id': 4,
            'municipality': 'Pasay City',
            'municipality_code': 'PSY-004',
            'submitted_by': 'Linda Gomez',
            'submitter_role': 'Municipality Admin',
            'date_submitted': 'March 12, 2024',
            'time_submitted': '4:20 PM',
            'status': 'active',
            'arrival_id': '#ARR-004',
            'notes': 'Complete arrival submission with all required documentation attached.'
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
            'municipality': 'Quezon City',
            'municipality_code': 'QC-001',
            'submitted_by': 'Juan Dela Cruz',
            'submitter_role': 'Municipality Admin',
            'date_submitted': 'March 15, 2024',
            'time_submitted': '10:30 AM',
            'status': 'pending',
            'arrival_id': '#ARR-001',
            'notes': 'This arrival submission contains updated demographic data and visitor statistics for the current reporting period.'
        },
        2: {
            'municipality': 'Manila City',
            'municipality_code': 'MNL-002',
            'submitted_by': 'Maria Santos',
            'submitter_role': 'Staff Officer',
            'date_submitted': 'March 14, 2024',
            'time_submitted': '2:45 PM',
            'status': 'active',
            'arrival_id': '#ARR-002',
            'notes': 'Monthly arrival report with complete visitor logs and accommodation data.'
        },
        3: {
            'municipality': 'Caloocan City',
            'municipality_code': 'CAL-003',
            'submitted_by': 'Roberto Jose',
            'submitter_role': 'Data Encoder',
            'date_submitted': 'March 13, 2024',
            'time_submitted': '9:15 AM',
            'status': 'inactive',
            'arrival_id': '#ARR-003',
            'notes': 'Incomplete submission - missing visitor count verification.'
        },
        4: {
            'municipality': 'Pasay City',
            'municipality_code': 'PSY-004',
            'submitted_by': 'Linda Gomez',
            'submitter_role': 'Municipality Admin',
            'date_submitted': 'March 12, 2024',
            'time_submitted': '4:20 PM',
            'status': 'active',
            'arrival_id': '#ARR-004',
            'notes': 'Complete arrival submission with all required documentation attached.'
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
