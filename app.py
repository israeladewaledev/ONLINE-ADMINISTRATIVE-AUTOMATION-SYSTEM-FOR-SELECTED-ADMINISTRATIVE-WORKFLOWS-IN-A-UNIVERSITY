from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from db_manager import db
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "nile_university_secret_2026")

# --- Constants ---
UNIT_NAMES = {
    'library': 'Library Services',
    'accounts': 'Account Unit',
    'hostel': 'Hostel Unit',
    'services': 'Student Services',
    'division': 'Academic Division',
    'store': 'Central Store',
    'department': 'Academic Department',
    'honoris': 'Honoris 21C Skills Program'
}

# --- Authentication Logic ---
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    id_number = data.get('id_number')
    role = data.get('role')
    
    user = db.get_user_by_id_number(id_number)
    if user:
        if user['role'] != role and not (role.startswith('staff') and user['role'] == 'staff'):
            return jsonify({"success": False, "message": "Role mismatch."}), 401
            
        session['user_id'] = user['id']
        session['user_id_number'] = user['user_id_number']
        session['role'] = user['role']
        if user['unit_key']: session['staff_unit'] = user['unit_key']
        return jsonify({"success": True, "role": user['role'], "unit": user['unit_key']})
    return jsonify({"success": False, "message": "Invalid credentials."}), 404

@app.route('/api/student/initiate_clearance', methods=['POST'])
def api_initiate_clearance():
    user_id = session.get('user_id')
    if not user_id: return jsonify({"success": False}), 401
    
    success = True
    for unit in UNIT_NAMES.keys():
        if not db.update_clearance_status(user_id, unit, 'pending'):
            success = False
    return jsonify({"success": success})

# --- Student Routes ---
@app.route('/student/home')
def student_home():
    user_id = session.get('user_id')
    if not user_id: return redirect(url_for('index'))
    
    profile = db.get_student_profile(user_id)
    status_list = db.get_clearance_status(user_id)
    cleared_count = len([s for s in status_list if s['status'] == 'cleared'])
    progress = int((cleared_count / 8) * 100) if status_list else 0
    
    return render_template('student/home.html', profile=profile, progress=progress)

@app.route('/student/clearance')
def student_clearance():
    user_id = session.get('user_id')
    if not user_id: return redirect(url_for('index'))
    
    records = db.get_clearance_status(user_id)
    # Convert to dict for easier template lookups: { 'library': 'cleared', ... }
    status_map = {r['unit_key']: r for r in records}
    
    return render_template('student/clearance.html', status_map=status_map, unit_names=UNIT_NAMES)

@app.route('/student/complaints')
def student_complaints():
    user_id = session.get('user_id')
    if not user_id: return redirect(url_for('index'))
    
    # We need a new db method for this
    complaints = db.get_student_complaints(user_id)
    return render_template('student/complaints.html', complaints=complaints, unit_names=UNIT_NAMES)

@app.route('/student/profile')
def student_profile():
    user_id = session.get('user_id')
    if not user_id: return redirect(url_for('index'))
    profile = db.get_student_profile(user_id)
    return render_template('student/profile.html', profile=profile)

# --- Staff Routes ---
def get_staff_context():
    unit_key = request.args.get('unit', session.get('staff_unit'))
    if not unit_key: return None, None
    unit_info = {"name": unit_key.replace('_', ' ').title(), "id": f"S-{unit_key.upper()[:3]}"}
    return unit_key, unit_info

@app.route('/api/staff/update_clearance', methods=['POST'])
def api_update_clearance():
    data = request.json
    student_id = data.get('student_id')
    unit_key = data.get('unit_key')
    status = data.get('status')
    reason = data.get('reason')
    
    if db.update_clearance_status(student_id, unit_key, status, reason):
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Database update failed."}), 500

@app.route('/api/student/complaint', methods=['POST'])
def api_create_complaint():
    user_id = session.get('user_id')
    if not user_id: return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    data = request.json
    success = db.create_complaint(
        user_id, 
        data.get('subject'), 
        data.get('message'), 
        data.get('target_unit')
    )
    return jsonify({"success": success})

@app.route('/api/staff/resolve_complaint', methods=['POST'])
def api_resolve_complaint():
    data = request.json
    success = db.resolve_complaint(data.get('complaint_id'), data.get('note'))
    return jsonify({"success": success})

@app.route('/staff/home')
def staff_home():
    unit_key, unit_info = get_staff_context()
    if not unit_key: return redirect(url_for('index'))
    return render_template('staff/home.html', unit_key=unit_key, unit=unit_info)

@app.route('/staff/clearance')
def staff_clearance():
    unit_key, unit_info = get_staff_context()
    if not unit_key: return redirect(url_for('index'))
    students = db.get_all_pending_clearances(unit_key)
    return render_template('staff/clearance.html', unit_key=unit_key, unit=unit_info, students=students)

@app.route('/staff/academic')
def staff_academic():
    unit_key, unit_info = get_staff_context()
    if not unit_key: return redirect(url_for('index'))
    return render_template('staff/academic.html', unit_key=unit_key, unit=unit_info)

@app.route('/staff/complaints')
def staff_complaints():
    unit_key, unit_info = get_staff_context()
    if not unit_key: return redirect(url_for('index'))
    complaints = db.get_complaints(unit_key)
    return render_template('staff/complaints.html', unit_key=unit_key, unit=unit_info, complaints=complaints)

# --- Supplementary Pages ---
@app.route('/staff/inventory')
def staff_inventory():
    unit_key, unit_info = get_staff_context()
    return render_template('staff/inventory.html', unit_key=unit_key, unit=unit_info)

@app.route('/staff/finance')
def staff_finance():
    unit_key, unit_info = get_staff_context()
    return render_template('staff/finance.html', unit_key=unit_key, unit=unit_info)

@app.route('/staff/residents')
def staff_residents():
    unit_key, unit_info = get_staff_context()
    return render_template('staff/residents.html', unit_key=unit_key, unit=unit_info)

@app.route('/staff/amenities')
def staff_amenities():
    unit_key, unit_info = get_staff_context()
    return render_template('staff/amenities.html', unit_key=unit_key, unit=unit_info)

@app.route('/staff/skills')
def staff_skills():
    unit_key, unit_info = get_staff_context()
    return render_template('staff/skills.html', unit_key=unit_key, unit=unit_info)

# --- Admin Routes ---
@app.route('/admin/home')
def admin_home():
    return render_template('admin/home.html')

@app.route('/admin/records')
def admin_records():
    return render_template('admin/records.html')

@app.route('/admin/view_profile/<student_id>')
def admin_view_profile(student_id):
    return render_template('admin/view_profile.html', student_id=student_id)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
