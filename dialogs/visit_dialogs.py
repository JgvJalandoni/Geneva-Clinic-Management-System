"""
Visit-related dialogs for Tita's Clinic Management System
Handles quick visit entry workflow (patient search + visit form)
"""

import customtkinter as ctk
from tkinter import messagebox
from dialogs.base import BaseDialog
from config import COLORS
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
        super().__init__(parent, "🔍 Quick Visit - Select Patient", 650, 650)
        
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
                    font=("Segoe UI", 12, "bold"),
                    text_color=COLORS['text_secondary']).pack(anchor="w", padx=15, pady=(15, 5))
        
        self.entry_search = ctk.CTkEntry(search_frame,
                                        placeholder_text="Type patient name...",
                                        height=40,
                                        font=("Segoe UI", 13),
                                        fg_color=COLORS['bg_dark'],
                                        border_width=1,
                                        border_color=COLORS['border'])
        self.entry_search.pack(fill="x", padx=15, pady=(0, 15))
        self.entry_search.bind("<KeyRelease>", lambda e: self.search_patients())
        self.entry_search.focus_set()
        
        # Results Label
        self.lbl_results = ctk.CTkLabel(content, text="Recent Patients:",
                                       font=("Segoe UI", 12, "bold"),
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
                        font=("Segoe UI", 12),
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
                                 text=f"👤 {patient['full_name']}",
                                 font=("Segoe UI", 14, "bold"),
                                 text_color=COLORS['text_primary'],
                                 anchor="w")
        name_label.pack(anchor="w")
        name_label.bind("<Button-1>", lambda e: self.select_patient(patient))
        
        # Info row
        info_parts = [f"ID: {patient['patient_id']}"]
        if patient.get('contact_number'):
            info_parts.append(f"📞 {patient['contact_number']}")
        if patient.get('last_visit'):
            info_parts.append(f"Last visit: {patient['last_visit']}")
        
        info_label = ctk.CTkLabel(content_frame,
                                 text=" | ".join(info_parts),
                                 font=("Segoe UI", 11),
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
        self.callback(patient['patient_id'], patient['full_name'])
    
    def create_new_patient(self):
        """Open new patient dialog"""
        self.destroy()
        # Trigger new patient dialog in parent
        if hasattr(self.master, 'open_new_patient_dialog'):
            self.master.open_new_patient_dialog()


class QuickVisitFormDialog(BaseDialog):
    """Step 2: Quick visit entry form"""
    
    def __init__(self, parent, db, patient_id: int, patient_name: str, callback):
        """
        Initialize visit form dialog
        
        Args:
            parent: Parent window
            db: ClinicDatabase instance
            patient_id: ID of selected patient
            patient_name: Name of selected patient
            callback: Function to call after visit saved
        """
        super().__init__(parent, f"📋 Quick Visit - {patient_name}", 550, 720)
        
        self.db = db
        self.patient_id = patient_id
        self.patient_name = patient_name
        self.callback = callback
        
        self.build_ui()
    
    def build_ui(self):
        """Build the dialog UI"""
        # Header
        self.create_header("📋", "Quick Visit Entry",
                          f"Patient: {self.patient_name} (ID: {self.patient_id})",
                          color=COLORS['accent_green'], height=100)
        
        # Form
        form = ctk.CTkScrollableFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Date & Time Section
        datetime_frame = ctk.CTkFrame(form, fg_color=COLORS['bg_card'], corner_radius=10)
        datetime_frame.pack(fill="x", pady=(0, 15))
        
        dt_inner = ctk.CTkFrame(datetime_frame, fg_color="transparent")
        dt_inner.pack(fill="x", padx=15, pady=15)
        dt_inner.columnconfigure((0, 1), weight=1)
        
        # Date
        date_frame = ctk.CTkFrame(dt_inner, fg_color="transparent")
        date_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        ctk.CTkLabel(date_frame, text="📅 Visit Date",
                    font=("Segoe UI", 11, "bold"),
                    text_color=COLORS['text_secondary']).pack(anchor="w")
        self.entry_date = ctk.CTkEntry(date_frame, height=38,
                                      fg_color=COLORS['bg_dark'],
                                      border_width=1, border_color=COLORS['border'])
        self.entry_date.insert(0, get_current_date())
        self.entry_date.pack(fill="x", pady=(5, 0))
        
        # Time
        time_frame = ctk.CTkFrame(dt_inner, fg_color="transparent")
        time_frame.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        ctk.CTkLabel(time_frame, text="🕐 Visit Time",
                    font=("Segoe UI", 11, "bold"),
                    text_color=COLORS['text_secondary']).pack(anchor="w")
        self.entry_time = ctk.CTkEntry(time_frame, height=38,
                                      fg_color=COLORS['bg_dark'],
                                      border_width=1, border_color=COLORS['border'],
                                      placeholder_text="HH:MM AM/PM")
        self.entry_time.insert(0, get_current_time_12hr())
        self.entry_time.pack(fill="x", pady=(5, 0))
        
        # Vitals Section
        ctk.CTkLabel(form, text="Vital Signs (Optional)",
                    font=("Segoe UI", 13, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w", pady=(0, 10))
        
        vitals_card = ctk.CTkFrame(form, fg_color=COLORS['bg_card'], corner_radius=10)
        vitals_card.pack(fill="x", pady=(0, 15))
        
        grid = ctk.CTkFrame(vitals_card, fg_color="transparent")
        grid.pack(fill="x", padx=15, pady=15)
        grid.columnconfigure((0, 1), weight=1)
        
        self.entry_weight = self.create_grid_field(grid, "⚖️ Weight (kg)", "e.g., 65.5", 0, 0)
        self.entry_height = self.create_grid_field(grid, "📏 Height (cm)", "e.g., 170", 0, 1)
        self.entry_bp = self.create_grid_field(grid, "🩺 Blood Pressure", "e.g., 120/80", 1, 0)
        self.entry_temp = self.create_grid_field(grid, "🌡️ Temperature (°C)", "e.g., 37.2", 1, 1)
        
        # Medical Notes
        ctk.CTkLabel(form, text="📝 Medical Notes / Diagnosis",
                    font=("Segoe UI", 13, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w", pady=(0, 10))
        
        self.txt_notes = ctk.CTkTextbox(form, height=120,
                                       fg_color=COLORS['bg_card'],
                                       border_width=1, border_color=COLORS['border'],
                                       font=("Segoe UI", 12))
        self.txt_notes.pack(fill="x", pady=(0, 15))
        self.txt_notes.focus_set()
        
        # Buttons
        self.create_button_bar(form, [
            {'text': '← Back', 'command': self.go_back, 
             'style': 'secondary', 'side': 'left'},
            {'text': '✓ SAVE VISIT', 'command': self.save_visit, 
             'style': 'primary', 'side': 'right'}
        ])
    
    def create_grid_field(self, parent, label: str, placeholder: str, 
                         row: int, col: int) -> ctk.CTkEntry:
        """Create a grid form field"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=col, sticky="ew", padx=5, pady=5)
        
        ctk.CTkLabel(frame, text=label,
                    font=("Segoe UI", 11, "bold"),
                    text_color=COLORS['text_secondary']).pack(anchor="w")
        entry = ctk.CTkEntry(frame, height=35, placeholder_text=placeholder,
                           fg_color=COLORS['bg_dark'],
                           border_width=1, border_color=COLORS['border'])
        entry.pack(fill="x", pady=(3, 0))
        return entry
    
    def go_back(self):
        """Return to patient search"""
        self.destroy()
        QuickVisitSearchDialog(self.master, self.db,
                             lambda pid, name: QuickVisitFormDialog(
                                 self.master, self.db, pid, name, self.callback))
    
    def save_visit(self):
        """Validate and save visit"""
        visit_date = self.entry_date.get().strip()
        time_input = self.entry_time.get().strip()
        
        # Validate date
        is_valid, error_msg = validate_date(visit_date)
        if not is_valid:
            messagebox.showerror("Validation Error", error_msg, parent=self)
            return
        
        # Parse time
        visit_time = parse_time_input(time_input)
        if not visit_time:
            if not messagebox.askyesno("Invalid Time",
                "Time format not recognized. Save without time?", parent=self):
                return
            visit_time = get_current_time_24hr()
        
        # Parse and validate vitals
        weight = safe_float(self.entry_weight.get())
        height = safe_float(self.entry_height.get())
        temp = safe_float(self.entry_temp.get())
        
        is_valid, error_msg = validate_weight(weight)
        if not is_valid:
            messagebox.showerror("Validation Error", error_msg, parent=self)
            return
        
        is_valid, error_msg = validate_height(height)
        if not is_valid:
            messagebox.showerror("Validation Error", error_msg, parent=self)
            return
        
        is_valid, error_msg = validate_temperature(temp)
        if not is_valid:
            messagebox.showerror("Validation Error", error_msg, parent=self)
            return
        
        # Save visit
        visit_id = self.db.add_visit(
            patient_id=self.patient_id,
            visit_date=visit_date,
            visit_time=visit_time,
            weight=weight,
            height=height,
            bp=self.entry_bp.get().strip(),
            temp=temp,
            notes=self.txt_notes.get("1.0", "end-1c").strip()
        )
        
        if visit_id:
            self.show_success(visit_id, visit_date, visit_time)
        else:
            messagebox.showerror("Error", "Failed to save visit.", parent=self)
    
    def show_success(self, visit_id: int, visit_date: str, visit_time: str):
        """Show success dialog with options"""
        self.destroy()
        
        # Success dialog
        success_dialog = BaseDialog(self.master, "✅ Visit Saved", 400, 300)
        
        # Header
        success_dialog.create_header("✅", "Visit Saved Successfully!",
                                    color=COLORS['accent_green'], height=80)
        
        # Content
        content = ctk.CTkFrame(success_dialog, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=30)
        
        info_card = ctk.CTkFrame(content, fg_color=COLORS['bg_card'], corner_radius=10)
        info_card.pack(fill="x", pady=(0, 20))
        
        info_text = f"""Patient: {self.patient_name}
Visit ID: #{visit_id}
Date: {visit_date}
Time: {format_time_12hr(visit_time)}"""
        
        ctk.CTkLabel(info_card, text=info_text,
                    font=("Segoe UI", 12),
                    text_color=COLORS['text_primary'],
                    justify="left").pack(padx=20, pady=15)
        
        # Buttons
        def add_another():
            success_dialog.destroy()
            self.callback()
            QuickVisitSearchDialog(self.master, self.db,
                                 lambda pid, name: QuickVisitFormDialog(
                                     self.master, self.db, pid, name, self.callback))
        
        def close():
            success_dialog.destroy()
            self.callback()
        
        success_dialog.create_button_bar(content, [
            {'text': 'Close', 'command': close, 
             'style': 'secondary', 'side': 'left'},
            {'text': '➕ Add Another Visit', 'command': add_another, 
             'style': 'primary', 'side': 'right'}
        ])
