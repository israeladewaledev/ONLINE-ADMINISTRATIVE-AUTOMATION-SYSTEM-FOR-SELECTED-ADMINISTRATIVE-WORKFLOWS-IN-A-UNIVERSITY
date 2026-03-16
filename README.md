# Nile University Admin Portal

## How to Test Navigation

1. **Open the Login Page**
   - Double-click `index.html` OR
   - Right-click `index.html` → Open With → Your Browser

2. **Test Login Flow**
   - Select "Student" or "Staff" role
   - Click "Sign In to Portal"
   - Should redirect to respective dashboard

3. **Test Sidebar Navigation**
   - Click sidebar links
   - "Dashboard" and "My Clearance" should reload the page
   - "Logout" should return to login
   - Other links show "Coming Soon" alerts

## Files Structure
```
NileAdminPortal/
├── index.html              # Login Page (START HERE)
├── student_dashboard.html  # Student Portal
├── admin_dashboard.html    # Admin Portal
└── assets/
    └── css/
        └── style.css       # Shared styles
```

## Troubleshooting

**If navigation doesn't work:**

1. Make sure you're opening the files from the file system (not a web server)
2. Check browser console for errors (F12 → Console tab)
3. Verify all files are in the same directory
4. Try opening files directly by double-clicking them

**Common Issue:** Some browsers block JavaScript on local files. 
**Solution:** Use Chrome, Firefox, or Safari which allow local file navigation.
