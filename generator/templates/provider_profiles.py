"""Controlled synthetic clinician specialties, NUCC taxonomies, and facility types."""

from typing import List, Dict, Any

PROVIDER_SPECIALTIES: List[Dict[str, str]] = [
    {"specialty": "Family Medicine", "taxonomy_code": "208D00000X"},
    {"specialty": "Internal Medicine", "taxonomy_code": "207R00000X"},
    {"specialty": "Cardiology (Cardiovascular Disease)", "taxonomy_code": "207RC0000X"},
    {"specialty": "Orthopedic Surgery", "taxonomy_code": "207X00000X"},
    {"specialty": "Gastroenterology", "taxonomy_code": "207RG0100X"},
    {"specialty": "Dermatology", "taxonomy_code": "207N00000X"},
    {"specialty": "Emergency Medicine", "taxonomy_code": "207P00000X"},
    {"specialty": "Neurology", "taxonomy_code": "2084N0400X"},
    {"specialty": "Psychiatry", "taxonomy_code": "2084P0800X"},
    {"specialty": "Pulmonary Disease", "taxonomy_code": "207RP1001X"},
    {"specialty": "Urology", "taxonomy_code": "208800000X"},
    {"specialty": "General Surgery", "taxonomy_code": "208600000X"},
    {"specialty": "Diagnostic Radiology", "taxonomy_code": "2085R0202X"},
    {"specialty": "Pathology - Clinical", "taxonomy_code": "207ZP0102X"},
    {"specialty": "Physical Therapy", "taxonomy_code": "225100000X"},
]

FACILITY_TEMPLATES: List[Dict[str, str]] = [
    {"name_suffix": "General Hospital", "facility_type": "Short-Term Acute Care Hospital"},
    {"name_suffix": "Memorial Medical Center", "facility_type": "Regional Medical Center"},
    {"name_suffix": "Community Health Center", "facility_type": "Federally Qualified Health Center"},
    {"name_suffix": "Ambulatory Surgical Center", "facility_type": "Ambulatory Surgical Center"},
    {"name_suffix": "Urgent Care & Family Clinic", "facility_type": "Urgent Care Clinic"},
    {"name_suffix": "Specialty Care Pavilion", "facility_type": "Multi-Specialty Clinic"},
    {"name_suffix": "Advanced Imaging & Diagnostic Center", "facility_type": "Diagnostic Imaging Center"},
    {"name_suffix": "Orthopedic & Spine Institute", "facility_type": "Specialty Surgical Center"},
]
