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
    """Horizontal New Patient dialog to eliminate scrolling"""
    
    def __init__(self, parent, db, callback):
        """
        Initialize new patient dialog
        """
        super().__init__(parent, "➕ New Patient Registration", 1150, 450) # Wide but short
        
        self.db = db
        self.callback = callback
        self.result = None
        self.show_more_details = False
        
        self.build_ui()
    
    def build_ui(self):
        """Build the dialog UI with horizontal layout"""
        # Header
        self.create_header("➕", "New Patient Registration", 
                          color=COLORS['accent_blue'], height=60)
        
        # Form Container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # --- ROW 1: PERSONAL INFORMATION ---
        core_frame = ctk.CTkFrame(container, fg_color=COLORS['bg_card'], corner_radius=15)
        core_frame.pack(fill="x", pady=(0, 15))
        
        inner_core = ctk.CTkFrame(core_frame, fg_color="transparent")
        inner_core.pack(fill="x", padx=20, pady=20)

        # Name Row
        name_row = ctk.CTkFrame(inner_core, fg_color="transparent")
        name_row.pack(fill="x", pady=(0, 15))
        
        # Add Patient ID field
        self.entry_ref_num = self._add_field(name_row, "Patient ID #", 120)
        self.entry_ref_num.insert(0, str(self.db.get_next_reference_number()))
        
        self.entry_last_name = self._add_field(name_row, "Last Name *", 280)
        self.entry_first_name = self._add_field(name_row, "First Name *", 280)
        self.entry_middle_name = self._add_field(name_row, "Middle Name", 220)

        # DOB & Basic Row
        det_row = ctk.CTkFrame(inner_core, fg_color="transparent")
        det_row.pack(fill="x")

        self.entry_dob = self._add_field(det_row, "Date of Birth (MM/DD/YYYY)", 250)
        self.entry_sex = self._add_field(det_row, "Sex", 200)
        
        # Toggle Button
        self.btn_toggle_details = ctk.CTkButton(container, text="➕ Add more details (Occupation, School, Family, Contact)", 
                                               command=self.toggle_more_details,
                                               fg_color="transparent", text_color=COLORS['accent_blue'],
                                               hover_color=COLORS['bg_card_hover'],
                                               font=(FONT_FAMILY, 13, "bold"), height=35)
        self.btn_toggle_details.pack(fill="x", pady=(0, 10))

        # --- MORE DETAILS (HIDDEN) ---
        self.more_details_frame = ctk.CTkFrame(container, fg_color=COLORS['bg_card'], corner_radius=15)
        
        inner_more = ctk.CTkFrame(self.more_details_frame, fg_color="transparent")
        inner_more.pack(fill="both", expand=True, padx=20, pady=20)

        # Occ/School row
        occ_row = ctk.CTkFrame(inner_more, fg_color="transparent")
        occ_row.pack(fill="x", pady=(0, 15))
        self.entry_occupation = self._add_field(occ_row, "Occupation", 450)
        self.entry_school = self._add_field(occ_row, "School", 450)

        # Family & Contact side-by-side
        split_row = ctk.CTkFrame(inner_more, fg_color="transparent")
        split_row.pack(fill="x")

        fam_col = ctk.CTkFrame(split_row, fg_color="transparent")
        fam_col.pack(side="left", fill="both", expand=True, padx=(0, 20))
        ctk.CTkLabel(fam_col, text="FAMILY INFORMATION", font=(FONT_FAMILY, 11, "bold"), text_color=COLORS['accent_blue']).pack(anchor="w")
        self.entry_parents = self._add_field(fam_col, "Parents' Names", 450, pack=True)
        self.entry_parent_contact = self._add_field(fam_col, "Parent Contact Number", 450, pack=True)

        con_col = ctk.CTkFrame(split_row, fg_color="transparent")
        con_col.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(con_col, text="PATIENT CONTACT", font=(FONT_FAMILY, 11, "bold"), text_color=COLORS['accent_blue']).pack(anchor="w")
        self.entry_contact = self._add_field(con_col, "Contact Number", 450, pack=True)
        ctk.CTkLabel(con_col, text="Address", font=(FONT_FAMILY, 12, "bold")).pack(anchor="w", pady=(10, 0))
        self.entry_address = ctk.CTkTextbox(con_col, height=60, font=(FONT_FAMILY, 13), border_width=1, border_color=COLORS['border'])
        self.entry_address.pack(fill="x", pady=2)

        ctk.CTkLabel(inner_more, text="Additional Notes", font=(FONT_FAMILY, 12, "bold")).pack(anchor="w", pady=(10, 0))
        self.txt_notes = ctk.CTkTextbox(inner_more, height=60, font=(FONT_FAMILY, 13), border_width=1, border_color=COLORS['border'])
        self.txt_notes.pack(fill="x", pady=2)

        # Info Box (Always at bottom)
        self.info_box = self.create_info_box(container, 
                           "Last Name and First Name are required. Other fields are optional.")
        
        # Buttons (Always at bottom)
        self.button_bar = self.create_button_bar(container, [
            {'text': 'Cancel', 'command': self.destroy, 'style': 'secondary', 'side': 'left'},
            {'text': '✓ Create Patient', 'command': self.save_patient, 'style': 'primary', 'side': 'right'}
        ])

    def _add_field(self, parent, label, width, pack=False):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        if pack: f.pack(fill="x", pady=2)
        else: f.pack(side="left", padx=(0, 15))
        ctk.CTkLabel(f, text=label, font=(FONT_FAMILY, 12, "bold")).pack(anchor="w")
        e = ctk.CTkEntry(f, width=width, height=35)
        e.pack(pady=2)
        return e

    def toggle_more_details(self):
        """Toggle optional fields visibility"""
        self.show_more_details = not self.show_more_details
        if self.show_more_details:
            self.info_box.pack_forget()
            self.button_bar.pack_forget()
            self.more_details_frame.pack(fill="x", pady=(0, 15))
            self.info_box.pack(fill="x", pady=10)
            self.button_bar.pack(fill="x", pady=(15, 0))
            self.btn_toggle_details.configure(text="➖ Hide details")
            self.geometry("1150x880")
        else:
            self.more_details_frame.pack_forget()
            self.btn_toggle_details.configure(text="➕ Add more details")
            self.geometry("1150x450")
    
    def save_patient(self):
        """Validate and save new patient"""
        last_name = self.entry_last_name.get().strip()
        first_name = self.entry_first_name.get().strip()
        
        if not last_name or not first_name:
            messagebox.showerror("Validation Error", "Last Name and First Name are required.", parent=self)
            return
        
        # Patient ID (Reference Number)
        existing_patient_id = None
        try:
            raw_ref = self.entry_ref_num.get().strip()
            ref_num = int(raw_ref) if raw_ref else None
            if ref_num:
                existing = self.db.get_patient_by_reference(ref_num)
                if existing:
                    full_name = f"{existing['last_name']}, {existing['first_name']}"
                    if messagebox.askyesno("Patient ID Taken", 
                        f"Patient ID #{ref_num} is already taken by:\n\n{full_name}\n\nWould you like to OVERWRITE this patient's information?", 
                        parent=self):
                        existing_patient_id = existing['patient_id']
                    else:
                        return
        except ValueError:
            messagebox.showerror("Validation Error", "Patient ID must be a number!", parent=self)
            return

        # Validate contact if provided
        contact = self.entry_contact.get().strip()
        is_valid, warning_msg = validate_contact_number(contact)
        if not is_valid:
            if not messagebox.askyesno("Warning", 
                f"{warning_msg}\n\nSave anyway?", parent=self):
                return
        
        # Create or update patient
        if existing_patient_id:
            success = self.db.update_patient(
                patient_id=existing_patient_id,
                last_name=last_name,
                first_name=first_name,
                middle_name=self.entry_middle_name.get().strip(),
                dob=self.entry_dob.get().strip(),
                sex=self.entry_sex.get().strip(),
                occupation=self.entry_occupation.get().strip(),
                parents=self.entry_parents.get().strip(),
                parent_contact=self.entry_parent_contact.get().strip(),
                school=self.entry_school.get().strip(),
                contact=contact,
                address=self.entry_address.get().strip(),
                notes=self.txt_notes.get("1.0", "end-1c").strip(),
                reference_number=ref_num
            )
            patient_id = existing_patient_id if success else None
        else:
            patient_id = self.db.add_patient(
                last_name=last_name,
                first_name=first_name,
                middle_name=self.entry_middle_name.get().strip(),
                dob=self.entry_dob.get().strip(),
                sex=self.entry_sex.get().strip(),
                occupation=self.entry_occupation.get().strip(),
                parents=self.entry_parents.get().strip(),
                parent_contact=self.entry_parent_contact.get().strip(),
                school=self.entry_school.get().strip(),
                contact=contact,
                address=self.entry_address.get().strip(),
                notes=self.txt_notes.get("1.0", "end-1c").strip(),
                reference_number=ref_num
            )
        
        if patient_id:
            self.result = patient_id
            from utils import format_reference_number
            formatted_ref = format_reference_number(ref_num or patient_id)
            messagebox.showinfo("Success", 
                              f"✓ Patient created successfully!\n\nPatient ID: {formatted_ref}", 
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
        super().__init__(parent, f"✏️ Edit Patient #{patient_id}", 850, 750)
        
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
        self.entry_ref_num = self.create_form_field(form_container, "Patient ID #", "")
        self.entry_last_name = self.create_form_field(form_container, "Last Name *", "")
        self.entry_first_name = self.create_form_field(form_container, "First Name *", "")
        self.entry_middle_name = self.create_form_field(form_container, "Middle Name", "")
        self.entry_dob = self.create_form_field(form_container, "Date of Birth", "MM/DD/YYYY")
        self.entry_sex = self.create_form_field(form_container, "Sex", "")
        self.entry_civil_status = self.create_form_field(form_container, "Civil Status", "")
        self.entry_occupation = self.create_form_field(form_container, "Occupation", "")
        self.entry_school = self.create_form_field(form_container, "School", "")
        self.entry_parents = self.create_form_field(form_container, "Parents", "")
        self.entry_parent_contact = self.create_form_field(form_container, "Parent Contact", "")
        self.entry_address = self.create_form_field(form_container, "Address", "")
        self.entry_contact = self.create_form_field(form_container, "Contact Number", "")
        
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
            self.entry_ref_num.insert(0, str(patient['reference_number']) if patient.get('reference_number') else "")
            self.entry_last_name.insert(0, patient['last_name'] or "")
            self.entry_first_name.insert(0, patient['first_name'] or "")
            self.entry_middle_name.insert(0, patient['middle_name'] or "")
            from utils import db_date_to_ui
            self.entry_dob.insert(0, db_date_to_ui(patient['date_of_birth']))
            self.entry_sex.insert(0, patient['sex'] or "")
            self.entry_civil_status.insert(0, patient['civil_status'] or "")
            self.entry_occupation.insert(0, patient['occupation'] or "")
            self.entry_school.insert(0, patient['school'] or "")
            self.entry_parents.insert(0, patient['parents'] or "")
            self.entry_parent_contact.insert(0, patient['parent_contact'] or "")
            self.entry_address.insert(0, patient['address'] or "")
            self.entry_contact.insert(0, patient['contact_number'] or "")
            self.txt_notes.insert("1.0", patient['notes'] or "")
    
    def update_patient(self):
        """Validate and update patient"""
        last_name = self.entry_last_name.get().strip()
        first_name = self.entry_first_name.get().strip()
        
        if not last_name or not first_name:
            messagebox.showerror("Validation Error", "Last Name and First Name are required.", parent=self)
            return
        
        # Patient ID (Reference Number)
        try:
            raw_ref = self.entry_ref_num.get().strip()
            ref_num = int(raw_ref) if raw_ref else None
            # Only check if changed
            patient = self.db.get_patient(self.patient_id)
            if ref_num and ref_num != patient.get('reference_number'):
                if not self.db.is_reference_number_available(ref_num):
                    messagebox.showerror("Validation Error", f"Patient ID #{ref_num} is already taken!", parent=self)
                    return
        except ValueError:
            messagebox.showerror("Validation Error", "Patient ID must be a number!", parent=self)
            return

        from utils import ui_date_to_db
        # Update patient
        if self.db.update_patient(
            patient_id=self.patient_id,
            last_name=last_name,
            first_name=first_name,
            middle_name=self.entry_middle_name.get().strip(),
            dob=ui_date_to_db(self.entry_dob.get().strip()),
            sex=self.entry_sex.get().strip(),
            civil_status=self.entry_civil_status.get().strip(),
            occupation=self.entry_occupation.get().strip(),
            parents=self.entry_parents.get().strip(),
            parent_contact=self.entry_parent_contact.get().strip(),
            school=self.entry_school.get().strip(),
            address=self.entry_address.get().strip(),
            contact=self.entry_contact.get().strip(),
            notes=self.txt_notes.get("1.0", "end-1c").strip(),
            reference_number=ref_num
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
        super().__init__(parent, "📊 Patient History", 1100, 700)
        
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
            from utils import format_reference_number
            formatted_ref = format_reference_number(patient.get('reference_number'))
            stats_text = f"ID: {formatted_ref} | Total Visits: {stats.get('total_visits', 0)}"
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
