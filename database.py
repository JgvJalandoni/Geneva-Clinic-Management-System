"""
Database layer for Tita's Clinic Management System
Handles all SQLite database operations with proper error handling
"""

import sqlite3
import datetime
import hashlib
import shutil
import csv
from typing import Optional, List, Dict
from config import DB_NAME


class ClinicDatabase:
    """Handles all database operations with proper error handling"""
    
    def __init__(self, db_name: str = DB_NAME):
        self.db_name = db_name
        self._conn = None
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Return cached database connection (reused for performance)"""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_name)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys = ON")
        return self._conn
    
    def init_db(self):
        """Initialize database schema - UPDATED with additional patient fields"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Patients Table - UPDATED with reference_number
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS patients (
                        patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        reference_number INTEGER,
                        last_name TEXT NOT NULL,
                        first_name TEXT NOT NULL,
                        middle_name TEXT,
                        date_of_birth TEXT,
                        sex TEXT,
                        civil_status TEXT,
                        occupation TEXT,
                        parents TEXT,
                        parent_contact TEXT,
                        school TEXT,
                        contact_number TEXT,
                        address TEXT,
                        notes TEXT,
                        registered_date TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Migration: Add missing columns if table already exists
                cursor.execute("PRAGMA table_info(patients)")
                columns = [column[1] for column in cursor.fetchall()]
                
                migrations = [
                    ("reference_number", "INTEGER"),
                    ("sex", "TEXT"),
                    ("civil_status", "TEXT"),
                    ("occupation", "TEXT"),
                    ("parents", "TEXT"),
                    ("parent_contact", "TEXT"),
                    ("school", "TEXT")
                ]
                
                for col_name, col_type in migrations:
                    if col_name not in columns:
                        cursor.execute(f"ALTER TABLE patients ADD COLUMN {col_name} {col_type}")
                
                # Visit Logs Table - with reference_number (now non-unique per visit, unique per patient)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS visit_logs (
                        visit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        patient_id INTEGER NOT NULL,
                        reference_number INTEGER NOT NULL,
                        visit_date TEXT NOT NULL,
                        visit_time TEXT,
                        weight_kg REAL,
                        height_cm REAL,
                        blood_pressure TEXT,
                        temperature_celsius REAL,
                        medical_notes TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        modified_at TEXT,
                        visit_type TEXT DEFAULT 'new',
                        FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
                    )
                """)

                # Migration: Add visit_type column to visit_logs if not present
                cursor.execute("PRAGMA table_info(visit_logs)")
                vl_columns = [column[1] for column in cursor.fetchall()]
                if "visit_type" not in vl_columns:
                    cursor.execute("ALTER TABLE visit_logs ADD COLUMN visit_type TEXT DEFAULT 'new'")

                # DATA MIGRATION: Populate patients.reference_number from visit_logs if not already set
                # We use the earliest reference number assigned to the patient
                cursor.execute("""
                    UPDATE patients
                    SET reference_number = (
                        SELECT MIN(reference_number)
                        FROM visit_logs
                        WHERE visit_logs.patient_id = patients.patient_id
                    )
                    WHERE reference_number IS NULL
                """)

                # Admin Users Table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS admin_users (
                        admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password_hash TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # High-performance indices - O(log n) lookups
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_first_name ON patients(first_name)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_last_name ON patients(last_name)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_dob ON patients(date_of_birth)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_ref ON patients(reference_number)")
                
                # UNIQUE index for patients to prevent "ghost" duplicates
                cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_patient_unique_ref ON patients(reference_number)")
                
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_visit_date ON visit_logs(visit_date)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_visits ON visit_logs(patient_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_reference_number ON visit_logs(reference_number)")
                
                # Remove unique index to allow multiple visits with same patient ref
                cursor.execute("DROP INDEX IF EXISTS idx_unique_reference")
                
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
            raise
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PATIENT OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def add_patient(self, last_name: str, first_name: str, middle_name: str = "",
                   dob: str = "", sex: str = "", civil_status: str = "", occupation: str = "", 
                   parents: str = "", parent_contact: str = "", school: str = "",
                   contact: str = "", address: str = "", notes: str = "",
                   reference_number: Optional[int] = None) -> Optional[int]:
        """
        Create new patient record - UPDATED with reference_number
        
        Args:
            last_name: Patient's last name (required)
            first_name: Patient's first name (required)
            middle_name: Patient's middle name (optional)
            dob: Date of birth in YYYY-MM-DD format (optional)
            sex: Male/Female (optional)
            civil_status: Single/Married/etc (optional)
            occupation: Patient's occupation (optional)
            parents: Parents' names (optional)
            parent_contact: Parents' contact number (optional)
            school: Patient's school (optional)
            contact: Patient's contact number (optional)
            address: Patient's address (optional)
            notes: Additional notes (optional)
            reference_number: Patient ID number (auto-generated if None)
            
        Returns:
            Patient ID if successful, None otherwise
        """
        try:
            # Auto-generate reference number if not provided
            if reference_number is None:
                reference_number = self.get_next_reference_number()

            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO patients (reference_number, last_name, first_name, middle_name, date_of_birth, 
                                        sex, civil_status, occupation, parents, parent_contact, school,
                                        contact_number, address, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (reference_number, last_name, first_name, middle_name or None, dob or None, 
                      sex or None, civil_status or None, occupation or None, parents or None, 
                      parent_contact or None, school or None,
                      contact or None, address or None, notes or None))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding patient: {e}")
            return None
    
    def update_patient(self, patient_id: int, last_name: str, first_name: str, middle_name: str = "",
                      dob: str = "", sex: str = "", civil_status: str = "", occupation: str = "", 
                      parents: str = "", parent_contact: str = "", school: str = "",
                      contact: str = "", address: str = "", notes: str = "",
                      reference_number: Optional[int] = None) -> bool:
        """
        Update existing patient record - UPDATED
        
        Args:
            patient_id: ID of patient to update
            last_name: Updated last name
            first_name: Updated first name
            middle_name: Updated middle name
            dob: Updated date of birth
            sex: Updated sex
            civil_status: Updated civil status
            occupation: Updated occupation
            parents: Updated parents
            parent_contact: Updated parent contact
            school: Updated school
            contact: Updated contact number
            address: Updated address
            notes: Updated notes
            reference_number: Updated reference number
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if reference_number is not None:
                    cursor.execute("""
                        UPDATE patients 
                        SET last_name=?, first_name=?, middle_name=?, date_of_birth=?, 
                            sex=?, civil_status=?, occupation=?, parents=?, parent_contact=?, school=?,
                            contact_number=?, address=?, notes=?, reference_number=?
                        WHERE patient_id=?
                    """, (last_name, first_name, middle_name or None, dob or None, 
                          sex or None, civil_status or None, occupation or None, parents or None, 
                          parent_contact or None, school or None,
                          contact or None, address or None, notes or None, reference_number, patient_id))
                else:
                    cursor.execute("""
                        UPDATE patients 
                        SET last_name=?, first_name=?, middle_name=?, date_of_birth=?, 
                            sex=?, civil_status=?, occupation=?, parents=?, parent_contact=?, school=?,
                            contact_number=?, address=?, notes=?
                        WHERE patient_id=?
                    """, (last_name, first_name, middle_name or None, dob or None, 
                          sex or None, civil_status or None, occupation or None, parents or None, 
                          parent_contact or None, school or None,
                          contact or None, address or None, notes or None, patient_id))
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error updating patient: {e}")
            return False
    
    def get_patient(self, patient_id: int) -> Optional[Dict]:
        """
        Get single patient by ID
        
        Args:
            patient_id: ID of patient to retrieve
            
        Returns:
            Dictionary with patient data or None if not found
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"Error fetching patient: {e}")
            return None

    def get_patient_by_reference(self, reference_number: int) -> Optional[Dict]:
        """
        Get single patient by their reference number (Patient ID)
        
        Args:
            reference_number: The patient ID to look up
            
        Returns:
            Dictionary with patient data or None if not found
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM patients WHERE reference_number = ?", (reference_number,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"Error fetching patient by reference: {e}")
            return None

    def delete_patient(self, patient_id: int) -> bool:
        """Delete a patient record"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM patients WHERE patient_id = ?", (patient_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting patient: {e}")
            return False

    def reassign_visits(self, old_patient_id: int, new_patient_id: int) -> bool:
        """Move all visit logs from one patient record to another"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Also update reference_number in visit_logs to match new patient
                cursor.execute("SELECT reference_number FROM patients WHERE patient_id = ?", (new_patient_id,))
                row = cursor.fetchone()
                new_ref = row[0] if row else None
                
                if new_ref:
                    cursor.execute("""
                        UPDATE visit_logs 
                        SET patient_id = ?, reference_number = ? 
                        WHERE patient_id = ?
                    """, (new_patient_id, new_ref, old_patient_id))
                else:
                    cursor.execute("UPDATE visit_logs SET patient_id = ? WHERE patient_id = ?", (new_patient_id, old_patient_id))
                
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Error reassigning visits: {e}")
            return False

    def merge_patients(self, source_patient_id: int, target_patient_id: int) -> bool:
        """Merge source patient info and history into target patient and delete source"""
        try:
            # 1. Reassign all visits first
            if not self.reassign_visits(source_patient_id, target_patient_id):
                return False
            
            # 2. Delete the source patient record
            return self.delete_patient(source_patient_id)
        except Exception as e:
            print(f"Error merging patients: {e}")
            return False
    
    def search_patients(self, query: str) -> List[Dict]:
        """
        Search patients by name or reference number - OPTIMIZED
        
        Args:
            query: Search query string (name or reference number)
            
        Returns:
            List of patient dictionaries matching the query
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if not query or len(query) < 1:
                    # Show recent patients if query too short
                    cursor.execute("""
                        SELECT p.*, MAX(v.visit_date) as last_visit
                        FROM patients p
                        LEFT JOIN visit_logs v ON p.patient_id = v.patient_id
                        GROUP BY p.patient_id
                        ORDER BY v.visit_date DESC
                        LIMIT 20
                    """)
                else:
                    # Clean query for reference number check (remove dashes)
                    clean_query = query.replace("-", "")
                    
                    # Search across name and reference number
                    cursor.execute("""
                        SELECT p.*, MAX(v.visit_date) as last_visit
                        FROM patients p
                        LEFT JOIN visit_logs v ON p.patient_id = v.patient_id
                        WHERE p.first_name LIKE ? 
                           OR p.middle_name LIKE ? 
                           OR p.last_name LIKE ?
                           OR CAST(p.reference_number AS TEXT) LIKE ?
                        GROUP BY p.patient_id
                        ORDER BY p.last_name, p.first_name
                        LIMIT 50
                    """, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{clean_query}%'))
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []
    
    def search_patients_filtered(self, query: str = "", filters: Dict = None, page: int = 1, per_page: int = 10) -> tuple:
        """
        Advanced search with filters and pagination
        
        Filters can include:
        - age_min, age_max
        - sex
        - civil_status
        - last_visit_start, last_visit_end
        - registered_start, registered_end
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                base_query = """
                    FROM patients p
                    LEFT JOIN (
                        SELECT patient_id, MAX(visit_date) as last_visit
                        FROM visit_logs
                        GROUP BY patient_id
                    ) v ON p.patient_id = v.patient_id
                    WHERE 1=1
                """
                params = []
                
                if query:
                    clean_query = query.replace("-", "")
                    base_query += " AND (p.first_name LIKE ? OR p.middle_name LIKE ? OR p.last_name LIKE ? OR CAST(p.reference_number AS TEXT) LIKE ?)"
                    params.extend([f"%{query}%", f"%{query}%", f"%{query}%", f"%{clean_query}%"])
                
                if filters:
                    if filters.get('sex'):
                        base_query += " AND p.sex = ?"
                        params.append(filters['sex'])
                    
                    if filters.get('civil_status'):
                        base_query += " AND p.civil_status = ?"
                        params.append(filters['civil_status'])
                    
                    # Age filter (calculated from DOB)
                    if filters.get('age_min') is not None or filters.get('age_max') is not None:
                        today = datetime.date.today()
                        if filters.get('age_min') is not None:
                            # Born on or before this date
                            max_birth_year = today.year - int(filters['age_min'])
                            max_dob = f"{max_birth_year}-{today.month:02d}-{today.day:02d}"
                            base_query += " AND p.date_of_birth <= ?"
                            params.append(max_dob)
                        
                        if filters.get('age_max') is not None:
                            # Born on or after this date
                            min_birth_year = today.year - int(filters['age_max']) - 1
                            min_dob = f"{min_birth_year}-{today.month:02d}-{today.day:02d}"
                            base_query += " AND p.date_of_birth >= ?"
                            params.append(min_dob)

                    if filters.get('last_visit_start'):
                        base_query += " AND v.last_visit >= ?"
                        params.append(filters['last_visit_start'])
                    
                    if filters.get('last_visit_end'):
                        base_query += " AND v.last_visit <= ?"
                        params.append(filters['last_visit_end'])
                        
                    if filters.get('registered_start'):
                        base_query += " AND p.registered_date >= ?"
                        params.append(filters['registered_start'] + " 00:00:00")
                    
                    if filters.get('registered_end'):
                        base_query += " AND p.registered_date <= ?"
                        params.append(filters['registered_end'] + " 23:59:59")
                    
                    if filters.get('alpha_last_name'):
                        base_query += " AND p.last_name LIKE ?"
                        params.append(f"{filters['alpha_last_name']}%")

                # Get total count
                cursor.execute(f"SELECT COUNT(DISTINCT p.patient_id) {base_query}", params)
                total = cursor.fetchone()[0]

                # Get paginated results
                offset = (page - 1) * per_page
                cursor.execute(f"""
                    SELECT p.*, v.last_visit
                    {base_query}
                    ORDER BY p.registered_date DESC, p.last_name, p.first_name
                    LIMIT ? OFFSET ?
                """, params + [per_page, offset])
                
                patients = [dict(row) for row in cursor.fetchall()]
                return patients, total
        except sqlite3.Error as e:
            print(f"Filtered search error: {e}")
            return [], 0

    def get_all_patients(self) -> List[Dict]:
        """
        Get all patients ordered by last name, first name - OPTIMIZED

        Returns:
            List of all patient dictionaries
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM patients ORDER BY last_name, first_name")
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    def get_patients_paginated(self, page: int = 1, per_page: int = 10) -> tuple:
        """
        Get patients with pagination

        Args:
            page: Page number (1-indexed)
            per_page: Records per page

        Returns:
            Tuple of (list of patients, total count)
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Get total count
                cursor.execute("SELECT COUNT(*) FROM patients")
                total = cursor.fetchone()[0]

                # Get paginated results
                offset = (page - 1) * per_page
                cursor.execute("""
                    SELECT * FROM patients
                    ORDER BY last_name, first_name
                    LIMIT ? OFFSET ?
                """, (per_page, offset))
                patients = [dict(row) for row in cursor.fetchall()]
                return patients, total
        except sqlite3.Error:
            return [], 0
    
    def get_patient_count(self) -> int:
        """Get total patient count efficiently using COUNT query"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM patients")
                return cursor.fetchone()[0]
        except sqlite3.Error:
            return 0

    def get_visit_count(self) -> int:
        """Get total visit count efficiently using COUNT query"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM visit_logs")
                return cursor.fetchone()[0]
        except sqlite3.Error:
            return 0

    # ═══════════════════════════════════════════════════════════════════════════
    # VISIT OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════════

    def get_next_reference_number(self) -> int:
        """
        Get the next available reference number - Checks both patients and visit_logs

        Returns:
            Next reference number (max + 1, or 1 if no visits exist)
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Get max from both tables to ensure global uniqueness for the next ID
                cursor.execute("""
                    SELECT MAX(ref) FROM (
                        SELECT MAX(reference_number) as ref FROM visit_logs
                        UNION
                        SELECT MAX(reference_number) as ref FROM patients
                    )
                """)
                result = cursor.fetchone()[0]
                return (result or 0) + 1
        except sqlite3.Error:
            return 1

    def is_reference_number_available(self, ref_num: int) -> bool:
        """
        Check if a reference number is available (not already used)
        NOTE: Reference numbers are now patient-based.

        Args:
            ref_num: Reference number to check

        Returns:
            True if available, False if already exists
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Check both tables
                cursor.execute("""
                    SELECT 1 FROM visit_logs WHERE reference_number = ?
                    UNION
                    SELECT 1 FROM patients WHERE reference_number = ?
                """, (ref_num, ref_num))
                return cursor.fetchone() is None
        except sqlite3.Error:
            return False

    def add_visit(self, patient_id: int, visit_date: str, visit_time: str,
                 weight: Optional[float] = None, height: Optional[float] = None,
                 bp: str = "", temp: Optional[float] = None, notes: str = "",
                 reference_number: Optional[int] = None, visit_type: str = "new") -> Optional[int]:
        """
        Create new visit record - Uses patient's reference number

        Args:
            patient_id: ID of the patient
            visit_date: Date of visit in YYYY-MM-DD format
            visit_time: Time of visit in HH:MM:SS format
            weight: Weight in kg (optional)
            height: Height in cm (optional)
            bp: Blood pressure reading (optional)
            temp: Temperature in celsius (optional)
            notes: Medical notes (optional)
            reference_number: Custom reference number (defaults to patient's ref)

        Returns:
            Visit ID if successful, None otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get patient's reference number if not provided
                if reference_number is None:
                    cursor.execute("SELECT reference_number FROM patients WHERE patient_id = ?", (patient_id,))
                    row = cursor.fetchone()
                    if row and row[0]:
                        reference_number = row[0]
                    else:
                        # Fallback to next available if patient doesn't have one
                        reference_number = self.get_next_reference_number()
                        # Also update patient's record with this new reference number
                        cursor.execute("UPDATE patients SET reference_number = ? WHERE patient_id = ?", (reference_number, patient_id))

                cursor.execute("""
                    INSERT INTO visit_logs
                    (patient_id, reference_number, visit_date, visit_time, weight_kg, height_cm,
                     blood_pressure, temperature_celsius, medical_notes, visit_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (patient_id, reference_number, visit_date, visit_time, weight, height, bp or None, temp, notes or None, visit_type))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding visit: {e}")
            return None

    def get_last_encoded_visit_date(self) -> Optional[str]:
        """Get the visit_date of the most recently created 'encode' type visit.

        Returns:
            Date string in YYYY-MM-DD format, or None if no encoded visits exist.
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT visit_date FROM visit_logs WHERE visit_type = 'encode' ORDER BY created_at DESC LIMIT 1"
                )
                row = cursor.fetchone()
                return row[0] if row else None
        except sqlite3.Error:
            return None

    def get_visits_by_date(self, date_str: str) -> List[Dict]:
        """
        Get all visits for a specific date with patient information - OPTIMIZED

        Args:
            date_str: Date string in YYYY-MM-DD format

        Returns:
            List of visit dictionaries with patient names
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT v.visit_id, v.reference_number, v.visit_date, v.visit_time, v.weight_kg, v.height_cm,
                           v.blood_pressure, v.temperature_celsius, v.medical_notes, v.created_at,
                           p.patient_id, p.first_name, p.middle_name, p.last_name,
                           (p.last_name || ', ' || p.first_name ||
                            CASE WHEN p.middle_name IS NOT NULL THEN ' ' || p.middle_name ELSE '' END) as full_name
                    FROM visit_logs v
                    JOIN patients p ON v.patient_id = p.patient_id
                    WHERE v.visit_date = ?
                    ORDER BY v.reference_number DESC
                """, (date_str,))
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []
    
    def get_patient_visits(self, patient_id: int) -> List[Dict]:
        """
        Get all visits for a specific patient

        Args:
            patient_id: ID of the patient

        Returns:
            List of visit dictionaries for the patient
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM visit_logs
                    WHERE patient_id = ?
                    ORDER BY reference_number DESC
                """, (patient_id,))
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    def get_patient_visits_paginated(self, patient_id: int, page: int = 1, per_page: int = 10, 
                                    start_date: str = None, end_date: str = None) -> tuple:
        """
        Get visits for a patient with pagination and optional date filters

        Args:
            patient_id: ID of the patient
            page: Page number
            per_page: Records per page
            start_date: YYYY-MM-DD
            end_date: YYYY-MM-DD

        Returns:
            Tuple of (list of visits, total count)
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query_cond = "WHERE patient_id = ?"
                params = [patient_id]
                
                if start_date:
                    query_cond += " AND visit_date >= ?"
                    params.append(start_date)
                if end_date:
                    query_cond += " AND visit_date <= ?"
                    params.append(end_date)

                # Get total count
                cursor.execute(f"SELECT COUNT(*) FROM visit_logs {query_cond}", params)
                total = cursor.fetchone()[0]

                # Get paginated results
                offset = (page - 1) * per_page
                cursor.execute(f"""
                    SELECT * FROM visit_logs
                    {query_cond}
                    ORDER BY reference_number DESC
                    LIMIT ? OFFSET ?
                """, params + [per_page, offset])
                
                visits = [dict(row) for row in cursor.fetchall()]
                return visits, total
        except sqlite3.Error:
            return [], 0

    def get_all_visits(self) -> List[Dict]:
        """
        Get all visits with patient information, ordered by reference number

        Returns:
            List of all visit dictionaries with patient names
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT v.visit_id, v.reference_number, v.visit_date, v.visit_time, v.weight_kg, v.height_cm,
                           v.blood_pressure, v.temperature_celsius, v.medical_notes, v.created_at,
                           p.patient_id, p.first_name, p.middle_name, p.last_name,
                           (p.last_name || ', ' || p.first_name ||
                            CASE WHEN p.middle_name IS NOT NULL THEN ' ' || p.middle_name ELSE '' END) as full_name
                    FROM visit_logs v
                    JOIN patients p ON v.patient_id = p.patient_id
                    ORDER BY v.reference_number DESC
                """)
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    def get_visits_paginated(self, page: int = 1, per_page: int = 10, query: str = "", 
                             start_date: str = None, end_date: str = None) -> tuple:
        """
        Get visits with pagination and optional search/date filters

        Args:
            page: Page number (1-indexed)
            per_page: Records per page
            query: Search string for patient name or reference number
            start_date: YYYY-MM-DD
            end_date: YYYY-MM-DD

        Returns:
            Tuple of (list of visits, total count)
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query_cond = "WHERE 1=1"
                params = []
                
                if query:
                    clean_query = query.replace("-", "")
                    query_cond += " AND (p.first_name LIKE ? OR p.middle_name LIKE ? OR p.last_name LIKE ? OR CAST(p.reference_number AS TEXT) LIKE ?)"
                    params.extend([f"%{query}%", f"%{query}%", f"%{query}%", f"%{clean_query}%"])
                
                if start_date:
                    query_cond += " AND v.visit_date >= ?"
                    params.append(start_date)
                if end_date:
                    query_cond += " AND v.visit_date <= ?"
                    params.append(end_date)

                # Get total count
                cursor.execute(f"""
                    SELECT COUNT(*) 
                    FROM visit_logs v
                    JOIN patients p ON v.patient_id = p.patient_id
                    {query_cond}
                """, params)
                total = cursor.fetchone()[0]

                # Get paginated results - prioritized p.reference_number
                offset = (page - 1) * per_page
                cursor.execute(f"""
                    SELECT v.visit_id, COALESCE(p.reference_number, v.reference_number) as reference_number, 
                           v.visit_date, v.visit_time, v.weight_kg, v.height_cm,
                           v.blood_pressure, v.temperature_celsius, v.medical_notes, v.created_at,
                           p.patient_id, p.first_name, p.middle_name, p.last_name,
                           (p.last_name || ', ' || p.first_name ||
                            CASE WHEN p.middle_name IS NOT NULL THEN ' ' || p.middle_name ELSE '' END) as full_name
                    FROM visit_logs v
                    JOIN patients p ON v.patient_id = p.patient_id
                    {query_cond}
                    ORDER BY v.visit_date DESC, v.visit_time DESC, v.reference_number DESC
                    LIMIT ? OFFSET ?
                """, params + [per_page, offset])
                
                visits = [dict(row) for row in cursor.fetchall()]
                return visits, total
                return visits, total
        except sqlite3.Error as e:
            print(f"Paginated visits error: {e}")
            return [], 0
    
    def get_visit_by_id(self, visit_id: int) -> Optional[Dict]:
        """
        Get a single visit by ID with patient information

        Args:
            visit_id: ID of the visit

        Returns:
            Visit dictionary or None if not found
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT v.visit_id, v.reference_number, v.visit_date, v.visit_time, v.weight_kg, v.height_cm,
                           v.blood_pressure, v.temperature_celsius, v.medical_notes, v.created_at,
                           p.patient_id, p.first_name, p.middle_name, p.last_name, p.date_of_birth,
                           (p.last_name || ', ' || p.first_name ||
                            CASE WHEN p.middle_name IS NOT NULL THEN ' ' || p.middle_name ELSE '' END) as full_name
                    FROM visit_logs v
                    JOIN patients p ON v.patient_id = p.patient_id
                    WHERE v.visit_id = ?
                """, (visit_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error:
            return None

    def get_visit_by_reference(self, reference_number: int) -> Optional[Dict]:
        """
        Get a single visit by reference number with patient information

        Args:
            reference_number: Reference number of the visit

        Returns:
            Visit dictionary or None if not found
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT v.visit_id, v.reference_number, v.visit_date, v.visit_time, v.weight_kg, v.height_cm,
                           v.blood_pressure, v.temperature_celsius, v.medical_notes, v.created_at,
                           p.patient_id, p.first_name, p.middle_name, p.last_name, p.date_of_birth,
                           (p.last_name || ', ' || p.first_name ||
                            CASE WHEN p.middle_name IS NOT NULL THEN ' ' || p.middle_name ELSE '' END) as full_name
                    FROM visit_logs v
                    JOIN patients p ON v.patient_id = p.patient_id
                    WHERE v.reference_number = ?
                """, (reference_number,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error:
            return None

    def update_visit(self, visit_id: int, visit_date: str, visit_time: str,
                    weight: Optional[float] = None, height: Optional[float] = None,
                    bp: str = "", temp: Optional[float] = None, notes: str = "",
                    reference_number: Optional[int] = None) -> bool:
        """
        Update an existing visit record

        Args:
            visit_id: ID of the visit to update
            visit_date: Date of visit in YYYY-MM-DD format
            visit_time: Time of visit in HH:MM:SS format
            weight: Weight in kg (optional)
            height: Height in cm (optional)
            bp: Blood pressure reading (optional)
            temp: Temperature in celsius (optional)
            notes: Medical notes (optional)
            reference_number: Reference number (optional, only update if provided)

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # If reference_number is provided, we should check if it belongs to a DIFFERENT patient
                # and potentially update the patient_id of this visit log.
                if reference_number is not None:
                    cursor.execute("SELECT patient_id FROM patients WHERE reference_number = ?", (reference_number,))
                    row = cursor.fetchone()
                    if row:
                        new_patient_id = row[0]
                        cursor.execute("""
                            UPDATE visit_logs
                            SET patient_id = ?, reference_number = ?, visit_date = ?, visit_time = ?, 
                                weight_kg = ?, height_cm = ?, blood_pressure = ?, 
                                temperature_celsius = ?, medical_notes = ?,
                                modified_at = CURRENT_TIMESTAMP
                            WHERE visit_id = ?
                        """, (new_patient_id, reference_number, visit_date, visit_time, weight, height, bp or None, temp, notes or None, visit_id))
                    else:
                        # If no patient has this ID, we just update the reference_number
                        cursor.execute("""
                            UPDATE visit_logs
                            SET reference_number = ?, visit_date = ?, visit_time = ?, weight_kg = ?, height_cm = ?,
                                blood_pressure = ?, temperature_celsius = ?, medical_notes = ?,
                                modified_at = CURRENT_TIMESTAMP
                            WHERE visit_id = ?
                        """, (reference_number, visit_date, visit_time, weight, height, bp or None, temp, notes or None, visit_id))
                else:
                    cursor.execute("""
                        UPDATE visit_logs
                        SET visit_date = ?, visit_time = ?, weight_kg = ?, height_cm = ?,
                            blood_pressure = ?, temperature_celsius = ?, medical_notes = ?,
                            modified_at = CURRENT_TIMESTAMP
                        WHERE visit_id = ?
                    """, (visit_date, visit_time, weight, height, bp or None, temp, notes or None, visit_id))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating visit: {e}")
            return False

    def get_patient_stats(self, patient_id: int) -> Dict:
        """
        Get patient statistics (visit counts, dates)

        Args:
            patient_id: ID of the patient

        Returns:
            Dictionary with statistics (total_visits, first_visit, last_visit)
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT
                        COUNT(*) as total_visits,
                        MIN(visit_date) as first_visit,
                        MAX(visit_date) as last_visit
                    FROM visit_logs
                    WHERE patient_id = ?
                """, (patient_id,))
                row = cursor.fetchone()
                return dict(row) if row else {}
        except sqlite3.Error:
            return {}
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ADMIN OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════════

    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash password with SHA-256"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def admin_exists(self) -> bool:
        """Check if any admin account exists"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM admin_users LIMIT 1")
                return cursor.fetchone() is not None
        except sqlite3.Error:
            return False

    def create_admin(self, username: str, password: str) -> bool:
        """Create a new admin account"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO admin_users (username, password_hash) VALUES (?, ?)",
                    (username, self._hash_password(password))
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
        except sqlite3.Error:
            return False

    def verify_admin(self, username: str, password: str) -> bool:
        """Verify admin credentials"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT password_hash FROM admin_users WHERE username = ?",
                    (username,)
                )
                row = cursor.fetchone()
                if row:
                    return row['password_hash'] == self._hash_password(password)
                return False
        except sqlite3.Error:
            return False

    def get_admin_username(self) -> Optional[str]:
        """Get the current admin username"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT username FROM admin_users LIMIT 1")
                row = cursor.fetchone()
                return row['username'] if row else None
        except sqlite3.Error:
            return None

    def update_admin_username(self, old_username: str, new_username: str) -> bool:
        """Update admin username"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE admin_users SET username = ? WHERE username = ?",
                    (new_username, old_username)
                )
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            return False
        except sqlite3.Error:
            return False

    def update_admin_password(self, username: str, new_password: str) -> bool:
        """Update admin password"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE admin_users SET password_hash = ? WHERE username = ?",
                    (self._hash_password(new_password), username)
                )
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error:
            return False

    # ═══════════════════════════════════════════════════════════════════════════
    # UTILITY OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def backup_database(self, destination: str = None) -> str:
        """
        Create database backup
        
        Args:
            destination: Backup file path (auto-generated if None)
            
        Returns:
            Path to backup file
            
        Raises:
            Exception if backup fails
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            if destination:
                backup_path = destination
            else:
                backup_path = f"backup_clinic_{timestamp}.db"
            shutil.copy2(self.db_name, backup_path)
            return backup_path
        except Exception as e:
            raise Exception(f"Backup failed: {e}")
    
    def merge_database(self, source_path: str) -> Dict:
        """
        Merge patients and visits from another .db file into the current database.
        Skips patients with duplicate reference_numbers, merges new visits for existing patients.

        Args:
            source_path: Path to the .db file to merge from

        Returns:
            Dict with merge stats: patients_added, visits_added, patients_skipped, errors
        """
        stats = {'patients_added': 0, 'visits_added': 0, 'patients_skipped': 0, 'visits_skipped': 0, 'errors': []}

        try:
            src_conn = sqlite3.connect(source_path)
            src_conn.row_factory = sqlite3.Row
            src_cursor = src_conn.cursor()

            # Verify the source DB has the expected tables
            src_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in src_cursor.fetchall()]
            if 'patients' not in tables:
                stats['errors'].append("Source database has no 'patients' table")
                src_conn.close()
                return stats

            has_visits = 'visit_logs' in tables

            # Build a mapping: source patient_id -> target patient_id
            patient_id_map = {}

            # Get all patients from source
            src_cursor.execute("SELECT * FROM patients")
            src_patients = [dict(row) for row in src_cursor.fetchall()]

            with self.get_connection() as conn:
                cursor = conn.cursor()

                for sp in src_patients:
                    src_pid = sp['patient_id']
                    ref_num = sp.get('reference_number')

                    # Check if patient with this reference_number already exists
                    if ref_num is not None:
                        cursor.execute("SELECT patient_id FROM patients WHERE reference_number = ?", (ref_num,))
                        existing = cursor.fetchone()
                        if existing:
                            # Patient already exists - map to existing and skip
                            patient_id_map[src_pid] = existing[0]
                            stats['patients_skipped'] += 1
                            continue

                    # Insert new patient (let autoincrement assign new patient_id)
                    try:
                        cursor.execute("""
                            INSERT INTO patients (reference_number, last_name, first_name, middle_name,
                                date_of_birth, sex, civil_status, occupation, parents, parent_contact,
                                school, contact_number, address, notes, registered_date)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            ref_num, sp.get('last_name', ''), sp.get('first_name', ''),
                            sp.get('middle_name'), sp.get('date_of_birth'), sp.get('sex'),
                            sp.get('civil_status'), sp.get('occupation'), sp.get('parents'),
                            sp.get('parent_contact'), sp.get('school'), sp.get('contact_number'),
                            sp.get('address'), sp.get('notes'), sp.get('registered_date')
                        ))
                        patient_id_map[src_pid] = cursor.lastrowid
                        stats['patients_added'] += 1
                    except sqlite3.IntegrityError as e:
                        stats['patients_skipped'] += 1
                        stats['errors'].append(f"Patient ref#{ref_num}: {e}")

                # Merge visits if the source DB has visit_logs
                if has_visits:
                    src_cursor.execute("SELECT * FROM visit_logs")
                    src_visits = [dict(row) for row in src_cursor.fetchall()]

                    for sv in src_visits:
                        src_pid = sv['patient_id']
                        target_pid = patient_id_map.get(src_pid)

                        if target_pid is None:
                            stats['visits_skipped'] += 1
                            continue

                        # Check for duplicate visit (same patient, same date, same time)
                        cursor.execute("""
                            SELECT 1 FROM visit_logs
                            WHERE patient_id = ? AND visit_date = ? AND visit_time = ?
                        """, (target_pid, sv.get('visit_date'), sv.get('visit_time')))
                        if cursor.fetchone():
                            stats['visits_skipped'] += 1
                            continue

                        try:
                            cursor.execute("""
                                INSERT INTO visit_logs (patient_id, reference_number, visit_date,
                                    visit_time, weight_kg, height_cm, blood_pressure,
                                    temperature_celsius, medical_notes, created_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                target_pid, sv.get('reference_number'), sv.get('visit_date'),
                                sv.get('visit_time'), sv.get('weight_kg'), sv.get('height_cm'),
                                sv.get('blood_pressure'), sv.get('temperature_celsius'),
                                sv.get('medical_notes'), sv.get('created_at')
                            ))
                            stats['visits_added'] += 1
                        except sqlite3.Error as e:
                            stats['visits_skipped'] += 1
                            stats['errors'].append(f"Visit: {e}")

                conn.commit()

            src_conn.close()
        except sqlite3.Error as e:
            stats['errors'].append(f"Database error: {e}")
        except Exception as e:
            stats['errors'].append(f"Error: {e}")

        return stats

    def export_to_csv(self, filepath: str) -> bool:
        """
        Export all visit data to CSV file - UPDATED
        
        Args:
            filepath: Destination CSV file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        p.patient_id, p.last_name, p.first_name, p.middle_name, 
                        p.date_of_birth, p.sex, p.occupation, p.parents, p.parent_contact, p.school,
                        p.contact_number, p.address,
                        v.visit_id, v.visit_date, v.visit_time, v.weight_kg, v.height_cm, 
                        v.blood_pressure, v.temperature_celsius, v.medical_notes, v.created_at
                    FROM visit_logs v
                    JOIN patients p ON v.patient_id = p.patient_id
                    ORDER BY v.visit_date DESC, v.visit_time DESC
                """)
                data = cursor.fetchall()
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Patient ID", "Last Name", "First Name", "Middle Name", 
                               "DOB", "Sex", "Occupation", "Parents", "Parent Contact", "School",
                               "Contact", "Address",
                               "Visit ID", "Date", "Time", "Weight (kg)", "Height (cm)", 
                               "BP", "Temp (°C)", "Notes", "Timestamp"])
                writer.writerows(data)
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False