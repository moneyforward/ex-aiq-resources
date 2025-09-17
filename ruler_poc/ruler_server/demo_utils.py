"""
Demo utilities for the expense rule validator.
This module contains functions for generating demo data and options.
"""

from typing import Dict, Any


def build_demo_options(rule: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build demo input options for a rule based on its required_fields.inputs.
    
    Args:
        rule: The rule definition from the rulebook
        
    Returns:
        Dict mapping field keys to lists of demo options
    """
    options = {}
    
    for i in rule.get("required_fields", {}).get("inputs", []):
        key = i.get("key", "")
        field_type = i.get("type", "string")
        allowed_values = i.get("allowed_values", [])
        
        if key in ("amount"):
            opts = [
                {"label": "1000", "value": 1000, "type": "money"},
                {"label": "5000", "value": 5000, "type": "money"},
                {"label": "15000", "value": 15000, "type": "money"}
            ]
        elif key in ("currency"):
            opts = [
                {"label": "JPY", "value": "JPY", "type": "string"},
                {"label": "USD", "value": "USD", "type": "string"}
            ]
        elif key in ("recognized_at", "check_in_date", "check_out_date"):
            opts = [
                {"label": "2024-01-15", "value": "2024-01-15", "type": "date"},
                {"label": "2024-01-20", "value": "2024-01-20", "type": "date"},
                {"label": "2024-02-01", "value": "2024-02-01", "type": "date"}
            ]
        elif key in ("remark"):
            opts = [
                {"label": "Business meeting with client", "value": "Business meeting with client", "type": "string"},
                {"label": "Team lunch", "value": "Team lunch", "type": "string"},
                {"label": "Office supplies purchase", "value": "Office supplies purchase", "type": "string"}
            ]
        elif key in ("payment_details"):
            opts = [
                {"label": "manual", "value": "manual", "type": "enum"},
                {"label": "corporate_card", "value": "corporate_card", "type": "enum"},
                {"label": "route_import", "value": "route_import", "type": "enum"}
            ]
        elif key in ("receipt_type"):
            opts = [
                {"label": "e_doc", "value": "e_doc", "type": "enum"},
                {"label": "paper", "value": "paper", "type": "enum"}
            ]
        elif key in ("receipt_images"):
            opts = [
                {"label": "receipt1.jpg", "value": "receipt1.jpg", "type": "file"},
                {"label": "receipt2.jpg", "value": "receipt2.jpg", "type": "file"},
                {"label": "No receipt", "value": "", "type": "file"}
            ]
        elif key in ("invoice_registration_number"):
            opts = [
                {"label": "T1234567890123", "value": "T1234567890123", "type": "string"},
                {"label": "T9876543210987", "value": "T9876543210987", "type": "string"},
                {"label": "No invoice number", "value": "", "type": "string"}
            ]
        elif key in ("pre_approval_id"):
            opts = [
                {"label": "PRE_001", "value": "PRE_001", "type": "string"},
                {"label": "PRE_002", "value": "PRE_002", "type": "string"}
            ]
        elif key in ("project_code"):
            opts = [
                {"label": "PROJ_A", "value": "PROJ_A", "type": "string"},
                {"label": "PROJ_B", "value": "PROJ_B", "type": "string"}
            ]
        elif key in ("route", "destination"):
            opts = [
                {"label": "Tokyo → Osaka", "value": "Tokyo → Osaka", "type": "string"},
                {"label": "Shinjuku → Shibuya", "value": "Shinjuku → Shibuya", "type": "string"}
            ]
        elif key in ("hotel_name"):
            opts = [
                {"label": "Tokyo Grand Hotel", "value": "Tokyo Grand Hotel", "type": "string"},
                {"label": "Osaka Business Inn", "value": "Osaka Business Inn", "type": "string"},
                {"label": "Kyoto Traditional Ryokan", "value": "Kyoto Traditional Ryokan", "type": "string"}
            ]
        elif key in ("hotel_location"):
            opts = [
                {"label": "Tokyo, Shibuya", "value": "Tokyo, Shibuya", "type": "string"},
                {"label": "Osaka, Namba", "value": "Osaka, Namba", "type": "string"},
                {"label": "Kyoto, Gion", "value": "Kyoto, Gion", "type": "string"}
            ]
        elif key in ("room_type"):
            opts = [
                {"label": "single", "value": "single", "type": "enum"},
                {"label": "double", "value": "double", "type": "enum"},
                {"label": "twin", "value": "twin", "type": "enum"},
                {"label": "suite", "value": "suite", "type": "enum"},
                {"label": "business", "value": "business", "type": "enum"},
                {"label": "economy", "value": "economy", "type": "enum"}
            ]
        elif key in ("confirmation_number"):
            opts = [
                {"label": "BK123456789", "value": "BK123456789", "type": "string"},
                {"label": "RES987654321", "value": "RES987654321", "type": "string"},
                {"label": "No confirmation", "value": "", "type": "string"}
            ]
        elif key in ("exchange_rate"):
            opts = [
                {"label": "1.00 (JPY)", "value": 1.00, "type": "decimal"},
                {"label": "0.0067 (USD to JPY)", "value": 0.0067, "type": "decimal"},
                {"label": "0.0059 (EUR to JPY)", "value": 0.0059, "type": "decimal"}
            ]
        elif key in ("purpose"):
            opts = [
                {"label": "Client meeting", "value": "Client meeting", "type": "string"},
                {"label": "Business conference", "value": "Business conference", "type": "string"}
            ]
        elif key in ("participants_info"):
            opts = [
                {"label": "John Doe (Company A), Jane Smith (Company B)", "value": "John Doe (Company A), Jane Smith (Company B)", "type": "string"},
                {"label": "Team members: 5 people", "value": "Team members: 5 people", "type": "string"}
            ]
        elif key in ("campaign_description"):
            opts = [
                {"label": "Q1 Marketing Campaign", "value": "Q1 Marketing Campaign", "type": "string"},
                {"label": "User Survey Incentive", "value": "User Survey Incentive", "type": "string"}
            ]
        elif key in ("num_nights", "num_people", "num_guests"):
            # Integer fields for accommodation/personnel
            opts = [
                {"label": "1", "value": 1, "type": "integer"},
                {"label": "2", "value": 2, "type": "integer"},
                {"label": "3", "value": 3, "type": "integer"},
                {"label": "5", "value": 5, "type": "integer"}
            ]
        elif field_type == "integer":
            # Generic integer fields
            opts = [
                {"label": "1", "value": 1, "type": "integer"},
                {"label": "5", "value": 5, "type": "integer"},
                {"label": "10", "value": 10, "type": "integer"}
            ]
        elif field_type == "money":
            # Generic money fields
            opts = [
                {"label": "1000", "value": 1000, "type": "money"},
                {"label": "5000", "value": 5000, "type": "money"},
                {"label": "15000", "value": 15000, "type": "money"}
            ]
        elif field_type == "date":
            # Generic date fields
            opts = [
                {"label": "2024-01-15", "value": "2024-01-15", "type": "date"},
                {"label": "2024-01-20", "value": "2024-01-20", "type": "date"}
            ]
        elif field_type == "enum" and allowed_values:
            # Enum fields with allowed values
            opts = []
            for val in allowed_values:
                opts.append({"label": val, "value": val, "type": "enum"})
        elif field_type == "file":
            # File fields
            opts = [
                {"label": "document1.pdf", "value": "document1.pdf", "type": "file"},
                {"label": "document2.pdf", "value": "document2.pdf", "type": "file"},
                {"label": "No file", "value": "", "type": "file"}
            ]
        elif field_type == "files":
            # Multiple files fields
            opts = [
                {"label": "doc1.pdf, doc2.pdf", "value": ["doc1.pdf", "doc2.pdf"], "type": "files"},
                {"label": "Single file", "value": ["doc1.pdf"], "type": "files"},
                {"label": "No files", "value": [], "type": "files"}
            ]
        elif field_type == "structured":
            # Structured data fields
            opts = [
                {"label": "Simple structure", "value": {"key": "value"}, "type": "structured"},
                {"label": "Complex structure", "value": {"nested": {"data": "example"}}, "type": "structured"}
            ]
        elif field_type == "note":
            # Note fields
            opts = [
                {"label": "Short note", "value": "Brief explanation", "type": "note"},
                {"label": "Detailed note", "value": "Comprehensive explanation with details", "type": "note"}
            ]
        else:
            # Generic string fields or unknown types
            opts = [
                {"label": "Sample text", "value": "sample_text", "type": "string"},
                {"label": "Another example", "value": "another_example", "type": "string"}
            ]
        
        options[key] = opts
    return options


def get_demo_rule_summary(rule: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get a summary of a rule for demo display purposes.
    
    Args:
        rule: The rule definition
        
    Returns:
        Dict with summary information for the demo
    """
    return {
        "clause_id": rule.get("clause_id"),
        "category": rule.get("clause_id", "").split("_")[0] if rule.get("clause_id") else "",
        "expense_category": rule.get("expense_category", {}),
        "usage_conditions": rule.get("usage_conditions", {}),
        "validation_rules": rule.get("validation_rules", {}),
        "required_fields_count": len(rule.get("required_fields", {}).get("inputs", [])),
        "risk_level": rule.get("risk_level", "UNKNOWN")
    }
