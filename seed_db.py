from db_manager import db
import uuid

def seed_data():
    if not db.client:
        print("ERROR: Supabase client not initialized.")
        return

    try:
        # 1. Create a Student User
        # First, we need to check if the table exists by trying a select
        # If it fails with the "schema cache" error, we know the tables aren't there.
        
        print("Attempting to seed test data...")
        
        # We'll use a hardcoded UUID for the demo user to keep it consistent
        student_id = "d1b1e1a1-1111-4444-8888-c1c1c1c1c1c1"
        staff_id = "55555555-5555-5555-5555-555555555555"
        
        # Test if table exists
        try:
            db.client.table("portal_users").select("id").limit(1).execute()
        except Exception as e:
            if "PGRST205" in str(e) or "Could not find the table" in str(e):
                print("ERROR: Tables do not exist in the database. Please run the SQL schema first.")
                return
            else:
                print(f"Unexpected error checking table: {e}")
                return

        # Insert Student
        user_data = {
            "id": student_id,
            "email": "student@nile.edu.ng",
            "user_id_number": "NU/CS/2021/452",
            "role": "student"
        }
        db.client.table("portal_users").upsert(user_data).execute()
        
        profile_data = {
            "id": student_id,
            "full_name": "Umar Farouk",
            "matric_no": "NU/CS/2021/452",
            "department": "Computer Science",
            "cgpa": 3.85,
            "credits_earned": 120,
            "level": 400
        }
        db.client.table("student_profiles").upsert(profile_data).execute()
        
        # Insert Library Staff
        staff_data = {
            "id": staff_id,
            "email": "library@nile.edu.ng",
            "user_id_number": "STAFF-LIB-01",
            "role": "staff",
            "unit_key": "library"
        }
        db.client.table("portal_users").upsert(staff_data).execute()
        
        print("Successfully seeded Student and Library Staff data!")
        print("Student ID: NU/CS/2021/452")
        print("Staff ID: STAFF-LIB-01")

    except Exception as e:
        print(f"FATAL ERROR during seeding: {e}")

if __name__ == "__main__":
    seed_data()
