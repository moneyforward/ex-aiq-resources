"""
Pure validation logic for expense rules.
This module contains the core validation functions without any server/demo dependencies.
"""

from typing import Dict, Any, List


def evaluate_rule(rule: Dict[str, Any], given: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate a rule against given input data.
    
    Args:
        rule: The rule definition from the rulebook
        given: The input data to validate
        
    Returns:
        Dict with clause_id, status (OK/NG), and reasons list
    """
    reasons: List[str] = []
    ok = True

    # Check required fields
    for i in rule.get("required_fields", {}).get("inputs", []):
        key = i.get("key")
        field_type = i.get("type", "string")
        required = i.get("required", False)
        allowed_values = i.get("allowed_values", [])
        
        if required and (given.get(key) in (None, "")):
            ok = False
            reasons.append(f"missing:{key}")
            continue
            
        # Validate field values based on type
        if key in given and given[key] not in (None, ""):
            value = given[key]
            
            # Validate enum fields
            if field_type == "enum" and allowed_values and value not in allowed_values:
                ok = False
                reasons.append(f"invalid_enum:{key}={value}")
            
            # Validate currency
            elif key == "currency" and value not in ["JPY", "USD", "EUR"]:
                ok = False
                reasons.append(f"invalid_currency:{value}")
            
            # Validate date format (basic check)
            elif field_type == "date" and isinstance(value, str):
                try:
                    from datetime import datetime
                    datetime.strptime(value, "%Y-%m-%d")
                except ValueError:
                    ok = False
                    reasons.append(f"invalid_date_format:{key}={value}")
            
            # Validate amount ranges (reasonable limits)
            elif field_type == "money" and isinstance(value, (int, float)):
                if value <= 0:
                    ok = False
                    reasons.append(f"invalid_amount:{key}={value}_must_be_positive")
                elif value > 1000000:  # 1M JPY reasonable limit
                    ok = False
                    reasons.append(f"amount_suspiciously_high:{key}={value}")
            
            # Validate integer fields
            elif field_type == "integer" and isinstance(value, (int, float)):
                if value <= 0:
                    ok = False
                    reasons.append(f"invalid_integer:{key}={value}_must_be_positive")
                elif key in ["num_nights", "num_people"] and value > 100:
                    ok = False
                    reasons.append(f"integer_unreasonably_high:{key}={value}")

    # Check validation rules
    vr = rule.get("validation_rules", {})
    
    # Receipt validation
    if vr.get("receipt_required") is True and not given.get("receipt_images"):
        ok = False
        reasons.append("missing:receipt_images")

    # Invoice validation
    inv = vr.get("invoice_number_required")
    if inv is True and not given.get("invoice_registration_number"):
        ok = False
        reasons.append("missing:invoice_registration_number")

    # Amount constraints
    amt = vr.get("amount_constraints", {})
    amount = given.get("amount")
    if isinstance(amount, (int, float)):
        if amt.get("max_amount_jpy") is not None and amount > amt["max_amount_jpy"]:
            ok = False
            reasons.append("amount:exceeds_max")
        if amt.get("per_person_max_amount_jpy") is not None and amount > amt["per_person_max_amount_jpy"]:
            ok = False
            reasons.append("amount:exceeds_per_person_max")
        if amt.get("per_person_min_amount_jpy") is not None and amt.get("per_person_min_exclusive") and amount <= amt["per_person_min_amount_jpy"]:
            ok = False
            reasons.append("amount:below_min_exclusive")

    return {
        "clause_id": rule.get("clause_id"),
        "status": "OK" if ok else "NG", 
        "reasons": reasons
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
