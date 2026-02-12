"""
Visit-related dialogs for Tita's Clinic Management System
Handles quick visit entry workflow (patient search + visit form)
"""

import customtkinter as ctk
from tkinter import messagebox
from dialogs.base import BaseDialog
from config import COLORS, FONT_FAMILY
from utils import (
    format_time_12hr, format_timestamp, parse_time_input,
    get_current_date, get_current_time_12hr, get_current_time_24hr,
    validate_date, validate_weight, validate_height, validate_temperature,
    safe_float
)


class QuickVisitSearchDialog(BaseDialog):
    """Step 1: Search and select patient for quick visit"""
    
    def __init__(self, parent, db, callback):
        """
        Initialize patient search dialog
        
        Args:
            parent: Parent window
            db: ClinicDatabase instance
            callback: Function to call with selected patient (patient_id, patient_name)
        """
        super().__init__(parent, "🔍 Quick Visit - Select Patient", 850, 750)
        
        self.db = db
        self.callback = callback
        
        self.build_ui()
        self.load_recent_patients()
    
    def build_ui(self):
        """Build the dialog UI"""
        # Header
        self.create_header("🔍", "Quick Visit Entry - Select Patient",
                          "Search or select from recent patients",
                          color=COLORS['accent_green'], height=90)
        
        # Content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Search Box
        search_frame = ctk.CTkFrame(content, fg_color=COLORS['bg_card'], corner_radius=10)
        search_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(search_frame, text="Search Patient:",
                    font=(FONT_FAMILY, 14, "bold"),
                    text_color=COLORS['text_secondary']).pack(anchor="w", padx=15, pady=(15, 5))
        
        self.entry_search = ctk.CTkEntry(search_frame,
                                        placeholder_text="Type patient name...",
                                        height=44,
                                        font=(FONT_FAMILY, 13),
                                        fg_color=COLORS['bg_dark'],
                                        border_width=1,
                                        border_color=COLORS['border'])
        self.entry_search.pack(fill="x", padx=15, pady=(0, 15))
        self.entry_search.bind("<KeyRelease>", lambda e: self.search_patients())
        self.entry_search.focus_set()
        
        # Results Label
        self.lbl_results = ctk.CTkLabel(content, text="Recent Patients:",
                                       font=(FONT_FAMILY, 14, "bold"),
                                       text_color=COLORS['text_secondary'])
        self.lbl_results.pack(anchor="w", pady=(0, 10))
        
        # Results Container (Scrollable)
        self.results_container = ctk.CTkScrollableFrame(content,
                                                        fg_color=COLORS['bg_card'],
                                                        corner_radius=10)
        self.results_container.pack(fill="both", expand=True)
        
        # Buttons
        self.create_button_bar(content, [
            {'text': '+ Create New Patient', 'command': self.create_new_patient, 
             'style': 'primary', 'side': 'left'},
            {'text': 'Cancel', 'command': self.destroy, 
             'style': 'secondary', 'side': 'right'}
        ])
    
    def load_recent_patients(self):
        """Load recent patients (most recent visits)"""
        self.search_patients()
    
    def search_patients(self):
        """Search patients and display results"""
        query = self.entry_search.get().strip()
        
        # Update label
        if query:
            self.lbl_results.configure(text=f"Search Results for '{query}':")
        else:
            self.lbl_results.configure(text="Recent Patients:")
        
        # Clear previous results
        for widget in self.results_container.winfo_children():
            widget.destroy()
        
        # Get results
        patients = self.db.search_patients(query)
        
        if not patients:
            ctk.CTkLabel(self.results_container,
                        text="No patients found" if query else "No patients in database",
                        font=(FONT_FAMILY, 14),
                        text_color=COLORS['text_secondary']).pack(pady=20)
            return
        
        # Display results as clickable cards
        for patient in patients:
            self.create_patient_card(patient)
    
    def create_patient_card(self, patient: dict):
        """Create a clickable patient card"""
        card = ctk.CTkFrame(self.results_container,
                           fg_color=COLORS['bg_dark'],
                           corner_radius=8,
                           cursor="hand2")
        card.pack(fill="x", padx=10, pady=5)
        
        # Make card clickable
        card.bind("<Button-1>", lambda e: self.select_patient(patient))
        
        # Content
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=12)
        content_frame.bind("<Button-1>", lambda e: self.select_patient(patient))
        
        # Name (bold, larger)
        name_label = ctk.CTkLabel(content_frame,
                                 text=f"👤 {patient['last_name']}, {patient['first_name']}",
                                 font=(FONT_FAMILY, 14, "bold"),
                                 text_color=COLORS['text_primary'],
                                 anchor="w")
        name_label.pack(anchor="w")
        name_label.bind("<Button-1>", lambda e: self.select_patient(patient))
        
        # Info row
        from utils import format_phone_number, format_reference_number
        ref_num = format_reference_number(patient.get('reference_number'))
        info_parts = [f"ID: {ref_num}"]
        if patient.get('contact_number'):
            info_parts.append(f"📞 {format_phone_number(patient['contact_number'])}")
        if patient.get('last_visit'):
            from utils import format_date_readable
            info_parts.append(f"Last visit: {format_date_readable(patient['last_visit'])}")
        
        info_label = ctk.CTkLabel(content_frame,
                                 text=" | ".join(info_parts),
                                 font=(FONT_FAMILY, 13),
                                 text_color=COLORS['text_secondary'],
                                 anchor="w")
        info_label.pack(anchor="w", pady=(3, 0))
        info_label.bind("<Button-1>", lambda e: self.select_patient(patient))
        
        # Hover effect
        def on_enter(e):
            card.configure(fg_color=COLORS['bg_card_hover'])
        
        def on_leave(e):
            card.configure(fg_color=COLORS['bg_dark'])
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        for child in [content_frame, name_label, info_label]:
            child.bind("<Enter>", on_enter)
            child.bind("<Leave>", on_leave)
    
    def select_patient(self, patient: dict):
        """Patient selected - proceed to visit form"""
        self.destroy()
        full_name = f"{patient['last_name']}, {patient['first_name']}"
        # Pass patient_id, full_name, AND reference_number
        self.callback(patient['patient_id'], full_name, patient.get('reference_number'))
    
    def create_new_patient(self):
        """Open new patient dialog"""
        self.destroy()
        # Trigger new patient dialog in parent
        if hasattr(self.master, 'open_new_patient_dialog'):
            self.master.open_new_patient_dialog()


class QuickVisitFormDialog(BaseDialog):
    """Step 2: Quick visit entry form - Optimized Horizontal Layout"""
    
    def __init__(self, parent, db, patient_id: int, patient_name: str, reference_number: int, callback):
        """
        Initialize visit form dialog
        """
        super().__init__(parent, f"📋 Quick Visit - {patient_name}", 1100, 600)
        
        self.db = db
        self.patient_id = patient_id
        self.patient_name = patient_name
        self.reference_number = reference_number
        self.callback = callback
        
        self.build_ui()
    
    def build_ui(self):
        """Build the dialog UI"""
        from utils import format_reference_number
        formatted_ref = format_reference_number(self.reference_number)
        
        # Header - Slimmer
        self.create_header("📋", "Quick Visit Entry",
                          f"Patient: {self.patient_name} (ID: {formatted_ref})",
                          color=COLORS['accent_green'], height=80)
        
        # Form Container (No scroll if possible)
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=25, pady=20)
        
        # --- ROW 1: CORE DATA ---
        core_frame = ctk.CTkFrame(container, fg_color=COLORS['bg_card'], corner_radius=15)
        core_frame.pack(fill="x", pady=(0, 15))
        
        inner_core = ctk.CTkFrame(core_frame, fg_color="transparent")
        inner_core.pack(fill="x", padx=15, pady=15)
        
        # Ref
        ref_f = ctk.CTkFrame(inner_core, fg_color="transparent")
        ref_f.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(ref_f, text="PATIENT ID #", font=(FONT_FAMILY, 12, "bold"), text_color=COLORS['accent_orange']).pack(anchor="w")
        
        ref_row = ctk.CTkFrame(ref_f, fg_color="transparent")
        ref_row.pack()
        
        self.entry_ref = ctk.CTkEntry(ref_row, height=40, width=100, font=(FONT_FAMILY, 16, "bold"), justify="center")
        self.entry_ref.pack(side="left", pady=2)
        
        # Use existing reference number or get next if new patient
        current_ref = self.reference_number or self.db.get_next_reference_number()
        self.entry_ref.insert(0, str(current_ref))
        
        ctk.CTkButton(ref_row, text="📋 History", command=self._view_history,
                     fg_color=COLORS['bg_dark'], text_color=COLORS['text_primary'],
                     width=90, height=40, corner_radius=12, border_width=1, border_color=COLORS['border']).pack(side="left", padx=10)

        # Date
        date_f = ctk.CTkFrame(inner_core, fg_color="transparent")
        date_f.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(date_f, text="DATE (MM/DD/YYYY)", font=(FONT_FAMILY, 12, "bold"), text_color=COLORS['accent_blue']).pack(anchor="w")
        self.entry_date = ctk.CTkEntry(date_f, height=40, width=150)
        self.entry_date.pack(pady=2)
        from utils import get_current_date
        self.entry_date.insert(0, get_current_date())

        # Time
        time_f = ctk.CTkFrame(inner_core, fg_color="transparent")
        time_f.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(time_f, text="TIME", font=(FONT_FAMILY, 12, "bold"), text_color=COLORS['accent_blue']).pack(anchor="w")
        self.entry_time = ctk.CTkEntry(time_f, height=40, placeholder_text="HH:MM AM/PM")
        self.entry_time.pack(fill="x", pady=2)
        from utils import get_current_time_12hr
        self.entry_time.insert(0, get_current_time_12hr())

        # --- ROW 2: VITALS & NOTES ---
        details_row = ctk.CTkFrame(container, fg_color="transparent")
        details_row.pack(fill="both", expand=True)

        # Vitals (Left)
        v_card = ctk.CTkFrame(details_row, fg_color=COLORS['bg_card'], corner_radius=15)
        v_card.pack(side="left", fill="y", padx=(0, 15))
        
        v_inner = ctk.CTkFrame(v_card, fg_color="transparent")
        v_inner.pack(padx=15, pady=15)
        
        ctk.CTkLabel(v_inner, text="VITALS", font=(FONT_FAMILY, 12, "bold"), text_color=COLORS['text_secondary']).pack(anchor="w", pady=(0, 10))
        v_grid = ctk.CTkFrame(v_inner, fg_color="transparent")
        v_grid.pack()
        
        self.entry_weight = self.create_grid_field(v_grid, "Weight", "65", 0, 0)
        self.entry_height = self.create_grid_field(v_grid, "Height", "170", 0, 1)
        self.entry_bp = self.create_grid_field(v_grid, "BP", "120/80", 1, 0)
        self.entry_temp = self.create_grid_field(v_grid, "Temp", "37", 1, 1)

        # Notes (Right)
        n_card = ctk.CTkFrame(details_row, fg_color=COLORS['bg_card'], corner_radius=15)
        n_card.pack(side="left", fill="both", expand=True)
        
        n_inner = ctk.CTkFrame(n_card, fg_color="transparent")
        n_inner.pack(fill="both", expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(n_inner, text="MEDICAL NOTES", font=(FONT_FAMILY, 12, "bold"), text_color=COLORS['text_secondary']).pack(anchor="w")
        self.txt_notes = ctk.CTkTextbox(n_inner, font=(FONT_FAMILY, 14), border_width=1, border_color=COLORS['border'])
        self.txt_notes.pack(fill="both", expand=True, pady=(5, 0))

        # --- BUTTONS ---
        self.create_button_bar(container, [
            {'text': '← Back', 'command': self.go_back, 'style': 'secondary', 'side': 'left'},
            {'text': '✓ SAVE VISIT', 'command': self.save_visit, 'style': 'primary', 'side': 'right'}
        ])
    
    def create_grid_field(self, parent, label, placeholder, row, col):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=row, column=col, padx=5, pady=5)
        ctk.CTkLabel(f, text=label, font=(FONT_FAMILY, 10, "bold")).pack(anchor="w")
        e = ctk.CTkEntry(f, width=100, height=35, placeholder_text=placeholder)
        e.pack()
        return e
    
    def _view_history(self):
        """Open visit logs for selected patient"""
        from main import PatientVisitLogsDialog
        # Mock patient data for the dialog
        p_data = {'patient_id': self.patient_id, 'last_name': self.patient_name.split(',')[0], 'first_name': self.patient_name.split(',')[-1].strip()}
        PatientVisitLogsDialog(self, self.db, self.patient_id, p_data)

    def go_back(self):
        """Return to patient search"""
        self.destroy()
        QuickVisitSearchDialog(self.master, self.db,
                             lambda pid, name, ref: QuickVisitFormDialog(
                                 self.master, self.db, pid, name, ref, self.callback))
    
    def save_visit(self):
        """Validate and save visit"""
        visit_date_ui = self.entry_date.get().strip()
        time_input = self.entry_time.get().strip()
        
        from utils import validate_date, ui_date_to_db
        # Validate date
        is_valid, error_msg = validate_date(visit_date_ui)
        if not is_valid:
            messagebox.showerror("Validation Error", error_msg, parent=self)
            return
            
        visit_date = ui_date_to_db(visit_date_ui)
        
        # Parse time
        visit_time = parse_time_input(time_input)
        if not visit_time:
            if not messagebox.askyesno("Invalid Time",
                "Time format not recognized. Save without time?", parent=self):
                return
            visit_time = get_current_time_24hr()
            
        # Reference number
        try:
            raw_ref = self.entry_ref.get().strip()
            if not raw_ref:
                reference_number = self.reference_number
            else:
                reference_number = int(raw_ref)
                
            # If changed, check if it belongs to someone else
            if reference_number != self.reference_number:
                existing = self.db.get_patient_by_reference(reference_number)
                if existing:
                    full_name = f"{existing['last_name']}, {existing['first_name']}"
                    if not messagebox.askyesno("Patient ID Taken", 
                        f"Patient ID #{reference_number} is already taken by:\n\n{full_name}\n\nReassign this visit log to this patient?", 
                        parent=self):
                        return
        except ValueError:
            messagebox.showerror("Validation Error", "Invalid reference number! Please enter digits only.", parent=self)
            return
        
        # Parse and validate vitals
        weight = safe_float(self.entry_weight.get())
        height = safe_float(self.entry_height.get())
        temp = safe_float(self.entry_temp.get())
        
        # Save visit
        visit_id = self.db.add_visit(
            patient_id=self.patient_id,
            visit_date=visit_date,
            visit_time=visit_time,
            weight=weight,
            height=height,
            bp=self.entry_bp.get().strip(),
            temp=temp,
            notes=self.txt_notes.get("1.0", "end-1c").strip(),
            reference_number=reference_number
        )
        
        if visit_id:
            self.show_success(visit_id, visit_date_ui, visit_time, reference_number)
        else:
            messagebox.showerror("Error", "Failed to save visit.", parent=self)
    
    def show_success(self, visit_id: int, visit_date: str, visit_time: str, reference_number: int):
        """Show success dialog with options"""
        self.destroy()
        
        # Success dialog
        success_dialog = BaseDialog(self.master, "✅ Visit Saved", 400, 320)
        
        # Header
        success_dialog.create_header("✅", "Visit Saved Successfully!",
                                    color=COLORS['accent_green'], height=80)
        
        # Content
        content = ctk.CTkFrame(success_dialog, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=30)
        
        info_card = ctk.CTkFrame(content, fg_color=COLORS['bg_card'], corner_radius=10)
        info_card.pack(fill="x", pady=(0, 20))
        
        from utils import format_reference_number
        info_text = f"""Patient: {self.patient_name}
Reference: {format_reference_number(reference_number)}
Date: {visit_date}
Time: {format_time_12hr(visit_time)}"""
        
        ctk.CTkLabel(info_card, text=info_text,
                    font=(FONT_FAMILY, 14),
                    text_color=COLORS['text_primary'],
                    justify="left").pack(padx=20, pady=15)
        
        # Buttons
        def add_another():
            success_dialog.destroy()
            self.callback()
            QuickVisitSearchDialog(self.master, self.db,
                                 lambda pid, name, ref: QuickVisitFormDialog(
                                     self.master, self.db, pid, name, ref, self.callback))
        
        def close():
            success_dialog.destroy()
            self.callback()
        
        success_dialog.create_button_bar(content, [
            {'text': 'Close', 'command': close, 
             'style': 'secondary', 'side': 'left'},
            {'text': '➕ Add Another Visit', 'command': add_another, 
             'style': 'primary', 'side': 'right'}
        ])
