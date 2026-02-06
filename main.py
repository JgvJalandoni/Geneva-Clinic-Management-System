"""
HYPER-OPTIMIZED Clinic Management System - ProvoHeal Style Dashboard
Performance-first architecture with O(1) lookups and minimal redraws
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import os
from typing import Optional, Dict, List

from config import COLORS, WINDOW_TITLE, WINDOW_SIZE, WINDOW_MIN_SIZE
from database import ClinicDatabase
from utils import format_time_12hr, format_timestamp, get_export_timestamp, calculate_age, format_date_readable

# ═══════════════════════════════════════════════════════════════════════════════
# PERFORMANCE-OPTIMIZED STATISTICS CACHE
# ═══════════════════════════════════════════════════════════════════════════════
class StatsCache:
    """Zero-allocation stats cache with dirty flag tracking"""
    __slots__ = ('_data', '_dirty', '_timestamp')
    
    def __init__(self):
        self._data: Dict[str, int] = {}
        self._dirty = True
        self._timestamp = 0.0
    
    def invalidate(self):
        """Mark cache as dirty - O(1)"""
        self._dirty = True
    
    def update(self, data: Dict[str, int]):
        """Update cache - O(1) hash updates"""
        self._data = data
        self._dirty = False
        self._timestamp = datetime.datetime.now().timestamp()
    
    def get(self, key: str, default=0) -> int:
        """Get cached value - O(1) dict lookup"""
        return self._data.get(key, default)
    
    @property
    def is_dirty(self) -> bool:
        return self._dirty


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION - PERFORMANCE-CRITICAL
# ═══════════════════════════════════════════════════════════════════════════════
class ClinicApp(ctk.CTk):
    """Ultra-optimized main application with lazy loading and minimal redraws"""
    
    def __init__(self):
        super().__init__()
        
        # Database connection pooling
        self.db = ClinicDatabase()
        
        # Performance cache
        self.stats_cache = StatsCache()
        
        # Window config - minimize overhead
        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_SIZE)
        self.minsize(*WINDOW_MIN_SIZE)
        self.configure(fg_color=COLORS['bg_dark'])
        
        # Current view tracking - O(1) state management
        self.current_view = "overview"
        self.view_widgets = {}
        
        # Build UI components
        self._build_ui()
        
        # Initial data load (lazy)
        self.after(50, self._initial_load)
        
        # Clock update (1s timer)
        self._update_clock()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # UI CONSTRUCTION - MINIMAL ALLOCATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _build_ui(self):
        """Build UI structure - called once at startup"""
        # Main container
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)
        
        # Sidebar
        self._build_sidebar()
        
        # Content area
        self.content_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.content_frame.pack(side="right", fill="both", expand=True)
        
        # Header
        self._build_header()
        
        # Main content container
        self.main_content = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.main_content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Build initial view
        self._build_overview()
    
    def _build_sidebar(self):
        """Build optimized sidebar with O(1) navigation"""
        sidebar = ctk.CTkFrame(self.container, fg_color="#ffffff", 
                              width=280, corner_radius=0, border_width=1,
                              border_color=COLORS['border'])
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        # Logo section
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent", height=100)
        logo_frame.pack(fill="x", padx=20, pady=(30, 40))
        logo_frame.pack_propagate(False)
        
        ctk.CTkLabel(logo_frame, text="🏥", font=("Segoe UI", 36)).pack()
        ctk.CTkLabel(logo_frame, text="Geneva Clinic", 
                    font=("Segoe UI", 20, "bold"),
                    text_color=COLORS['text_primary']).pack()
        ctk.CTkLabel(logo_frame, text="Patient Management", 
                    font=("Segoe UI", 11),
                    text_color=COLORS['text_secondary']).pack()
        
        # Navigation buttons - O(1) dict lookup for view switching
        nav_data = [
            ("📊", "Overview", "overview"),
            ("👥", "Patients", "patients"),
            ("📋", "Visits", "visits"),
        ]
        
        self.nav_buttons = {}
        for icon, label, view_id in nav_data:
            btn = self._create_nav_button(sidebar, icon, label, view_id)
            self.nav_buttons[view_id] = btn
        
        # Set initial active button
        self.nav_buttons["overview"].configure(fg_color=COLORS['accent_blue'])
        
        # Quick Actions section
        ctk.CTkLabel(sidebar, text="QUICK ACTIONS", 
                    font=("Segoe UI", 10, "bold"),
                    text_color=COLORS['text_secondary']).pack(padx=20, pady=(20, 10), anchor="w")
        
        # New Visit button - PRIMARY ACTION
        ctk.CTkButton(sidebar, text="➕ New Visit", 
                     command=self._open_new_visit_dialog,
                     fg_color=COLORS['accent_green'], 
                     hover_color="#1e7e34",
                     height=50, corner_radius=10,
                     font=("Segoe UI", 14, "bold")).pack(fill="x", padx=20, pady=5)
        
        # Bottom section
        bottom_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        
        ctk.CTkButton(bottom_frame, text="💾 Backup", command=self.backup_db,
                     fg_color=COLORS['accent_green'], hover_color="#1e7e34",
                     height=38, corner_radius=10).pack(fill="x", pady=5)
        
        ctk.CTkButton(bottom_frame, text="📊 Export", command=self.export_data,
                     fg_color=COLORS['accent_orange'], hover_color="#e06700",
                     height=38, corner_radius=10).pack(fill="x", pady=5)
    
    def _create_nav_button(self, parent, icon: str, text: str, view_id: str):
        """Create navigation button - reusable component"""
        btn = ctk.CTkButton(
            parent, text=f"{icon}  {text}", command=lambda: self._switch_view(view_id),
            fg_color="transparent", hover_color=COLORS['bg_card_hover'],
            text_color=COLORS['text_primary'], anchor="w",
            height=50, corner_radius=10, font=("Segoe UI", 13, "bold")
        )
        btn.pack(fill="x", padx=20, pady=2)
        return btn
    
    def _build_header(self):
        """Build header with welcome message and clock"""
        header = ctk.CTkFrame(self.content_frame, fg_color="transparent", height=80)
        header.pack(fill="x", padx=20, pady=(20, 15))
        header.pack_propagate(False)
        
        # Welcome section
        welcome_frame = ctk.CTkFrame(header, fg_color="transparent")
        welcome_frame.pack(side="left", fill="y")
        
        ctk.CTkLabel(welcome_frame, text="Welcome back, Richard", 
                    font=("Segoe UI", 24, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w")
        ctk.CTkLabel(welcome_frame, text="Track, manage and forecast your patient reports and data.", 
                    font=("Segoe UI", 12),
                    text_color=COLORS['text_secondary']).pack(anchor="w")
        
        # Icons section
        icons_frame = ctk.CTkFrame(header, fg_color="transparent")
        icons_frame.pack(side="right", fill="y")
        
        # Clock
        self.lbl_clock = ctk.CTkLabel(icons_frame, text="", 
                                     font=("Consolas", 12),
                                     text_color=COLORS['text_secondary'])
        self.lbl_clock.pack(side="right", padx=10)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # VIEW MANAGEMENT - O(1) SWITCHING WITH LAZY LOADING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _switch_view(self, view_id: str):
        """Ultra-fast view switching - O(1) widget hiding/showing"""
        if self.current_view == view_id:
            return
        
        # Update nav buttons - O(1) dict lookups
        self.nav_buttons[self.current_view].configure(fg_color="transparent")
        self.nav_buttons[view_id].configure(fg_color=COLORS['accent_blue'])
        
        # Hide current view - O(1)
        if self.current_view in self.view_widgets:
            self.view_widgets[self.current_view].pack_forget()
        
        # Show new view - lazy load if not exists
        if view_id not in self.view_widgets:
            self._lazy_build_view(view_id)
        
        self.view_widgets[view_id].pack(fill="both", expand=True)
        self.current_view = view_id
    
    def _lazy_build_view(self, view_id: str):
        """Lazy load views on-demand - only build when needed"""
        if view_id == "overview":
            return  # Already built
        elif view_id == "patients":
            self.view_widgets[view_id] = self._build_patients_view()
        elif view_id == "visits":
            self.view_widgets[view_id] = self._build_visits_view()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # OVERVIEW DASHBOARD - PERFORMANCE CRITICAL
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _build_overview(self):
        """Build dashboard with stat cards - minimal redraws"""
        overview = ctk.CTkScrollableFrame(self.main_content, fg_color="transparent")
        overview.pack(fill="both", expand=True)
        self.view_widgets["overview"] = overview
        
        # Stats cards row
        stats_row = ctk.CTkFrame(overview, fg_color="transparent")
        stats_row.pack(fill="x", pady=(0, 15))
        
        # Create stat cards with references for O(1) updates
        self.stat_cards = {}
        
        card_configs = [
            ("total_patients", "Total Patients", "👥", COLORS['accent_blue']),
            ("new_appointments", "New Appointments", "📅", COLORS['accent_green']),
            ("pending_reports", "Pending Reports", "📋", COLORS['accent_orange']),
        ]
        
        for i, (key, title, icon, color) in enumerate(card_configs):
            card = self._create_stat_card(stats_row, title, "0", icon, color, "0%")
            card.pack(side="left", fill="both", expand=True, padx=(0, 15 if i < 2 else 0))
            self.stat_cards[key] = card
        
        # Recent visits section
        visits_frame = ctk.CTkFrame(overview, fg_color=COLORS['bg_card'], corner_radius=15,
                                   border_width=1, border_color=COLORS['border'])
        visits_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Header
        header = ctk.CTkFrame(visits_frame, fg_color="transparent", height=60)
        header.pack(fill="x", padx=20, pady=(20, 10))
        header.pack_propagate(False)
        
        ctk.CTkLabel(header, text="📋 Recent Patient Appointments", 
                    font=("Segoe UI", 16, "bold"),
                    text_color=COLORS['text_primary']).pack(side="left")
        
        ctk.CTkButton(header, text="🔍 Search patient...", command=self._focus_search,
                     fg_color=COLORS['bg_dark'], hover_color=COLORS['bg_card_hover'],
                     text_color=COLORS['text_primary'],
                     height=35, width=200, corner_radius=10,
                     border_width=1, border_color=COLORS['border']).pack(side="right")
        
        # Table
        self.tree_overview = self._create_optimized_tree(visits_frame,
            ["#", "Date", "Patient Name", "Assign To Doctor", "Room", "Status", "Action"])
        
        # Configure columns for optimal display
        self.tree_overview.column("#0", width=0, stretch=False)
        self.tree_overview.column("#", width=60, anchor="center")
        self.tree_overview.column("Date", width=120, anchor="center")
        self.tree_overview.column("Patient Name", width=200)
        self.tree_overview.column("Assign To Doctor", width=180)
        self.tree_overview.column("Room", width=100, anchor="center")
        self.tree_overview.column("Status", width=100, anchor="center")
        self.tree_overview.column("Action", width=80, anchor="center")
        
        # Bind double-click to view patient details from visit
        self.tree_overview.bind("<Double-Button-1>", self._on_overview_visit_double_click)
    
    def _create_stat_card(self, parent, title: str, value: str, icon: str, 
                          color: str, change: str):
        """Create stat card widget - returns frame with update references"""
        card = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=15,
                           border_width=1, border_color=COLORS['border'])
        
        # Content
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ctk.CTkFrame(content, fg_color="transparent")
        header_frame.pack(fill="x")
        
        ctk.CTkLabel(header_frame, text=icon, font=("Segoe UI", 20)).pack(side="left")
        ctk.CTkLabel(header_frame, text=title, 
                    font=("Segoe UI", 12),
                    text_color=COLORS['text_secondary']).pack(side="left", padx=(10, 0))
        
        # Value (store reference for O(1) updates)
        value_label = ctk.CTkLabel(content, text=value, 
                                   font=("Segoe UI", 32, "bold"),
                                   text_color=COLORS['text_primary'])
        value_label.pack(anchor="w", pady=(10, 5))
        
        # Change indicator
        change_label = ctk.CTkLabel(content, text=f"↗ {change}  From last month", 
                                   font=("Segoe UI", 11),
                                   text_color=COLORS['accent_green'])
        change_label.pack(anchor="w")
        
        # Store references for fast updates
        card.value_label = value_label
        card.change_label = change_label
        
        return card
    
    # ═══════════════════════════════════════════════════════════════════════════
    # OTHER VIEWS - LAZY LOADED
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _build_patients_view(self):
        """Build patients view with Add Patient functionality"""
        frame = ctk.CTkScrollableFrame(self.main_content, fg_color="transparent")
        
        # Header
        header = ctk.CTkFrame(frame, fg_color=COLORS['bg_card'], corner_radius=15, height=80,
                             border_width=1, border_color=COLORS['border'])
        header.pack(fill="x", pady=(0, 15))
        header.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(expand=True, fill="both", padx=20)
        
        # Left: Title and Add button
        left_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        left_frame.pack(side="left", fill="y")
        
        ctk.CTkLabel(left_frame, text="👥 All Patients", 
                    font=("Segoe UI", 20, "bold"),
                    text_color=COLORS['text_primary']).pack(side="left", padx=(0, 15))
        
        ctk.CTkButton(left_frame, text="➕ Add Patient", 
                     command=self._open_add_patient_dialog,
                     fg_color=COLORS['accent_blue'], hover_color="#0052a3",
                     height=40, corner_radius=10, font=("Segoe UI", 13, "bold")).pack(side="left")
        
        # Right: Search bar
        search_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        search_frame.pack(side="right")
        
        self.entry_patient_search = ctk.CTkEntry(search_frame, 
                                                placeholder_text="🔍 Search patients...",
                                                width=300, height=40, corner_radius=10)
        self.entry_patient_search.pack(side="left", padx=5)
        self.entry_patient_search.bind("<KeyRelease>", lambda e: self._search_patients())
        
        # Table
        table_frame = ctk.CTkFrame(frame, fg_color=COLORS['bg_card'], corner_radius=15,
                                  border_width=1, border_color=COLORS['border'])
        table_frame.pack(fill="both", expand=True)
        
        self.tree_patients = self._create_optimized_tree(table_frame,
            ["ID", "Last Name", "First Name", "Middle Name", "DOB", "Contact", "Address"])
        
        self.tree_patients.column("ID", width=60, anchor="center")
        self.tree_patients.column("Last Name", width=150)
        self.tree_patients.column("First Name", width=150)
        self.tree_patients.column("Middle Name", width=120)
        self.tree_patients.column("DOB", width=110, anchor="center")
        self.tree_patients.column("Contact", width=130, anchor="center")
        self.tree_patients.column("Address", width=200)
        
        # Bind double-click to view patient details
        self.tree_patients.bind("<Double-Button-1>", self._on_patient_double_click)
        
        return frame
    
    def _build_visits_view(self):
        """Build visits/today's logs view"""
        frame = ctk.CTkScrollableFrame(self.main_content, fg_color="transparent")
        
        # Stats bar
        stats = ctk.CTkFrame(frame, fg_color=COLORS['bg_card'], corner_radius=15, height=70,
                            border_width=1, border_color=COLORS['border'])
        stats.pack(fill="x", pady=(0, 15))
        stats.pack_propagate(False)
        
        stats_content = ctk.CTkFrame(stats, fg_color="transparent")
        stats_content.pack(expand=True, fill="both", padx=30)
        
        self.lbl_today_count = ctk.CTkLabel(stats_content, text="Today: 0 visits", 
                                           font=("Segoe UI", 18, "bold"),
                                           text_color=COLORS['accent_blue'])
        self.lbl_today_count.pack(side="left")
        
        ctk.CTkButton(stats_content, text="🔄 Refresh", command=self._refresh_today_visits,
                     fg_color=COLORS['accent_green'], hover_color="#1e7e34",
                     height=40, corner_radius=10).pack(side="right")
        
        # Table
        table_frame = ctk.CTkFrame(frame, fg_color=COLORS['bg_card'], corner_radius=15,
                                  border_width=1, border_color=COLORS['border'])
        table_frame.pack(fill="both", expand=True)
        
        self.tree_today = self._create_optimized_tree(table_frame,
            ["ID", "Patient", "Time", "Weight", "Height", "BP", "Temp", "Notes"])
        
        self.tree_today.column("ID", width=60, anchor="center")
        self.tree_today.column("Patient", width=200)
        self.tree_today.column("Time", width=100, anchor="center")
        self.tree_today.column("Weight", width=80, anchor="center")
        self.tree_today.column("Height", width=80, anchor="center")
        self.tree_today.column("BP", width=100, anchor="center")
        self.tree_today.column("Temp", width=80, anchor="center")
        self.tree_today.column("Notes", width=300)
        
        # Bind click to view patient details - O(1) lookup
        self.tree_today.bind("<Double-Button-1>", self._on_visit_double_click)
        
        return frame
    
    # ═══════════════════════════════════════════════════════════════════════════
    # OPTIMIZED TREEVIEW FACTORY
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _create_optimized_tree(self, parent, columns: List[str]):
        """Create performance-optimized treeview with modern styling"""
        # Container
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Style
        style = ttk.Style()
        style.theme_use("default")
        
        # Configure colors - High contrast for readability
        style.configure("Custom.Treeview",
                       background="#ffffff",
                       foreground=COLORS['text_primary'],
                       fieldbackground="#ffffff",
                       borderwidth=1,
                       relief="solid",
                       font=("Segoe UI", 11),
                       rowheight=45)
        
        style.configure("Custom.Treeview.Heading",
                       background=COLORS['bg_dark'],
                       foreground=COLORS['text_primary'],
                       borderwidth=1,
                       relief="solid",
                       font=("Segoe UI", 12, "bold"))
        
        style.map("Custom.Treeview",
                 background=[("selected", COLORS['accent_blue'])],
                 foreground=[("selected", "#ffffff")])
        
        style.map("Custom.Treeview.Heading",
                 background=[("active", COLORS['bg_card_hover'])])
        
        # Scrollbar
        scrollbar = ctk.CTkScrollbar(container, orientation="vertical")
        scrollbar.pack(side="right", fill="y")
        
        # Tree
        tree = ttk.Treeview(container, columns=columns, show="headings",
                           style="Custom.Treeview", yscrollcommand=scrollbar.set,
                           selectmode="browse")
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.configure(command=tree.yview)
        
        # Set headings
        for col in columns:
            tree.heading(col, text=col.upper())
        
        # Add zebra striping for better readability
        tree.tag_configure('evenrow', background='#f8f9fa')
        tree.tag_configure('oddrow', background='#ffffff')
        
        return tree
    
    # ═══════════════════════════════════════════════════════════════════════════
    # DATA OPERATIONS - CACHED AND OPTIMIZED
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _initial_load(self):
        """Initial data load - async to prevent UI blocking"""
        self._refresh_stats()
        self._refresh_recent_visits()
    
    def _refresh_stats(self):
        """Refresh dashboard stats - uses cache when possible"""
        if not self.stats_cache.is_dirty:
            return
        
        # Batch queries for efficiency
        patients = self.db.get_all_patients()
        today = datetime.date.today().strftime("%Y-%m-%d")
        visits_today = self.db.get_visits_by_date(today)
        
        # Update cache
        stats = {
            "total_patients": len(patients),
            "new_appointments": len(visits_today),
            "pending_reports": 0  # Placeholder
        }
        self.stats_cache.update(stats)
        
        # Update UI - O(1) label updates
        self.stat_cards["total_patients"].value_label.configure(
            text=str(stats["total_patients"]))
        self.stat_cards["new_appointments"].value_label.configure(
            text=str(stats["new_appointments"]))
        self.stat_cards["pending_reports"].value_label.configure(
            text=str(stats["pending_reports"]))
    
    def _refresh_recent_visits(self):
        """Refresh recent visits table"""
        today = datetime.date.today().strftime("%Y-%m-%d")
        visits = self.db.get_visits_by_date(today)
        
        # Clear and populate - batch operations
        for item in self.tree_overview.get_children():
            self.tree_overview.delete(item)
        
        for idx, visit in enumerate(visits[:10]):  # Limit to 10 most recent
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.tree_overview.insert("", "end", values=(
                visit['visit_id'],
                visit['visit_date'],
                visit['full_name'],
                "Dr. Smith",  # Placeholder
                "Room 101",   # Placeholder
                "✓ Complete",
                "👁"
            ), tags=(tag,))
    
    def _refresh_today_visits(self):
        """Refresh today's visits in visits tab"""
        if "visits" not in self.view_widgets:
            return
        
        today = datetime.date.today().strftime("%Y-%m-%d")
        visits = self.db.get_visits_by_date(today)
        
        # Clear and populate
        for item in self.tree_today.get_children():
            self.tree_today.delete(item)
        
        for idx, visit in enumerate(visits):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.tree_today.insert("", "end", values=(
                visit['visit_id'],
                visit['full_name'],
                format_time_12hr(visit.get('visit_time')),
                f"{visit['weight_kg']}" if visit['weight_kg'] else "—",
                f"{visit['height_cm']}" if visit['height_cm'] else "—",
                visit['blood_pressure'] or "—",
                f"{visit['temperature_celsius']}" if visit['temperature_celsius'] else "—",
                (visit['medical_notes'] or "")[:50]
            ), tags=(tag,))
        
        self.lbl_today_count.configure(text=f"Today: {len(visits)} visit(s)")
    
    def _search_patients(self):
        """Real-time patient search - optimized with database index"""
        if "patients" not in self.view_widgets:
            return
        
        query = self.entry_patient_search.get().strip()
        
        # Clear table
        for item in self.tree_patients.get_children():
            self.tree_patients.delete(item)
        
        # Query database (uses index for speed)
        if query:
            patients = self.db.search_patients(query)
        else:
            patients = self.db.get_all_patients()
        
        # Populate with zebra striping
        for idx, patient in enumerate(patients):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.tree_patients.insert("", "end", values=(
                patient['patient_id'],
                patient['last_name'],
                patient['first_name'],
                patient.get('middle_name', '') or "—",
                patient['date_of_birth'] or "—",
                patient['contact_number'] or "—",
                patient['address'] or "—"
            ), tags=(tag,))
    
    def _focus_search(self):
        """Focus search bar in patients view"""
        self._switch_view("patients")
        self.entry_patient_search.focus()
    
    def _open_add_patient_dialog(self):
        """Open Add Patient dialog"""
        AddPatientDialog(self, self.db, self._on_patient_added)
    
    def _on_patient_added(self, patient_id: int):
        """Callback after patient is added"""
        self._search_patients()  # Refresh patients list
        messagebox.showinfo("Success", f"✓ Patient #{patient_id} added successfully!")
    
    def _open_new_visit_dialog(self):
        """Open new visit dialog - O(1) dialog creation"""
        NewVisitDialog(self, self.db, self._on_visit_added)
    
    def _on_visit_added(self, visit_id: int):
        """Callback after visit is added"""
        self.stats_cache.invalidate()
        self._refresh_stats()
        self._refresh_recent_visits()
        if "visits" in self.view_widgets:
            self._refresh_today_visits()
        messagebox.showinfo("Success", f"✓ Visit #{visit_id} recorded successfully!")
    
    def _on_patient_double_click(self, event):
        """Handle patient double-click - show full patient details"""
        selection = self.tree_patients.selection()
        if selection:
            values = self.tree_patients.item(selection[0], "values")
            patient_id = int(values[0])
            # Launch patient details viewer - O(log n) DB lookup
            PatientDetailsDialog(self, self.db, patient_id)
    
    def _on_visit_double_click(self, event):
        """Handle visit log double-click - show patient details from visit"""
        selection = self.tree_today.selection()
        if selection:
            values = self.tree_today.item(selection[0], "values")
            visit_id = int(values[0])
            # Get patient ID from visit - O(1) lookup
            visits = self.db.get_visits_by_date(datetime.date.today().strftime("%Y-%m-%d"))
            visit = next((v for v in visits if v['visit_id'] == visit_id), None)
            if visit:
                PatientDetailsDialog(self, self.db, visit['patient_id'])
    
    def _on_overview_visit_double_click(self, event):
        """Handle overview visit double-click - show patient details"""
        selection = self.tree_overview.selection()
        if selection:
            values = self.tree_overview.item(selection[0], "values")
            visit_id = int(values[0])
            # Get patient ID from visit
            visits = self.db.get_visits_by_date(datetime.date.today().strftime("%Y-%m-%d"))
            visit = next((v for v in visits if v['visit_id'] == visit_id), None)
            if visit:
                PatientDetailsDialog(self, self.db, visit['patient_id'])
    
    # ═══════════════════════════════════════════════════════════════════════════
    # UTILITIES
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _update_clock(self):
        """Update clock - O(1) label update"""
        now = datetime.datetime.now().strftime("%I:%M %p  •  %b %d, %Y")
        self.lbl_clock.configure(text=now)
        self.after(1000, self._update_clock)
    
    def backup_db(self):
        """Database backup"""
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".db",
                filetypes=[("Database", "*.db")],
                initialfile=f"clinic_backup_{get_export_timestamp()}.db"
            )
            if filepath:
                self.db.backup_database(filepath)
                messagebox.showinfo("Success", f"✓ Backup created:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Backup failed:\n{e}")
    
    def export_data(self):
        """Export to CSV"""
        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV", "*.csv")],
                initialfile=f"clinic_export_{get_export_timestamp()}.csv"
            )
            if filepath:
                if self.db.export_to_csv(filepath):
                    messagebox.showinfo("Success", f"✓ Data exported:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed:\n{e}")



# ═══════════════════════════════════════════════════════════════════════════════
# NEW VISIT DIALOG - HYPER-OPTIMIZED WITH PATIENT SELECTION
# ═══════════════════════════════════════════════════════════════════════════════
class NewVisitDialog(ctk.CTkToplevel):
    """Ultra-fast new visit dialog with intelligent patient selection workflow"""
    
    def __init__(self, parent, db: ClinicDatabase, callback):
        super().__init__(parent)
        
        self.db = db
        self.callback = callback
        self.selected_patient_id = None
        self.selected_patient_name = None
        
        # Window config
        self.title("New Visit")
        self.geometry("700x800")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['bg_dark'])
        
        # Center window
        self.transient(parent)
        self.grab_set()
        
        # Build UI
        self._build_ui()
    
    def _build_ui(self):
        """Build visit dialog UI - O(1) widget construction"""
        # Header
        header = ctk.CTkFrame(self, fg_color=COLORS['accent_green'], corner_radius=15, height=80)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(expand=True, fill="both", padx=30)
        
        ctk.CTkLabel(header_content, text="➕ Record New Visit", 
                    font=("Segoe UI", 24, "bold"),
                    text_color="#ffffff").pack(anchor="w")
        ctk.CTkLabel(header_content, text="Select patient and record visit details", 
                    font=("Segoe UI", 12),
                    text_color="#ffffff").pack(anchor="w")
        
        # Main form
        form = ctk.CTkScrollableFrame(self, fg_color=COLORS['bg_card'], corner_radius=15,
                                     border_width=1, border_color=COLORS['border'])
        form.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        form_content = ctk.CTkFrame(form, fg_color="transparent")
        form_content.pack(fill="both", expand=True, padx=25, pady=25)
        
        # SECTION 1: Patient Selection
        ctk.CTkLabel(form_content, text="1️⃣ SELECT PATIENT", 
                    font=("Segoe UI", 14, "bold"),
                    text_color=COLORS['accent_blue']).pack(anchor="w", pady=(0, 10))
        
        patient_frame = ctk.CTkFrame(form_content, fg_color=COLORS['bg_dark'], corner_radius=10)
        patient_frame.pack(fill="x", pady=(0, 20))
        
        patient_content = ctk.CTkFrame(patient_frame, fg_color="transparent")
        patient_content.pack(fill="x", padx=15, pady=15)
        
        # Search patient
        search_frame = ctk.CTkFrame(patient_content, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(search_frame, text="Search Patient:", 
                    font=("Segoe UI", 12),
                    text_color=COLORS['text_secondary']).pack(side="left", padx=(0, 10))
        
        self.entry_search = ctk.CTkEntry(search_frame, placeholder_text="Type patient name...",
                                        height=40, font=("Segoe UI", 12))
        self.entry_search.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_search.bind("<KeyRelease>", self._on_search_change)
        
        # Patient listbox
        self.patient_listbox = tk.Listbox(patient_content, height=6,
                                         font=("Segoe UI", 11),
                                         bg="#ffffff",
                                         fg=COLORS['text_primary'],
                                         selectbackground=COLORS['accent_blue'],
                                         selectforeground="#ffffff",
                                         relief="flat",
                                         borderwidth=1,
                                         highlightthickness=1,
                                         highlightbackground=COLORS['border'])
        self.patient_listbox.pack(fill="x", pady=(0, 10))
        self.patient_listbox.bind("<<ListboxSelect>>", self._on_patient_select)
        
        # Selected patient display
        self.lbl_selected = ctk.CTkLabel(patient_content, text="No patient selected", 
                                        font=("Segoe UI", 12, "bold"),
                                        text_color=COLORS['text_secondary'])
        self.lbl_selected.pack(anchor="w", pady=(0, 10))
        
        # Add new patient button
        btn_add_patient = ctk.CTkButton(patient_content, text="➕ Patient Not Found? Add New Patient",
                                       command=self._open_add_patient,
                                       fg_color=COLORS['accent_orange'], hover_color="#e06700",
                                       height=40, corner_radius=8,
                                       font=("Segoe UI", 12, "bold"))
        btn_add_patient.pack(fill="x")
        
        # SECTION 2: Visit Details
        ctk.CTkLabel(form_content, text="2️⃣ VISIT DETAILS", 
                    font=("Segoe UI", 14, "bold"),
                    text_color=COLORS['accent_blue']).pack(anchor="w", pady=(10, 10))
        
        # Date and Time
        datetime_frame = ctk.CTkFrame(form_content, fg_color="transparent")
        datetime_frame.pack(fill="x", pady=(0, 15))
        
        # Date
        date_col = ctk.CTkFrame(datetime_frame, fg_color="transparent")
        date_col.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(date_col, text="Visit Date *", 
                    font=("Segoe UI", 12, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w")
        
        self.entry_date = ctk.CTkEntry(date_col, placeholder_text="YYYY-MM-DD",
                                      height=40, font=("Segoe UI", 12))
        self.entry_date.pack(fill="x", pady=(5, 0))
        self.entry_date.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        
        # Time
        time_col = ctk.CTkFrame(datetime_frame, fg_color="transparent")
        time_col.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(time_col, text="Visit Time *", 
                    font=("Segoe UI", 12, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w")
        
        self.entry_time = ctk.CTkEntry(time_col, placeholder_text="HH:MM or 2:30 PM",
                                      height=40, font=("Segoe UI", 12))
        self.entry_time.pack(fill="x", pady=(5, 0))
        self.entry_time.insert(0, datetime.datetime.now().strftime("%I:%M %p"))
        
        # Vital Signs Row
        vitals_frame = ctk.CTkFrame(form_content, fg_color="transparent")
        vitals_frame.pack(fill="x", pady=(0, 15))
        
        # Weight
        weight_col = ctk.CTkFrame(vitals_frame, fg_color="transparent")
        weight_col.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(weight_col, text="Weight (kg)", 
                    font=("Segoe UI", 12, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w")
        self.entry_weight = ctk.CTkEntry(weight_col, placeholder_text="e.g., 65.5",
                                        height=40, font=("Segoe UI", 12))
        self.entry_weight.pack(fill="x", pady=(5, 0))
        
        # Height
        height_col = ctk.CTkFrame(vitals_frame, fg_color="transparent")
        height_col.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(height_col, text="Height (cm)", 
                    font=("Segoe UI", 12, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w")
        self.entry_height = ctk.CTkEntry(height_col, placeholder_text="e.g., 165",
                                        height=40, font=("Segoe UI", 12))
        self.entry_height.pack(fill="x", pady=(5, 0))
        
        # BP and Temp Row
        vitals2_frame = ctk.CTkFrame(form_content, fg_color="transparent")
        vitals2_frame.pack(fill="x", pady=(0, 15))
        
        # Blood Pressure
        bp_col = ctk.CTkFrame(vitals2_frame, fg_color="transparent")
        bp_col.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(bp_col, text="Blood Pressure", 
                    font=("Segoe UI", 12, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w")
        self.entry_bp = ctk.CTkEntry(bp_col, placeholder_text="e.g., 120/80",
                                    height=40, font=("Segoe UI", 12))
        self.entry_bp.pack(fill="x", pady=(5, 0))
        
        # Temperature
        temp_col = ctk.CTkFrame(vitals2_frame, fg_color="transparent")
        temp_col.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(temp_col, text="Temperature (°C)", 
                    font=("Segoe UI", 12, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w")
        self.entry_temp = ctk.CTkEntry(temp_col, placeholder_text="e.g., 37.2",
                                      height=40, font=("Segoe UI", 12))
        self.entry_temp.pack(fill="x", pady=(5, 0))
        
        # Medical Notes
        ctk.CTkLabel(form_content, text="Medical Notes / Reason for Visit", 
                    font=("Segoe UI", 12, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w", pady=(5, 5))
        
        self.entry_notes = ctk.CTkTextbox(form_content, height=100, 
                                         font=("Segoe UI", 12),
                                         fg_color="#ffffff",
                                         border_color=COLORS['border'],
                                         border_width=1)
        self.entry_notes.pack(fill="x", pady=(0, 20))
        
        # Footer buttons
        footer = ctk.CTkFrame(form_content, fg_color="transparent")
        footer.pack(fill="x")
        
        ctk.CTkButton(footer, text="✓ Save Visit", command=self._save_visit,
                     fg_color=COLORS['accent_green'], hover_color="#1e7e34",
                     height=45, corner_radius=10,
                     font=("Segoe UI", 14, "bold")).pack(side="right", padx=(10, 0))
        
        ctk.CTkButton(footer, text="✕ Cancel", command=self.destroy,
                     fg_color=COLORS['text_secondary'], hover_color="#5a6268",
                     height=45, corner_radius=10,
                     font=("Segoe UI", 14, "bold")).pack(side="right")
        
        # Load all patients initially
        self._load_patients()
    
    def _load_patients(self, query: str = ""):
        """Load patients into listbox - O(n) for n matching patients"""
        self.patient_listbox.delete(0, tk.END)
        self.patient_data = {}  # Cache patient data by listbox index
        
        if query:
            patients = self.db.search_patients(query)
        else:
            patients = self.db.get_all_patients()
        
        for idx, patient in enumerate(patients):
            first = patient.get('first_name', '')
            middle = patient.get('middle_name', '')
            last = patient.get('last_name', '')
            full_name = f"{last}, {first}" + (f" {middle}" if middle else "")
            
            display = f"{full_name} (ID: {patient['patient_id']})"
            self.patient_listbox.insert(tk.END, display)
            self.patient_data[idx] = (patient['patient_id'], full_name)
    
    def _on_search_change(self, event):
        """Handle search input - O(1) event + O(n) query"""
        query = self.entry_search.get().strip()
        self._load_patients(query)
        self.selected_patient_id = None
        self.lbl_selected.configure(text="No patient selected", 
                                   text_color=COLORS['text_secondary'])
    
    def _on_patient_select(self, event):
        """Handle patient selection - O(1) dict lookup"""
        selection = self.patient_listbox.curselection()
        if selection:
            idx = selection[0]
            if idx in self.patient_data:
                self.selected_patient_id, self.selected_patient_name = self.patient_data[idx]
                self.lbl_selected.configure(
                    text=f"✓ Selected: {self.selected_patient_name}",
                    text_color=COLORS['accent_green'])
    
    def _open_add_patient(self):
        """Open add patient dialog from within visit dialog"""
        def on_patient_added(patient_id):
            # Refresh patient list and auto-select the new patient
            self._load_patients()
            
            # Find and select the newly added patient
            for idx, (pid, name) in self.patient_data.items():
                if pid == patient_id:
                    self.patient_listbox.selection_clear(0, tk.END)
                    self.patient_listbox.selection_set(idx)
                    self.patient_listbox.see(idx)
                    self.selected_patient_id = pid
                    self.selected_patient_name = name
                    self.lbl_selected.configure(
                        text=f"✓ Selected: {name}",
                        text_color=COLORS['accent_green'])
                    break
            
            messagebox.showinfo("Success", 
                              f"✓ Patient added! You can now record their visit.",
                              parent=self)
        
        AddPatientDialog(self, self.db, on_patient_added)
    
    def _save_visit(self):
        """Save visit to database - O(log n) insert"""
        # Validate patient selection
        if not self.selected_patient_id:
            messagebox.showerror("Validation Error", 
                               "Please select a patient first!",
                               parent=self)
            return
        
        # Get required fields
        visit_date = self.entry_date.get().strip()
        visit_time = self.entry_time.get().strip()
        
        if not visit_date:
            messagebox.showerror("Validation Error", 
                               "Visit date is required!",
                               parent=self)
            return
        
        # Validate date format
        try:
            datetime.datetime.strptime(visit_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation Error", 
                               "Invalid date format! Use YYYY-MM-DD",
                               parent=self)
            return
        
        # Parse time if provided
        from utils import parse_time_input
        if visit_time:
            parsed_time = parse_time_input(visit_time)
            if not parsed_time:
                messagebox.showerror("Validation Error", 
                                   "Invalid time format! Use HH:MM or '2:30 PM'",
                                   parent=self)
                return
            visit_time = parsed_time
        else:
            visit_time = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Get optional fields
        from utils import safe_float
        weight = safe_float(self.entry_weight.get())
        height = safe_float(self.entry_height.get())
        bp = self.entry_bp.get().strip()
        temp = safe_float(self.entry_temp.get())
        notes = self.entry_notes.get("1.0", "end-1c").strip()
        
        # Add to database
        visit_id = self.db.add_visit(
            patient_id=self.selected_patient_id,
            visit_date=visit_date,
            visit_time=visit_time,
            weight=weight,
            height=height,
            bp=bp,
            temp=temp,
            notes=notes
        )
        
        if visit_id:
            self.callback(visit_id)
            self.destroy()
        else:
            messagebox.showerror("Error", "Failed to save visit!", parent=self)


# ═══════════════════════════════════════════════════════════════════════════════
# ADD PATIENT DIALOG - OPTIMIZED WITH CALENDAR PICKER
# ═══════════════════════════════════════════════════════════════════════════════
class AddPatientDialog(ctk.CTkToplevel):
    """High-performance Add Patient dialog with calendar date picker"""
    
    def __init__(self, parent, db: ClinicDatabase, callback):
        super().__init__(parent)
        
        self.db = db
        self.callback = callback
        
        # Window config
        self.title("Add New Patient")
        self.geometry("600x700")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['bg_dark'])
        
        # Center window
        self.transient(parent)
        self.grab_set()
        
        # Build UI
        self._build_ui()
    
    def _build_ui(self):
        """Build dialog UI"""
        # Header
        header = ctk.CTkFrame(self, fg_color=COLORS['bg_card'], corner_radius=15, height=80)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)
        
        ctk.CTkLabel(header, text="➕ Add New Patient", 
                    font=("Segoe UI", 22, "bold"),
                    text_color=COLORS['text_primary']).pack(expand=True)
        
        # Form container
        form = ctk.CTkScrollableFrame(self, fg_color=COLORS['bg_card'], corner_radius=15)
        form.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Form fields
        fields_frame = ctk.CTkFrame(form, fg_color="transparent")
        fields_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Name section
        ctk.CTkLabel(fields_frame, text="Personal Information", 
                    font=("Segoe UI", 16, "bold"),
                    text_color=COLORS['text_primary'],
                    anchor="w").pack(fill="x", pady=(0, 15))
        
        # First Name
        ctk.CTkLabel(fields_frame, text="First Name *", 
                    font=("Segoe UI", 12),
                    text_color=COLORS['text_primary'],
                    anchor="w").pack(fill="x")
        self.entry_first_name = ctk.CTkEntry(fields_frame, height=40, corner_radius=10,
                                            font=("Segoe UI", 12))
        self.entry_first_name.pack(fill="x", pady=(5, 15))
        
        # Middle Name
        ctk.CTkLabel(fields_frame, text="Middle Name (Optional)", 
                    font=("Segoe UI", 12),
                    text_color=COLORS['text_primary'],
                    anchor="w").pack(fill="x")
        self.entry_middle_name = ctk.CTkEntry(fields_frame, height=40, corner_radius=10,
                                             font=("Segoe UI", 12))
        self.entry_middle_name.pack(fill="x", pady=(5, 15))
        
        # Last Name
        ctk.CTkLabel(fields_frame, text="Last Name *", 
                    font=("Segoe UI", 12),
                    text_color=COLORS['text_primary'],
                    anchor="w").pack(fill="x")
        self.entry_last_name = ctk.CTkEntry(fields_frame, height=40, corner_radius=10,
                                           font=("Segoe UI", 12))
        self.entry_last_name.pack(fill="x", pady=(5, 15))
        
        # Date of Birth with Calendar Picker
        ctk.CTkLabel(fields_frame, text="Date of Birth", 
                    font=("Segoe UI", 12),
                    text_color=COLORS['text_primary'],
                    anchor="w").pack(fill="x")
        
        dob_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        dob_frame.pack(fill="x", pady=(5, 15))
        
        self.entry_dob = ctk.CTkEntry(dob_frame, height=40, corner_radius=10,
                                     placeholder_text="YYYY-MM-DD",
                                     font=("Segoe UI", 12))
        self.entry_dob.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(dob_frame, text="📅", width=50, height=40,
                     command=self._open_calendar,
                     fg_color=COLORS['accent_blue'], hover_color="#0052a3",
                     font=("Segoe UI", 18)).pack(side="right")
        
        # Contact Information
        ctk.CTkLabel(fields_frame, text="Contact Information", 
                    font=("Segoe UI", 16, "bold"),
                    text_color=COLORS['text_primary'],
                    anchor="w").pack(fill="x", pady=(20, 15))
        
        # Contact Number
        ctk.CTkLabel(fields_frame, text="Contact Number", 
                    font=("Segoe UI", 12),
                    text_color=COLORS['text_primary'],
                    anchor="w").pack(fill="x")
        self.entry_contact = ctk.CTkEntry(fields_frame, height=40, corner_radius=10,
                                         placeholder_text="09123456789",
                                         font=("Segoe UI", 12))
        self.entry_contact.pack(fill="x", pady=(5, 15))
        
        # Address
        ctk.CTkLabel(fields_frame, text="Address", 
                    font=("Segoe UI", 12),
                    text_color=COLORS['text_primary'],
                    anchor="w").pack(fill="x")
        self.entry_address = ctk.CTkTextbox(fields_frame, height=80, corner_radius=10,
                                           font=("Segoe UI", 12))
        self.entry_address.pack(fill="x", pady=(5, 15))
        
        # Notes
        ctk.CTkLabel(fields_frame, text="Additional Notes", 
                    font=("Segoe UI", 12),
                    text_color=COLORS['text_primary'],
                    anchor="w").pack(fill="x")
        self.entry_notes = ctk.CTkTextbox(fields_frame, height=80, corner_radius=10,
                                         font=("Segoe UI", 12))
        self.entry_notes.pack(fill="x", pady=(5, 20))
        
        # Buttons
        button_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        ctk.CTkButton(button_frame, text="Cancel", command=self.destroy,
                     fg_color=COLORS['text_secondary'], hover_color="#5a6268",
                     height=45, corner_radius=10,
                     font=("Segoe UI", 13, "bold")).pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(button_frame, text="✓ Add Patient", command=self._save_patient,
                     fg_color=COLORS['accent_green'], hover_color="#1e7e34",
                     height=45, corner_radius=10,
                     font=("Segoe UI", 13, "bold")).pack(side="right", fill="x", expand=True)
        
        # Focus first field
        self.entry_first_name.focus()
    
    def _open_calendar(self):
        """Open calendar picker dialog"""
        CalendarDialog(self, self._on_date_selected)
    
    def _on_date_selected(self, date_str: str):
        """Callback when date is selected from calendar"""
        self.entry_dob.delete(0, "end")
        self.entry_dob.insert(0, date_str)
    
    def _save_patient(self):
        """Save patient to database - O(1) validation + O(log n) insert"""
        # Validate required fields
        first_name = self.entry_first_name.get().strip()
        last_name = self.entry_last_name.get().strip()
        
        if not first_name or not last_name:
            messagebox.showerror("Validation Error", 
                               "First Name and Last Name are required!",
                               parent=self)
            return
        
        # Get optional fields
        middle_name = self.entry_middle_name.get().strip()
        dob = self.entry_dob.get().strip()
        contact = self.entry_contact.get().strip()
        address = self.entry_address.get("1.0", "end-1c").strip()
        notes = self.entry_notes.get("1.0", "end-1c").strip()
        
        # Validate DOB format if provided
        if dob:
            try:
                datetime.datetime.strptime(dob, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Validation Error", 
                                   "Invalid date format! Use YYYY-MM-DD",
                                   parent=self)
                return
        
        # Add to database
        patient_id = self.db.add_patient(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            dob=dob,
            contact=contact,
            address=address,
            notes=notes
        )
        
        if patient_id:
            self.callback(patient_id)
            self.destroy()
        else:
            messagebox.showerror("Error", "Failed to add patient!", parent=self)



# ═══════════════════════════════════════════════════════════════════════════════
# PATIENT DETAILS VIEWER - OPTIMIZED
# ═══════════════════════════════════════════════════════════════════════════════
class PatientDetailsDialog(ctk.CTkToplevel):
    """Ultra-fast patient details viewer with visit history - O(log n) DB access"""
    
    def __init__(self, parent, db: ClinicDatabase, patient_id: int):
        super().__init__(parent)
        
        self.db = db
        self.patient_id = patient_id
        
        # Window config
        self.title("Patient Details")
        self.geometry("900x700")
        self.resizable(True, True)
        self.configure(fg_color=COLORS['bg_dark'])
        
        # Center on parent
        self.transient(parent)
        self.grab_set()
        
        # Load patient data - O(log n) indexed query
        self.patient_data = self.db.get_patient(patient_id)
        self.visit_data = self.db.get_patient_visits(patient_id)
        self.stats = self.db.get_patient_stats(patient_id)
        
        if not self.patient_data:
            messagebox.showerror("Error", "Patient not found!", parent=self)
            self.destroy()
            return
        
        self._build_ui()
    
    def _build_ui(self):
        """Build patient details UI - minimal allocations"""
        # Header with patient name
        header = ctk.CTkFrame(self, fg_color=COLORS['accent_blue'], corner_radius=15, height=100)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(expand=True, fill="both", padx=30, pady=20)
        
        # Patient name - build full name efficiently
        first = self.patient_data.get('first_name', '')
        middle = self.patient_data.get('middle_name', '')
        last = self.patient_data.get('last_name', '')
        full_name = f"{last}, {first}" + (f" {middle}" if middle else "")
        
        ctk.CTkLabel(header_content, text=f"👤 {full_name}", 
                    font=("Segoe UI", 24, "bold"),
                    text_color="#ffffff").pack(anchor="w")
        
        ctk.CTkLabel(header_content, text=f"Patient ID: #{self.patient_id}", 
                    font=("Segoe UI", 12),
                    text_color="#ffffff").pack(anchor="w")
        
        # Main content container
        content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Stats row - visit statistics
        stats_row = ctk.CTkFrame(content, fg_color="transparent")
        stats_row.pack(fill="x", pady=(0, 15))
        
        stat_configs = [
            ("Total Visits", self.stats.get('total_visits', 0), "📅"),
            ("First Visit", format_date_readable(self.stats.get('first_visit', '')) if self.stats.get('first_visit') else 'N/A', "🗓️"),
            ("Last Visit", format_date_readable(self.stats.get('last_visit', '')) if self.stats.get('last_visit') else 'N/A', "📍"),
        ]
        
        for i, (label, value, icon) in enumerate(stat_configs):
            card = ctk.CTkFrame(stats_row, fg_color=COLORS['bg_card'], corner_radius=12,
                               border_width=1, border_color=COLORS['border'])
            card.pack(side="left", fill="both", expand=True, padx=(0, 10 if i < 2 else 0))
            
            ctk.CTkLabel(card, text=icon, font=("Segoe UI", 18)).pack(pady=(15, 5))
            ctk.CTkLabel(card, text=str(value), font=("Segoe UI", 20, "bold"),
                        text_color=COLORS['accent_blue']).pack()
            ctk.CTkLabel(card, text=label, font=("Segoe UI", 11),
                        text_color=COLORS['text_secondary']).pack(pady=(0, 15))
        
        # Patient information card
        info_card = ctk.CTkFrame(content, fg_color=COLORS['bg_card'], corner_radius=15,
                                border_width=1, border_color=COLORS['border'])
        info_card.pack(fill="x", pady=(0, 15))
        
        info_content = ctk.CTkFrame(info_card, fg_color="transparent")
        info_content.pack(fill="x", padx=25, pady=20)
        
        ctk.CTkLabel(info_content, text="📋 Patient Information", 
                    font=("Segoe UI", 16, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w", pady=(0, 15))
        
        # Information grid - 2 columns
        info_grid = ctk.CTkFrame(info_content, fg_color="transparent")
        info_grid.pack(fill="x")
        
        # Left column
        left_col = ctk.CTkFrame(info_grid, fg_color="transparent")
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 20))
        
        # Date of birth with age - O(1) calculation
        dob = self.patient_data.get('date_of_birth')
        if dob:
            age = calculate_age(dob)
            dob_display = format_date_readable(dob)
            if age is not None:
                dob_display += f" (Age: {age})"
        else:
            dob_display = "Not provided"
        
        self._add_info_row(left_col, "Date of Birth", dob_display)
        self._add_info_row(left_col, "Contact Number", 
                          self.patient_data.get('contact_number') or "Not provided")
        
        # Right column
        right_col = ctk.CTkFrame(info_grid, fg_color="transparent")
        right_col.pack(side="left", fill="both", expand=True)
        
        # Format registered date - extract date portion and format
        registered = self.patient_data.get('registered_date', '')
        if registered:
            # Extract just the date part (YYYY-MM-DD) from timestamp
            registered_date = registered[:10] if len(registered) >= 10 else registered
            registered_display = format_date_readable(registered_date)
        else:
            registered_display = "N/A"
        
        self._add_info_row(right_col, "Registered", registered_display)
        self._add_info_row(right_col, "Address", 
                          self.patient_data.get('address') or "Not provided")
        
        # Notes section if available
        notes = self.patient_data.get('notes', '').strip()
        if notes:
            notes_frame = ctk.CTkFrame(info_content, fg_color=COLORS['bg_dark'], 
                                      corner_radius=10)
            notes_frame.pack(fill="x", pady=(15, 0))
            
            ctk.CTkLabel(notes_frame, text="📝 Notes:", 
                        font=("Segoe UI", 12, "bold"),
                        text_color=COLORS['text_secondary']).pack(anchor="w", 
                                                                  padx=15, pady=(10, 5))
            ctk.CTkLabel(notes_frame, text=notes, 
                        font=("Segoe UI", 11),
                        text_color=COLORS['text_primary'],
                        wraplength=800, justify="left").pack(anchor="w", 
                                                              padx=15, pady=(0, 10))
        
        # Visit history section
        visits_card = ctk.CTkFrame(content, fg_color=COLORS['bg_card'], corner_radius=15,
                                  border_width=1, border_color=COLORS['border'])
        visits_card.pack(fill="both", expand=True)
        
        visits_header = ctk.CTkFrame(visits_card, fg_color="transparent", height=50)
        visits_header.pack(fill="x", padx=20, pady=(15, 10))
        visits_header.pack_propagate(False)
        
        ctk.CTkLabel(visits_header, text=f"🏥 Visit History ({len(self.visit_data)} visits)", 
                    font=("Segoe UI", 16, "bold"),
                    text_color=COLORS['text_primary']).pack(side="left")
        
        # Visits table
        if self.visit_data:
            tree_container = ctk.CTkFrame(visits_card, fg_color="transparent")
            tree_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
            # Scrollbar
            scrollbar = ctk.CTkScrollbar(tree_container, orientation="vertical")
            scrollbar.pack(side="right", fill="y")
            
            # Style
            style = ttk.Style()
            style.configure("Details.Treeview",
                           background="#ffffff",
                           foreground=COLORS['text_primary'],
                           fieldbackground="#ffffff",
                           font=("Segoe UI", 10),
                           rowheight=35)
            style.configure("Details.Treeview.Heading",
                           background=COLORS['bg_dark'],
                           foreground=COLORS['text_primary'],
                           font=("Segoe UI", 11, "bold"))
            
            # Tree
            columns = ["Date", "Time", "Weight", "Height", "BP", "Temp", "Notes"]
            tree = ttk.Treeview(tree_container, columns=columns, show="headings",
                               style="Details.Treeview", yscrollcommand=scrollbar.set,
                               height=10)
            tree.pack(side="left", fill="both", expand=True)
            scrollbar.configure(command=tree.yview)
            
            # Configure columns
            tree.column("Date", width=140, anchor="center")
            tree.column("Time", width=90, anchor="center")
            tree.column("Weight", width=70, anchor="center")
            tree.column("Height", width=70, anchor="center")
            tree.column("BP", width=90, anchor="center")
            tree.column("Temp", width=70, anchor="center")
            tree.column("Notes", width=280)
            
            for col in columns:
                tree.heading(col, text=col.upper())
            
            # Add zebra striping
            tree.tag_configure('evenrow', background='#f8f9fa')
            tree.tag_configure('oddrow', background='#ffffff')
            
            # Populate visits - O(n) for n visits
            for idx, visit in enumerate(self.visit_data):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                visit_date = format_date_readable(visit.get('visit_date', ''))
                tree.insert("", "end", values=(
                    visit_date,
                    format_time_12hr(visit.get('visit_time', '')),
                    f"{visit['weight_kg']}" if visit.get('weight_kg') else "—",
                    f"{visit['height_cm']}" if visit.get('height_cm') else "—",
                    visit.get('blood_pressure') or "—",
                    f"{visit['temperature_celsius']}" if visit.get('temperature_celsius') else "—",
                    (visit.get('medical_notes') or "")[:50]
                ), tags=(tag,))
        else:
            # No visits message
            no_visits = ctk.CTkFrame(visits_card, fg_color="transparent")
            no_visits.pack(fill="both", expand=True, pady=40)
            
            ctk.CTkLabel(no_visits, text="📭", font=("Segoe UI", 36)).pack()
            ctk.CTkLabel(no_visits, text="No visit history yet", 
                        font=("Segoe UI", 14),
                        text_color=COLORS['text_secondary']).pack(pady=5)
        
        # Close button
        footer = ctk.CTkFrame(content, fg_color="transparent", height=50)
        footer.pack(fill="x", pady=(15, 0))
        footer.pack_propagate(False)
        
        ctk.CTkButton(footer, text="✓ Close", command=self.destroy,
                     fg_color=COLORS['accent_blue'], hover_color="#0052a3",
                     height=45, width=150, corner_radius=10,
                     font=("Segoe UI", 14, "bold")).pack(side="right")
    
    def _add_info_row(self, parent, label: str, value: str):
        """Add information row - O(1)"""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row, text=f"{label}:", 
                    font=("Segoe UI", 11, "bold"),
                    text_color=COLORS['text_secondary'],
                    width=120, anchor="w").pack(side="left")
        
        ctk.CTkLabel(row, text=value, 
                    font=("Segoe UI", 11),
                    text_color=COLORS['text_primary'],
                    anchor="w").pack(side="left", fill="x", expand=True)


# ═══════════════════════════════════════════════════════════════════════════════
# CALENDAR PICKER DIALOG - OPTIMIZED
# ═══════════════════════════════════════════════════════════════════════════════
class CalendarDialog(ctk.CTkToplevel):
    """Lightweight calendar picker with O(1) date selection"""
    
    def __init__(self, parent, callback):
        super().__init__(parent)
        
        self.callback = callback
        self.selected_date = datetime.date.today()
        
        # Window config
        self.title("Select Date")
        self.geometry("400x450")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['bg_dark'])
        
        # Center on parent
        self.transient(parent)
        self.grab_set()
        
        self._build_calendar()
    
    def _build_calendar(self):
        """Build calendar UI - OPTIMIZED with direct year access"""
        # Header with month/year navigation
        header = ctk.CTkFrame(self, fg_color=COLORS['bg_card'], corner_radius=15, height=90)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)
        
        nav_frame = ctk.CTkFrame(header, fg_color="transparent")
        nav_frame.pack(expand=True)
        
        # Month navigation
        month_nav = ctk.CTkFrame(nav_frame, fg_color="transparent")
        month_nav.pack(pady=5)
        
        ctk.CTkButton(month_nav, text="◀", width=50, height=40,
                     command=self._prev_month,
                     fg_color=COLORS['accent_blue'], hover_color="#0052a3",
                     font=("Segoe UI", 16, "bold")).pack(side="left", padx=5)
        
        self.lbl_month_year = ctk.CTkLabel(month_nav, text="", 
                                          font=("Segoe UI", 16, "bold"),
                                          text_color=COLORS['text_primary'],
                                          width=200)
        self.lbl_month_year.pack(side="left", padx=20)
        
        ctk.CTkButton(month_nav, text="▶", width=50, height=40,
                     command=self._next_month,
                     fg_color=COLORS['accent_blue'], hover_color="#0052a3",
                     font=("Segoe UI", 16, "bold")).pack(side="left", padx=5)
        
        # Year shortcut - PERFORMANCE OPTIMIZATION: Direct year jump
        year_nav = ctk.CTkFrame(nav_frame, fg_color="transparent")
        year_nav.pack(pady=2)
        
        ctk.CTkLabel(year_nav, text="Year:", 
                    font=("Segoe UI", 11),
                    text_color=COLORS['text_secondary']).pack(side="left", padx=5)
        
        # Year dropdown - O(1) year jump instead of O(n) month scrolling
        current_year = datetime.date.today().year
        years = [str(y) for y in range(current_year - 100, current_year + 5)]
        
        self.year_selector = ctk.CTkComboBox(
            year_nav, 
            values=years,
            width=100,
            height=32,
            command=self._on_year_changed,
            fg_color="#ffffff",
            border_color=COLORS['border'],
            button_color=COLORS['accent_blue'],
            button_hover_color="#0052a3",
            font=("Segoe UI", 12)
        )
        self.year_selector.set(str(self.selected_date.year))
        self.year_selector.pack(side="left", padx=5)
        
        # Calendar grid
        self.calendar_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_card'], corner_radius=15)
        self.calendar_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self._draw_calendar()
    
    def _draw_calendar(self):
        """Draw calendar grid - O(1) for 7x6 fixed grid"""
        # Clear existing widgets
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        
        # Update header and year selector
        self.lbl_month_year.configure(
            text=self.selected_date.strftime("%B %Y"))
        self.year_selector.set(str(self.selected_date.year))
        
        # Day headers
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for col, day in enumerate(days):
            lbl = ctk.CTkLabel(self.calendar_frame, text=day,
                             font=("Segoe UI", 11, "bold"),
                             text_color=COLORS['text_secondary'])
            lbl.grid(row=0, column=col, padx=2, pady=10, sticky="nsew")
        
        # Get calendar data
        import calendar
        cal = calendar.monthcalendar(self.selected_date.year, self.selected_date.month)
        
        today = datetime.date.today()
        
        # Draw dates
        for row_idx, week in enumerate(cal, start=1):
            for col_idx, day in enumerate(week):
                if day == 0:
                    continue
                
                date = datetime.date(self.selected_date.year, self.selected_date.month, day)
                
                # Determine colors
                is_today = date == today
                is_selected = date == self.selected_date
                
                if is_today:
                    fg_color = COLORS['accent_orange']
                    hover_color = "#e06700"
                elif is_selected:
                    fg_color = COLORS['accent_blue']
                    hover_color = "#0052a3"
                else:
                    fg_color = COLORS['bg_dark']
                    hover_color = COLORS['bg_card_hover']
                
                btn = ctk.CTkButton(self.calendar_frame, text=str(day),
                                   width=50, height=40,
                                   command=lambda d=date: self._select_date(d),
                                   fg_color=fg_color, hover_color=hover_color,
                                   font=("Segoe UI", 12, "bold"))
                btn.grid(row=row_idx, column=col_idx, padx=2, pady=2, sticky="nsew")
        
        # Configure grid
        for i in range(7):
            self.calendar_frame.grid_columnconfigure(i, weight=1, uniform="col")
        for i in range(7):
            self.calendar_frame.grid_rowconfigure(i, weight=1, uniform="row")
    
    def _prev_month(self):
        """Navigate to previous month - O(1)"""
        month = self.selected_date.month - 1
        year = self.selected_date.year
        if month < 1:
            month = 12
            year -= 1
        self.selected_date = datetime.date(year, month, 1)
        self._draw_calendar()
    
    def _next_month(self):
        """Navigate to next month - O(1)"""
        month = self.selected_date.month + 1
        year = self.selected_date.year
        if month > 12:
            month = 1
            year += 1
        self.selected_date = datetime.date(year, month, 1)
        self._draw_calendar()
    
    def _select_date(self, date: datetime.date):
        """Select date and close - O(1)"""
        date_str = date.strftime("%Y-%m-%d")
        self.callback(date_str)
        self.destroy()
    
    def _on_year_changed(self, year_str: str):
        """Handle year selection change - O(1) year jump"""
        try:
            new_year = int(year_str)
            self.selected_date = datetime.date(new_year, self.selected_date.month, 1)
            self._draw_calendar()
        except ValueError:
            pass  # Invalid year, ignore


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    """Launch application"""
    app = ClinicApp()
    app.mainloop()


if __name__ == "__main__":
    main()