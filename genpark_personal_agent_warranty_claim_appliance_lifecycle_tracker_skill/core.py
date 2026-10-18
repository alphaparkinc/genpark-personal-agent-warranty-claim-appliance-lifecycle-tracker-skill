# -*- coding: utf-8 -*-
"""Warranty Claim & Appliance Lifecycle Tracker Skill for GenPark Personal Agents."""
import json
from datetime import datetime, timedelta
from typing import Dict, Any

def assess_appliance_warranty_status(appliance_name: str, purchase_date_iso: str, warranty_duration_months: int, repair_incidents_count: int = 0, total_out_of_service_days: int = 0) -> Dict[str, Any]:
    try:
        p_date = datetime.strptime(purchase_date_iso, "%Y-%m-%d")
    except ValueError:
        return {"error": "Invalid purchase_date_iso, must be YYYY-MM-DD"}

    # Approximate warranty end date
    approx_warranty_days = int(warranty_duration_months * 30.4375)
    expiration_date = p_date + timedelta(days=approx_warranty_days)
    today = datetime.now()
    remaining_days = (expiration_date - today).days

    is_expired = remaining_days < 0
    
    # Lemon Law indicator: Typically 3+ repair attempts for same issue or > 30 cumulated days out of service
    lemon_law_qualified = (repair_incidents_count >= 3) or (total_out_of_service_days >= 30)

    if is_expired:
        lifecycle_stage = "OUT_OF_WARRANTY"
        action = "Consider third-party extended protection or independent repair provider."
    elif remaining_days <= 30:
        lifecycle_stage = "IMMINENT_EXPIRATION"
        action = "Urgent: Inspect appliance immediately and lodge outstanding service tickets prior to expiry."
    else:
        lifecycle_stage = "ACTIVE_COVERAGE"
        action = "Normal coverage active; log all diagnostic and maintenance incidents."

    return {
        "appliance_name": appliance_name,
        "purchase_date": purchase_date_iso,
        "warranty_expiration_date": expiration_date.strftime("%Y-%m-%d"),
        "remaining_coverage_days": max(0, remaining_days),
        "lifecycle_stage": lifecycle_stage,
        "repair_incidents_logged": repair_incidents_count,
        "days_out_of_service": total_out_of_service_days,
        "lemon_law_statutory_threshold_met": lemon_law_qualified,
        "recommended_action": action,
        "rights_guidance": "Magnuson-Moss Warranty Act & state consumer protection statutes apply."
    }

def generate_warranty_claim_dossier(claimant_name: str, manufacturer: str, model_serial_number: str, fault_description: str, desired_resolution: str) -> Dict[str, Any]:
    formal_letter = (
        f"FORMAL NOTICE OF WARRANTY CLAIM / REPAIR DEMAND\n"
        f"To: {manufacturer} Customer Support & Legal Compliance\n"
        f"From: {claimant_name}\n"
        f"Product / Serial ID: {model_serial_number}\n\n"
        f"Notice is hereby served that the above-referenced unit has suffered a material failure:\n"
        f"'{fault_description}'\n\n"
        f"Under governing consumer product warranty statutes and the terms of express warranty, "
        f"I respectfully demand: {desired_resolution.upper().replace('_', ' ')} within 14 business days.\n"
        f"Failure to resolve may result in escalation to statutory dispute resolution bodies.\n"
        f"Sincerely,\n{claimant_name}"
    )

    return {
        "claimant": claimant_name,
        "manufacturer": manufacturer,
        "serial_id": model_serial_number,
        "requested_remedy": desired_resolution,
        "statutory_claim_letter_text": formal_letter,
        "filing_status": "DOSSIER_COMPILED",
        "compliance_engine": "GenPark Consumer Rights Legal Agent"
    }
