"""
HYPER-OPTIMIZED Clinic Management System - ProvoHeal Style Dashboard
Performance-first architecture with O(1) lookups and minimal redraws
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import os
import sys
from typing import Optional, Dict, List

from config import COLORS, FONT_FAMILY, WINDOW_TITLE, WINDOW_SIZE, WINDOW_MIN_SIZE
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
        self.attributes('-fullscreen', True)
        self.bind("<Escape>", lambda e: self.attributes('-fullscreen', False))
        self.bind("<F11>", lambda e: self.attributes(
            '-fullscreen', not self.attributes('-fullscreen')))

        # Current view tracking - O(1) state management
        self.current_view = "overview"
        self.view_widgets = {}

        # Pagination state
        self.patients_page = 1
        self.patients_per_page = 10
        self.patients_total = 0
        self.visits_page = 1
        self.visits_per_page = 10
        self.visits_total = 0
        self.overview_page = 1
        self.overview_per_page = 20
        self.overview_total = 0

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
        
        ctk.CTkLabel(logo_frame, text="🏥", font=(FONT_FAMILY, 40)).pack()
        ctk.CTkLabel(logo_frame, text="Geneva Clinic",
                    font=(FONT_FAMILY, 22, "bold"),
                    text_color=COLORS['text_primary']).pack()
        ctk.CTkLabel(logo_frame, text="Patient Management",
                    font=(FONT_FAMILY, 13, "bold"),
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
                    font=(FONT_FAMILY, 14, "bold"),
                    text_color=COLORS['text_secondary']).pack(padx=20, pady=(20, 10), anchor="w")
        
        # New Visit button - PRIMARY ACTION
        ctk.CTkButton(sidebar, text="+ New Visit",
                     command=self._open_new_visit_dialog,
                     fg_color=COLORS['accent_green'],
                     hover_color="#16a34a",
                     height=52, corner_radius=18,
                     font=(FONT_FAMILY, 16, "bold")).pack(fill="x", padx=15, pady=4)

        # Encode Visit button - FOR OLD RECORDS
        ctk.CTkButton(sidebar, text="Encode Old Record",
                     command=self._open_encode_dialog,
                     fg_color=COLORS['accent_orange'],
                     hover_color="#ea580c",
                     height=52, corner_radius=18,
                     font=(FONT_FAMILY, 16, "bold")).pack(fill="x", padx=15, pady=4)
        
        # Bottom section
        bottom_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        
        ctk.CTkButton(bottom_frame, text="💾 Backup", command=self.backup_db,
                     fg_color=COLORS['accent_green'], hover_color="#1e7e34",
                     height=44, corner_radius=20,
                     font=(FONT_FAMILY, 14, "bold")).pack(fill="x", pady=5)

        ctk.CTkButton(bottom_frame, text="📊 Export", command=self.export_data,
                     fg_color=COLORS['accent_orange'], hover_color="#e06700",
                     height=44, corner_radius=20,
                     font=(FONT_FAMILY, 14, "bold")).pack(fill="x", pady=5)

        ctk.CTkButton(bottom_frame, text="⚙ Admin Settings", command=self._open_admin_settings,
                     fg_color=COLORS['accent_purple'], hover_color="#7c3aed",
                     height=44, corner_radius=20,
                     font=(FONT_FAMILY, 14, "bold")).pack(fill="x", pady=5)

        if sys.platform.startswith('linux'):
            ctk.CTkButton(bottom_frame, text="⏻ Shutdown", command=self._shutdown_computer,
                         fg_color=COLORS['accent_red'], hover_color="#d32f2f",
                         height=44, corner_radius=20,
                         font=(FONT_FAMILY, 14, "bold")).pack(fill="x", pady=5)

        # Branding
        brand_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand_frame.pack(side="bottom", fill="x", padx=20, pady=(0, 15))
        ctk.CTkLabel(brand_frame, text="\u00a9 2026 Rainberry Corp. All rights reserved.",
                    font=(FONT_FAMILY, 12, "bold"),
                    text_color=COLORS['text_muted']).pack()
        ctk.CTkLabel(brand_frame, text="Created and Designed by Jesbert V. Jalandoni",
                    font=(FONT_FAMILY, 11),
                    text_color=COLORS['text_muted']).pack()
        site_label = ctk.CTkLabel(brand_frame, text="jalandoni.jesbert.cloud",
                    font=(FONT_FAMILY, 11, "underline"),
                    text_color=COLORS['accent_blue'], cursor="hand2")
        site_label.pack()
        site_label.bind("<Button-1>", lambda e: __import__('webbrowser').open("https://jalandoni.jesbert.cloud/"))
    
    def _create_nav_button(self, parent, icon: str, text: str, view_id: str):
        """Create navigation button - modern style"""
        btn = ctk.CTkButton(
            parent, text=f"{icon}  {text}", command=lambda: self._switch_view(view_id),
            fg_color="transparent", hover_color=COLORS['bg_card_hover'],
            text_color=COLORS['text_primary'], anchor="w",
            height=50, corner_radius=20, font=(FONT_FAMILY, 15, "bold")
        )
        btn.pack(fill="x", padx=15, pady=2)
        return btn
    
    def _build_header(self):
        """Build header with clock"""
        header = ctk.CTkFrame(self.content_frame, fg_color="transparent", height=50)
        header.pack(fill="x", padx=20, pady=(20, 15))
        header.pack_propagate(False)

        # Clock on the right
        self.lbl_clock = ctk.CTkLabel(header, text="",
                                     font=(FONT_FAMILY, 20, "bold"),
                                     text_color=COLORS['text_primary'])
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
            self._search_patients()  # Populate patients
        elif view_id == "visits":
            self.view_widgets[view_id] = self._build_visits_view()
            self._refresh_today_visits()  # Populate visits
    
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
            ("total_patients", "Total Patients", COLORS['accent_blue']),
            ("total_records", "Total Records", COLORS['accent_green']),
        ]

        for i, (key, title, color) in enumerate(card_configs):
            card = self._create_stat_card(stats_row, title, "0", color)
            card.pack(side="left", fill="both", expand=True, padx=(0, 15 if i < 1 else 0))
            self.stat_cards[key] = card
        
        # Recent visits section - transparent, tree creates its own rounded container
        visits_frame = ctk.CTkFrame(overview, fg_color="transparent")
        visits_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Header
        header = ctk.CTkFrame(visits_frame, fg_color="transparent", height=60)
        header.pack(fill="x", padx=20, pady=(20, 10))
        header.pack_propagate(False)
        
        ctk.CTkLabel(header, text="📋 Recent Patient Appointments",
                    font=(FONT_FAMILY, 20, "bold"),
                    text_color=COLORS['text_primary']).pack(side="left")

        ctk.CTkButton(header, text="🔍 Search patient...", command=self._focus_search,
                     fg_color=COLORS['bg_dark'], hover_color=COLORS['bg_card_hover'],
                     text_color=COLORS['text_primary'],
                     height=42, width=240, corner_radius=20,
                     border_width=1, border_color=COLORS['border'],
                     font=(FONT_FAMILY, 14, "bold")).pack(side="right")
        
        # Table
        self.tree_overview = self._create_optimized_tree(visits_frame,
            ["Ref#", "Date", "Patient Name", "Weight", "BP", "Temp", "Notes"])

        # Configure columns for optimal display
        self.tree_overview.column("#0", width=0, stretch=False)
        self.tree_overview.column("Ref#", width=70, anchor="center")
        self.tree_overview.column("Date", width=150, anchor="center")
        self.tree_overview.column("Patient Name", width=200)
        self.tree_overview.column("Weight", width=80, anchor="center")
        self.tree_overview.column("BP", width=100, anchor="center")
        self.tree_overview.column("Temp", width=80, anchor="center")
        self.tree_overview.column("Notes", width=250)
        
        # Bind double-click to view patient details from visit
        self.tree_overview.bind("<Double-Button-1>", self._on_overview_visit_double_click)

        # Pagination controls
        overview_pagination = ctk.CTkFrame(overview, fg_color=COLORS['bg_card'], corner_radius=20, height=60)
        overview_pagination.pack(fill="x", padx=15, pady=(0, 15))
        overview_pagination.pack_propagate(False)

        overview_pg_content = ctk.CTkFrame(overview_pagination, fg_color="transparent")
        overview_pg_content.pack(expand=True)

        ctk.CTkButton(overview_pg_content, text="◀ Previous",
                     command=self._overview_prev_page,
                     fg_color=COLORS['accent_blue'], hover_color="#0052a3",
                     height=40, width=120, corner_radius=15,
                     font=(FONT_FAMILY, 14, "bold")).pack(side="left", padx=10)

        self.lbl_overview_page = ctk.CTkLabel(overview_pg_content, text="Page 1 of 1",
                                              font=(FONT_FAMILY, 15, "bold"),
                                              text_color=COLORS['text_primary'])
        self.lbl_overview_page.pack(side="left", padx=20)

        ctk.CTkButton(overview_pg_content, text="Next ▶",
                     command=self._overview_next_page,
                     fg_color=COLORS['accent_blue'], hover_color="#0052a3",
                     height=40, width=120, corner_radius=15,
                     font=(FONT_FAMILY, 14, "bold")).pack(side="left", padx=10)
    
    def _create_stat_card(self, parent, title: str, value: str, color: str):
        """Create stat card widget - returns frame with update references"""
        card = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=15,
                           border_width=1, border_color=COLORS['border'])

        # Content
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(content, text=title,
                    font=(FONT_FAMILY, 16, "bold"),
                    text_color=COLORS['text_secondary']).pack(anchor="w")

        # Value (store reference for O(1) updates)
        value_label = ctk.CTkLabel(content, text=value,
                                   font=(FONT_FAMILY, 36, "bold"),
                                   text_color=color)
        value_label.pack(anchor="w", pady=(5, 0))

        # Store reference for fast updates
        card.value_label = value_label

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
                    font=(FONT_FAMILY, 22, "bold"),
                    text_color=COLORS['text_primary']).pack(side="left", padx=(0, 15))

        ctk.CTkButton(left_frame, text="➕ Add Patient",
                     command=self._open_add_patient_dialog,
                     fg_color=COLORS['accent_blue'], hover_color="#0052a3",
                     height=44, corner_radius=20, font=(FONT_FAMILY, 15, "bold")).pack(side="left", padx=(0, 10))

        ctk.CTkButton(left_frame, text="🔄 Refresh",
                     command=self._search_patients,
                     fg_color=COLORS['accent_green'], hover_color="#1e7e34",
                     height=44, corner_radius=20, font=(FONT_FAMILY, 15, "bold")).pack(side="left")

        # Right: Search bar
        search_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        search_frame.pack(side="right")
        
        self.entry_patient_search = ctk.CTkEntry(search_frame,
                                                placeholder_text="🔍 Search patients...",
                                                width=350, height=48, corner_radius=20,
                                                font=(FONT_FAMILY, 15))
        self.entry_patient_search.pack(side="left", padx=5)
        self.entry_patient_search.bind("<KeyRelease>", lambda e: self._search_patients())
        
        # Table - transparent container, tree has its own rounded frame
        table_frame = ctk.CTkFrame(frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True)

        self.tree_patients = self._create_optimized_tree(table_frame,
            ["ID", "Last Name", "First Name", "Middle Name", "Age", "Contact", "Address"])

        self.tree_patients.column("ID", width=60, anchor="center")
        self.tree_patients.column("Last Name", width=150)
        self.tree_patients.column("First Name", width=150)
        self.tree_patients.column("Middle Name", width=120)
        self.tree_patients.column("Age", width=70, anchor="center")
        self.tree_patients.column("Contact", width=130, anchor="center")
        self.tree_patients.column("Address", width=200)

        # Bind double-click to view patient details
        self.tree_patients.bind("<Double-Button-1>", self._on_patient_double_click)

        # Pagination controls
        pagination_frame = ctk.CTkFrame(frame, fg_color=COLORS['bg_card'], corner_radius=20, height=60)
        pagination_frame.pack(fill="x", pady=(10, 0))
        pagination_frame.pack_propagate(False)

        pagination_content = ctk.CTkFrame(pagination_frame, fg_color="transparent")
        pagination_content.pack(expand=True)

        ctk.CTkButton(pagination_content, text="◀ Previous",
                     command=self._patients_prev_page,
                     fg_color=COLORS['accent_blue'], hover_color="#0052a3",
                     height=40, width=120, corner_radius=15,
                     font=(FONT_FAMILY, 14, "bold")).pack(side="left", padx=10)

        self.lbl_patients_page = ctk.CTkLabel(pagination_content, text="Page 1 of 1",
                                              font=(FONT_FAMILY, 15, "bold"),
                                              text_color=COLORS['text_primary'])
        self.lbl_patients_page.pack(side="left", padx=20)

        ctk.CTkButton(pagination_content, text="Next ▶",
                     command=self._patients_next_page,
                     fg_color=COLORS['accent_blue'], hover_color="#0052a3",
                     height=40, width=120, corner_radius=15,
                     font=(FONT_FAMILY, 14, "bold")).pack(side="left", padx=10)

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
        
        self.lbl_today_count = ctk.CTkLabel(stats_content, text="Total: 0 record(s)",
                                           font=(FONT_FAMILY, 20, "bold"),
                                           text_color=COLORS['accent_blue'])
        self.lbl_today_count.pack(side="left")

        ctk.CTkButton(stats_content, text="🔄 Refresh", command=self._refresh_today_visits,
                     fg_color=COLORS['accent_green'], hover_color="#1e7e34",
                     height=44, corner_radius=20,
                     font=(FONT_FAMILY, 14, "bold")).pack(side="right")
        
        # Table - transparent container, tree has its own rounded frame
        table_frame = ctk.CTkFrame(frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True)

        self.tree_today = self._create_optimized_tree(table_frame,
            ["Ref#", "Patient", "Date", "Time", "Weight", "Height", "BP", "Temp", "Notes"])

        self.tree_today.column("Ref#", width=60, anchor="center")
        self.tree_today.column("Patient", width=180)
        self.tree_today.column("Date", width=150, anchor="center")
        self.tree_today.column("Time", width=80, anchor="center")
        self.tree_today.column("Weight", width=70, anchor="center")
        self.tree_today.column("Height", width=70, anchor="center")
        self.tree_today.column("BP", width=80, anchor="center")
        self.tree_today.column("Temp", width=70, anchor="center")
        self.tree_today.column("Notes", width=200)
        
        # Bind click to view patient details - O(1) lookup
        self.tree_today.bind("<Double-Button-1>", self._on_visit_double_click)

        # Pagination controls
        pagination_frame = ctk.CTkFrame(frame, fg_color=COLORS['bg_card'], corner_radius=20, height=60)
        pagination_frame.pack(fill="x", pady=(10, 0))
        pagination_frame.pack_propagate(False)

        pagination_content = ctk.CTkFrame(pagination_frame, fg_color="transparent")
        pagination_content.pack(expand=True)

        ctk.CTkButton(pagination_content, text="◀ Previous",
                     command=self._visits_prev_page,
                     fg_color=COLORS['accent_blue'], hover_color="#0052a3",
                     height=40, width=120, corner_radius=15,
                     font=(FONT_FAMILY, 14, "bold")).pack(side="left", padx=10)

        self.lbl_visits_page = ctk.CTkLabel(pagination_content, text="Page 1 of 1",
                                            font=(FONT_FAMILY, 15, "bold"),
                                            text_color=COLORS['text_primary'])
        self.lbl_visits_page.pack(side="left", padx=20)

        ctk.CTkButton(pagination_content, text="Next ▶",
                     command=self._visits_next_page,
                     fg_color=COLORS['accent_blue'], hover_color="#0052a3",
                     height=40, width=120, corner_radius=15,
                     font=(FONT_FAMILY, 14, "bold")).pack(side="left", padx=10)

        return frame

    # ═══════════════════════════════════════════════════════════════════════════
    # OPTIMIZED TREEVIEW FACTORY
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _create_optimized_tree(self, parent, columns: List[str]):
        """Create performance-optimized treeview with modern styling"""
        # Outer rounded container for modern look
        outer_container = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=25)
        outer_container.pack(fill="both", expand=True, padx=15, pady=15)

        # Inner container with padding
        container = ctk.CTkFrame(outer_container, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=8, pady=8)

        # Style
        style = ttk.Style()
        style.theme_use("default")

        # Configure colors - Modern clean look with softer colors
        style.configure("Custom.Treeview",
                       background="#ffffff",
                       foreground=COLORS['text_primary'],
                       fieldbackground="#ffffff",
                       borderwidth=0,
                       relief="flat",
                       font=(FONT_FAMILY, 13),
                       rowheight=52)

        style.configure("Custom.Treeview.Heading",
                       background=COLORS['accent_blue'],
                       foreground="#ffffff",
                       borderwidth=0,
                       relief="flat",
                       font=(FONT_FAMILY, 13, "bold"),
                       padding=(14, 12))

        style.map("Custom.Treeview",
                 background=[("selected", COLORS['accent_blue'])],
                 foreground=[("selected", "#ffffff")])

        style.map("Custom.Treeview.Heading",
                 background=[("active", "#2563eb")])

        # Scrollbar with modern styling
        scrollbar = ctk.CTkScrollbar(container, orientation="vertical", corner_radius=10)
        scrollbar.pack(side="right", fill="y", padx=(5, 0))

        # Tree
        tree = ttk.Treeview(container, columns=columns, show="headings",
                           style="Custom.Treeview", yscrollcommand=scrollbar.set,
                           selectmode="browse")
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.configure(command=tree.yview)

        # Set headings
        for col in columns:
            tree.heading(col, text=col.upper())

        # Add zebra striping with softer colors
        tree.tag_configure('evenrow', background='#f8fafc')
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

        # Use efficient COUNT queries instead of loading all records
        stats = {
            "total_patients": self.db.get_patient_count(),
            "total_records": self.db.get_visit_count(),
        }
        self.stats_cache.update(stats)

        # Update UI - O(1) label updates
        self.stat_cards["total_patients"].value_label.configure(
            text=str(stats["total_patients"]))
        self.stat_cards["total_records"].value_label.configure(
            text=str(stats["total_records"]))
    
    def _refresh_recent_visits(self, reset_page: bool = True):
        """Refresh recent visits table with pagination"""
        if reset_page:
            self.overview_page = 1

        visits, self.overview_total = self.db.get_visits_paginated(
            self.overview_page, self.overview_per_page)
        total_pages = max(1, (self.overview_total + self.overview_per_page - 1) // self.overview_per_page)

        # Update pagination label
        self.lbl_overview_page.configure(
            text=f"Page {self.overview_page} of {total_pages}  ({self.overview_total} total)")

        # Clear and populate - batch operations
        for item in self.tree_overview.get_children():
            self.tree_overview.delete(item)

        for idx, visit in enumerate(visits):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.tree_overview.insert("", "end", values=(
                visit['reference_number'],
                format_date_readable(visit['visit_date']),
                visit['full_name'],
                f"{visit['weight_kg']}" if visit.get('weight_kg') else "-",
                visit.get('blood_pressure') or "-",
                f"{visit['temperature_celsius']}" if visit.get('temperature_celsius') else "-",
                (visit.get('medical_notes') or "")[:40]
            ), tags=(tag,))
    
    def _refresh_today_visits(self, reset_page: bool = True):
        """Refresh visits tab with pagination"""
        if "visits" not in self.view_widgets:
            return

        # Reset to page 1 on refresh
        if reset_page:
            self.visits_page = 1

        # Get paginated visits
        visits, self.visits_total = self.db.get_visits_paginated(
            self.visits_page, self.visits_per_page)
        total_pages = max(1, (self.visits_total + self.visits_per_page - 1) // self.visits_per_page)

        # Update pagination label
        self.lbl_visits_page.configure(
            text=f"Page {self.visits_page} of {total_pages}  ({self.visits_total} total)")

        # Clear and populate
        for item in self.tree_today.get_children():
            self.tree_today.delete(item)

        for idx, visit in enumerate(visits):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.tree_today.insert("", "end", values=(
                visit['reference_number'],
                visit['full_name'],
                format_date_readable(visit['visit_date']),
                format_time_12hr(visit.get('visit_time')),
                f"{visit['weight_kg']}" if visit.get('weight_kg') else "-",
                f"{visit['height_cm']}" if visit.get('height_cm') else "-",
                visit.get('blood_pressure') or "-",
                f"{visit['temperature_celsius']}" if visit.get('temperature_celsius') else "-",
                (visit.get('medical_notes') or "")[:40]
            ), tags=(tag,))

        self.lbl_today_count.configure(text=f"Showing {len(visits)} of {self.visits_total} record(s)")

    def _visits_prev_page(self):
        """Go to previous page of visits"""
        if self.visits_page > 1:
            self.visits_page -= 1
            self._refresh_today_visits(reset_page=False)

    def _visits_next_page(self):
        """Go to next page of visits"""
        total_pages = max(1, (self.visits_total + self.visits_per_page - 1) // self.visits_per_page)
        if self.visits_page < total_pages:
            self.visits_page += 1
            self._refresh_today_visits(reset_page=False)

    def _overview_prev_page(self):
        """Go to previous page of overview visits"""
        if self.overview_page > 1:
            self.overview_page -= 1
            self._refresh_recent_visits(reset_page=False)

    def _overview_next_page(self):
        """Go to next page of overview visits"""
        total_pages = max(1, (self.overview_total + self.overview_per_page - 1) // self.overview_per_page)
        if self.overview_page < total_pages:
            self.overview_page += 1
            self._refresh_recent_visits(reset_page=False)

    def _search_patients(self, reset_page: bool = True):
        """Real-time patient search with pagination"""
        if "patients" not in self.view_widgets:
            return

        query = self.entry_patient_search.get().strip()

        # Reset to page 1 when searching
        if reset_page:
            self.patients_page = 1

        # Clear table
        for item in self.tree_patients.get_children():
            self.tree_patients.delete(item)

        # Query database with pagination
        if query:
            # For search, use existing method (limited results)
            patients = self.db.search_patients(query)
            self.patients_total = len(patients)
            total_pages = 1
        else:
            # Use paginated query
            patients, self.patients_total = self.db.get_patients_paginated(
                self.patients_page, self.patients_per_page)
            total_pages = max(1, (self.patients_total + self.patients_per_page - 1) // self.patients_per_page)

        # Update pagination label
        self.lbl_patients_page.configure(
            text=f"Page {self.patients_page} of {total_pages}  ({self.patients_total} total)")

        # Populate with zebra striping
        from utils import calculate_age
        for idx, patient in enumerate(patients):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            # Calculate age from DOB
            age = calculate_age(patient.get('date_of_birth'))
            age_display = str(age) if age is not None else "-"
            self.tree_patients.insert("", "end", values=(
                patient['patient_id'],
                patient['last_name'],
                patient['first_name'],
                patient.get('middle_name', '') or "-",
                age_display,
                patient['contact_number'] or "-",
                patient['address'] or "-"
            ), tags=(tag,))

    def _patients_prev_page(self):
        """Go to previous page of patients"""
        if self.patients_page > 1:
            self.patients_page -= 1
            self._search_patients(reset_page=False)

    def _patients_next_page(self):
        """Go to next page of patients"""
        total_pages = max(1, (self.patients_total + self.patients_per_page - 1) // self.patients_per_page)
        if self.patients_page < total_pages:
            self.patients_page += 1
            self._search_patients(reset_page=False)
    
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

    def _open_encode_dialog(self):
        """Open encode dialog for old physical records"""
        EncodeVisitDialog(self, self.db, self._on_encode_added)

    def _on_encode_added(self, visit_id: int, reference_number: int):
        """Callback after encoded visit is added"""
        self.stats_cache.invalidate()
        self._refresh_stats()
        self._refresh_recent_visits()
        if "visits" in self.view_widgets:
            self._refresh_today_visits()
        messagebox.showinfo("Success", f"Record #{reference_number} encoded successfully!")

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
        """Handle visit log double-click - open edit dialog"""
        selection = self.tree_today.selection()
        if selection:
            values = self.tree_today.item(selection[0], "values")
            reference_number = int(values[0])
            # Get visit by reference number
            visit = self.db.get_visit_by_reference(reference_number)
            if visit:
                def on_edit_complete():
                    self.stats_cache.invalidate()
                    self._refresh_stats()
                    self._refresh_recent_visits()
                    self._refresh_today_visits()
                EditVisitDialog(self, self.db, visit['visit_id'], on_edit_complete)
    
    def _on_overview_visit_double_click(self, event):
        """Handle overview visit double-click - open edit dialog"""
        selection = self.tree_overview.selection()
        if selection:
            values = self.tree_overview.item(selection[0], "values")
            reference_number = int(values[0])
            # Get visit by reference number
            visit = self.db.get_visit_by_reference(reference_number)
            if visit:
                def on_edit_complete():
                    self.stats_cache.invalidate()
                    self._refresh_stats()
                    self._refresh_recent_visits()
                    if "visits" in self.view_widgets:
                        self._refresh_today_visits()
                EditVisitDialog(self, self.db, visit['visit_id'], on_edit_complete)
    
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
    
    def _open_admin_settings(self):
        """Open admin settings dialog"""
        AdminSettingsDialog(self, self.db)

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

    def _shutdown_computer(self):
        """Shutdown the computer (Linux/Raspberry Pi) with confirmation"""
        if messagebox.askyesno("Shutdown",
                               "Are you sure you want to shut down the computer?\n\n"
                               "Make sure all work is saved.",
                               icon="warning"):
            os.system("sudo poweroff")


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

        # Modal
        self.transient(parent)
        self.after(150, self.grab_set)

        # Build UI
        self._build_ui()

        # Center on screen
        self.update_idletasks()
        sx = self.winfo_screenwidth()
        sy = self.winfo_screenheight()
        self.geometry(f"700x800+{(sx - 700) // 2}+{(sy - 800) // 2}")
    
    def _build_ui(self):
        """Build visit dialog UI - O(1) widget construction"""
        # Header
        header = ctk.CTkFrame(self, fg_color=COLORS['accent_green'], corner_radius=15, height=80)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(expand=True, fill="both", padx=30)
        
        ctk.CTkLabel(header_content, text="➕ Record New Visit", 
                    font=(FONT_FAMILY, 24, "bold"),
                    text_color="#ffffff").pack(anchor="w")
        ctk.CTkLabel(header_content, text="Select patient and record visit details", 
                    font=(FONT_FAMILY, 14),
                    text_color="#ffffff").pack(anchor="w")
        
        # Main form
        form = ctk.CTkScrollableFrame(self, fg_color=COLORS['bg_card'], corner_radius=15,
                                     border_width=1, border_color=COLORS['border'])
        form.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        form_content = ctk.CTkFrame(form, fg_color="transparent")
        form_content.pack(fill="both", expand=True, padx=25, pady=25)
        
        # SECTION 1: Patient Selection
        ctk.CTkLabel(form_content, text="1️⃣ SELECT PATIENT", 
                    font=(FONT_FAMILY, 16, "bold"),
                    text_color=COLORS['accent_blue']).pack(anchor="w", pady=(0, 10))
        
        patient_frame = ctk.CTkFrame(form_content, fg_color=COLORS['bg_dark'], corner_radius=20)
        patient_frame.pack(fill="x", pady=(0, 20))
        
        patient_content = ctk.CTkFrame(patient_frame, fg_color="transparent")
        patient_content.pack(fill="x", padx=15, pady=15)
        
        # Search patient
        search_frame = ctk.CTkFrame(patient_content, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(search_frame, text="Search Patient:", 
                    font=(FONT_FAMILY, 14),
                    text_color=COLORS['text_secondary']).pack(side="left", padx=(0, 10))
        
        self.entry_search = ctk.CTkEntry(search_frame, placeholder_text="Type patient name...",
                                        height=44, font=(FONT_FAMILY, 14))
        self.entry_search.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_search.bind("<KeyRelease>", self._on_search_change)
        
        # Modern patient list with scrollable frame
        list_container = ctk.CTkFrame(patient_content, fg_color="#ffffff", corner_radius=15,
                                     border_width=1, border_color=COLORS['border'], height=180)
        list_container.pack(fill="x", pady=(0, 10))
        list_container.pack_propagate(False)

        self.patient_list_frame = ctk.CTkScrollableFrame(list_container, fg_color="transparent")
        self.patient_list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.patient_buttons = []  # Store patient button references
        
        # Selected patient display
        self.lbl_selected = ctk.CTkLabel(patient_content, text="No patient selected", 
                                        font=(FONT_FAMILY, 14, "bold"),
                                        text_color=COLORS['text_secondary'])
        self.lbl_selected.pack(anchor="w", pady=(0, 10))
        
        # Add new patient button
        btn_add_patient = ctk.CTkButton(patient_content, text="➕ Patient Not Found? Add New Patient",
                                       command=self._open_add_patient,
                                       fg_color=COLORS['accent_orange'], hover_color="#e06700",
                                       height=40, corner_radius=15,
                                       font=(FONT_FAMILY, 12, "bold"))
        btn_add_patient.pack(fill="x")
        
        # SECTION 2: Reference Number (editable for old records)
        ctk.CTkLabel(form_content, text="2️⃣ REFERENCE NUMBER",
                    font=(FONT_FAMILY, 16, "bold"),
                    text_color=COLORS['accent_orange']).pack(anchor="w", pady=(10, 10))

        ref_frame = ctk.CTkFrame(form_content, fg_color=COLORS['bg_dark'], corner_radius=15)
        ref_frame.pack(fill="x", pady=(0, 15))

        ref_content = ctk.CTkFrame(ref_frame, fg_color="transparent")
        ref_content.pack(fill="x", padx=15, pady=15)

        ref_row = ctk.CTkFrame(ref_content, fg_color="transparent")
        ref_row.pack(fill="x")

        ctk.CTkLabel(ref_row, text="Reference #:",
                    font=(FONT_FAMILY, 12, "bold"),
                    text_color=COLORS['text_primary']).pack(side="left", padx=(0, 10))

        next_ref = self.db.get_next_reference_number()
        self.entry_ref = ctk.CTkEntry(ref_row, width=120, height=40,
                                     font=(FONT_FAMILY, 14, "bold"),
                                     justify="center")
        self.entry_ref.pack(side="left", padx=(0, 15))
        self.entry_ref.insert(0, str(next_ref))
        self.entry_ref.bind("<KeyRelease>", self._validate_reference)

        self.lbl_ref_validation = ctk.CTkLabel(ref_row, text=f"Next available: {next_ref}",
                                               font=(FONT_FAMILY, 13),
                                               text_color=COLORS['accent_green'])
        self.lbl_ref_validation.pack(side="left")

        # SECTION 3: Visit Details
        ctk.CTkLabel(form_content, text="3️⃣ VISIT DETAILS",
                    font=(FONT_FAMILY, 16, "bold"),
                    text_color=COLORS['accent_blue']).pack(anchor="w", pady=(10, 10))

        # Date and Time
        datetime_frame = ctk.CTkFrame(form_content, fg_color="transparent")
        datetime_frame.pack(fill="x", pady=(0, 15))
        
        # Date
        date_col = ctk.CTkFrame(datetime_frame, fg_color="transparent")
        date_col.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(date_col, text="Visit Date",
                    font=(FONT_FAMILY, 14, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w")

        date_input_frame = ctk.CTkFrame(date_col, fg_color="transparent")
        date_input_frame.pack(fill="x", pady=(5, 0))

        self.entry_date = ctk.CTkEntry(date_input_frame, placeholder_text="YYYY-MM-DD",
                                      height=44, font=(FONT_FAMILY, 14))
        self.entry_date.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry_date.insert(0, datetime.date.today().strftime("%Y-%m-%d"))

        ctk.CTkButton(date_input_frame, text="📅", width=45, height=40,
                     command=self._open_date_calendar,
                     fg_color=COLORS['accent_blue'], hover_color="#0052a3",
                     font=(FONT_FAMILY, 16)).pack(side="right")

        # Time
        time_col = ctk.CTkFrame(datetime_frame, fg_color="transparent")
        time_col.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(time_col, text="Visit Time",
                    font=(FONT_FAMILY, 14, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w")

        time_input_frame = ctk.CTkFrame(time_col, fg_color="transparent")
        time_input_frame.pack(fill="x", pady=(5, 0))

        # Hour dropdown
        hours = [f"{h:02d}" for h in range(1, 13)]
        self.hour_var = ctk.StringVar(value=datetime.datetime.now().strftime("%I"))
        self.hour_dropdown = ctk.CTkComboBox(time_input_frame, values=hours,
                                            variable=self.hour_var, width=70, height=40,
                                            font=(FONT_FAMILY, 14))
        self.hour_dropdown.pack(side="left", padx=(0, 5))

        ctk.CTkLabel(time_input_frame, text=":", font=(FONT_FAMILY, 16, "bold"),
                    text_color=COLORS['text_primary']).pack(side="left")

        # Minute dropdown
        minutes = [f"{m:02d}" for m in range(0, 60, 5)]
        current_min = (datetime.datetime.now().minute // 5) * 5
        self.minute_var = ctk.StringVar(value=f"{current_min:02d}")
        self.minute_dropdown = ctk.CTkComboBox(time_input_frame, values=minutes,
                                              variable=self.minute_var, width=70, height=40,
                                              font=(FONT_FAMILY, 14))
        self.minute_dropdown.pack(side="left", padx=(5, 5))

        # AM/PM dropdown
        self.ampm_var = ctk.StringVar(value=datetime.datetime.now().strftime("%p"))
        self.ampm_dropdown = ctk.CTkComboBox(time_input_frame, values=["AM", "PM"],
                                            variable=self.ampm_var, width=70, height=40,
                                            font=(FONT_FAMILY, 14))
        self.ampm_dropdown.pack(side="left")
        
        # Vital Signs Row
        vitals_frame = ctk.CTkFrame(form_content, fg_color="transparent")
        vitals_frame.pack(fill="x", pady=(0, 15))
        
        # Weight
        weight_col = ctk.CTkFrame(vitals_frame, fg_color="transparent")
        weight_col.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(weight_col, text="Weight (kg)", 
                    font=(FONT_FAMILY, 14, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w")
        self.entry_weight = ctk.CTkEntry(weight_col, placeholder_text="e.g., 65.5",
                                        height=44, font=(FONT_FAMILY, 14))
        self.entry_weight.pack(fill="x", pady=(5, 0))
        
        # Height
        height_col = ctk.CTkFrame(vitals_frame, fg_color="transparent")
        height_col.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(height_col, text="Height (cm)", 
                    font=(FONT_FAMILY, 14, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w")
        self.entry_height = ctk.CTkEntry(height_col, placeholder_text="e.g., 165",
                                        height=44, font=(FONT_FAMILY, 14))
        self.entry_height.pack(fill="x", pady=(5, 0))
        
        # BP and Temp Row
        vitals2_frame = ctk.CTkFrame(form_content, fg_color="transparent")
        vitals2_frame.pack(fill="x", pady=(0, 15))
        
        # Blood Pressure
        bp_col = ctk.CTkFrame(vitals2_frame, fg_color="transparent")
        bp_col.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(bp_col, text="Blood Pressure", 
                    font=(FONT_FAMILY, 14, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w")
        self.entry_bp = ctk.CTkEntry(bp_col, placeholder_text="e.g., 120/80",
                                    height=44, font=(FONT_FAMILY, 14))
        self.entry_bp.pack(fill="x", pady=(5, 0))
        
        # Temperature
        temp_col = ctk.CTkFrame(vitals2_frame, fg_color="transparent")
        temp_col.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(temp_col, text="Temperature (°C)", 
                    font=(FONT_FAMILY, 14, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w")
        self.entry_temp = ctk.CTkEntry(temp_col, placeholder_text="e.g., 37.2",
                                      height=44, font=(FONT_FAMILY, 14))
        self.entry_temp.pack(fill="x", pady=(5, 0))
        
        # Medical Notes
        ctk.CTkLabel(form_content, text="Medical Notes / Reason for Visit", 
                    font=(FONT_FAMILY, 12, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w", pady=(5, 5))
        
        self.entry_notes = ctk.CTkTextbox(form_content, height=100, 
                                         font=(FONT_FAMILY, 14),
                                         fg_color="#ffffff",
                                         border_color=COLORS['border'],
                                         border_width=1)
        self.entry_notes.pack(fill="x", pady=(0, 20))
        
        # Footer buttons
        footer = ctk.CTkFrame(form_content, fg_color="transparent")
        footer.pack(fill="x")
        
        ctk.CTkButton(footer, text="Save Visit", command=self._save_visit,
                     fg_color=COLORS['accent_green'], hover_color="#16a34a",
                     height=44, corner_radius=20,
                     font=(FONT_FAMILY, 14, "bold")).pack(side="right", padx=(10, 0))

        ctk.CTkButton(footer, text="Cancel", command=self.destroy,
                     fg_color=COLORS['text_muted'], hover_color=COLORS['text_secondary'],
                     height=44, corner_radius=20,
                     font=(FONT_FAMILY, 14, "bold")).pack(side="right")
        
        # Load all patients initially
        self._load_patients()
    
    def _load_patients(self, query: str = ""):
        """Load patients into modern scrollable list"""
        # Clear existing buttons
        for widget in self.patient_list_frame.winfo_children():
            widget.destroy()
        self.patient_buttons = []
        self.patient_data = {}

        if query:
            patients = self.db.search_patients(query)
        else:
            patients = self.db.get_all_patients()

        for idx, patient in enumerate(patients):
            first = patient.get('first_name', '')
            middle = patient.get('middle_name', '')
            last = patient.get('last_name', '')
            full_name = f"{last}, {first}" + (f" {middle}" if middle else "")

            patient_id = patient['patient_id']
            self.patient_data[idx] = (patient_id, full_name)

            # Create modern clickable card for each patient
            btn = ctk.CTkButton(
                self.patient_list_frame,
                text=f"{full_name}  •  ID: {patient_id}",
                font=(FONT_FAMILY, 14),
                fg_color="transparent",
                hover_color=COLORS['status_info'],
                text_color=COLORS['text_primary'],
                anchor="w",
                height=40,
                corner_radius=18,
                command=lambda pid=patient_id, name=full_name: self._select_patient(pid, name)
            )
            btn.pack(fill="x", pady=2)
            self.patient_buttons.append((btn, patient_id))
    
    def _on_search_change(self, event):
        """Handle search input - O(1) event + O(n) query"""
        query = self.entry_search.get().strip()
        self._load_patients(query)
        self.selected_patient_id = None
        self.lbl_selected.configure(text="No patient selected", 
                                   text_color=COLORS['text_secondary'])
    
    def _select_patient(self, patient_id, patient_name):
        """Handle patient selection from modern list"""
        self.selected_patient_id = patient_id
        self.selected_patient_name = patient_name
        self.lbl_selected.configure(
            text=f"✓ Selected: {patient_name}",
            text_color=COLORS['accent_green'])

        # Highlight selected button
        for btn, pid in self.patient_buttons:
            if pid == patient_id:
                btn.configure(fg_color=COLORS['accent_blue'], text_color="#ffffff")
            else:
                btn.configure(fg_color="transparent", text_color=COLORS['text_primary'])
    
    def _open_add_patient(self):
        """Open add patient dialog from within visit dialog"""
        def on_patient_added(patient_id):
            # Refresh patient list and auto-select the new patient
            self._load_patients()

            # Find and select the newly added patient
            for idx, (pid, name) in self.patient_data.items():
                if pid == patient_id:
                    self._select_patient(pid, name)
                    break

            messagebox.showinfo("Success",
                              f"Patient added! You can now record their visit.",
                              parent=self)

        AddPatientDialog(self, self.db, on_patient_added)

    def _open_date_calendar(self):
        """Open calendar picker for visit date"""
        def on_date_selected(date_str):
            self.entry_date.delete(0, "end")
            self.entry_date.insert(0, date_str)
        CalendarDialog(self, on_date_selected)
    
    def _validate_reference(self, event=None):
        """Validate reference number availability"""
        try:
            ref_num = int(self.entry_ref.get().strip())
            if not self.db.is_reference_number_available(ref_num):
                self.lbl_ref_validation.configure(
                    text=f"⚠ Reference #{ref_num} already exists!",
                    text_color=COLORS['accent_red'])
            else:
                self.lbl_ref_validation.configure(
                    text=f"✓ Reference #{ref_num} is available",
                    text_color=COLORS['accent_green'])
        except ValueError:
            self.lbl_ref_validation.configure(
                text="Enter a valid number",
                text_color=COLORS['accent_red'])

    def _save_visit(self):
        """Save visit to database - all fields optional except patient"""
        # Validate patient selection (only required field)
        if not self.selected_patient_id:
            messagebox.showerror("Validation Error",
                               "Please select a patient first!",
                               parent=self)
            return

        # Validate and get reference number
        try:
            reference_number = int(self.entry_ref.get().strip())
            if not self.db.is_reference_number_available(reference_number):
                messagebox.showerror("Validation Error",
                                   f"Reference #{reference_number} already exists! Choose another.",
                                   parent=self)
                return
        except ValueError:
            messagebox.showerror("Validation Error",
                               "Invalid reference number!",
                               parent=self)
            return

        # Get date - use today if not provided
        visit_date = self.entry_date.get().strip()
        if not visit_date:
            visit_date = datetime.date.today().strftime("%Y-%m-%d")
        else:
            try:
                datetime.datetime.strptime(visit_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Validation Error",
                                   "Invalid date format! Use YYYY-MM-DD",
                                   parent=self)
                return

        # Get time from dropdowns
        hour = self.hour_var.get()
        minute = self.minute_var.get()
        ampm = self.ampm_var.get()
        time_str = f"{hour}:{minute} {ampm}"
        from utils import parse_time_input
        visit_time = parse_time_input(time_str) or datetime.datetime.now().strftime("%H:%M:%S")

        # Get optional fields - no validation limits
        from utils import safe_float
        weight = safe_float(self.entry_weight.get())
        height = safe_float(self.entry_height.get())
        bp = self.entry_bp.get().strip()
        temp = safe_float(self.entry_temp.get())
        notes = self.entry_notes.get("1.0", "end-1c").strip()

        # Add to database with custom reference number
        visit_id = self.db.add_visit(
            patient_id=self.selected_patient_id,
            visit_date=visit_date,
            visit_time=visit_time,
            weight=weight,
            height=height,
            bp=bp,
            temp=temp,
            notes=notes,
            reference_number=reference_number
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

        # Modal
        self.transient(parent)
        self.after(150, self.grab_set)

        # Build UI
        self._build_ui()

        # Center on screen
        self.update_idletasks()
        sx = self.winfo_screenwidth()
        sy = self.winfo_screenheight()
        self.geometry(f"600x700+{(sx - 600) // 2}+{(sy - 700) // 2}")
    
    def _build_ui(self):
        """Build dialog UI"""
        # Header
        header = ctk.CTkFrame(self, fg_color=COLORS['bg_card'], corner_radius=15, height=80)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)
        
        ctk.CTkLabel(header, text="➕ Add New Patient", 
                    font=(FONT_FAMILY, 22, "bold"),
                    text_color=COLORS['text_primary']).pack(expand=True)
        
        # Form container
        form = ctk.CTkScrollableFrame(self, fg_color=COLORS['bg_card'], corner_radius=15)
        form.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Form fields
        fields_frame = ctk.CTkFrame(form, fg_color="transparent")
        fields_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Name section
        ctk.CTkLabel(fields_frame, text="Personal Information", 
                    font=(FONT_FAMILY, 16, "bold"),
                    text_color=COLORS['text_primary'],
                    anchor="w").pack(fill="x", pady=(0, 15))
        
        # First Name
        ctk.CTkLabel(fields_frame, text="First Name",
                    font=(FONT_FAMILY, 14),
                    text_color=COLORS['text_primary'],
                    anchor="w").pack(fill="x")
        self.entry_first_name = ctk.CTkEntry(fields_frame, height=40, corner_radius=20,
                                            font=(FONT_FAMILY, 14))
        self.entry_first_name.pack(fill="x", pady=(5, 15))
        
        # Middle Name
        ctk.CTkLabel(fields_frame, text="Middle Name (Optional)", 
                    font=(FONT_FAMILY, 14),
                    text_color=COLORS['text_primary'],
                    anchor="w").pack(fill="x")
        self.entry_middle_name = ctk.CTkEntry(fields_frame, height=40, corner_radius=20,
                                             font=(FONT_FAMILY, 14))
        self.entry_middle_name.pack(fill="x", pady=(5, 15))
        
        # Last Name
        ctk.CTkLabel(fields_frame, text="Last Name",
                    font=(FONT_FAMILY, 14),
                    text_color=COLORS['text_primary'],
                    anchor="w").pack(fill="x")
        self.entry_last_name = ctk.CTkEntry(fields_frame, height=40, corner_radius=20,
                                           font=(FONT_FAMILY, 14))
        self.entry_last_name.pack(fill="x", pady=(5, 15))
        
        # Date of Birth with Calendar Picker
        ctk.CTkLabel(fields_frame, text="Date of Birth", 
                    font=(FONT_FAMILY, 14),
                    text_color=COLORS['text_primary'],
                    anchor="w").pack(fill="x")
        
        dob_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        dob_frame.pack(fill="x", pady=(5, 15))
        
        self.entry_dob = ctk.CTkEntry(dob_frame, height=40, corner_radius=20,
                                     placeholder_text="YYYY-MM-DD",
                                     font=(FONT_FAMILY, 14))
        self.entry_dob.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(dob_frame, text="📅", width=50, height=40,
                     command=self._open_calendar,
                     fg_color=COLORS['accent_blue'], hover_color="#0052a3",
                     font=(FONT_FAMILY, 18)).pack(side="right")
        
        # Contact Information
        ctk.CTkLabel(fields_frame, text="Contact Information", 
                    font=(FONT_FAMILY, 16, "bold"),
                    text_color=COLORS['text_primary'],
                    anchor="w").pack(fill="x", pady=(20, 15))
        
        # Contact Number
        ctk.CTkLabel(fields_frame, text="Contact Number", 
                    font=(FONT_FAMILY, 14),
                    text_color=COLORS['text_primary'],
                    anchor="w").pack(fill="x")
        self.entry_contact = ctk.CTkEntry(fields_frame, height=40, corner_radius=20,
                                         placeholder_text="09123456789",
                                         font=(FONT_FAMILY, 14))
        self.entry_contact.pack(fill="x", pady=(5, 15))
        
        # Address
        ctk.CTkLabel(fields_frame, text="Address", 
                    font=(FONT_FAMILY, 14),
                    text_color=COLORS['text_primary'],
                    anchor="w").pack(fill="x")
        self.entry_address = ctk.CTkTextbox(fields_frame, height=80, corner_radius=20,
                                           font=(FONT_FAMILY, 14))
        self.entry_address.pack(fill="x", pady=(5, 15))
        
        # Notes
        ctk.CTkLabel(fields_frame, text="Additional Notes", 
                    font=(FONT_FAMILY, 14),
                    text_color=COLORS['text_primary'],
                    anchor="w").pack(fill="x")
        self.entry_notes = ctk.CTkTextbox(fields_frame, height=80, corner_radius=20,
                                         font=(FONT_FAMILY, 14))
        self.entry_notes.pack(fill="x", pady=(5, 20))
        
        # Buttons
        button_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        ctk.CTkButton(button_frame, text="Cancel", command=self.destroy,
                     fg_color=COLORS['text_muted'], hover_color=COLORS['text_secondary'],
                     height=44, corner_radius=20,
                     font=(FONT_FAMILY, 13, "bold")).pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(button_frame, text="Add Patient", command=self._save_patient,
                     fg_color=COLORS['accent_green'], hover_color="#16a34a",
                     height=44, corner_radius=20,
                     font=(FONT_FAMILY, 13, "bold")).pack(side="right", fill="x", expand=True)
        
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
        """Save patient to database - all fields optional"""
        # Get all fields - none required
        first_name = self.entry_first_name.get().strip() or "Unknown"
        middle_name = self.entry_middle_name.get().strip()
        last_name = self.entry_last_name.get().strip() or "Unknown"
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

        # Modal
        self.transient(parent)
        self.after(150, self.grab_set)

        # Load patient data - O(log n) indexed query
        self.patient_data = self.db.get_patient(patient_id)
        self.visit_data = self.db.get_patient_visits(patient_id)
        self.stats = self.db.get_patient_stats(patient_id)

        if not self.patient_data:
            messagebox.showerror("Error", "Patient not found!", parent=self)
            self.destroy()
            return

        self._build_ui()

        # Center on screen
        self.update_idletasks()
        sx = self.winfo_screenwidth()
        sy = self.winfo_screenheight()
        self.geometry(f"900x700+{(sx - 900) // 2}+{(sy - 700) // 2}")
    
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
                    font=(FONT_FAMILY, 24, "bold"),
                    text_color="#ffffff").pack(anchor="w")
        
        ctk.CTkLabel(header_content, text=f"Patient ID: #{self.patient_id}", 
                    font=(FONT_FAMILY, 14),
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
            card = ctk.CTkFrame(stats_row, fg_color=COLORS['bg_card'], corner_radius=18,
                               border_width=1, border_color=COLORS['border'])
            card.pack(side="left", fill="both", expand=True, padx=(0, 10 if i < 2 else 0))
            
            ctk.CTkLabel(card, text=icon, font=(FONT_FAMILY, 18)).pack(pady=(15, 5))
            ctk.CTkLabel(card, text=str(value), font=(FONT_FAMILY, 20, "bold"),
                        text_color=COLORS['accent_blue']).pack()
            ctk.CTkLabel(card, text=label, font=(FONT_FAMILY, 13),
                        text_color=COLORS['text_secondary']).pack(pady=(0, 15))
        
        # Patient information card
        info_card = ctk.CTkFrame(content, fg_color=COLORS['bg_card'], corner_radius=15,
                                border_width=1, border_color=COLORS['border'])
        info_card.pack(fill="x", pady=(0, 15))
        
        info_content = ctk.CTkFrame(info_card, fg_color="transparent")
        info_content.pack(fill="x", padx=25, pady=20)
        
        ctk.CTkLabel(info_content, text="📋 Patient Information", 
                    font=(FONT_FAMILY, 16, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w", pady=(0, 15))
        
        # Information grid - 2 columns
        info_grid = ctk.CTkFrame(info_content, fg_color="transparent")
        info_grid.pack(fill="x")
        
        # Left column
        left_col = ctk.CTkFrame(info_grid, fg_color="transparent")
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 20))
        
        # Date of birth with age - O(1) calculation
        dob = self.patient_data.get('date_of_birth')
        age = calculate_age(dob) if dob else None
        age_display = f"{age} years old" if age is not None else "Unknown"
        dob_display = format_date_readable(dob) if dob else "Not provided"

        self._add_info_row(left_col, "Age", age_display)
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
        notes = (self.patient_data.get('notes') or '').strip()
        if notes:
            notes_frame = ctk.CTkFrame(info_content, fg_color=COLORS['bg_dark'], 
                                      corner_radius=20)
            notes_frame.pack(fill="x", pady=(15, 0))
            
            ctk.CTkLabel(notes_frame, text="📝 Notes:", 
                        font=(FONT_FAMILY, 12, "bold"),
                        text_color=COLORS['text_secondary']).pack(anchor="w", 
                                                                  padx=15, pady=(10, 5))
            ctk.CTkLabel(notes_frame, text=notes, 
                        font=(FONT_FAMILY, 13),
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
                    font=(FONT_FAMILY, 16, "bold"),
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
                           font=(FONT_FAMILY, 12),
                           rowheight=35)
            style.configure("Details.Treeview.Heading",
                           background=COLORS['bg_dark'],
                           foreground=COLORS['text_primary'],
                           font=(FONT_FAMILY, 13, "bold"))
            
            # Tree
            columns = ["Ref#", "Date", "Time", "Weight", "Height", "BP", "Temp", "Notes"]
            tree = ttk.Treeview(tree_container, columns=columns, show="headings",
                               style="Details.Treeview", yscrollcommand=scrollbar.set,
                               height=10)
            tree.pack(side="left", fill="both", expand=True)
            scrollbar.configure(command=tree.yview)

            # Configure columns
            tree.column("Ref#", width=60, anchor="center")
            tree.column("Date", width=150, anchor="center")
            tree.column("Time", width=80, anchor="center")
            tree.column("Weight", width=65, anchor="center")
            tree.column("Height", width=65, anchor="center")
            tree.column("BP", width=80, anchor="center")
            tree.column("Temp", width=60, anchor="center")
            tree.column("Notes", width=250)

            for col in columns:
                tree.heading(col, text=col.upper())

            # Add zebra striping
            tree.tag_configure('evenrow', background='#f8fafc')
            tree.tag_configure('oddrow', background='#ffffff')

            # Populate visits - O(n) for n visits
            for idx, visit in enumerate(self.visit_data):
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                visit_date = format_date_readable(visit.get('visit_date', ''))
                tree.insert("", "end", values=(
                    visit.get('reference_number', '-'),
                    visit_date,
                    format_time_12hr(visit.get('visit_time', '')),
                    f"{visit['weight_kg']}" if visit.get('weight_kg') else "-",
                    f"{visit['height_cm']}" if visit.get('height_cm') else "-",
                    visit.get('blood_pressure') or "-",
                    f"{visit['temperature_celsius']}" if visit.get('temperature_celsius') else "-",
                    (visit.get('medical_notes') or "")[:40]
                ), tags=(tag,))
        else:
            # No visits message
            no_visits = ctk.CTkFrame(visits_card, fg_color="transparent")
            no_visits.pack(fill="both", expand=True, pady=40)
            
            ctk.CTkLabel(no_visits, text="📭", font=(FONT_FAMILY, 36)).pack()
            ctk.CTkLabel(no_visits, text="No visit history yet", 
                        font=(FONT_FAMILY, 14),
                        text_color=COLORS['text_secondary']).pack(pady=5)
        
        # Close button
        footer = ctk.CTkFrame(content, fg_color="transparent", height=50)
        footer.pack(fill="x", pady=(15, 0))
        footer.pack_propagate(False)
        
        ctk.CTkButton(footer, text="✓ Close", command=self.destroy,
                     fg_color=COLORS['accent_blue'], hover_color="#0052a3",
                     height=45, width=150, corner_radius=20,
                     font=(FONT_FAMILY, 14, "bold")).pack(side="right")
    
    def _add_info_row(self, parent, label: str, value: str):
        """Add information row - O(1)"""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=5)
        
        ctk.CTkLabel(row, text=f"{label}:", 
                    font=(FONT_FAMILY, 13, "bold"),
                    text_color=COLORS['text_secondary'],
                    width=120, anchor="w").pack(side="left")
        
        ctk.CTkLabel(row, text=value, 
                    font=(FONT_FAMILY, 13),
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

        # Modal
        self.transient(parent)
        self.after(150, self.grab_set)

        self._build_calendar()

        # Center on screen
        self.update_idletasks()
        sx = self.winfo_screenwidth()
        sy = self.winfo_screenheight()
        self.geometry(f"400x450+{(sx - 400) // 2}+{(sy - 450) // 2}")
    
    def _build_calendar(self):
        """Build calendar UI - Modern horizontal layout with year input"""
        # Header with month/year navigation
        header = ctk.CTkFrame(self, fg_color=COLORS['bg_card'], corner_radius=18, height=80)
        header.pack(fill="x", padx=15, pady=15)
        header.pack_propagate(False)

        # Year navigation row
        year_row = ctk.CTkFrame(header, fg_color="transparent")
        year_row.pack(fill="x", pady=(10, 5))

        ctk.CTkButton(year_row, text="<<", width=45, height=32,
                     command=self._prev_year,
                     fg_color=COLORS['accent_purple'], hover_color="#7c3aed",
                     corner_radius=15, font=(FONT_FAMILY, 14, "bold")).pack(side="left", padx=(15, 5))

        self.entry_year = ctk.CTkEntry(year_row, width=80, height=32,
                                       font=(FONT_FAMILY, 16, "bold"),
                                       justify="center",
                                       border_width=1,
                                       border_color=COLORS['border'])
        self.entry_year.pack(side="left", expand=True)
        self.entry_year.bind("<Return>", lambda e: self._on_year_entered())
        self.entry_year.bind("<FocusOut>", lambda e: self._on_year_entered())

        ctk.CTkButton(year_row, text=">>", width=45, height=32,
                     command=self._next_year,
                     fg_color=COLORS['accent_purple'], hover_color="#7c3aed",
                     corner_radius=15, font=(FONT_FAMILY, 14, "bold")).pack(side="right", padx=(5, 15))

        # Month navigation row
        month_row = ctk.CTkFrame(header, fg_color="transparent")
        month_row.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(month_row, text="<", width=45, height=32,
                     command=self._prev_month,
                     fg_color=COLORS['accent_blue'], hover_color="#2563eb",
                     corner_radius=15, font=(FONT_FAMILY, 14, "bold")).pack(side="left", padx=(15, 5))

        self.lbl_month = ctk.CTkLabel(month_row, text="",
                                     font=(FONT_FAMILY, 15, "bold"),
                                     text_color=COLORS['text_primary'])
        self.lbl_month.pack(side="left", expand=True)

        ctk.CTkButton(month_row, text=">", width=45, height=32,
                     command=self._next_month,
                     fg_color=COLORS['accent_blue'], hover_color="#2563eb",
                     corner_radius=15, font=(FONT_FAMILY, 14, "bold")).pack(side="right", padx=(5, 15))

        # Calendar grid
        self.calendar_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_card'], corner_radius=18)
        self.calendar_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self._draw_calendar()

    def _sync_year_selection(self):
        """Sync internal date with year entry box before navigation"""
        try:
            entry_val = self.entry_year.get().strip()
            if entry_val:
                year = int(entry_val)
                if 1900 <= year <= 2100:
                    self.selected_date = datetime.date(year, self.selected_date.month, 1)
        except (ValueError, TypeError):
            pass

    def _prev_year(self):
        """Go to previous year"""
        self._sync_year_selection()
        self.selected_date = datetime.date(self.selected_date.year - 1, self.selected_date.month, 1)
        self._draw_calendar()

    def _next_year(self):
        """Go to next year"""
        self._sync_year_selection()
        self.selected_date = datetime.date(self.selected_date.year + 1, self.selected_date.month, 1)
        self._draw_calendar()

    def _on_year_entered(self):
        """Handle year typed into the entry field"""
        self._sync_year_selection()
        self._draw_calendar()
    
    def _draw_calendar(self):
        """Draw calendar grid - O(1) for 7x6 fixed grid"""
        # Clear existing widgets
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        # Update header labels
        self.entry_year.delete(0, "end")
        self.entry_year.insert(0, str(self.selected_date.year))
        self.lbl_month.configure(text=self.selected_date.strftime("%B"))
        
        # Day headers
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for col, day in enumerate(days):
            lbl = ctk.CTkLabel(self.calendar_frame, text=day,
                             font=(FONT_FAMILY, 13, "bold"),
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

                # Determine colors - modern clean look
                is_today = date == today

                if is_today:
                    fg_color = COLORS['accent_blue']
                    hover_color = "#2563eb"
                    text_color = "#ffffff"
                else:
                    fg_color = "#ffffff"
                    hover_color = COLORS['bg_card_hover']
                    text_color = COLORS['text_primary']

                btn = ctk.CTkButton(self.calendar_frame, text=str(day),
                                   width=48, height=42,
                                   command=lambda d=date: self._select_date(d),
                                   fg_color=fg_color, hover_color=hover_color,
                                   text_color=text_color,
                                   corner_radius=15,
                                   border_width=1, border_color=COLORS['border'],
                                   font=(FONT_FAMILY, 13, "bold"))
                btn.grid(row=row_idx, column=col_idx, padx=2, pady=2, sticky="nsew")
        
        # Configure grid
        for i in range(7):
            self.calendar_frame.grid_columnconfigure(i, weight=1, uniform="col")
        for i in range(7):
            self.calendar_frame.grid_rowconfigure(i, weight=1, uniform="row")
    
    def _prev_month(self):
        """Navigate to previous month - O(1)"""
        self._sync_year_selection()
        month = self.selected_date.month - 1
        year = self.selected_date.year
        if month < 1:
            month = 12
            year -= 1
        self.selected_date = datetime.date(year, month, 1)
        self._draw_calendar()
    
    def _next_month(self):
        """Navigate to next month - O(1)"""
        self._sync_year_selection()
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
    


# ═══════════════════════════════════════════════════════════════════════════════
# ENCODE VISIT DIALOG - FOR ENCODING OLD PHYSICAL RECORDS
# ═══════════════════════════════════════════════════════════════════════════════
class EncodeVisitDialog(ctk.CTkToplevel):
    """
    Dialog for encoding old physical records into the system.
    Allows editing of date and reference number for historical data entry.
    """

    def __init__(self, parent, db: ClinicDatabase, callback):
        super().__init__(parent)

        self.db = db
        self.callback = callback
        self.selected_patient_id = None
        self.selected_patient_name = None

        # Window config
        self.title("Encode Visit Record")
        self.geometry("750x900")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['bg_dark'])

        # Modal
        self.transient(parent)
        self.after(150, self.grab_set)

        # Build UI
        self._build_ui()

        # Center on screen
        self.update_idletasks()
        sx = self.winfo_screenwidth()
        sy = self.winfo_screenheight()
        self.geometry(f"750x900+{(sx - 750) // 2}+{(sy - 900) // 2}")

    def _build_ui(self):
        """Build encode dialog UI"""
        # Header - Orange to distinguish from regular New Visit
        header = ctk.CTkFrame(self, fg_color=COLORS['accent_orange'], corner_radius=15, height=80)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)

        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(expand=True, fill="both", padx=30)

        ctk.CTkLabel(header_content, text="📝 Encode Visit Record",
                    font=(FONT_FAMILY, 24, "bold"),
                    text_color="#ffffff").pack(anchor="w")
        ctk.CTkLabel(header_content, text="Enter old physical records with custom date and reference number",
                    font=(FONT_FAMILY, 14),
                    text_color="#ffffff").pack(anchor="w")

        # Main form
        form = ctk.CTkScrollableFrame(self, fg_color=COLORS['bg_card'], corner_radius=15,
                                     border_width=1, border_color=COLORS['border'])
        form.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        form_content = ctk.CTkFrame(form, fg_color="transparent")
        form_content.pack(fill="both", expand=True, padx=25, pady=25)

        # SECTION 1: Patient Selection
        ctk.CTkLabel(form_content, text="1. SELECT PATIENT",
                    font=(FONT_FAMILY, 16, "bold"),
                    text_color=COLORS['accent_blue']).pack(anchor="w", pady=(0, 10))

        patient_frame = ctk.CTkFrame(form_content, fg_color=COLORS['bg_dark'], corner_radius=20)
        patient_frame.pack(fill="x", pady=(0, 20))

        patient_content = ctk.CTkFrame(patient_frame, fg_color="transparent")
        patient_content.pack(fill="x", padx=15, pady=15)

        # Search patient
        search_frame = ctk.CTkFrame(patient_content, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(search_frame, text="Search Patient:",
                    font=(FONT_FAMILY, 14),
                    text_color=COLORS['text_secondary']).pack(side="left", padx=(0, 10))

        self.entry_search = ctk.CTkEntry(search_frame, placeholder_text="Type patient name...",
                                        height=44, font=(FONT_FAMILY, 14))
        self.entry_search.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_search.bind("<KeyRelease>", self._on_search_change)

        # Modern patient list with scrollable frame
        list_container = ctk.CTkFrame(patient_content, fg_color="#ffffff", corner_radius=15,
                                     border_width=1, border_color=COLORS['border'], height=150)
        list_container.pack(fill="x", pady=(0, 10))
        list_container.pack_propagate(False)

        self.patient_list_frame = ctk.CTkScrollableFrame(list_container, fg_color="transparent")
        self.patient_list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.patient_buttons = []  # Store patient button references

        # Selected patient display
        self.lbl_selected = ctk.CTkLabel(patient_content, text="No patient selected",
                                        font=(FONT_FAMILY, 14, "bold"),
                                        text_color=COLORS['text_secondary'])
        self.lbl_selected.pack(anchor="w", pady=(0, 10))

        # Add new patient button
        ctk.CTkButton(patient_content, text="➕ Patient Not Found? Add New Patient",
                     command=self._open_add_patient,
                     fg_color=COLORS['accent_purple'], hover_color="#5a32a3",
                     height=40, corner_radius=15,
                     font=(FONT_FAMILY, 14, "bold")).pack(fill="x")

        # SECTION 2: Reference Number and Date (CRITICAL FOR ENCODING)
        ctk.CTkLabel(form_content, text="2. REFERENCE NUMBER & DATE",
                    font=(FONT_FAMILY, 16, "bold"),
                    text_color=COLORS['accent_orange']).pack(anchor="w", pady=(10, 10))

        ref_date_frame = ctk.CTkFrame(form_content, fg_color=COLORS['bg_dark'], corner_radius=20)
        ref_date_frame.pack(fill="x", pady=(0, 20))

        ref_date_content = ctk.CTkFrame(ref_date_frame, fg_color="transparent")
        ref_date_content.pack(fill="x", padx=15, pady=15)

        # Reference Number row
        ref_row = ctk.CTkFrame(ref_date_content, fg_color="transparent")
        ref_row.pack(fill="x", pady=(0, 15))

        ref_col = ctk.CTkFrame(ref_row, fg_color="transparent")
        ref_col.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkLabel(ref_col, text="Reference Number",
                    font=(FONT_FAMILY, 14, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w")
        ctk.CTkLabel(ref_col, text="(Auto-generated if left empty)",
                    font=(FONT_FAMILY, 12),
                    text_color=COLORS['text_secondary']).pack(anchor="w")

        self.entry_ref_num = ctk.CTkEntry(ref_col, placeholder_text="Enter reference number",
                                         height=44, font=(FONT_FAMILY, 14))
        self.entry_ref_num.pack(fill="x", pady=(5, 0))

        # Auto-fill next reference number button
        next_ref = self.db.get_next_reference_number()
        ctk.CTkButton(ref_col, text=f"Use Next Available: {next_ref}",
                     command=lambda: self._set_ref_number(next_ref),
                     fg_color=COLORS['accent_blue'], hover_color="#0052a3",
                     height=35, corner_radius=15,
                     font=(FONT_FAMILY, 13)).pack(fill="x", pady=(5, 0))

        # Reference number validation label
        self.lbl_ref_validation = ctk.CTkLabel(ref_col, text="",
                                              font=(FONT_FAMILY, 13),
                                              text_color=COLORS['accent_red'])
        self.lbl_ref_validation.pack(anchor="w", pady=(5, 0))

        # Bind validation on reference number change
        self.entry_ref_num.bind("<KeyRelease>", self._validate_ref_number)

        # Date row
        date_row = ctk.CTkFrame(ref_date_content, fg_color="transparent")
        date_row.pack(fill="x")

        date_col = ctk.CTkFrame(date_row, fg_color="transparent")
        date_col.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkLabel(date_col, text="Visit Date",
                    font=(FONT_FAMILY, 14, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w")

        date_input_frame = ctk.CTkFrame(date_col, fg_color="transparent")
        date_input_frame.pack(fill="x", pady=(5, 0))

        self.entry_date = ctk.CTkEntry(date_input_frame, placeholder_text="YYYY-MM-DD",
                                      height=44, font=(FONT_FAMILY, 14))
        self.entry_date.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(date_input_frame, text="📅", width=50, height=40,
                     command=self._open_calendar,
                     fg_color=COLORS['accent_blue'], hover_color="#0052a3",
                     font=(FONT_FAMILY, 18)).pack(side="right")

        # Time column
        time_col = ctk.CTkFrame(date_row, fg_color="transparent")
        time_col.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(time_col, text="Visit Time",
                    font=(FONT_FAMILY, 14, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w")

        time_input_frame = ctk.CTkFrame(time_col, fg_color="transparent")
        time_input_frame.pack(fill="x", pady=(5, 0))

        # Hour dropdown
        hours = [f"{h:02d}" for h in range(1, 13)]
        self.hour_var = ctk.StringVar(value="12")
        self.hour_dropdown = ctk.CTkComboBox(time_input_frame, values=hours,
                                            variable=self.hour_var, width=65, height=40,
                                            font=(FONT_FAMILY, 14))
        self.hour_dropdown.pack(side="left", padx=(0, 3))

        ctk.CTkLabel(time_input_frame, text=":", font=(FONT_FAMILY, 14, "bold"),
                    text_color=COLORS['text_primary']).pack(side="left")

        # Minute dropdown
        minutes = [f"{m:02d}" for m in range(0, 60, 5)]
        self.minute_var = ctk.StringVar(value="00")
        self.minute_dropdown = ctk.CTkComboBox(time_input_frame, values=minutes,
                                              variable=self.minute_var, width=65, height=40,
                                              font=(FONT_FAMILY, 14))
        self.minute_dropdown.pack(side="left", padx=(3, 3))

        # AM/PM dropdown
        self.ampm_var = ctk.StringVar(value="AM")
        self.ampm_dropdown = ctk.CTkComboBox(time_input_frame, values=["AM", "PM"],
                                            variable=self.ampm_var, width=65, height=40,
                                            font=(FONT_FAMILY, 14))
        self.ampm_dropdown.pack(side="left")

        # SECTION 3: Vital Signs
        ctk.CTkLabel(form_content, text="3. VITAL SIGNS (Optional)",
                    font=(FONT_FAMILY, 16, "bold"),
                    text_color=COLORS['accent_blue']).pack(anchor="w", pady=(10, 10))

        # Vital Signs Row 1
        vitals_frame = ctk.CTkFrame(form_content, fg_color="transparent")
        vitals_frame.pack(fill="x", pady=(0, 15))

        # Weight
        weight_col = ctk.CTkFrame(vitals_frame, fg_color="transparent")
        weight_col.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkLabel(weight_col, text="Weight (kg)",
                    font=(FONT_FAMILY, 14, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w")
        self.entry_weight = ctk.CTkEntry(weight_col, placeholder_text="e.g., 65.5",
                                        height=44, font=(FONT_FAMILY, 14))
        self.entry_weight.pack(fill="x", pady=(5, 0))

        # Height
        height_col = ctk.CTkFrame(vitals_frame, fg_color="transparent")
        height_col.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(height_col, text="Height (cm)",
                    font=(FONT_FAMILY, 14, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w")
        self.entry_height = ctk.CTkEntry(height_col, placeholder_text="e.g., 165",
                                        height=44, font=(FONT_FAMILY, 14))
        self.entry_height.pack(fill="x", pady=(5, 0))

        # Vital Signs Row 2
        vitals2_frame = ctk.CTkFrame(form_content, fg_color="transparent")
        vitals2_frame.pack(fill="x", pady=(0, 15))

        # Blood Pressure
        bp_col = ctk.CTkFrame(vitals2_frame, fg_color="transparent")
        bp_col.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkLabel(bp_col, text="Blood Pressure",
                    font=(FONT_FAMILY, 14, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w")
        self.entry_bp = ctk.CTkEntry(bp_col, placeholder_text="e.g., 120/80",
                                    height=44, font=(FONT_FAMILY, 14))
        self.entry_bp.pack(fill="x", pady=(5, 0))

        # Temperature
        temp_col = ctk.CTkFrame(vitals2_frame, fg_color="transparent")
        temp_col.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(temp_col, text="Temperature (C)",
                    font=(FONT_FAMILY, 14, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w")
        self.entry_temp = ctk.CTkEntry(temp_col, placeholder_text="e.g., 37.2",
                                      height=44, font=(FONT_FAMILY, 14))
        self.entry_temp.pack(fill="x", pady=(5, 0))

        # Medical Notes
        ctk.CTkLabel(form_content, text="Medical Notes / Reason for Visit",
                    font=(FONT_FAMILY, 12, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w", pady=(5, 5))

        self.entry_notes = ctk.CTkTextbox(form_content, height=80,
                                         font=(FONT_FAMILY, 14),
                                         fg_color="#ffffff",
                                         border_color=COLORS['border'],
                                         border_width=1)
        self.entry_notes.pack(fill="x", pady=(0, 20))

        # Footer buttons
        footer = ctk.CTkFrame(form_content, fg_color="transparent")
        footer.pack(fill="x")

        ctk.CTkButton(footer, text="Save Record", command=self._save_visit,
                     fg_color=COLORS['accent_orange'], hover_color="#ea580c",
                     height=44, corner_radius=20,
                     font=(FONT_FAMILY, 14, "bold")).pack(side="right", padx=(10, 0))

        ctk.CTkButton(footer, text="Cancel", command=self.destroy,
                     fg_color=COLORS['text_muted'], hover_color=COLORS['text_secondary'],
                     height=44, corner_radius=20,
                     font=(FONT_FAMILY, 14, "bold")).pack(side="right")

        # Load all patients initially
        self._load_patients()

    def _set_ref_number(self, ref_num: int):
        """Set reference number field"""
        self.entry_ref_num.delete(0, "end")
        self.entry_ref_num.insert(0, str(ref_num))
        self._validate_ref_number(None)

    def _validate_ref_number(self, event):
        """Validate reference number in real-time"""
        ref_str = self.entry_ref_num.get().strip()
        if not ref_str:
            self.lbl_ref_validation.configure(text="", text_color=COLORS['accent_red'])
            return

        try:
            ref_num = int(ref_str)
            if ref_num < 1:
                self.lbl_ref_validation.configure(
                    text="Reference number must be 1 or higher",
                    text_color=COLORS['accent_red'])
            elif not self.db.is_reference_number_available(ref_num):
                self.lbl_ref_validation.configure(
                    text=f"Reference #{ref_num} already exists!",
                    text_color=COLORS['accent_red'])
            else:
                self.lbl_ref_validation.configure(
                    text=f"Reference #{ref_num} is available",
                    text_color=COLORS['accent_green'])
        except ValueError:
            self.lbl_ref_validation.configure(
                text="Enter a valid number",
                text_color=COLORS['accent_red'])

    def _load_patients(self, query: str = ""):
        """Load patients into modern scrollable list"""
        # Clear existing buttons
        for widget in self.patient_list_frame.winfo_children():
            widget.destroy()
        self.patient_buttons = []
        self.patient_data = {}

        if query:
            patients = self.db.search_patients(query)
        else:
            patients = self.db.get_all_patients()

        for idx, patient in enumerate(patients):
            first = patient.get('first_name', '')
            middle = patient.get('middle_name', '')
            last = patient.get('last_name', '')
            full_name = f"{last}, {first}" + (f" {middle}" if middle else "")

            patient_id = patient['patient_id']
            self.patient_data[idx] = (patient_id, full_name)

            # Create modern clickable card for each patient
            btn = ctk.CTkButton(
                self.patient_list_frame,
                text=f"{full_name}  •  ID: {patient_id}",
                font=(FONT_FAMILY, 14),
                fg_color="transparent",
                hover_color=COLORS['status_info'],
                text_color=COLORS['text_primary'],
                anchor="w",
                height=40,
                corner_radius=18,
                command=lambda pid=patient_id, name=full_name: self._select_patient(pid, name)
            )
            btn.pack(fill="x", pady=2)
            self.patient_buttons.append((btn, patient_id))

    def _on_search_change(self, event):
        """Handle search input"""
        query = self.entry_search.get().strip()
        self._load_patients(query)
        self.selected_patient_id = None
        self.lbl_selected.configure(text="No patient selected",
                                   text_color=COLORS['text_secondary'])

    def _select_patient(self, patient_id, patient_name):
        """Handle patient selection from modern list"""
        self.selected_patient_id = patient_id
        self.selected_patient_name = patient_name
        self.lbl_selected.configure(
            text=f"✓ Selected: {patient_name}",
            text_color=COLORS['accent_green'])

        # Highlight selected button
        for btn, pid in self.patient_buttons:
            if pid == patient_id:
                btn.configure(fg_color=COLORS['accent_orange'], text_color="#ffffff")
            else:
                btn.configure(fg_color="transparent", text_color=COLORS['text_primary'])

    def _open_add_patient(self):
        """Open add patient dialog"""
        def on_patient_added(patient_id):
            self._load_patients()
            for idx, (pid, name) in self.patient_data.items():
                if pid == patient_id:
                    self._select_patient(pid, name)
                    break
            messagebox.showinfo("Success",
                              "Patient added! You can now encode their visit.",
                              parent=self)

        AddPatientDialog(self, self.db, on_patient_added)

    def _open_calendar(self):
        """Open calendar picker"""
        CalendarDialog(self, self._on_date_selected)

    def _on_date_selected(self, date_str: str):
        """Callback when date is selected"""
        self.entry_date.delete(0, "end")
        self.entry_date.insert(0, date_str)

    def _save_visit(self):
        """Save encoded visit to database - all fields optional except patient"""
        # Validate patient selection (only required field)
        if not self.selected_patient_id:
            messagebox.showerror("Validation Error",
                               "Please select a patient first!",
                               parent=self)
            return

        # Reference number - auto-generate if not provided
        ref_str = self.entry_ref_num.get().strip()
        reference_number = None
        if ref_str:
            try:
                reference_number = int(ref_str)
                if not self.db.is_reference_number_available(reference_number):
                    messagebox.showerror("Validation Error",
                                       f"Reference #{reference_number} already exists!",
                                       parent=self)
                    return
            except ValueError:
                messagebox.showerror("Validation Error",
                                   "Reference number must be a valid number!",
                                   parent=self)
                return

        # Date - use today if not provided
        visit_date = self.entry_date.get().strip()
        if not visit_date:
            visit_date = datetime.date.today().strftime("%Y-%m-%d")
        else:
            try:
                datetime.datetime.strptime(visit_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Validation Error",
                                   "Invalid date format! Use YYYY-MM-DD",
                                   parent=self)
                return

        # Get time from dropdowns
        hour = self.hour_var.get()
        minute = self.minute_var.get()
        ampm = self.ampm_var.get()
        time_str = f"{hour}:{minute} {ampm}"
        from utils import parse_time_input
        visit_time = parse_time_input(time_str) or "00:00:00"

        # Get optional fields - no validation limits
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
            notes=notes,
            reference_number=reference_number
        )

        if visit_id:
            # Get the actual reference number used
            actual_ref = reference_number if reference_number else self.db.get_next_reference_number() - 1
            self.callback(visit_id, actual_ref)
            self.destroy()
        else:
            messagebox.showerror("Error", "Failed to save encoded visit!", parent=self)


# ═══════════════════════════════════════════════════════════════════════════════
# EDIT VISIT DIALOG - FOR EDITING EXISTING RECORDS
# ═══════════════════════════════════════════════════════════════════════════════
class EditVisitDialog(ctk.CTkToplevel):
    """
    Dialog for editing existing visit records.
    """

    def __init__(self, parent, db: ClinicDatabase, visit_id: int, callback):
        super().__init__(parent)

        self.db = db
        self.visit_id = visit_id
        self.callback = callback

        # Load visit data
        self.visit_data = self.db.get_visit_by_id(visit_id)
        if not self.visit_data:
            messagebox.showerror("Error", "Visit not found!")
            self.destroy()
            return

        # Window config
        self.title(f"Edit Record #{self.visit_data['reference_number']}")
        self.geometry("650x750")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['bg_dark'])

        # Modal
        self.transient(parent)
        self.after(150, self.grab_set)

        # Build UI
        self._build_ui()

        # Center on screen
        self.update_idletasks()
        sx = self.winfo_screenwidth()
        sy = self.winfo_screenheight()
        self.geometry(f"650x750+{(sx - 650) // 2}+{(sy - 750) // 2}")

    def _build_ui(self):
        """Build edit dialog UI"""
        # Header
        header = ctk.CTkFrame(self, fg_color=COLORS['accent_blue'], corner_radius=18, height=70)
        header.pack(fill="x", padx=15, pady=15)
        header.pack_propagate(False)

        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(expand=True, fill="both", padx=20)

        ctk.CTkLabel(header_content, text=f"Edit Record #{self.visit_data['reference_number']}",
                    font=(FONT_FAMILY, 20, "bold"),
                    text_color="#ffffff").pack(anchor="w")

        # Calculate patient age
        from utils import calculate_age
        age = calculate_age(self.visit_data.get('date_of_birth'))
        age_str = f" ({age} yrs)" if age else ""

        ctk.CTkLabel(header_content, text=f"Patient: {self.visit_data['full_name']}{age_str}",
                    font=(FONT_FAMILY, 14),
                    text_color="#ffffff").pack(anchor="w")

        # Main form
        form = ctk.CTkScrollableFrame(self, fg_color=COLORS['bg_card'], corner_radius=18,
                                     border_width=1, border_color=COLORS['border'])
        form.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        form_content = ctk.CTkFrame(form, fg_color="transparent")
        form_content.pack(fill="both", expand=True, padx=20, pady=20)

        # Reference Number (read-only display)
        ref_frame = ctk.CTkFrame(form_content, fg_color="transparent")
        ref_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(ref_frame, text="Reference #",
                    font=(FONT_FAMILY, 14, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w")

        self.lbl_ref = ctk.CTkLabel(ref_frame, text=str(self.visit_data['reference_number']),
                                   font=(FONT_FAMILY, 16, "bold"),
                                   text_color=COLORS['accent_blue'])
        self.lbl_ref.pack(anchor="w")

        # Date and Time row
        datetime_frame = ctk.CTkFrame(form_content, fg_color="transparent")
        datetime_frame.pack(fill="x", pady=(0, 15))

        # Date
        date_col = ctk.CTkFrame(datetime_frame, fg_color="transparent")
        date_col.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkLabel(date_col, text="Visit Date",
                    font=(FONT_FAMILY, 14, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w")

        date_input_frame = ctk.CTkFrame(date_col, fg_color="transparent")
        date_input_frame.pack(fill="x", pady=(5, 0))

        self.entry_date = ctk.CTkEntry(date_input_frame, placeholder_text="YYYY-MM-DD",
                                      height=44, font=(FONT_FAMILY, 14))
        self.entry_date.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry_date.insert(0, self.visit_data.get('visit_date') or "")

        ctk.CTkButton(date_input_frame, text="📅", width=45, height=40,
                     command=self._open_calendar,
                     fg_color=COLORS['accent_blue'], hover_color="#2563eb",
                     font=(FONT_FAMILY, 16)).pack(side="right")

        # Time
        time_col = ctk.CTkFrame(datetime_frame, fg_color="transparent")
        time_col.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(time_col, text="Visit Time",
                    font=(FONT_FAMILY, 14, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w")

        time_input_frame = ctk.CTkFrame(time_col, fg_color="transparent")
        time_input_frame.pack(fill="x", pady=(5, 0))

        # Parse existing time
        existing_time = self.visit_data.get('visit_time') or "12:00:00"
        try:
            time_obj = datetime.datetime.strptime(existing_time, "%H:%M:%S")
            hour_12 = time_obj.strftime("%I")
            minute = time_obj.strftime("%M")
            ampm = time_obj.strftime("%p")
        except (ValueError, TypeError):
            hour_12, minute, ampm = "12", "00", "AM"

        # Round minute to nearest 5
        min_val = int(minute)
        min_rounded = (min_val // 5) * 5

        # Hour dropdown
        hours = [f"{h:02d}" for h in range(1, 13)]
        self.hour_var = ctk.StringVar(value=hour_12)
        self.hour_dropdown = ctk.CTkComboBox(time_input_frame, values=hours,
                                            variable=self.hour_var, width=65, height=40,
                                            font=(FONT_FAMILY, 14))
        self.hour_dropdown.pack(side="left", padx=(0, 3))

        ctk.CTkLabel(time_input_frame, text=":", font=(FONT_FAMILY, 14, "bold"),
                    text_color=COLORS['text_primary']).pack(side="left")

        # Minute dropdown
        minutes = [f"{m:02d}" for m in range(0, 60, 5)]
        self.minute_var = ctk.StringVar(value=f"{min_rounded:02d}")
        self.minute_dropdown = ctk.CTkComboBox(time_input_frame, values=minutes,
                                              variable=self.minute_var, width=65, height=40,
                                              font=(FONT_FAMILY, 14))
        self.minute_dropdown.pack(side="left", padx=(3, 3))

        # AM/PM dropdown
        self.ampm_var = ctk.StringVar(value=ampm)
        self.ampm_dropdown = ctk.CTkComboBox(time_input_frame, values=["AM", "PM"],
                                            variable=self.ampm_var, width=65, height=40,
                                            font=(FONT_FAMILY, 14))
        self.ampm_dropdown.pack(side="left")

        # Vital Signs
        ctk.CTkLabel(form_content, text="Vital Signs",
                    font=(FONT_FAMILY, 16, "bold"),
                    text_color=COLORS['accent_blue']).pack(anchor="w", pady=(10, 10))

        # Vitals Row 1
        vitals_frame = ctk.CTkFrame(form_content, fg_color="transparent")
        vitals_frame.pack(fill="x", pady=(0, 10))

        # Weight
        weight_col = ctk.CTkFrame(vitals_frame, fg_color="transparent")
        weight_col.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkLabel(weight_col, text="Weight (kg)",
                    font=(FONT_FAMILY, 14),
                    text_color=COLORS['text_primary']).pack(anchor="w")
        self.entry_weight = ctk.CTkEntry(weight_col, placeholder_text="e.g., 65.5",
                                        height=44, font=(FONT_FAMILY, 14))
        self.entry_weight.pack(fill="x", pady=(5, 0))
        if self.visit_data.get('weight_kg'):
            self.entry_weight.insert(0, str(self.visit_data['weight_kg']))

        # Height
        height_col = ctk.CTkFrame(vitals_frame, fg_color="transparent")
        height_col.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(height_col, text="Height (cm)",
                    font=(FONT_FAMILY, 14),
                    text_color=COLORS['text_primary']).pack(anchor="w")
        self.entry_height = ctk.CTkEntry(height_col, placeholder_text="e.g., 165",
                                        height=44, font=(FONT_FAMILY, 14))
        self.entry_height.pack(fill="x", pady=(5, 0))
        if self.visit_data.get('height_cm'):
            self.entry_height.insert(0, str(self.visit_data['height_cm']))

        # Vitals Row 2
        vitals2_frame = ctk.CTkFrame(form_content, fg_color="transparent")
        vitals2_frame.pack(fill="x", pady=(0, 10))

        # Blood Pressure
        bp_col = ctk.CTkFrame(vitals2_frame, fg_color="transparent")
        bp_col.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkLabel(bp_col, text="Blood Pressure",
                    font=(FONT_FAMILY, 14),
                    text_color=COLORS['text_primary']).pack(anchor="w")
        self.entry_bp = ctk.CTkEntry(bp_col, placeholder_text="e.g., 120/80",
                                    height=44, font=(FONT_FAMILY, 14))
        self.entry_bp.pack(fill="x", pady=(5, 0))
        if self.visit_data.get('blood_pressure'):
            self.entry_bp.insert(0, self.visit_data['blood_pressure'])

        # Temperature
        temp_col = ctk.CTkFrame(vitals2_frame, fg_color="transparent")
        temp_col.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(temp_col, text="Temperature (C)",
                    font=(FONT_FAMILY, 14),
                    text_color=COLORS['text_primary']).pack(anchor="w")
        self.entry_temp = ctk.CTkEntry(temp_col, placeholder_text="e.g., 37.2",
                                      height=44, font=(FONT_FAMILY, 14))
        self.entry_temp.pack(fill="x", pady=(5, 0))
        if self.visit_data.get('temperature_celsius'):
            self.entry_temp.insert(0, str(self.visit_data['temperature_celsius']))

        # Medical Notes
        ctk.CTkLabel(form_content, text="Medical Notes",
                    font=(FONT_FAMILY, 12, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w", pady=(10, 5))

        self.entry_notes = ctk.CTkTextbox(form_content, height=100,
                                         font=(FONT_FAMILY, 14),
                                         fg_color="#ffffff",
                                         border_color=COLORS['border'],
                                         border_width=1)
        self.entry_notes.pack(fill="x", pady=(0, 15))
        if self.visit_data.get('medical_notes'):
            self.entry_notes.insert("1.0", self.visit_data['medical_notes'])

        # Footer buttons
        footer = ctk.CTkFrame(form_content, fg_color="transparent")
        footer.pack(fill="x")

        ctk.CTkButton(footer, text="Save Changes", command=self._save_visit,
                     fg_color=COLORS['accent_green'], hover_color="#16a34a",
                     height=44, corner_radius=20,
                     font=(FONT_FAMILY, 14, "bold")).pack(side="right", padx=(10, 0))

        ctk.CTkButton(footer, text="Cancel", command=self.destroy,
                     fg_color=COLORS['text_muted'], hover_color=COLORS['text_secondary'],
                     height=44, corner_radius=20,
                     font=(FONT_FAMILY, 14, "bold")).pack(side="right")

    def _open_calendar(self):
        """Open calendar picker"""
        def on_date_selected(date_str):
            self.entry_date.delete(0, "end")
            self.entry_date.insert(0, date_str)
        CalendarDialog(self, on_date_selected)

    def _save_visit(self):
        """Save updated visit to database"""
        # Get date
        visit_date = self.entry_date.get().strip()
        if not visit_date:
            visit_date = datetime.date.today().strftime("%Y-%m-%d")
        else:
            try:
                datetime.datetime.strptime(visit_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Validation Error",
                                   "Invalid date format! Use YYYY-MM-DD",
                                   parent=self)
                return

        # Get time from dropdowns
        hour = self.hour_var.get()
        minute = self.minute_var.get()
        ampm = self.ampm_var.get()
        time_str = f"{hour}:{minute} {ampm}"
        from utils import parse_time_input
        visit_time = parse_time_input(time_str) or "00:00:00"

        # Get optional fields
        from utils import safe_float
        weight = safe_float(self.entry_weight.get())
        height = safe_float(self.entry_height.get())
        bp = self.entry_bp.get().strip()
        temp = safe_float(self.entry_temp.get())
        notes = self.entry_notes.get("1.0", "end-1c").strip()

        # Update in database
        success = self.db.update_visit(
            visit_id=self.visit_id,
            visit_date=visit_date,
            visit_time=visit_time,
            weight=weight,
            height=height,
            bp=bp,
            temp=temp,
            notes=notes
        )

        if success:
            self.callback()
            self.destroy()
            messagebox.showinfo("Success", f"Record #{self.visit_data['reference_number']} updated!")
        else:
            messagebox.showerror("Error", "Failed to update record!", parent=self)


# ═══════════════════════════════════════════════════════════════════════════════
# FIRST-RUN ADMIN SETUP
# ═══════════════════════════════════════════════════════════════════════════════
class FirstRunSetup(ctk.CTk):
    """First-run dialog to create the initial admin account"""

    def __init__(self, db: ClinicDatabase):
        super().__init__()
        self.db = db
        self.success = False

        self.title("Geneva Clinic - Initial Setup")
        self.configure(fg_color=COLORS['bg_dark'])
        self.attributes('-fullscreen', True)

        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=COLORS['accent_blue'], corner_radius=18, height=100)
        header.pack(fill="x", padx=25, pady=(25, 0))
        header.pack_propagate(False)

        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(expand=True, fill="both", padx=30)

        ctk.CTkLabel(header_content, text="Welcome to Geneva Clinic",
                    font=(FONT_FAMILY, 22, "bold"),
                    text_color="#ffffff").pack(anchor="w")
        ctk.CTkLabel(header_content, text="Create your admin account to get started",
                    font=(FONT_FAMILY, 14),
                    text_color="#ffffff").pack(anchor="w")

        # Form card
        card = ctk.CTkFrame(self, fg_color=COLORS['bg_card'], corner_radius=18,
                           border_width=1, border_color=COLORS['border'])
        card.pack(fill="both", expand=True, padx=25, pady=25)

        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(expand=True, fill="both", padx=40, pady=40)

        ctk.CTkLabel(form, text="Create Admin Account",
                    font=(FONT_FAMILY, 18, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w", pady=(0, 25))

        # Username
        ctk.CTkLabel(form, text="Username",
                    font=(FONT_FAMILY, 15, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w")
        self.entry_username = ctk.CTkEntry(form, height=50, corner_radius=15,
                                          font=(FONT_FAMILY, 15),
                                          placeholder_text="Enter admin username")
        self.entry_username.pack(fill="x", pady=(5, 15))

        # Password
        ctk.CTkLabel(form, text="Password",
                    font=(FONT_FAMILY, 15, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w")
        self.entry_password = ctk.CTkEntry(form, height=50, corner_radius=15,
                                          font=(FONT_FAMILY, 15), show="*",
                                          placeholder_text="Enter password")
        self.entry_password.pack(fill="x", pady=(5, 15))

        # Confirm Password
        ctk.CTkLabel(form, text="Confirm Password",
                    font=(FONT_FAMILY, 15, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w")
        self.entry_confirm = ctk.CTkEntry(form, height=50, corner_radius=15,
                                         font=(FONT_FAMILY, 15), show="*",
                                         placeholder_text="Re-enter password")
        self.entry_confirm.pack(fill="x", pady=(5, 25))

        # Status label
        self.lbl_status = ctk.CTkLabel(form, text="",
                                      font=(FONT_FAMILY, 14),
                                      text_color=COLORS['accent_red'])
        self.lbl_status.pack(pady=(0, 10))

        # Create button
        ctk.CTkButton(form, text="Create Account",
                     command=self._create_admin,
                     fg_color=COLORS['accent_green'], hover_color="#16a34a",
                     height=48, corner_radius=20,
                     font=(FONT_FAMILY, 14, "bold")).pack(fill="x")

        # Branding
        ctk.CTkLabel(form, text="\u00a9 2026 Rainberry Corp. All rights reserved.",
                    font=(FONT_FAMILY, 12, "bold"),
                    text_color=COLORS['text_muted']).pack(pady=(15, 0))
        ctk.CTkLabel(form, text="Created and Designed by Jesbert V. Jalandoni",
                    font=(FONT_FAMILY, 11),
                    text_color=COLORS['text_muted']).pack()
        site_label = ctk.CTkLabel(form, text="jalandoni.jesbert.cloud",
                    font=(FONT_FAMILY, 11, "underline"),
                    text_color=COLORS['accent_blue'], cursor="hand2")
        site_label.pack()
        site_label.bind("<Button-1>", lambda e: __import__('webbrowser').open("https://jalandoni.jesbert.cloud/"))

        self.entry_username.focus()
        self.entry_confirm.bind("<Return>", lambda e: self._create_admin())

    def _create_admin(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get()
        confirm = self.entry_confirm.get()

        if not username:
            self.lbl_status.configure(text="Username is required")
            return
        if len(username) < 3:
            self.lbl_status.configure(text="Username must be at least 3 characters")
            return
        if not password:
            self.lbl_status.configure(text="Password is required")
            return
        if len(password) < 4:
            self.lbl_status.configure(text="Password must be at least 4 characters")
            return
        if password != confirm:
            self.lbl_status.configure(text="Passwords do not match")
            return

        if self.db.create_admin(username, password):
            self.success = True
            self.destroy()
        else:
            self.lbl_status.configure(text="Failed to create account. Try a different username.")


# ═══════════════════════════════════════════════════════════════════════════════
# LOGIN WINDOW
# ═══════════════════════════════════════════════════════════════════════════════
class LoginWindow(ctk.CTk):
    """Login screen shown before the main application"""

    def __init__(self, db: ClinicDatabase):
        super().__init__()
        self.db = db
        self.success = False

        self.title("Geneva Clinic - Login")
        self.configure(fg_color=COLORS['bg_dark'])
        self.attributes('-fullscreen', True)

        self._build_ui()

    def _build_ui(self):
        # Logo section
        logo_frame = ctk.CTkFrame(self, fg_color="transparent", height=120)
        logo_frame.pack(fill="x", padx=25, pady=(30, 0))
        logo_frame.pack_propagate(False)

        ctk.CTkLabel(logo_frame, text="Geneva Clinic",
                    font=(FONT_FAMILY, 32, "bold"),
                    text_color=COLORS['text_primary']).pack()
        ctk.CTkLabel(logo_frame, text="Patient Management System",
                    font=(FONT_FAMILY, 15),
                    text_color=COLORS['text_secondary']).pack(pady=(5, 0))

        # Login card
        card = ctk.CTkFrame(self, fg_color=COLORS['bg_card'], corner_radius=18,
                           border_width=1, border_color=COLORS['border'])
        card.pack(fill="both", expand=True, padx=25, pady=25)

        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(expand=True, fill="both", padx=40, pady=40)

        ctk.CTkLabel(form, text="Admin Login",
                    font=(FONT_FAMILY, 20, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w", pady=(0, 25))

        # Username
        ctk.CTkLabel(form, text="Username",
                    font=(FONT_FAMILY, 15, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w")
        self.entry_username = ctk.CTkEntry(form, height=50, corner_radius=15,
                                          font=(FONT_FAMILY, 15),
                                          placeholder_text="Enter username")
        self.entry_username.pack(fill="x", pady=(5, 15))

        # Password
        ctk.CTkLabel(form, text="Password",
                    font=(FONT_FAMILY, 15, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w")
        self.entry_password = ctk.CTkEntry(form, height=50, corner_radius=15,
                                          font=(FONT_FAMILY, 15), show="*",
                                          placeholder_text="Enter password")
        self.entry_password.pack(fill="x", pady=(5, 20))

        # Status label
        self.lbl_status = ctk.CTkLabel(form, text="",
                                      font=(FONT_FAMILY, 14),
                                      text_color=COLORS['accent_red'])
        self.lbl_status.pack(pady=(0, 10))

        # Login button
        ctk.CTkButton(form, text="Login",
                     command=self._login,
                     fg_color=COLORS['accent_blue'], hover_color="#2563eb",
                     height=48, corner_radius=20,
                     font=(FONT_FAMILY, 14, "bold")).pack(fill="x")

        # Branding
        ctk.CTkLabel(form, text="\u00a9 2026 Rainberry Corp. All rights reserved.",
                    font=(FONT_FAMILY, 12, "bold"),
                    text_color=COLORS['text_muted']).pack(pady=(15, 0))
        ctk.CTkLabel(form, text="Created and Designed by Jesbert V. Jalandoni",
                    font=(FONT_FAMILY, 11),
                    text_color=COLORS['text_muted']).pack()
        site_label = ctk.CTkLabel(form, text="jalandoni.jesbert.cloud",
                    font=(FONT_FAMILY, 11, "underline"),
                    text_color=COLORS['accent_blue'], cursor="hand2")
        site_label.pack()
        site_label.bind("<Button-1>", lambda e: __import__('webbrowser').open("https://jalandoni.jesbert.cloud/"))

        self.entry_username.focus()
        self.entry_password.bind("<Return>", lambda e: self._login())

    def _login(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get()

        if not username or not password:
            self.lbl_status.configure(text="Please enter username and password")
            return

        if self.db.verify_admin(username, password):
            self.success = True
            self.destroy()
        else:
            self.lbl_status.configure(text="Invalid username or password")
            self.entry_password.delete(0, "end")
            self.entry_password.focus()


# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN SETTINGS DIALOG
# ═══════════════════════════════════════════════════════════════════════════════
class AdminSettingsDialog(ctk.CTkToplevel):
    """Dialog for changing admin username and password"""

    def __init__(self, parent, db: ClinicDatabase):
        super().__init__(parent)
        self.db = db

        self.title("Admin Settings")
        self.geometry("500x600")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['bg_dark'])

        self.transient(parent)
        self.after(150, self.grab_set)

        self._build_ui()

        # Center on screen
        self.update_idletasks()
        sx = self.winfo_screenwidth()
        sy = self.winfo_screenheight()
        self.geometry(f"500x600+{(sx - 500) // 2}+{(sy - 600) // 2}")

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=COLORS['accent_purple'], corner_radius=18, height=70)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="Admin Settings",
                    font=(FONT_FAMILY, 22, "bold"),
                    text_color="#ffffff").pack(expand=True)

        # Content
        content = ctk.CTkScrollableFrame(self, fg_color=COLORS['bg_card'], corner_radius=18,
                                         border_width=1, border_color=COLORS['border'])
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        form = ctk.CTkFrame(content, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=30, pady=30)

        current_username = self.db.get_admin_username() or ""

        # ---- Change Username Section ----
        ctk.CTkLabel(form, text="Change Username",
                    font=(FONT_FAMILY, 16, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(form, text="Current Username",
                    font=(FONT_FAMILY, 14),
                    text_color=COLORS['text_secondary']).pack(anchor="w")
        self.entry_current_user = ctk.CTkEntry(form, height=40, corner_radius=15,
                                               font=(FONT_FAMILY, 14))
        self.entry_current_user.pack(fill="x", pady=(5, 10))
        self.entry_current_user.insert(0, current_username)
        self.entry_current_user.configure(state="disabled")

        ctk.CTkLabel(form, text="New Username",
                    font=(FONT_FAMILY, 14),
                    text_color=COLORS['text_secondary']).pack(anchor="w")
        self.entry_new_user = ctk.CTkEntry(form, height=40, corner_radius=15,
                                           font=(FONT_FAMILY, 14),
                                           placeholder_text="Enter new username")
        self.entry_new_user.pack(fill="x", pady=(5, 10))

        self.lbl_user_status = ctk.CTkLabel(form, text="",
                                           font=(FONT_FAMILY, 13),
                                           text_color=COLORS['accent_red'])
        self.lbl_user_status.pack(anchor="w")

        ctk.CTkButton(form, text="Update Username",
                     command=self._update_username,
                     fg_color=COLORS['accent_blue'], hover_color="#2563eb",
                     height=40, corner_radius=15,
                     font=(FONT_FAMILY, 13, "bold")).pack(fill="x", pady=(5, 25))

        # Separator
        ctk.CTkFrame(form, fg_color=COLORS['border'], height=2).pack(fill="x", pady=(0, 25))

        # ---- Change Password Section ----
        ctk.CTkLabel(form, text="Change Password",
                    font=(FONT_FAMILY, 16, "bold"),
                    text_color=COLORS['text_primary']).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(form, text="Current Password",
                    font=(FONT_FAMILY, 14),
                    text_color=COLORS['text_secondary']).pack(anchor="w")
        self.entry_current_pass = ctk.CTkEntry(form, height=40, corner_radius=15,
                                               font=(FONT_FAMILY, 14), show="*",
                                               placeholder_text="Enter current password")
        self.entry_current_pass.pack(fill="x", pady=(5, 10))

        ctk.CTkLabel(form, text="New Password",
                    font=(FONT_FAMILY, 14),
                    text_color=COLORS['text_secondary']).pack(anchor="w")
        self.entry_new_pass = ctk.CTkEntry(form, height=40, corner_radius=15,
                                           font=(FONT_FAMILY, 14), show="*",
                                           placeholder_text="Enter new password")
        self.entry_new_pass.pack(fill="x", pady=(5, 10))

        ctk.CTkLabel(form, text="Confirm New Password",
                    font=(FONT_FAMILY, 14),
                    text_color=COLORS['text_secondary']).pack(anchor="w")
        self.entry_confirm_pass = ctk.CTkEntry(form, height=40, corner_radius=15,
                                               font=(FONT_FAMILY, 14), show="*",
                                               placeholder_text="Re-enter new password")
        self.entry_confirm_pass.pack(fill="x", pady=(5, 10))

        self.lbl_pass_status = ctk.CTkLabel(form, text="",
                                           font=(FONT_FAMILY, 13),
                                           text_color=COLORS['accent_red'])
        self.lbl_pass_status.pack(anchor="w")

        ctk.CTkButton(form, text="Update Password",
                     command=self._update_password,
                     fg_color=COLORS['accent_green'], hover_color="#16a34a",
                     height=40, corner_radius=15,
                     font=(FONT_FAMILY, 13, "bold")).pack(fill="x", pady=(5, 10))

    def _update_username(self):
        current = self.db.get_admin_username()
        new_user = self.entry_new_user.get().strip()

        if not new_user:
            self.lbl_user_status.configure(text="New username is required",
                                          text_color=COLORS['accent_red'])
            return
        if len(new_user) < 3:
            self.lbl_user_status.configure(text="Username must be at least 3 characters",
                                          text_color=COLORS['accent_red'])
            return
        if new_user == current:
            self.lbl_user_status.configure(text="New username is the same as current",
                                          text_color=COLORS['accent_red'])
            return

        if self.db.update_admin_username(current, new_user):
            self.lbl_user_status.configure(text="Username updated successfully!",
                                          text_color=COLORS['accent_green'])
            self.entry_current_user.configure(state="normal")
            self.entry_current_user.delete(0, "end")
            self.entry_current_user.insert(0, new_user)
            self.entry_current_user.configure(state="disabled")
            self.entry_new_user.delete(0, "end")
        else:
            self.lbl_user_status.configure(text="Failed to update username",
                                          text_color=COLORS['accent_red'])

    def _update_password(self):
        current_user = self.db.get_admin_username()
        current_pass = self.entry_current_pass.get()
        new_pass = self.entry_new_pass.get()
        confirm_pass = self.entry_confirm_pass.get()

        if not current_pass:
            self.lbl_pass_status.configure(text="Current password is required",
                                          text_color=COLORS['accent_red'])
            return
        if not self.db.verify_admin(current_user, current_pass):
            self.lbl_pass_status.configure(text="Current password is incorrect",
                                          text_color=COLORS['accent_red'])
            return
        if not new_pass:
            self.lbl_pass_status.configure(text="New password is required",
                                          text_color=COLORS['accent_red'])
            return
        if len(new_pass) < 4:
            self.lbl_pass_status.configure(text="New password must be at least 4 characters",
                                          text_color=COLORS['accent_red'])
            return
        if new_pass != confirm_pass:
            self.lbl_pass_status.configure(text="New passwords do not match",
                                          text_color=COLORS['accent_red'])
            return

        if self.db.update_admin_password(current_user, new_pass):
            self.lbl_pass_status.configure(text="Password updated successfully!",
                                          text_color=COLORS['accent_green'])
            self.entry_current_pass.delete(0, "end")
            self.entry_new_pass.delete(0, "end")
            self.entry_confirm_pass.delete(0, "end")
        else:
            self.lbl_pass_status.configure(text="Failed to update password",
                                          text_color=COLORS['accent_red'])


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    """Launch application with login flow"""
    db = ClinicDatabase()

    # First-run: create admin account if none exists
    if not db.admin_exists():
        setup = FirstRunSetup(db)
        setup.mainloop()
        if not setup.success:
            return

    # Login screen
    login = LoginWindow(db)
    login.mainloop()
    if not login.success:
        return

    # Launch main app
    app = ClinicApp()
    app.mainloop()


if __name__ == "__main__":
    main()