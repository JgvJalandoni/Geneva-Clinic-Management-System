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
        self.init_db()
    
    def get_connection(self) -> sqlite3.Connection:
        """Create and return a database connection with Row factory"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database schema - OPTIMIZED structure with separated name fields"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Patients Table - OPTIMIZED with separated name fields
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS patients (
                        patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        first_name TEXT NOT NULL,
                        middle_name TEXT,
                        last_name TEXT NOT NULL,
                        date_of_birth TEXT,
                        contact_number TEXT,
                        address TEXT,
                        notes TEXT,
                        registered_date TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Visit Logs Table - with reference_number for encoding old records
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
                        FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
                    )
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
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_visit_date ON visit_logs(visit_date)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_patient_visits ON visit_logs(patient_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_reference_number ON visit_logs(reference_number)")
                cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_reference ON visit_logs(reference_number)")
                
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
            raise
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PATIENT OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def add_patient(self, first_name: str, middle_name: str, last_name: str,
                   dob: str = "", contact: str = "", address: str = "", notes: str = "") -> Optional[int]:
        """
        Create new patient record - OPTIMIZED with separated name fields
        
        Args:
            first_name: Patient's first name (required)
            middle_name: Patient's middle name (optional)
            last_name: Patient's last name (required)
            dob: Date of birth in YYYY-MM-DD format (optional)
            contact: Contact number (optional)
            address: Patient's address (optional)
            notes: Additional notes (optional)
            
        Returns:
            Patient ID if successful, None otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO patients (first_name, middle_name, last_name, date_of_birth, 
                                        contact_number, address, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (first_name, middle_name or None, last_name, dob or None, 
                      contact or None, address or None, notes or None))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding patient: {e}")
            return None
    
    def update_patient(self, patient_id: int, first_name: str, middle_name: str, last_name: str,
                      dob: str = "", contact: str = "", address: str = "", notes: str = "") -> bool:
        """
        Update existing patient record - OPTIMIZED
        
        Args:
            patient_id: ID of patient to update
            first_name: Updated first name
            middle_name: Updated middle name
            last_name: Updated last name
            dob: Updated date of birth
            contact: Updated contact number
            address: Updated address
            notes: Updated notes
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE patients 
                    SET first_name=?, middle_name=?, last_name=?, date_of_birth=?, 
                        contact_number=?, address=?, notes=?
                    WHERE patient_id=?
                """, (first_name, middle_name or None, last_name, dob or None, 
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
    
    def search_patients(self, query: str) -> List[Dict]:
        """
        Search patients by name (first, middle, or last) - OPTIMIZED with indices
        
        Args:
            query: Search query string
            
        Returns:
            List of patient dictionaries matching the query
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                if not query or len(query) < 2:
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
                    # Search across first, middle, and last name - uses indices
                    cursor.execute("""
                        SELECT p.*, MAX(v.visit_date) as last_visit
                        FROM patients p
                        LEFT JOIN visit_logs v ON p.patient_id = v.patient_id
                        WHERE p.first_name LIKE ? OR p.middle_name LIKE ? OR p.last_name LIKE ?
                        GROUP BY p.patient_id
                        ORDER BY p.last_name, p.first_name
                        LIMIT 50
                    """, (f'%{query}%', f'%{query}%', f'%{query}%'))
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []
    
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
    
    # ═══════════════════════════════════════════════════════════════════════════
    # VISIT OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════════

    def get_next_reference_number(self) -> int:
        """
        Get the next available reference number

        Returns:
            Next reference number (max + 1, or 1 if no visits exist)
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT MAX(reference_number) FROM visit_logs")
                result = cursor.fetchone()[0]
                return (result or 0) + 1
        except sqlite3.Error:
            return 1

    def is_reference_number_available(self, ref_num: int) -> bool:
        """
        Check if a reference number is available (not already used)

        Args:
            ref_num: Reference number to check

        Returns:
            True if available, False if already exists
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM visit_logs WHERE reference_number = ?", (ref_num,))
                return cursor.fetchone() is None
        except sqlite3.Error:
            return False

    def add_visit(self, patient_id: int, visit_date: str, visit_time: str,
                 weight: Optional[float] = None, height: Optional[float] = None,
                 bp: str = "", temp: Optional[float] = None, notes: str = "",
                 reference_number: Optional[int] = None) -> Optional[int]:
        """
        Create new visit record

        Args:
            patient_id: ID of the patient
            visit_date: Date of visit in YYYY-MM-DD format
            visit_time: Time of visit in HH:MM:SS format
            weight: Weight in kg (optional)
            height: Height in cm (optional)
            bp: Blood pressure reading (optional)
            temp: Temperature in celsius (optional)
            notes: Medical notes (optional)
            reference_number: Custom reference number (auto-generated if None)

        Returns:
            Visit ID if successful, None otherwise
        """
        try:
            # Auto-generate reference number if not provided
            if reference_number is None:
                reference_number = self.get_next_reference_number()

            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO visit_logs
                    (patient_id, reference_number, visit_date, visit_time, weight_kg, height_cm,
                     blood_pressure, temperature_celsius, medical_notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (patient_id, reference_number, visit_date, visit_time, weight, height, bp or None, temp, notes or None))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding visit: {e}")
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

    def get_visits_paginated(self, page: int = 1, per_page: int = 10) -> tuple:
        """
        Get visits with pagination

        Args:
            page: Page number (1-indexed)
            per_page: Records per page

        Returns:
            Tuple of (list of visits, total count)
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Get total count
                cursor.execute("SELECT COUNT(*) FROM visit_logs")
                total = cursor.fetchone()[0]

                # Get paginated results
                offset = (page - 1) * per_page
                cursor.execute("""
                    SELECT v.visit_id, v.reference_number, v.visit_date, v.visit_time, v.weight_kg, v.height_cm,
                           v.blood_pressure, v.temperature_celsius, v.medical_notes, v.created_at,
                           p.patient_id, p.first_name, p.middle_name, p.last_name,
                           (p.last_name || ', ' || p.first_name ||
                            CASE WHEN p.middle_name IS NOT NULL THEN ' ' || p.middle_name ELSE '' END) as full_name
                    FROM visit_logs v
                    JOIN patients p ON v.patient_id = p.patient_id
                    ORDER BY v.reference_number DESC
                    LIMIT ? OFFSET ?
                """, (per_page, offset))
                visits = [dict(row) for row in cursor.fetchall()]
                return visits, total
        except sqlite3.Error:
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
                if reference_number is not None:
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
    
    def export_to_csv(self, filepath: str) -> bool:
        """
        Export all visit data to CSV file - OPTIMIZED
        
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
                        p.patient_id, p.first_name, p.middle_name, p.last_name, 
                        p.date_of_birth, p.contact_number, p.address,
                        v.visit_id, v.visit_date, v.visit_time, v.weight_kg, v.height_cm, 
                        v.blood_pressure, v.temperature_celsius, v.medical_notes, v.created_at
                    FROM visit_logs v
                    JOIN patients p ON v.patient_id = p.patient_id
                    ORDER BY v.visit_date DESC, v.visit_time DESC
                """)
                data = cursor.fetchall()
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Patient ID", "First Name", "Middle Name", "Last Name", 
                               "DOB", "Contact", "Address",
                               "Visit ID", "Date", "Time", "Weight (kg)", "Height (cm)", 
                               "BP", "Temp (°C)", "Notes", "Timestamp"])
                writer.writerows(data)
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False