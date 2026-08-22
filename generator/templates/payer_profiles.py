"""Controlled synthetic payer and health insurance plan templates."""

from typing import List, Dict, Any

SYNTHETIC_PAYERS: List[Dict[str, Any]] = [
    # Commercial Payers (60% weight)
    {"name": "Apex Health Plan", "type": "Commercial", "timely_filing_days": 180, "plans": [
        {"name": "Apex Choice PPO Silver", "type": "PPO"},
        {"name": "Apex Choice PPO Gold", "type": "PPO"},
        {"name": "Apex Premier HMO Plus", "type": "HMO"},
    ]},
    {"name": "Northstar Health Care", "type": "Commercial", "timely_filing_days": 365, "plans": [
        {"name": "Northstar Open Access EPO", "type": "EPO"},
        {"name": "Northstar Value PPO", "type": "PPO"},
        {"name": "Northstar Complete HMO", "type": "HMO"},
    ]},
    {"name": "SummitCare Insurance", "type": "Commercial", "timely_filing_days": 90, "plans": [
        {"name": "SummitCare Bronze Saver HDHP", "type": "HDHP"},
        {"name": "SummitCare Platinum PPO", "type": "PPO"},
    ]},
    {"name": "Blue Horizon Health", "type": "Commercial", "timely_filing_days": 180, "plans": [
        {"name": "Blue Horizon Preferred PPO", "type": "PPO"},
        {"name": "Blue Horizon Core HMO", "type": "HMO"},
        {"name": "Blue Horizon Select POS", "type": "POS"},
    ]},
    {"name": "MetroCare Insurance Co", "type": "Commercial", "timely_filing_days": 365, "plans": [
        {"name": "MetroCare Essential Choice PPO", "type": "PPO"},
        {"name": "MetroCare Premier HMO", "type": "HMO"},
    ]},
    {"name": "Pinnacle Mutual Assurance", "type": "Commercial", "timely_filing_days": 180, "plans": [
        {"name": "Pinnacle Standard PPO", "type": "PPO"},
        {"name": "Pinnacle Executive Care", "type": "PPO"},
    ]},
    # Medicare / Medicare Advantage (25% weight)
    {"name": "Federal Medicare Part B (MAC Region A)", "type": "Medicare", "timely_filing_days": 365, "plans": [
        {"name": "Traditional Fee-for-Service Medicare Part B", "type": "Medicare FFS"},
    ]},
    {"name": "Evergreen Medicare Advantage", "type": "Medicare", "timely_filing_days": 365, "plans": [
        {"name": "Evergreen Senior Advantage HMO", "type": "Medicare Advantage"},
        {"name": "Evergreen Senior Choice PPO", "type": "Medicare Advantage"},
    ]},
    {"name": "Vanguard Senior Health Solutions", "type": "Medicare", "timely_filing_days": 180, "plans": [
        {"name": "Vanguard Medicare Complete PPO", "type": "Medicare Advantage"},
        {"name": "Vanguard Dual Eligible Special Needs Plan", "type": "D-SNP"},
    ]},
    # Medicaid / Managed Medicaid (15% weight)
    {"name": "State Community Health Medicaid", "type": "Medicaid", "timely_filing_days": 365, "plans": [
        {"name": "State Fee-for-Service Medicaid Program", "type": "Medicaid FFS"},
    ]},
    {"name": "Keystone Community Health Plan", "type": "Medicaid", "timely_filing_days": 180, "plans": [
        {"name": "Keystone Family Care Managed Medicaid", "type": "Managed Medicaid"},
        {"name": "Keystone Community Health Plus", "type": "Managed Medicaid"},
    ]},
    {"name": "Horizon Family Health Medicaid", "type": "Medicaid", "timely_filing_days": 90, "plans": [
        {"name": "Horizon Managed Family Health Plan", "type": "Managed Medicaid"},
    ]},
]
