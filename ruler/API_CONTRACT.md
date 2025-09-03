# Expense Rule Validation API Contract

**Version:** 1.0  
**Last Updated:** 2025-09-03  
**Team:** AIQ (AI Quality Assurance)  
**Purpose:** Production API contract for EAF implementation

## Overview

This document defines the contract for the Expense Rule Validation API that EAF will implement in production. The API validates expense submissions against the Master rulebook and returns structured validation results with clear references to specific rule clauses.

## Base URL

```
POST /api/v1/expense/validate
```

## Request Format

### Request Body

```json
{
  "clause_id": "string",
  "inputs": [
    {
      "key": "string",
      "value": "any"
    }
  ]
}
```

#### Field Descriptions

- **`clause_id`** (required): Unique identifier from the Master rulebook (e.g., "TRAVEL_001")
- **`inputs`** (required): Array of key-value pairs representing the expense data
  - **`key`**: Field identifier (e.g., "amount", "receipt_images", "destination")
  - **`value`**: Field value (string, number, boolean, array, or null)

#### Common Input Keys

| Key | Type | Description | Example |
|-----|------|-------------|---------|
| `amount` | number | Expense amount in JPY | `5000` |
| `receipt_images` | array | Array of receipt file references | `["receipt1.jpg", "receipt2.jpg"]` |
| `invoice_registration_number` | string | Qualified invoice issuer number | `"T1234567890123"` |
| `destination` | string | Travel destination | `"Tokyo"` |
| `purpose` | string | Business purpose | `"Client meeting"` |
| `route` | string | Travel route | `"Shinjuku → Shibuya"` |

## Response Format

### Success Response (200 OK)

```json
{
  "clause_id": "string",
  "status": "OK" | "NG",
  "reasons": ["string"],
  "standardized_reasons": ["string"],
  "suggested_fixes": [
    {
      "code": "string",
      "label": "string",
      "description": "string",
      "severity": "error" | "warning",
      "suggested_fix": "string",
      "required_variables": ["string"]
    }
  ],
  "total_issues": "number",
  "error_count": "number",
  "warning_count": "number",
  "variables": "object"
}
```

#### Field Descriptions

- **`clause_id`** (required): The Master rulebook clause ID that was validated
- **`status`** (required): Validation result
  - `"OK"`: All validation rules passed
  - `"NG"`: One or more validation rules failed
- **`reasons`** (required): Array of reason codes explaining the result
  - Empty array `[]` for `"OK"` status
  - One or more reason codes for `"NG"` status
- **`standardized_reasons`** (required): Array of standardized reason codes (same as reasons for now)
- **`suggested_fixes`** (required): Array of detailed fix information with labels, descriptions, and suggested fixes
- **`total_issues`** (required): Total number of validation issues found
- **`error_count`** (required): Number of error-level issues
- **`warning_count`** (required): Number of warning-level issues
- **`variables`** (required): Context variables used for validation (amounts, dates, field names, etc.)

### Error Responses

#### 400 Bad Request
```json
{
  "detail": "Invalid request format"
}
```

#### 404 Not Found
```json
{
  "detail": "Rule not found"
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Reason Codes

The system uses 16 standardized reason codes that cover all validation scenarios. Reason codes can be:

- **Base codes**: Direct reason codes (e.g., `missing_field`, `amount_exceeds_limit`)
- **Field-specific codes**: Extended with field names (e.g., `missing_field:receipt_images`, `missing_field:pre_approval_id`)

### Standardized Reason Codes

| Code | Severity | Description |
|------|----------|-------------|
| `missing_field` | Error | Required field is missing |
| `amount_exceeds_limit` | Error | Amount exceeds allowed limit |
| `amount_below_minimum` | Error | Amount below required minimum |
| `invalid_date` | Error | Date format or value is invalid |
| `invalid_accommodation_period` | Error | Check-out date is before check-in date |
| `duplicate_expense` | Warning | Duplicate expense detected |
| `invalid_currency` | Error | Currency not allowed for this category |
| `invalid_receipt_type` | Error | Receipt type not allowed |
| `invalid_payment_method` | Error | Payment method not allowed |
| `file_format_not_allowed` | Error | File format not supported |
| `file_size_exceeds_limit` | Error | File size exceeds maximum allowed |
| `invalid_business_rule` | Error | Business rule violation |
| `frequency_limit_exceeded` | Warning | Frequency limit exceeded |
| `invalid_field_format` | Error | Field format is invalid |
| `invalid_field_value` | Error | Field value is not allowed |
| `missing_approval` | Error | Required approval is missing |

### Missing Field Errors
- `missing:{field_name}` - Required field is missing or empty
  - Example: `"missing:amount"`, `"missing:receipt_images"`

### Amount Validation Errors
- `amount:exceeds_max` - Amount exceeds maximum limit
- `amount:exceeds_per_person_max` - Amount exceeds per-person maximum
- `amount:below_min_exclusive` - Amount below minimum threshold

### Receipt/Invoice Errors
- `missing:receipt_images` - Receipt images required but not provided
- `missing:invoice_registration_number` - Invoice number required but not provided

## Validation Rules

The API applies the following validation rules based on the Master rulebook:

1. **Required Fields**: All fields marked as `required: true` must be present and non-empty
2. **Receipt Requirements**: If `receipt_required: true`, receipt images must be provided
3. **Invoice Requirements**: If `invoice_number_required: true`, invoice registration number must be provided
4. **Amount Constraints**: Amount must be within specified min/max limits
5. **Per-Person Limits**: Amount must not exceed per-person maximums

## Example Usage

### Valid Travel Expense
```json
POST /api/v1/expense/validate
{
  "clause_id": "TRAVEL_001",
  "inputs": [
    {"key": "amount", "value": 1500},
    {"key": "route", "value": "Shinjuku → Shibuya"},
    {"key": "purpose", "value": "Client meeting"}
  ]
}
```

**Response:**
```json
{
  "clause_id": "TRAVEL_001",
  "status": "OK",
  "reasons": []
}
```

### Invalid Travel Expense (Missing Required Field)
```json
POST /api/v1/expense/validate
{
  "clause_id": "TRAVEL_001",
  "inputs": [
    {"key": "amount", "value": 1500}
    // Missing required "route" field
  ]
}
```

**Response:**
```json
{
  "clause_id": "TRAVEL_001",
  "status": "NG",
  "reasons": ["missing_field:route"],
  "standardized_reasons": ["missing_field:route"],
  "suggested_fixes": [
    {
      "code": "missing_field:route",
      "label": "Missing Required Field: Route",
      "description": "A required field (route) is missing from the expense submission for category (Domestic Travel). Context: This field is required for proper expense validation and processing.",
      "severity": "error",
      "suggested_fix": "Please provide the route field. This field is required for Domestic Travel expenses. This field is required for proper expense validation and processing.",
      "required_variables": ["field_name", "category", "field_context"]
    }
  ],
  "total_issues": 1,
  "error_count": 1,
  "warning_count": 0,
  "variables": {
    "field_name": "route",
    "category": "Domestic Travel",
    "field_context": "This field is required for proper expense validation and processing."
  }
}
```

### Amount Exceeds Limit
```json
POST /api/v1/expense/validate
{
  "clause_id": "TRAVEL_002",
  "inputs": [
    {"key": "amount", "value": 50000},
    {"key": "destination", "value": "Osaka"},
    {"key": "receipt_images", "value": ["receipt.jpg"]}
  ]
}
```

**Response:**
```json
{
  "clause_id": "TRAVEL_002",
  "status": "NG",
  "reasons": ["amount_exceeds_limit"],
  "standardized_reasons": ["amount_exceeds_limit"],
  "suggested_fixes": [
    {
      "code": "amount_exceeds_limit",
      "label": "Amount Exceeds Limit",
      "description": "The expense amount (50000 JPY) exceeds the allowed limit (30000 JPY) for this category (Domestic Travel)",
      "severity": "error",
      "suggested_fix": "The amount 50000 JPY exceeds the limit of 30000 JPY for Domestic Travel expenses. Please reduce the amount or obtain additional approval.",
      "required_variables": ["amount", "currency", "limit", "category"]
    }
  ],
  "total_issues": 1,
  "error_count": 1,
  "warning_count": 0,
  "variables": {
    "amount": 50000,
    "currency": "JPY",
    "limit": 30000,
    "category": "Domestic Travel"
  }
}
```

### Hotel Accommodation Validation
```json
POST /api/v1/expense/validate
{
  "clause_id": "HOTEL_001",
  "inputs": [
    {"key": "amount", "value": 15000},
    {"key": "hotel_name", "value": "Tokyo Grand Hotel"},
    {"key": "check_in_date", "value": "2025-01-20"},
    {"key": "check_out_date", "value": "2025-01-15"},
    {"key": "num_guests", "value": 2}
  ]
}
```

**Response:**
```json
{
  "clause_id": "HOTEL_001",
  "status": "NG",
  "reasons": ["invalid_accommodation_period"],
  "standardized_reasons": ["invalid_accommodation_period"],
  "suggested_fixes": [
    {
      "code": "invalid_accommodation_period",
      "label": "Invalid Accommodation Period",
      "description": "The accommodation period is invalid: check-out date (2025-01-15) must be after check-in date (2025-01-20)",
      "severity": "error",
      "suggested_fix": "The check-out date 2025-01-15 must be after the check-in date 2025-01-20. Please provide valid accommodation dates.",
      "required_variables": ["check_out_date", "check_in_date"]
    }
  ],
  "total_issues": 1,
  "error_count": 1,
  "warning_count": 0,
  "variables": {
    "check_in_date": "2025-01-20",
    "check_out_date": "2025-01-15"
  }
}
```

## Contact

For questions about this API contract, contact the AIQ team.
