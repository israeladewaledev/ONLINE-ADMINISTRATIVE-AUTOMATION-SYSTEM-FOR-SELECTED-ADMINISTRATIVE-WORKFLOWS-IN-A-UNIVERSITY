---
description: how to run and test the Nile Admin Portal
---

# Nile Admin Portal Workflow

Follow these steps to run the application and test the full clearance cycle.

## 1. Start the Application
// turbo
1. Run the Flask server:
```bash
python3 app.py
```
2. Open your browser to `http://127.0.0.1:5000`.

## 2. Test the Student Clearance Flow
1. **Login**: Use `NU/CS/2021/452` and password `password123`.
2. **View Dashboard**: Confirm your profile and "Pending" clearance status are visible.
3. **Submit Complaint**: Go to the Complaints page and submit a test ticket.

## 3. Test the Staff Approval Flow
1. **Logout** and Log in as **Library Staff**:
   - User ID: `STAFF-LIB-01`
   - Password: `password123`
2. **Approve Record**: Find student `NU/CS/2021/452` and click "Approve" for the Library unit.
3. **Verify**: Log back in as the student to see the "Library" status updated to "Cleared".

## 4. Manage the Database
- **View Data**: Go to your [Supabase Table Editor](https://supabase.com/dashboard/project/owjofbyaicgvounwojrm/editor/public/portal_users).
- **Reset Data**: If you want to start fresh, run `python3 seed_db.py` from your terminal.
