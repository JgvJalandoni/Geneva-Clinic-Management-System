"""
Patient-related dialogs for Tita's Clinic Management System
Handles new patient creation, editing, and patient history viewing
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
from dialogs.base import BaseDialog
from config import COLORS, FONT_FAMILY
from utils import validate_patient_name, validate_contact_number


class NewPatientDialog(BaseDialog):
    """Dialog for creating new patient"""
    
    def __init__(self, parent, db, callback):
        """
        Initialize new patient dialog
        
        Args:
            parent: Parent window
            db: ClinicDatabase instance
            callback: Function to call after patient creation (receives patient_id)
        """
        super().__init__(parent, "➕ New Patient Registration", 500, 650)
        
        self.db = db
        self.callback = callback
        self.result = None
        
        self.build_ui()
    
    def build_ui(self):
        """Build the dialog UI"""
        # Header
        self.create_header("➕", "New Patient Registration", 
                          color=COLORS['accent_blue'], height=80)
        
        # Scrollable Form
        form_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        form_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Form Fields
        self.entry_name = self.create_form_field(
            form_container, "Full Name *", "e.g., Juan Dela Cruz")
        self.entry_address = self.create_form_field(
            form_container, "Address", "e.g., 123 Main St, Quezon City")
        self.entry_contact = self.create_form_field(
            form_container, "Contact Number", "e.g., 09123456789")
        self.entry_dob = self.create_form_field(
            form_container, "Date of Birth", "YYYY-MM-DD (optional)")
        
        # Patient Notes
        ctk.CTkLabel(form_container, text="Patient Notes",
                    font=(FONT_FAMILY, 14),
                    text_color=COLORS['text_secondary']).pack(anchor="w", pady=(10, 5))
        self.txt_notes = ctk.CTkTextbox(form_container, height=100,
                                       fg_color=COLORS['bg_card'],
                                       border_width=1,
                                       border_color=COLORS['border'])
        self.txt_notes.pack(fill="x", pady=(0, 10))
        
        # Info Box
        self.create_info_box(form_container, 
                           "Only Full Name is required. Other fields are optional.")
        
        # Buttons
        self.create_button_bar(form_container, [
            {'text': 'Cancel', 'command': self.destroy, 'style': 'secondary', 'side': 'left'},
            {'text': '✓ Create Patient', 'command': self.save_patient, 'style': 'primary', 'side': 'right'}
        ])
    
    def save_patient(self):
        """Validate and save new patient"""
        name = self.entry_name.get().strip()
        
        # Validate name
        is_valid, error_msg = validate_patient_name(name)
        if not is_valid:
            messagebox.showerror("Validation Error", error_msg, parent=self)
            return
        
        # Validate contact if provided
        contact = self.entry_contact.get().strip()
        is_valid, warning_msg = validate_contact_number(contact)
        if not is_valid:
            if not messagebox.askyesno("Warning", 
                f"{warning_msg}\n\nSave anyway?", parent=self):
                return
        
        # Create patient
        patient_id = self.db.add_patient(
            full_name=name,
            address=self.entry_address.get().strip(),
            contact=contact,
            dob=self.entry_dob.get().strip(),
            notes=self.txt_notes.get("1.0", "end-1c").strip()
        )
        
        if patient_id:
            self.result = patient_id
            messagebox.showinfo("Success", 
                              f"✓ Patient created successfully!\n\nPatient ID: {patient_id}", 
                              parent=self)
            self.callback(patient_id)
            self.destroy()
        else:
            messagebox.showerror("Error", 
                               "Failed to create patient. Please try again.", 
                               parent=self)


class EditPatientDialog(BaseDialog):
    """Dialog for editing existing patient"""
    
    def __init__(self, parent, db, patient_id: int, callback):
        """
        Initialize edit patient dialog
        
        Args:
            parent: Parent window
            db: ClinicDatabase instance
            patient_id: ID of patient to edit
            callback: Function to call after update
        """
        super().__init__(parent, f"✏️ Edit Patient #{patient_id}", 500, 650)
        
        self.db = db
        self.patient_id = patient_id
        self.callback = callback
        
        self.build_ui()
        self.load_data()
    
    def build_ui(self):
        """Build the dialog UI"""
        # Header
        self.create_header("✏️", f"Edit Patient #{self.patient_id}",
                          color=COLORS['accent_orange'], height=80)
        
        # Form
        form_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        form_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Form Fields
        self.entry_name = self.create_form_field(form_container, "Full Name *", "")
        self.entry_address = self.create_form_field(form_container, "Address", "")
        self.entry_contact = self.create_form_field(form_container, "Contact Number", "")
        self.entry_dob = self.create_form_field(form_container, "Date of Birth", "YYYY-MM-DD")
        
        # Patient Notes
        ctk.CTkLabel(form_container, text="Patient Notes",
                    font=(FONT_FAMILY, 14),
                    text_color=COLORS['text_secondary']).pack(anchor="w", pady=(10, 5))
        self.txt_notes = ctk.CTkTextbox(form_container, height=100,
                                       fg_color=COLORS['bg_card'],
                                       border_width=1,
                                       border_color=COLORS['border'])
        self.txt_notes.pack(fill="x", pady=(0, 10))
        
        # Buttons
        self.create_button_bar(form_container, [
            {'text': 'Cancel', 'command': self.destroy, 'style': 'secondary', 'side': 'left'},
            {'text': '✓ Save Changes', 'command': self.update_patient, 'style': 'primary', 'side': 'right'}
        ])
    
    def load_data(self):
        """Load existing patient data"""
        patient = self.db.get_patient(self.patient_id)
        if patient:
            self.entry_name.insert(0, patient['full_name'] or "")
            self.entry_address.insert(0, patient['address'] or "")
            self.entry_contact.insert(0, patient['contact_number'] or "")
            self.entry_dob.insert(0, patient['date_of_birth'] or "")
            self.txt_notes.insert("1.0", patient['notes'] or "")
    
    def update_patient(self):
        """Validate and update patient"""
        name = self.entry_name.get().strip()
        
        # Validate name
        is_valid, error_msg = validate_patient_name(name)
        if not is_valid:
            messagebox.showerror("Validation Error", error_msg, parent=self)
            return
        
        # Update patient
        if self.db.update_patient(
            patient_id=self.patient_id,
            full_name=name,
            address=self.entry_address.get().strip(),
            contact=self.entry_contact.get().strip(),
            dob=self.entry_dob.get().strip(),
            notes=self.txt_notes.get("1.0", "end-1c").strip()
        ):
            messagebox.showinfo("Success", "✓ Patient updated successfully!", parent=self)
            self.callback()
            self.destroy()
        else:
            messagebox.showerror("Error", "Failed to update patient.", parent=self)


class PatientHistoryDialog(BaseDialog):
    """Dialog showing complete patient history"""
    
    def __init__(self, parent, db, patient_id: int):
        """
        Initialize patient history dialog
        
        Args:
            parent: Parent window
            db: ClinicDatabase instance
            patient_id: ID of patient to show history for
        """
        super().__init__(parent, "📊 Patient History", 900, 600)
        
        self.db = db
        self.patient_id = patient_id
        
        self.build_ui()
        self.load_data()
    
    def build_ui(self):
        """Build the dialog UI"""
        # Header
        header = self.create_header("📊", "", "", 
                                   color=COLORS['accent_blue'], height=120)
        
        # Patient name (will be filled by load_data)
        self.lbl_patient_name = ctk.CTkLabel(header, text="Loading...",
                                            font=(FONT_FAMILY, 20, "bold"))
        self.lbl_patient_name.pack()
        
        # Stats (will be filled by load_data)
        self.lbl_stats = ctk.CTkLabel(header, text="",
                                     font=(FONT_FAMILY, 13),
                                     text_color="#e3f2fd")
        self.lbl_stats.pack(pady=(5, 10))
        
        # Content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Table
        self.tree = self.create_history_treeview(content)
        
        # Close button
        self.create_button_bar(content, [
            {'text': 'Close', 'command': self.destroy, 'style': 'secondary'}
        ])
    
    def create_history_treeview(self, parent):
        """Create treeview for visit history"""
        # Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("History.Treeview",
                       background=COLORS['bg_card'],
                       foreground=COLORS['text_primary'],
                       fieldbackground=COLORS['bg_card'],
                       borderwidth=0,
                       rowheight=48,
                       font=(FONT_FAMILY, 14))
        style.configure("History.Treeview.Heading",
                       background=COLORS['border'],
                       foreground=COLORS['text_primary'],
                       relief="flat",
                       font=(FONT_FAMILY, 14, "bold"))
        style.map("History.Treeview",
                 background=[("selected", COLORS['accent_blue'])])
        
        # Tree container
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="both", expand=True)
        
        # Treeview
        tree = ttk.Treeview(container,
                           columns=("date", "time", "weight", "height", "bp", "temp", "notes"),
                           show="headings",
                           style="History.Treeview")
        
        # Configure columns
        tree.heading("date", text="Date")
        tree.heading("time", text="Time")
        tree.heading("weight", text="Weight (kg)")
        tree.heading("height", text="Height (cm)")
        tree.heading("bp", text="Blood Pressure")
        tree.heading("temp", text="Temp (°C)")
        tree.heading("notes", text="Medical Notes")
        
        tree.column("date", width=100, anchor="center")
        tree.column("time", width=90, anchor="center")
        tree.column("weight", width=90, anchor="center")
        tree.column("height", width=90, anchor="center")
        tree.column("bp", width=120, anchor="center")
        tree.column("temp", width=80, anchor="center")
        tree.column("notes", width=300)
        
        # Scrollbar
        scrollbar = ctk.CTkScrollbar(container, orientation="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        return tree
    
    def load_data(self):
        """Load patient data and visit history"""
        from utils import format_time_12hr
        
        # Load patient info
        patient = self.db.get_patient(self.patient_id)
        if patient:
            self.lbl_patient_name.configure(text=patient['full_name'])
            
            # Load stats
            stats = self.db.get_patient_stats(self.patient_id)
            stats_text = f"ID: {self.patient_id} | Total Visits: {stats.get('total_visits', 0)}"
            if stats.get('first_visit'):
                stats_text += f" | First Visit: {stats['first_visit']}"
            if stats.get('last_visit'):
                stats_text += f" | Last Visit: {stats['last_visit']}"
            self.lbl_stats.configure(text=stats_text)
        
        # Load visit history
        visits = self.db.get_patient_visits(self.patient_id)
        for visit in visits:
            self.tree.insert("", "end", values=(
                visit['visit_date'],
                format_time_12hr(visit.get('visit_time')),
                f"{visit['weight_kg']}" if visit['weight_kg'] else "—",
                f"{visit['height_cm']}" if visit['height_cm'] else "—",
                visit['blood_pressure'] or "—",
                f"{visit['temperature_celsius']}" if visit['temperature_celsius'] else "—",
                (visit['medical_notes'] or "")[:50]
            ))
