"""Controlled synthetic clinical coding library (CPT-4 and ICD-10-CM).

Note: These codes and descriptions represent public standardized healthcare coding
terminology used exclusively as fictional content for ClaimIQ synthetic data operations.
"""

from decimal import Decimal
from typing import Dict, List, Any

CPT_CODES: List[Dict[str, Any]] = [
    # Evaluation & Management (E/M)
    {"code": "99202", "description": "Office/outpatient visit, new patient, 15-29 min", "category": "E/M", "min_price": Decimal("75.00"), "max_price": Decimal("120.00")},
    {"code": "99203", "description": "Office/outpatient visit, new patient, 30-44 min", "category": "E/M", "min_price": Decimal("110.00"), "max_price": Decimal("180.00")},
    {"code": "99204", "description": "Office/outpatient visit, new patient, 45-59 min", "category": "E/M", "min_price": Decimal("165.00"), "max_price": Decimal("260.00")},
    {"code": "99205", "description": "Office/outpatient visit, new patient, 60-74 min", "category": "E/M", "min_price": Decimal("220.00"), "max_price": Decimal("350.00")},
    {"code": "99211", "description": "Office/outpatient visit, established patient, minimal", "category": "E/M", "min_price": Decimal("25.00"), "max_price": Decimal("45.00")},
    {"code": "99212", "description": "Office/outpatient visit, established patient, 10-19 min", "category": "E/M", "min_price": Decimal("55.00"), "max_price": Decimal("85.00")},
    {"code": "99213", "description": "Office/outpatient visit, established patient, 20-29 min", "category": "E/M", "min_price": Decimal("90.00"), "max_price": Decimal("145.00")},
    {"code": "99214", "description": "Office/outpatient visit, established patient, 30-39 min", "category": "E/M", "min_price": Decimal("130.00"), "max_price": Decimal("210.00")},
    {"code": "99215", "description": "Office/outpatient visit, established patient, 40-54 min", "category": "E/M", "min_price": Decimal("180.00"), "max_price": Decimal("290.00")},
    {"code": "99282", "description": "Emergency dept visit, low-level severity", "category": "Emergency", "min_price": Decimal("120.00"), "max_price": Decimal("220.00")},
    {"code": "99283", "description": "Emergency dept visit, moderate severity", "category": "Emergency", "min_price": Decimal("200.00"), "max_price": Decimal("380.00")},
    {"code": "99284", "description": "Emergency dept visit, high severity without threat", "category": "Emergency", "min_price": Decimal("350.00"), "max_price": Decimal("650.00")},
    {"code": "99285", "description": "Emergency dept visit, high severity with threat", "category": "Emergency", "min_price": Decimal("500.00"), "max_price": Decimal("950.00")},
    # Pathology & Laboratory
    {"code": "36415", "description": "Routine venipuncture / blood draw", "category": "Laboratory", "min_price": Decimal("12.00"), "max_price": Decimal("25.00")},
    {"code": "80053", "description": "Comprehensive metabolic panel (CMP)", "category": "Laboratory", "min_price": Decimal("45.00"), "max_price": Decimal("85.00")},
    {"code": "80061", "description": "Lipid panel (Cholesterol, HDL, Triglycerides)", "category": "Laboratory", "min_price": Decimal("35.00"), "max_price": Decimal("70.00")},
    {"code": "85025", "description": "Complete blood count (CBC) with automated differential", "category": "Laboratory", "min_price": Decimal("28.00"), "max_price": Decimal("55.00")},
    {"code": "83036", "description": "Hemoglobin A1c test for diabetes", "category": "Laboratory", "min_price": Decimal("30.00"), "max_price": Decimal("60.00")},
    {"code": "84443", "description": "Thyroid stimulating hormone (TSH)", "category": "Laboratory", "min_price": Decimal("40.00"), "max_price": Decimal("75.00")},
    {"code": "81003", "description": "Urinalysis, automated without microscopy", "category": "Laboratory", "min_price": Decimal("15.00"), "max_price": Decimal("30.00")},
    # Radiology & Diagnostic Imaging
    {"code": "71045", "description": "Chest X-ray, single view", "category": "Radiology", "min_price": Decimal("60.00"), "max_price": Decimal("110.00")},
    {"code": "71046", "description": "Chest X-ray, 2 views frontal and lateral", "category": "Radiology", "min_price": Decimal("85.00"), "max_price": Decimal("150.00")},
    {"code": "70450", "description": "CT head/brain without contrast", "category": "Radiology", "min_price": Decimal("450.00"), "max_price": Decimal("850.00")},
    {"code": "73721", "description": "MRI knee joint without contrast", "category": "Radiology", "min_price": Decimal("600.00"), "max_price": Decimal("1200.00")},
    {"code": "76700", "description": "Ultrasound abdominal, complete", "category": "Radiology", "min_price": Decimal("220.00"), "max_price": Decimal("420.00")},
    # Medicine / Cardiology / Procedures
    {"code": "93000", "description": "Electrocardiogram (ECG/EKG), routine with interpretation", "category": "Cardiology", "min_price": Decimal("50.00"), "max_price": Decimal("95.00")},
    {"code": "93306", "description": "Echocardiography, complete transthoracic with Doppler", "category": "Cardiology", "min_price": Decimal("400.00"), "max_price": Decimal("780.00")},
    {"code": "90471", "description": "Immunization administration, 1 vaccine", "category": "Preventive", "min_price": Decimal("25.00"), "max_price": Decimal("45.00")},
    {"code": "90686", "description": "Influenza vaccine, quadrivalent 0.5 mL", "category": "Preventive", "min_price": Decimal("30.00"), "max_price": Decimal("55.00")},
    {"code": "97110", "description": "Therapeutic exercises, each 15 minutes", "category": "Physical Therapy", "min_price": Decimal("45.00"), "max_price": Decimal("80.00")},
    {"code": "97140", "description": "Manual therapy techniques, 15 minutes", "category": "Physical Therapy", "min_price": Decimal("50.00"), "max_price": Decimal("90.00")},
    # Surgical / Specialty Procedures
    {"code": "43239", "description": "Upper GI endoscopy with biopsy", "category": "Gastroenterology", "min_price": Decimal("850.00"), "max_price": Decimal("1600.00")},
    {"code": "45380", "description": "Colonoscopy with biopsy single/multiple", "category": "Gastroenterology", "min_price": Decimal("950.00"), "max_price": Decimal("1800.00")},
    {"code": "29881", "description": "Arthroscopy knee surgical with meniscectomy", "category": "Orthopedics", "min_price": Decimal("1800.00"), "max_price": Decimal("3200.00")},
    {"code": "10060", "description": "Incision and drainage of abscess, simple/single", "category": "Dermatology", "min_price": Decimal("140.00"), "max_price": Decimal("260.00")},
]

ICD10_CODES: List[Dict[str, str]] = [
    # Circulatory & Hypertension
    {"code": "I10", "description": "Essential (primary) hypertension", "specialty": "Cardiology"},
    {"code": "I25.10", "description": "Atherosclerotic heart disease of native coronary artery", "specialty": "Cardiology"},
    {"code": "I50.9", "description": "Heart failure, unspecified", "specialty": "Cardiology"},
    {"code": "I48.91", "description": "Unspecified atrial fibrillation", "specialty": "Cardiology"},
    {"code": "I73.9", "description": "Peripheral vascular disease, unspecified", "specialty": "Cardiology"},
    # Endocrine & Metabolic
    {"code": "E11.9", "description": "Type 2 diabetes mellitus without complications", "specialty": "Endocrinology"},
    {"code": "E11.65", "description": "Type 2 diabetes mellitus with hyperglycemia", "specialty": "Endocrinology"},
    {"code": "E78.5", "description": "Hyperlipidemia, unspecified", "specialty": "Internal Medicine"},
    {"code": "E03.9", "description": "Hypothyroidism, unspecified", "specialty": "Endocrinology"},
    {"code": "E66.01", "description": "Morbid (severe) obesity due to excess calories", "specialty": "Endocrinology"},
    # Respiratory
    {"code": "J06.9", "description": "Acute upper respiratory infection, unspecified", "specialty": "Family Medicine"},
    {"code": "J45.909", "description": "Unspecified asthma, uncomplicated", "specialty": "Pulmonology"},
    {"code": "J44.9", "description": "Chronic obstructive pulmonary disease, unspecified", "specialty": "Pulmonology"},
    {"code": "J20.9", "description": "Acute bronchitis, unspecified", "specialty": "Family Medicine"},
    {"code": "J01.90", "description": "Acute sinusitis, unspecified", "specialty": "Family Medicine"},
    # Musculoskeletal & Joint
    {"code": "M54.5", "description": "Low back pain", "specialty": "Orthopedics"},
    {"code": "M54.2", "description": "Cervicalgia (neck pain)", "specialty": "Orthopedics"},
    {"code": "M25.561", "description": "Pain in right knee", "specialty": "Orthopedics"},
    {"code": "M25.562", "description": "Pain in left knee", "specialty": "Orthopedics"},
    {"code": "M17.11", "description": "Primary osteoarthritis, right knee", "specialty": "Orthopedics"},
    {"code": "M79.3", "description": "Panniculitis, unspecified (fibromyalgia/myalgia)", "specialty": "Rheumatology"},
    # Digestive
    {"code": "K21.9", "description": "Gastro-esophageal reflux disease without esophagitis", "specialty": "Gastroenterology"},
    {"code": "K58.9", "description": "Irritable bowel syndrome without diarrhea", "specialty": "Gastroenterology"},
    {"code": "K29.70", "description": "Gastritis, unspecified, without bleeding", "specialty": "Gastroenterology"},
    {"code": "K57.90", "description": "Diverticulosis of intestine, part unspecified", "specialty": "Gastroenterology"},
    # Mental Health & Behavioral
    {"code": "F41.1", "description": "Generalized anxiety disorder", "specialty": "Psychiatry"},
    {"code": "F32.9", "description": "Major depressive disorder, single episode, unspecified", "specialty": "Psychiatry"},
    {"code": "F43.10", "description": "Post-traumatic stress disorder, unspecified", "specialty": "Psychiatry"},
    {"code": "G47.00", "description": "Insomnia, unspecified", "specialty": "Neurology"},
    # Nervous System
    {"code": "G43.909", "description": "Migraine, unspecified, not intractable", "specialty": "Neurology"},
    {"code": "G56.01", "description": "Carpal tunnel syndrome, right upper limb", "specialty": "Neurology"},
    {"code": "R51.9", "description": "Headache, unspecified", "specialty": "Neurology"},
    {"code": "R42", "description": "Dizziness and giddiness", "specialty": "Neurology"},
    # Genitourinary & Renal
    {"code": "N39.0", "description": "Urinary tract infection, site not specified", "specialty": "Urology"},
    {"code": "N18.30", "description": "Chronic kidney disease, stage 3 unspecified", "specialty": "Nephrology"},
    {"code": "N40.0", "description": "Benign prostatic hyperplasia without lower urinary symptoms", "specialty": "Urology"},
    # Skin & Subcutaneous
    {"code": "L30.9", "description": "Dermatitis, unspecified", "specialty": "Dermatology"},
    {"code": "L03.90", "description": "Cellulitis, unspecified", "specialty": "Dermatology"},
    {"code": "L70.0", "description": "Acne vulgaris", "specialty": "Dermatology"},
    # General Symptoms & Preventive
    {"code": "Z00.00", "description": "Encounter for general adult medical exam without abnormal findings", "specialty": "Internal Medicine"},
    {"code": "Z23", "description": "Encounter for immunization", "specialty": "Preventive"},
    {"code": "R53.83", "description": "Other fatigue", "specialty": "Family Medicine"},
    {"code": "R10.9", "description": "Unspecified abdominal pain", "specialty": "Gastroenterology"},
    {"code": "R07.9", "description": "Chest pain, unspecified", "specialty": "Cardiology"},
    {"code": "Z79.899", "description": "Other long term (current) drug therapy", "specialty": "Internal Medicine"},
]
