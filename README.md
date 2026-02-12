# Geneva Clinic Management System 🏥

A hyper-optimized, high-performance Clinic Management System designed for local healthcare facilities. This project holds special significance as it was my first successful professional deployment, leveraging a **Raspberry Pi** as a dedicated database server and workstation for a local clinic.

## 🌟 Context & Origin
This application was born out of a need for a reliable, offline-first medical record system. It was specifically built to run on a Raspberry Pi, providing the clinic with a cost-effective yet powerful data management solution. The architecture prioritizes performance and accessibility, ensuring that even on modest hardware, the experience remains fluid and responsive.

## 🚀 Key Features
- **Modern Dashboard**: Real-time statistics tracking total patients and medical records.
- **Patient Management**: Complete CRUD operations for patient profiles, including advanced filtering (alphabetical, age, sex, etc.).
- **Visit Logs**: Optimized workflow for recording new visits, vital signs (Weight, BP, Temp, Height), and medical notes.
- **Ultra-Fast Search**: O(1) lookup strategies and caching mechanisms for near-instantaneous search results.
- **Data Integrity**: Integrated database backup and CSV export functionality for easy reporting and data security.
- **Accessibility Focused**: High-contrast UI theme designed for readability and reduced eye strain.
- **Raspberry Pi Optimized**: Built-in system commands for graceful shutdown on Linux-based systems.

## 🛠️ Tech Stack
- **Language**: Python 3
- **GUI Framework**: `customtkinter` (Modern, themed Tkinter)
- **Database**: SQLite3 (Local, reliable, and zero-configuration)
- **Deployment**: Raspberry Pi (Linux ARM) / Windows

## 📂 Code Structure & Logic

### `main.py`
The heart of the application. It implements:
- **`StatsCache`**: A dirty-flag-based cache system that prevents unnecessary database re-queries, ensuring the dashboard updates only when data changes.
- **`ClinicApp`**: The main class using a lazy-loading architecture—views are only instantiated when needed to minimize startup time and RAM usage.
- **Navigation**: Uses an O(1) state management system for switching between Overview, Patients, and Visits.

### `database.py`
Handles all persistence logic:
- **Connection Pooling**: Reuses database connections to reduce overhead.
- **Optimized Schema**: Uses proper indexing on search fields (names, reference numbers, dates) to maintain performance as the database grows.
- **Migrations**: Automated handling of schema updates to ensure data continuity.

### `config.py`
Centralized configuration for:
- **Cross-Platform Compatibility**: Dynamic font selection based on the operating system.
- **Theming**: A custom color palette (`COLORS`) designed for high visibility and professional aesthetics.

### `utils.py`
A collection of high-performance utility functions:
- **Date/Time Arithmetic**: O(1) age calculation and flexible date parsing.
- **Formatting**: Standardized display for phone numbers and reference numbers (e.g., `00-00-00`).
- **Validation**: Strict yet user-friendly input validation for medical data.

## 🏁 Getting Started

### Prerequisites
- Python 3.x
- pip

### Installation
1. Clone the repository to your Raspberry Pi or local machine.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

### First Run
Upon first launch, the system will guide you through creating an **Admin Account**. This ensures that the medical records are protected and only accessible by authorized personnel.

---
**Designed and Developed by Jesbert V. Jalandoni**
*© 2026 Rainberry Corp.*
[jalandoni.jesbert.cloud](https://jalandoni.jesbert.cloud/)
