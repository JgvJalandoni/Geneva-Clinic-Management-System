"""
Dialogs package for Tita's Clinic Management System
"""

from dialogs.base import BaseDialog
from dialogs.patient_dialogs import NewPatientDialog, EditPatientDialog, PatientHistoryDialog
from dialogs.visit_dialogs import QuickVisitSearchDialog, QuickVisitFormDialog

__all__ = [
    'BaseDialog',
    'NewPatientDialog',
    'EditPatientDialog',
    'PatientHistoryDialog',
    'QuickVisitSearchDialog',
    'QuickVisitFormDialog',
]
