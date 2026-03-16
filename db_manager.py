import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            print("WARNING: Supabase URL or Key is missing. Check your .env file.")
            self.client = None
        else:
            self.client: Client = create_client(self.url, self.key)

    def get_user_by_id_number(self, id_number):
        """Fetch a user and their role by their ID number (Matric No or Staff ID)"""
        if not self.client: return None
        
        response = self.client.table("portal_users").select("*").eq("user_id_number", id_number).execute()
        return response.data[0] if response.data else None

    def get_student_profile(self, user_id):
        """Fetch the full profile for a student"""
        if not self.client: return None
        
        response = self.client.table("student_profiles").select("*").eq("id", user_id).execute()
        return response.data[0] if response.data else None

    def get_clearance_status(self, student_id):
        """Fetch the clearance status for all units for a given student"""
        if not self.client: return []
        
        response = self.client.table("clearance_records").select("*").eq("student_id", student_id).execute()
        return response.data

    def get_all_pending_clearances(self, unit_key):
        """Fetch all students and their clearance status for a specific unit"""
        if not self.client: return []
        
        # We want to see all students and their status for this specific unit
        # In a real app, this would be a join between portal_users (students) and clearance_records
        response = self.client.table("student_profiles").select("*, portal_users(id, user_id_number)").execute()
        students = response.data
        
        status_response = self.client.table("clearance_records").select("*").eq("unit_key", unit_key).execute()
        statuses = {s['student_id']: s for s in status_response.data}
        
        # Merge status into student profile
        for student in students:
            student['clearance_status'] = statuses.get(student['portal_users']['id'], {"status": "pending"})
            
        return students

    def update_clearance_status(self, student_id, unit_key, status, reason=None):
        """Update the clearance status for a specific unit"""
        if not self.client: return False
        
        # Check if record exists
        existing = self.client.table("clearance_records").select("*").eq("student_id", student_id).eq("unit_key", unit_key).execute()
        
        data = {
            "student_id": student_id,
            "unit_key": unit_key,
            "status": status,
            "rejection_reason": reason,
            "updated_at": "now()"
        }
        
        if existing.data:
            response = self.client.table("clearance_records").update(data).eq("student_id", student_id).eq("unit_key", unit_key).execute()
        else:
            response = self.client.table("clearance_records").insert(data).execute()
            
        return len(response.data) > 0

    def get_student_complaints(self, student_id):
        """Fetch all complaints for a specific student"""
        if not self.client: return []
        
        response = self.client.table("student_complaints").select("*").eq("student_id", student_id).order("created_at", desc=True).execute()
        return response.data

    def get_complaints(self, unit_key=None):
        """Fetch complaints, optionally filtered by unit_key"""
        if not self.client: return []
        
        query = self.client.table("student_complaints").select("*, portal_users(user_id_number), student_profiles(full_name)")
        if unit_key:
            query = query.eq("target_unit", unit_key)
            
        response = query.eq("status", "open").execute()
        return response.data

    def resolve_complaint(self, complaint_id, note):
        """Mark a complaint as resolved with a note"""
        if not self.client: return False
        
        response = self.client.table("student_complaints").update({
            "status": "resolved",
            "resolution_note": note
        }).eq("id", complaint_id).execute()
        
        return len(response.data) > 0

    def create_complaint(self, student_id, subject, message, target_unit):
        """Create a new complaint ticket"""
        if not self.client: return False
        
        response = self.client.table("student_complaints").insert({
            "student_id": student_id,
            "subject": subject,
            "message": message,
            "target_unit": target_unit
        }).execute()
        
        return len(response.data) > 0

db = DatabaseManager()
