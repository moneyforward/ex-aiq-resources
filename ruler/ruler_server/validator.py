"""
Expense Rule Validator

This module provides validation logic for expense rules based on rulebook definitions.
"""

import json
from typing import Dict, List, Any, Optional, Tuple
import sys
from pathlib import Path

# Add the parent directory to the path to import output_schema
# This allows us to import from the parent directory where output_schema is located
current_file = Path(__file__)
parent_dir = current_file.parent.parent
sys.path.insert(0, str(parent_dir))

from output_schema.reason_processor import ReasonProcessor

# Centralized configuration for allowed values
# This eliminates duplication and makes maintenance easier
# 
# Benefits:
# - Single source of truth for all allowed values
# - Easy to update values in one place
# - Consistent across all validation logic
# - No risk of different parts of the system having different values
# - Easier to add new allowed values or modify existing ones
ALLOWED_VALUES = {
    "currencies": ["JPY", "USD", "EUR"],
    "file_formats": ["JPEG", "PNG", "PDF"],
    "receipt_types": ["receipt", "invoice", "credit_card"],
    "approvers": ["manager", "director", "vp"],
    "defaults": {
        "threshold": 1000,
        "limit": 1000000,
        "minimum": 0,
        "max_size": "10MB",
        "submission_window": 30
    }
}

# Global reason processor instance
_reason_processor = None

def get_reason_processor() -> ReasonProcessor:
    """Get or create the reason processor instance."""
    global _reason_processor
    if _reason_processor is None:
        _reason_processor = ReasonProcessor()
    return _reason_processor


def get_missing_field_reason(field_name: str, rule: Dict[str, Any]) -> tuple[str, str]:
    """
    Generic function to determine missing field reason and get field display info.
    
    Args:
        field_name: The name of the missing field
        rule: The rule definition for context
        
    Returns:
        Tuple of (reason_code, field_display_name)
    """
    processor = get_reason_processor()
    
    # Get the field definition from the rule
    field_def = None
    for field in rule.get("required_fields", {}).get("inputs", []):
        if field.get("key") == field_name:
            field_def = field
            break
    
    # Get field display name for better error messages
    field_display_name = field_name
    if field_def:
        # Use field label, description, or purpose if available
        label = field_def.get("label")
        if isinstance(label, dict):
            # If label is a dictionary with language keys, use English or fallback to first available
            field_display_name = label.get("en") or label.get("ja") or next(iter(label.values()), field_name)
        else:
            field_display_name = (
                label or 
                field_def.get("description") or 
                field_def.get("purpose") or 
                field_name
            )
    
    # Check validation rules for field-specific requirements
    validation_rules = rule.get("validation_rules", {})
    
    # Use field metadata to determine the reason
    if field_def:
        field_type = field_def.get("type", "")
        field_purpose = field_def.get("purpose", "")
        field_metadata = field_def.get("metadata", {})
        
        # Check if field has specific validation requirements from metadata
        # No hardcoded field name fallbacks - everything comes from metadata
        for metadata_key, reason_code in [
            ("receipt_required", "missing_receipt_images"),
            ("approval_required", "missing_pre_approval"),
            ("invoice_required", "missing_invoice_number"),
            ("project_required", "missing_project_code"),
            ("route_required", "missing_route_info"),
            ("destination_required", "missing_destination"),
            ("purpose_required", "missing_purpose"),
            ("payment_required", "missing_payment_details"),
            ("nights_required", "missing_nights_count"),
            ("people_required", "missing_people_count")
        ]:
            if field_metadata.get(metadata_key) and processor.validate_reason_code(reason_code):
                return reason_code, field_display_name
    
    # Fallback to generic missing field reason
    reason_code = "missing_field" if processor.validate_reason_code("missing_field") else "missing_field"
    return reason_code, field_display_name


def generate_field_context(field_name: str, rule: Dict[str, Any], variables: Dict[str, Any]) -> str:
    """
    Generate meaningful context for missing fields to improve user experience.
    
    Args:
        field_name: The name of the missing field
        rule: The rule definition for context
        variables: Current validation variables
        
    Returns:
        Context string explaining why the field is required
    """
    # Get the field definition from the rule
    field_def = None
    for field in rule.get("required_fields", {}).get("inputs", []):
        if field.get("key") == field_name:
            field_def = field
            break
    
    # Generate context based on field type and purpose
    if field_name in ["receipt_images", "receipt_image"]:
        threshold = variables.get("threshold", 1000)
        currency = variables.get("currency", "JPY")
        return f"Receipts are required for all expenses above {threshold} {currency}."
    
    elif field_name in ["pre_approval_id", "pre_approval"]:
        threshold = variables.get("threshold", 5000)
        currency = variables.get("currency", "JPY")
        return f"Pre-approval is required for expenses above {threshold} {currency}."
    
    elif field_name in ["invoice_registration_number", "invoice_number"]:
        return "Invoice numbers are required for tracking and compliance."
    
    elif field_name in ["project_code", "project"]:
        return "Project codes are required to ensure proper cost allocation."
    
    elif field_name in ["route", "route_info"]:
        return "Route information is required for travel expense validation."
    
    elif field_name in ["destination"]:
        return "Destination is required for travel expense validation."
    
    elif field_name in ["purpose"]:
        return "Business purpose is required for expense validation."
    
    elif field_name in ["payment_details", "payment_method"]:
        return "Payment details are required for expense tracking and reconciliation."
    
    elif field_name in ["num_nights", "nights_count"]:
        return "Number of nights is required for accommodation expense validation."
    
    elif field_name in ["num_people", "num_guests", "people_count"]:
        return "Number of people is required for expense validation."
    
    elif field_name in ["hotel_name"]:
        return "Hotel name is required for proper expense tracking and validation."
    
    elif field_name in ["check_in_date", "check_in"]:
        return "Check-in date is required to validate the accommodation period."
    
    elif field_name in ["check_out_date", "check_out"]:
        return "Check-out date is required to validate the accommodation period."
    
    elif field_name in ["hotel_location", "location"]:
        return "Hotel location is required for business trip validation and expense categorization."
    
    elif field_name in ["room_type"]:
        return "Room type helps categorize the accommodation expense properly."
    
    elif field_name in ["confirmation_number", "booking_reference"]:
        return "Booking confirmation number is required for expense verification."
    
    elif field_name in ["exchange_rate"]:
        return "Exchange rate is required for overseas expense conversion."
    
    elif field_name in ["approver", "approver_name"]:
        threshold = variables.get("threshold", 10000)
        currency = variables.get("currency", "JPY")
        return f"Approver is required for expenses above {threshold} {currency}."
    
    elif field_name in ["tax_information", "tax_details"]:
        threshold = variables.get("threshold", 1000)
        currency = variables.get("currency", "JPY")
        return f"Tax details are required for expenses above {threshold} {currency}."
    
    # Default context for unknown fields
    return "This field is required for proper expense validation and processing."


def analyze_validation_rules(validation_rules: Dict[str, Any], rule: Dict[str, Any], given: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generic validation rule analyzer that recursively processes all nested validation rules.
    
    Args:
        validation_rules: The validation rules from the rule
        rule: The complete rule definition
        given: The input data to validate
        
    Returns:
        List of validation checks with validity status and reason codes
    """
    processor = get_reason_processor()
    checks = []
    
    # Recursively process all validation rules (including nested ones)
    def process_validation_rules(rules: Dict[str, Any], path: str = "") -> None:
        for rule_key, rule_value in rules.items():
            current_path = f"{path}.{rule_key}" if path else rule_key
            
            if isinstance(rule_value, dict):
                # Recursively process nested validation rules
                process_validation_rules(rule_value, current_path)
                
                # Check if this is a validation rule with field_name and reason_code
                if "field_name" in rule_value and "reason_code" in rule_value:
                    field_name = rule_value["field_name"]
                    reason_code = rule_value["reason_code"]
                    validation_type = rule_value.get("type", "required")
                    
                    if processor.validate_reason_code(reason_code):
                        if validation_type == "required":
                            if not given.get(field_name):
                                checks.append({
                                    "valid": False,
                                    "reason": reason_code
                                })
                            else:
                                checks.append({"valid": True, "reason": None})
                                
                        elif validation_type == "format":
                            if given.get(field_name):
                                if not validate_field_format(given[field_name], rule_value):
                                    checks.append({
                                        "valid": False,
                                        "reason": reason_code
                                    })
                                else:
                                    checks.append({"valid": True, "reason": None})
                                    
                        elif validation_type == "range":
                            if given.get(field_name):
                                if not validate_field_range(given[field_name], rule_value):
                                    checks.append({
                                        "valid": False,
                                        "reason": reason_code
                                    })
                                else:
                                    checks.append({"valid": True, "reason": None})
                                    
                        elif validation_type == "date_validation":
                            if given.get(field_name):
                                date_checks = validate_date_field(given[field_name], rule_value, processor)
                                checks.extend(date_checks)
                                
                        elif validation_type == "business_rule":
                            if given.get(field_name):
                                business_checks = validate_business_rules(given[field_name], rule_value, given, processor)
                                checks.extend(business_checks)
                                
                        elif validation_type == "field_type":
                            if given.get(field_name):
                                type_checks = validate_field_type(given[field_name], rule_value, processor)
                                checks.extend(type_checks)
                                
                        elif validation_type == "amount_constraint":
                            if given.get(field_name):
                                amount_checks = validate_amount_constraints(given[field_name], rule_value, processor)
                                checks.extend(amount_checks)
                                
                        elif validation_type == "accommodation_dates":
                            # Validate accommodation dates (check-in vs check-out)
                            if given.get("check_in_date") and given.get("check_out_date"):
                                accommodation_checks = validate_accommodation_dates(given, processor)
                                checks.extend(accommodation_checks)
                
                # Handle schema-defined validation rules
                elif rule_key == "amount_constraints":
                    # Process amount constraints from schema
                    amount_checks = process_amount_constraints(rule_value, given, processor)
                    checks.extend(amount_checks)
                    
                elif rule_key == "dynamic_amount_formula":
                    # Process dynamic amount formulas
                    formula_checks = process_dynamic_amount_formula(rule_value, given, processor)
                    checks.extend(formula_checks)
                    
                elif rule_key == "frequency_constraints":
                    # Process frequency constraints
                    frequency_checks = process_frequency_constraints(rule_value, given, processor)
                    checks.extend(frequency_checks)
                    
                elif rule_key == "special_thresholds":
                    # Process special thresholds
                    threshold_checks = process_special_thresholds(rule_value, given, processor)
                    checks.extend(threshold_checks)
            
            elif isinstance(rule_value, bool) and rule_value:
                # Simple boolean validation rules
                boolean_checks = process_boolean_validation_rule(rule_key, rule_value, given, processor)
                checks.extend(boolean_checks)
                
            elif isinstance(rule_value, (int, float)):
                # Numeric validation rules (like max_amount)
                numeric_checks = process_numeric_validation_rule(rule_key, rule_value, given, processor)
                checks.extend(numeric_checks)
                
            elif isinstance(rule_value, str):
                # String validation rules (like tax_rate)
                string_checks = process_string_validation_rule(rule_key, rule_value, given, processor)
                checks.extend(string_checks)
    
    # Start recursive processing
    process_validation_rules(validation_rules)
    return checks


def process_amount_constraints(constraints: Dict[str, Any], given: Dict[str, Any], processor: ReasonProcessor) -> List[Dict[str, Any]]:
    """Process amount constraints from schema."""
    checks = []
    amount = given.get("amount")
    
    if not isinstance(amount, (int, float)):
        return checks
    
    # Max amount validation
    max_amount = constraints.get("max_amount_jpy")
    if max_amount is not None and amount > max_amount:
        if processor.validate_reason_code("amount_exceeds_limit"):
            checks.append({
                "valid": False,
                "reason": "amount_exceeds_limit"
            })
    
    # Per-person max amount validation
    per_person_max = constraints.get("per_person_max_amount_jpy")
    if per_person_max is not None and amount > per_person_max:
        if processor.validate_reason_code("amount_exceeds_limit"):
            checks.append({
                "valid": False,
                "reason": "amount_exceeds_limit"
            })
    
    # Per-person min amount validation
    per_person_min = constraints.get("per_person_min_amount_jpy")
    if per_person_min is not None:
        min_exclusive = constraints.get("per_person_min_exclusive", False)
        if min_exclusive and amount <= per_person_min:
            if processor.validate_reason_code("amount_below_minimum"):
                checks.append({
                    "valid": False,
                    "reason": "amount_below_minimum"
                })
        elif not min_exclusive and amount < per_person_min:
            if processor.validate_reason_code("amount_below_minimum"):
                checks.append({
                    "valid": False,
                    "reason": "amount_below_minimum"
                })
    
    # Item unit validations
    item_unit_max = constraints.get("item_unit_max_amount_jpy")
    if item_unit_max is not None and amount > item_unit_max:
        if processor.validate_reason_code("amount_exceeds_limit"):
            checks.append({
                "valid": False,
                "reason": "amount_exceeds_limit"
            })
    
    item_unit_min = constraints.get("item_unit_min_amount_jpy")
    if item_unit_min is not None:
        min_inclusive = constraints.get("item_unit_min_inclusive", True)
        if min_inclusive and amount < item_unit_min:
            if processor.validate_reason_code("amount_below_minimum"):
                checks.append({
                    "valid": False,
                    "reason": "amount_below_minimum"
                })
        elif not min_inclusive and amount <= item_unit_min:
            if processor.validate_reason_code("amount_below_minimum"):
                checks.append({
                    "valid": False,
                    "reason": "amount_below_minimum"
                })
    
    return checks


def process_dynamic_amount_formula(formula: Dict[str, Any], given: Dict[str, Any], processor: ReasonProcessor) -> List[Dict[str, Any]]:
    """Process dynamic amount formulas."""
    checks = []
    formula_type = formula.get("type")
    unit_amount = formula.get("unit_amount_jpy")
    variable = formula.get("variable")
    
    if not all([formula_type, unit_amount, variable]):
        return checks
    
    # Get the variable value (e.g., num_nights, num_people)
    variable_value = given.get(variable)
    if variable_value is None:
        return checks
    
    # Calculate expected amount based on formula
    expected_amount = unit_amount * variable_value
    actual_amount = given.get("amount")
    
    if actual_amount is not None and actual_amount > expected_amount:
        if processor.validate_reason_code("amount_exceeds_limit"):
            checks.append({
                "valid": False,
                "reason": "amount_exceeds_limit"
            })
    
    return checks


def process_frequency_constraints(constraints: Dict[str, Any], given: Dict[str, Any], processor: ReasonProcessor) -> List[Dict[str, Any]]:
    """Process frequency constraints."""
    checks = []
    
    max_occurrences = constraints.get("max_occurrences_per_period")
    if not max_occurrences:
        return checks
    
    scope = max_occurrences.get("scope")
    count = max_occurrences.get("count")
    period = max_occurrences.get("period")
    
    if scope == "person" and count is not None:
        # In real implementation, you'd check against database for frequency
        # For now, just a placeholder
        pass
    
    return checks


def process_special_thresholds(thresholds: Dict[str, Any], given: Dict[str, Any], processor: ReasonProcessor) -> List[Dict[str, Any]]:
    """Process special thresholds."""
    checks = []
    
    # Process any special threshold rules defined in the schema
    # This is extensible for future threshold types
    for threshold_key, threshold_value in thresholds.items():
        if isinstance(threshold_value, dict) and "field_name" in threshold_value:
            # Process as a validation rule
            field_name = threshold_value["field_name"]
            reason_code = threshold_value.get("reason_code", "amount_exceeds_limit")
            
            if processor.validate_reason_code(reason_code):
                if not given.get(field_name):
                    checks.append({
                        "valid": False,
                        "reason": reason_code
                    })
    
    return checks


def process_boolean_validation_rule(rule_key: str, rule_value: bool, given: Dict[str, Any], processor: ReasonProcessor) -> List[Dict[str, Any]]:
    """Process boolean validation rules."""
    checks = []
    
    # Map boolean rules to their corresponding validations
    rule_mappings = {
        "receipt_required": ("receipt_images", "missing_receipt_images"),
        "invoice_number_required": ("invoice_registration_number", "missing_invoice_number"),
        "project_code_required": ("project_code", "missing_project_code"),
        "pre_approval_required": ("pre_approval_id", "missing_pre_approval")
    }
    
    if rule_key in rule_mappings:
        field_name, reason_code = rule_mappings[rule_key]
        if not given.get(field_name):
            if processor.validate_reason_code(reason_code):
                checks.append({
                    "valid": False,
                    "reason": reason_code
                })
    
    return checks


def process_numeric_validation_rule(rule_key: str, rule_value: (int, float), given: Dict[str, Any], processor: ReasonProcessor) -> List[Dict[str, Any]]:
    """Process numeric validation rules."""
    checks = []
    
    if rule_key == "max_amount":
        amount = given.get("amount")
        if amount is not None and amount > rule_value:
            if processor.validate_reason_code("amount_exceeds_limit"):
                checks.append({
                    "valid": False,
                    "reason": "amount_exceeds_limit"
                })
    
    return checks


def process_string_validation_rule(rule_key: str, rule_value: str, given: Dict[str, Any], processor: ReasonProcessor) -> List[Dict[str, Any]]:
    """Process string validation rules."""
    checks = []
    
    if rule_key == "tax_rate":
        # Tax rate validation could be implemented here
        # For now, just a placeholder
        pass
    
    return checks


def validate_field_type(value: Any, rule: Dict[str, Any], processor: ReasonProcessor) -> List[Dict[str, Any]]:
    """Generic field type validator."""
    checks = []
    field_type = rule.get("field_type")
    
    if field_type == "enum":
        allowed_values = rule.get("allowed_values", [])
        if allowed_values and value not in allowed_values:
            if processor.validate_reason_code("invalid_enum_value"):
                checks.append({
                    "valid": False,
                    "reason": "invalid_enum_value"
                })
    
    elif field_type == "date":
        try:
            from datetime import datetime
            datetime.strptime(str(value), "%Y-%m-%d")
        except ValueError:
            if processor.validate_reason_code("invalid_date"):
                checks.append({
                    "valid": False,
                    "reason": "invalid_date"
                })
    
    elif field_type == "money":
        if not isinstance(value, (int, float)) or value <= 0:
            if processor.validate_reason_code("amount_exceeds_limit"):
                checks.append({
                    "valid": False,
                    "reason": "amount_exceeds_limit"
                })
    
    elif field_type == "integer":
        if not isinstance(value, (int, float)) or value <= 0:
            if processor.validate_reason_code("amount_exceeds_limit"):
                checks.append({
                    "valid": False,
                    "reason": "amount_exceeds_limit"
                })
    
    return checks


def validate_amount_constraints(value: Any, rule: Dict[str, Any], processor: ReasonProcessor) -> List[Dict[str, Any]]:
    """Generic amount constraint validator."""
    checks = []
    
    if not isinstance(value, (int, float)):
        return checks
    
    # Max amount validation
    max_amount = rule.get("max_amount")
    if max_amount is not None and value > max_amount:
        if processor.validate_reason_code("amount_exceeds_limit"):
            checks.append({
                "valid": False,
                "reason": "amount_exceeds_limit"
            })
    
    # Min amount validation
    min_amount = rule.get("min_amount")
    if min_amount is not None:
        if rule.get("min_exclusive", False):
            if value <= min_amount:
                if processor.validate_reason_code("amount_below_minimum"):
                    checks.append({
                        "valid": False,
                        "reason": "amount_below_minimum"
                    })
        else:
            if value < min_amount:
                if processor.validate_reason_code("amount_below_minimum"):
                    checks.append({
                        "valid": False,
                        "reason": "amount_below_minimum"
                    })
    
    # Per-person amount validations
    per_person_max = rule.get("per_person_max_amount")
    if per_person_max is not None and value > per_person_max:
        if processor.validate_reason_code("amount_exceeds_limit"):
            checks.append({
                "valid": False,
                "reason": "amount_exceeds_limit"
            })
    
    per_person_min = rule.get("per_person_min_amount")
    if per_person_min is not None:
        if rule.get("per_person_min_exclusive", False):
            if value <= per_person_min:
                if processor.validate_reason_code("amount_below_minimum"):
                    checks.append({
                        "valid": False,
                        "reason": "amount_below_minimum"
                    })
        else:
            if value < per_person_min:
                if processor.validate_reason_code("amount_below_minimum"):
                    checks.append({
                        "valid": False,
                        "reason": "amount_below_minimum"
                    })
    
    return checks


def validate_field_format(value: Any, rule: Dict[str, Any]) -> bool:
    """Generic field format validator."""
    format_type = rule.get("format_type")
    
    if format_type == "date":
        try:
            from datetime import datetime
            datetime.strptime(str(value), "%Y-%m-%d")
            return True
        except ValueError:
            return False
    elif format_type == "currency":
        return str(value) in ALLOWED_VALUES["currencies"]
    elif format_type == "enum":
        allowed_values = rule.get("allowed_values", [])
        return value in allowed_values
    
    return True


def validate_field_range(value: Any, rule: Dict[str, Any]) -> bool:
    """Generic field range validator."""
    if isinstance(value, (int, float)):
        min_val = rule.get("min_value")
        max_val = rule.get("max_value")
        
        if min_val is not None and value < min_val:
            return False
        if max_val is not None and value > max_val:
            return False
    
    return True


def validate_date_field(value: Any, rule: Dict[str, Any], processor: ReasonProcessor) -> List[Dict[str, Any]]:
    """Generic date field validator."""
    checks = []
    
    try:
        from datetime import datetime
        expense_date = datetime.strptime(str(value), "%Y-%m-%d")
        current_date = datetime.now()
        
        # Check for future dates
        if rule.get("future_dates_not_allowed") and expense_date > current_date:
            if processor.validate_reason_code("future_date_not_allowed"):
                checks.append({
                    "valid": False,
                    "reason": "future_date_not_allowed"
                })
        
        # Check for very old dates (beyond submission window)
        submission_window = rule.get("submission_window_days", 30)
        if (current_date - expense_date).days > submission_window:
            if processor.validate_reason_code("date_too_old"):
                checks.append({
                    "valid": False,
                    "reason": "date_too_old"
                })
        
        # Check for weekend restrictions
        if rule.get("weekend_expenses_not_allowed") and expense_date.weekday() >= 5:
            if processor.validate_reason_code("weekend_expense_restriction"):
                checks.append({
                    "valid": False,
                    "reason": "weekend_expense_restriction"
                })
        
        # Check for holiday restrictions
        if rule.get("holiday_expenses_not_allowed"):
            # In real implementation, you'd check against holiday calendar
            # For now, just a placeholder
            pass
            
    except ValueError:
        if processor.validate_reason_code("invalid_date"):
            checks.append({
                "valid": False,
                "reason": "invalid_date"
            })
    
    return checks


def validate_business_rules(value: Any, rule: Dict[str, Any], given: Dict[str, Any], processor: ReasonProcessor) -> List[Dict[str, Any]]:
    """Generic business rule validator."""
    checks = []
    
    # Currency validation
    if rule.get("currency_validation") and given.get("currency"):
        allowed_currencies = rule.get("allowed_currencies", ALLOWED_VALUES["currencies"])
        if given["currency"] not in allowed_currencies:
            if processor.validate_reason_code("invalid_currency"):
                checks.append({
                    "valid": False,
                    "reason": "invalid_currency"
                })
    
    # Receipt type validation
    if rule.get("receipt_type_validation") and given.get("receipt_type"):
        allowed_types = rule.get("allowed_receipt_types", ALLOWED_VALUES["receipt_types"])
        if allowed_types and given["receipt_type"] not in allowed_types:
            if processor.validate_reason_code("invalid_receipt_type"):
                checks.append({
                    "valid": False,
                    "reason": "invalid_receipt_type"
                })
    
    # File format validation
    if rule.get("file_format_validation") and given.get("receipt_images"):
        allowed_formats = rule.get("allowed_file_formats", ALLOWED_VALUES["file_formats"])
        if allowed_formats:
            # In real implementation, you'd validate actual file formats
            # For now, just a placeholder
            pass
    
    # Duplicate expense check
    if rule.get("duplicate_check") and given.get("amount") and given.get("recognized_at"):
        # In real implementation, you'd check against database
        # For now, just a placeholder
        pass
    
    return checks


def validate_accommodation_dates(given: Dict[str, Any], processor: ReasonProcessor) -> List[Dict[str, Any]]:
    """
    Validate accommodation dates (check-in vs check-out).
    
    Args:
        given: The input data containing check-in and check-out dates
        processor: The reason processor for validation
        
    Returns:
        List of validation checks with validity status and reason codes
    """
    checks = []
    
    try:
        from datetime import datetime
        
        check_in_str = given.get("check_in_date")
        check_out_str = given.get("check_out_date")
        
        if check_in_str and check_out_str:
            # Parse dates
            check_in_date = datetime.strptime(check_in_str, "%Y-%m-%d")
            check_out_date = datetime.strptime(check_out_str, "%Y-%m-%d")
            
            # Validate that check-out is on or after check-in
            if check_out_date < check_in_date:
                if processor.validate_reason_code("invalid_accommodation_period"):
                    checks.append({
                        "valid": False,
                        "reason": "invalid_accommodation_period"
                    })
                else:
                    checks.append({
                        "valid": False,
                        "reason": "invalid_date"
                    })
            else:
                checks.append({"valid": True, "reason": None})
                
    except ValueError:
        # If date parsing fails, add invalid date error
        if processor.validate_reason_code("invalid_date"):
            checks.append({
                "valid": False,
                "reason": "invalid_date"
            })
    
    return checks


def evaluate_rule(rule: Dict[str, Any], given: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate a rule against given input data.
    
    Args:
        rule: The rule definition from the rulebook
        given: The input data to validate
        
    Returns:
        Dict with clause_id, status (OK/NG), and standardized reasons list
    """
    standardized_reasons: List[str] = []
    ok = True

    # Check required fields
    missing_field_names = {}  # Store field display names for better error messages
    
    print(f"DEBUG: Starting validation for rule {rule.get('clause_id')}")
    print(f"DEBUG: Required fields: {rule.get('required_fields', {}).get('inputs', [])}")
    print(f"DEBUG: Given inputs: {given}")
    
    for i in rule.get("required_fields", {}).get("inputs", []):
        key = i.get("key")
        field_type = i.get("type", "string")
        required = i.get("required", False)
        allowed_values = i.get("allowed_values", [])
        
        print(f"DEBUG: Processing field {key}, required: {required}, value: {repr(given.get(key))}")
        
        # Check if field is empty (None, empty string, or default placeholder)
        field_value = given.get(key)
        is_empty = (field_value is None or 
                   field_value == "" or 
                   field_value == "(Default)" or
                   str(field_value).strip() == "")
        
        print(f"DEBUG: Field {key} is_empty: {is_empty}")
        
        if required and is_empty:
            ok = False
            # Dynamically determine the appropriate missing field reason and display name
            missing_reason, field_display_name = get_missing_field_reason(key, rule)
            print(f"DEBUG: Missing field {key} with reason {missing_reason}, display name: {field_display_name}")
            # Create unique reason code for each field to avoid conflicts
            unique_reason = f"{missing_reason}:{key}"
            standardized_reasons.append(unique_reason)
            
            # Store field display name for better error messages
            missing_field_names[unique_reason] = field_display_name
            continue
            
        # Field validation is now handled by the generic analyze_validation_rules function
        # No more hardcoded field type validation logic here

    # Check validation rules using intelligent analysis
    vr = rule.get("validation_rules", {})
    
    # Analyze validation rules to determine what should be validated
    validation_checks = analyze_validation_rules(vr, rule, given)
    
    # Apply the determined validation checks
    for check in validation_checks:
        if not check["valid"]:
            ok = False
            standardized_reasons.append(check["reason"])
    
    print(f"DEBUG: After validation - ok: {ok}, standardized_reasons: {standardized_reasons}")
    print(f"DEBUG: missing_field_names: {missing_field_names}")

    # Amount constraints are now handled by the generic analyze_validation_rules function
    # No more hardcoded amount validation logic here
    
    # All validation logic is now handled by the generic analyze_validation_rules function
    # No more hardcoded validation checks here

    # Get the reason processor
    reason_processor = get_reason_processor()
    
    # Get current date for dynamic date calculations
    from datetime import datetime, timedelta
    current_date = datetime.now()
    
    # Prepare variables for suggested fixes
    variables = {
        "amount": given.get("amount"),
        "currency": given.get("currency", "JPY"),
        "category": rule.get("expense_category", {}).get("en", "unknown"),
        "field_name": "unknown",
        "threshold": ALLOWED_VALUES["defaults"]["threshold"],
        "limit": ALLOWED_VALUES["defaults"]["limit"],
        "minimum": ALLOWED_VALUES["defaults"]["minimum"],
        "date": given.get("recognized_at"),
        "project_code": given.get("project_code"),
        "approver_name": given.get("approver"),
        "receipt_type": given.get("receipt_type"),
        "format": "unknown",
        "file_size": "unknown",
        "max_size": ALLOWED_VALUES["defaults"]["max_size"],
        "allowed_formats": ALLOWED_VALUES["file_formats"],
        "allowed_currencies": ALLOWED_VALUES["currencies"],
        "allowed_values": [],
        "allowed_receipt_types": ALLOWED_VALUES["receipt_types"],
        "allowed_approvers": ALLOWED_VALUES["approvers"],
        "submission_window": ALLOWED_VALUES["defaults"]["submission_window"],
        "current_date": current_date.strftime("%Y-%m-%d"),
        "min_date": (current_date - timedelta(days=365*5)).strftime("%Y-%m-%d"),  # 5 years ago
        "max_date": (current_date + timedelta(days=365)).strftime("%Y-%m-%d"),    # 1 year from now
        "duplicate_date": "unknown",
        "holiday_name": "unknown",
        "receipt_amount": given.get("amount"),
        "submitted_amount": given.get("amount"),
        "route": given.get("route"),
        "destination": given.get("destination"),
        "purpose": given.get("purpose"),
        "payment_details": given.get("payment_details"),
        "num_nights": given.get("num_nights"),
        "num_people": given.get("num_people"),
        "check_in_date": given.get("check_in_date"),
        "check_out_date": given.get("check_out_date")
    }
    
    # Add missing field names and context for better suggested fixes
    for reason_code, field_display_name in missing_field_names.items():
        # Extract the base reason code (remove the field-specific suffix)
        base_reason = reason_code.split(":")[0] if ":" in reason_code else reason_code
        
        # Set the field name variable
        variables["field_name"] = field_display_name
        
        # Generate meaningful context for the missing field
        field_context = generate_field_context(field_display_name, rule, variables)
        variables["field_context"] = field_context if field_context else " This field is required for proper expense validation and processing."
    

    
    # Generic rule-specific variable override system
    # Any rule-specific values automatically override defaults
    validation_rules = rule.get("validation_rules", {})
    
    # Recursively find and apply all rule-specific values
    def apply_rule_values(rules: Dict[str, Any], variables: Dict[str, Any]) -> None:
        for key, value in rules.items():
            if isinstance(value, dict):
                # Recursively process nested objects
                apply_rule_values(value, variables)
            elif isinstance(value, (int, float, str)) and value is not None:
                # Map rule keys to variable names
                key_mapping = {
                    # Amount constraints
                    "max_amount_jpy": "limit",
                    "per_person_max_amount_jpy": "threshold",
                    "per_person_min_amount_jpy": "minimum",
                    "item_unit_max_amount_jpy": "item_unit_limit",
                    "item_unit_min_amount_jpy": "item_unit_minimum",
                    
                    # Other constraints
                    "max_amount": "limit",
                    "min_amount": "minimum",
                    "submission_window_days": "submission_window",
                    "max_file_size_mb": "max_size",
                    
                    # Dynamic formulas
                    "unit_amount_jpy": "unit_amount",
                    
                    # Frequency constraints
                    "max_occurrences_per_period": "max_frequency",
                    
                    # Custom thresholds
                    "custom_threshold": "threshold"
                }
                
                # Apply the value if there's a mapping
                if key in key_mapping:
                    variable_name = key_mapping[key]
                    variables[variable_name] = value
                    
                    # Special handling for amount limits - use the most restrictive
                    if key in ["max_amount_jpy", "per_person_max_amount_jpy", "max_amount"]:
                        if "limit" not in variables or value < variables["limit"]:
                            variables["limit"] = value
    
    # Apply all rule-specific values
    apply_rule_values(validation_rules, variables)
    
    # Remove duplicates from standardized reasons to avoid duplicate suggested fixes
    unique_standardized_reasons = list(dict.fromkeys(standardized_reasons))
    
    # Generate enhanced validation results with suggested fixes - COMPLETELY GENERIC
    # The enhanced reason processor now handles field-specific reasons automatically
    enhanced_results = reason_processor.format_validation_result(unique_standardized_reasons, variables)
    
    print(f"DEBUG: Enhanced results: {enhanced_results}")

    return {
        "clause_id": rule.get("clause_id"),
        "status": "OK" if ok else "NG", 
        "reasons": unique_standardized_reasons,  # Now using standardized reasons as the main reasons
        "standardized_reasons": unique_standardized_reasons,
        "suggested_fixes": enhanced_results.get("reasons", []),
        "total_issues": enhanced_results.get("total_count", 0),
        "error_count": enhanced_results.get("error_count", 0),
        "warning_count": enhanced_results.get("warning_count", 0),
        "variables": variables  # Include variables for frontend template processing
    }


def validate_rulebook_schema(rulebook: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """
    Validate a rulebook against its JSON schema.
    
    Args:
        rulebook: The rulebook data to validate
        schema: The JSON schema to validate against
        
    Returns:
        List of validation errors (empty if valid)
    """
    try:
        import jsonschema
        jsonschema.validate(instance=rulebook, schema=schema)
        return []
    except jsonschema.exceptions.ValidationError as e:
        return [f"Schema validation error: {e.message} at {e.path}"]
    except ImportError:
        return ["jsonschema library not available for schema validation"]


def get_rule_by_id(rulebook: Dict[str, Any], clause_id: str) -> Dict[str, Any] | None:
    """
    Get a rule by its clause_id.
    
    Args:
        rulebook: The rulebook data
        clause_id: The clause ID to find
        
    Returns:
        The rule dict or None if not found
    """
    for rule in rulebook.get("rules", []):
        if rule.get("clause_id") == clause_id:
            return rule
    return None
