"""
Base dialog classes for Tita's Clinic Management System
Common dialog components and base functionality
"""

import customtkinter as ctk
from config import COLORS, FONT_FAMILY


class BaseDialog(ctk.CTkToplevel):
    """Base class for popup dialogs with consistent styling"""
    
    def __init__(self, parent, title: str, width: int = 500, height: int = 600):
        """
        Initialize base dialog
        
        Args:
            parent: Parent window
            title: Dialog title
            width: Dialog width in pixels
            height: Dialog height in pixels
        """
        super().__init__(parent)
        
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.after(150, self.grab_set)
        
        # Styling
        self.configure(fg_color=COLORS['bg_dark'])
        
        # Center window on screen
        self.update_idletasks()
        sx = self.winfo_screenwidth()
        sy = self.winfo_screenheight()
        x = (sx - width) // 2
        y = (sy - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_header(self, emoji: str, title: str, subtitle: str = "", 
                     color: str = None, height: int = 80):
        """
        Create a standardized header for dialogs
        
        Args:
            emoji: Emoji icon for header
            title: Main title text
            subtitle: Optional subtitle text
            color: Background color (uses accent_blue if None)
            height: Header height in pixels
            
        Returns:
            Header frame widget
        """
        header = ctk.CTkFrame(self, 
                             fg_color=color or COLORS['accent_blue'], 
                             corner_radius=0, 
                             height=height)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        # Emoji icon
        if emoji:
            ctk.CTkLabel(header, text=emoji, 
                        font=(FONT_FAMILY, 40)).pack(pady=(10, 0))
        
        # Title
        ctk.CTkLabel(header, text=title, 
                    font=(FONT_FAMILY, 20, "bold")).pack()
        
        # Subtitle (optional)
        if subtitle:
            ctk.CTkLabel(header, text=subtitle,
                        font=(FONT_FAMILY, 13 if len(subtitle) < 50 else 12), 
                        text_color="#e8f5e9").pack(pady=(5, 10))
        else:
            # Add padding if no subtitle
            ctk.CTkLabel(header, text="", height=10).pack()
        
        return header
    
    def create_button_bar(self, parent, buttons: list) -> ctk.CTkFrame:
        """
        Create a button bar with multiple buttons
        
        Args:
            parent: Parent widget
            buttons: List of button configs as dicts with keys:
                    - text: Button text
                    - command: Button callback
                    - style: 'primary', 'secondary', 'danger' (optional)
                    - side: 'left' or 'right' (default: 'left')
                    
        Returns:
            Button bar frame
        """
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(15, 0))
        
        for btn_config in buttons:
            text = btn_config.get('text', 'Button')
            command = btn_config.get('command', lambda: None)
            style = btn_config.get('style', 'secondary')
            side = btn_config.get('side', 'left')
            
            # Determine colors based on style
            if style == 'primary':
                fg_color = COLORS['accent_green']
                hover_color = "#45a049"
                border_width = 0
                border_color = None
            elif style == 'danger':
                fg_color = COLORS['accent_red']
                hover_color = "#d32f2f"
                border_width = 0
                border_color = None
            else:  # secondary
                fg_color = COLORS['bg_card_hover']
                hover_color = COLORS['border']
                border_width = 1
                border_color = COLORS['border']
            
            btn = ctk.CTkButton(btn_frame, 
                               text=text,
                               command=command,
                               fg_color=fg_color,
                               hover_color=hover_color,
                               border_width=border_width,
                               border_color=border_color,
                               height=45,
                               font=(FONT_FAMILY, 14, "bold" if style == 'primary' else "normal"))
            
            padding = (0, 5) if side == 'left' else (5, 0)
            btn.pack(side=side, fill="x", expand=True, padx=padding)
        
        return btn_frame
    
    def create_form_field(self, parent, label: str, placeholder: str = "", 
                         field_type: str = "entry") -> ctk.CTkEntry:
        """
        Create a standardized form field
        
        Args:
            parent: Parent widget
            label: Field label
            placeholder: Placeholder text
            field_type: 'entry' or 'textbox'
            
        Returns:
            Entry or Textbox widget
        """
        # Label
        ctk.CTkLabel(parent, 
                    text=label, 
                    font=(FONT_FAMILY, 14),
                    text_color=COLORS['text_secondary']).pack(anchor="w", pady=(10, 5))
        
        # Field
        if field_type == "textbox":
            field = ctk.CTkTextbox(parent, 
                                  height=100,
                                  fg_color=COLORS['bg_card'],
                                  border_width=1,
                                  border_color=COLORS['border'],
                                  font=(FONT_FAMILY, 14))
        else:  # entry
            field = ctk.CTkEntry(parent,
                               height=40,
                               placeholder_text=placeholder,
                               fg_color=COLORS['bg_card'],
                               border_width=1,
                               border_color=COLORS['border'])
        
        field.pack(fill="x", pady=(0, 5))
        return field
    
    def create_info_box(self, parent, message: str, icon: str = "ℹ️"):
        """
        Create an info/warning box
        
        Args:
            parent: Parent widget
            message: Info message
            icon: Icon emoji
        """
        info_frame = ctk.CTkFrame(parent, 
                                 fg_color=COLORS['bg_card'],
                                 border_width=1,
                                 border_color=COLORS['accent_blue'])
        info_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(info_frame, 
                    text=f"{icon} {message}",
                    font=(FONT_FAMILY, 14),
                    text_color=COLORS['text_secondary'],
                    wraplength=450).pack(pady=10, padx=10)
        
        return info_frame
