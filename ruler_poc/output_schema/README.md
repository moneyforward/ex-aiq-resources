# Output Schema for Expense Rule Validation

This directory contains the structured output schema for expense rule validation, including a comprehensive reason taxonomy and suggested fixes system.

## Overview

The output schema provides a systematic way to:
- Return validation reasons with consistent codes
- Generate human-readable suggested fixes
- Handle variable substitution in fix templates
- Categorize issues by severity (error vs warning)

## Files

### `reasons.json`
The main reason taxonomy file containing:
- **Reason codes**: Unique identifiers for each validation issue
- **Labels**: Human-readable names for each reason
- **Descriptions**: Detailed explanations of what each reason means
- **Suggested fixes**: Templates with variable placeholders
- **Variables**: List of required variables for each fix template
- **Severity**: Whether the issue is an error or warning

### `reasons.schema.json`
JSON Schema for validating the structure of `reasons.json`.

### `reason_processor.py`
Python utility module for:
- Loading and processing reasons
- Generating suggested fixes with variable substitution
- Formatting validation results
- Managing reason taxonomy

## Usage

### Basic Usage

```python
from output_schema.reason_processor import ReasonProcessor

# Initialize processor
processor = ReasonProcessor()

# Generate a suggested fix
variables = {
    "field_name": "receipt_images",
    "category": "TRAVEL",
    "amount": 5000,
    "currency": "JPY",
    "threshold": 1000
}

fix = processor.generate_suggested_fix("missing_receipt_images", variables)
# Result: "Please upload receipt images for the expense amount of 5000 JPY. 
#         Receipts are required for all expenses above 1000 JPY."
```

### Formatting Validation Results

```python
# Format multiple reasons with fixes
reason_codes = ["missing_receipt_images", "missing_pre_approval"]
results = processor.format_validation_result(reason_codes, variables)

# Results will include:
# - Individual reason details
# - Generated suggested fixes
# - Severity levels
# - Counts by severity
```

### Convenience Functions

```python
from output_schema.reason_processor import generate_fix, format_reasons

# Quick fix generation
fix = generate_fix("missing_field", {"field_name": "amount", "category": "SUPPLIES"})

# Quick result formatting
results = format_reasons(["missing_field"], {"field_name": "amount", "category": "SUPPLIES"})
```

## Reason Code Structure

Each reason follows this structure:

```json
{
  "code": "missing_receipt_images",
  "label": "Missing Receipt Images",
  "description": "Receipt images are required but not provided",
  "suggested_fix": "Please upload receipt images for the expense amount of {amount} {currency}. Receipts are required for all expenses above {threshold} {currency}.",
  "variables": ["amount", "currency", "threshold"],
  "severity": "error"
}
```

## Variable Substitution

The suggested fix templates use Python string formatting with named variables:

- `{amount}` - Expense amount
- `{currency}` - Currency code
- `{category}` - Expense category
- `{threshold}` - Limit/threshold value
- `{field_name}` - Field name
- And many more...

## Adding New Reasons

To add a new reason:

1. Add the reason to `reasons.json` following the existing pattern
2. Include all required fields: `code`, `label`, `description`, `suggested_fix`, `variables`, `severity`
3. Use appropriate variable placeholders in the suggested fix
4. Update the `total_reasons` count in metadata

## Integration with Validation Engine

The reason processor can be integrated with your validation engine to:

1. **Map validation failures to reason codes**: Convert internal validation logic to standardized reason codes
2. **Collect context variables**: Gather relevant values (amount, category, etc.) for variable substitution
3. **Generate user-friendly messages**: Use the processor to create helpful suggested fixes
4. **Categorize issues**: Separate errors from warnings for different handling

## Example Integration

```python
def validate_expense(expense_data):
    errors = []
    warnings = []
    
    # Your validation logic here
    if not expense_data.get('receipt_images'):
        errors.append("missing_receipt_images")
    
    if expense_data.get('amount', 0) > 10000:
        warnings.append("amount_exceeds_limit")
    
    # Generate formatted results
    variables = {
        "amount": expense_data.get('amount'),
        "currency": expense_data.get('currency'),
        "category": expense_data.get('category'),
        "threshold": 10000
    }
    
    return {
        "status": "ERROR" if errors else "OK",
        "reasons": errors + warnings,
        "formatted_results": processor.format_validation_result(errors + warnings, variables)
    }
```

## Benefits

1. **Consistency**: All validation messages follow the same format
2. **Localization Ready**: Easy to translate labels and descriptions
3. **Maintainable**: Centralized reason management
4. **User-Friendly**: Clear, actionable suggested fixes
5. **Extensible**: Easy to add new reasons and categories
6. **Structured**: Machine-readable format for API responses

## Schema Validation

The `reasons.schema.json` ensures data integrity. You can validate your reasons file using:

```bash
# Using jsonschema CLI tool
jsonschema -i reasons.json reasons.schema.json
```

## Versioning

The schema includes version information in metadata. When making breaking changes:

1. Increment the version number
2. Update the `last_updated` date
3. Document changes in the description
4. Ensure backward compatibility or provide migration paths
