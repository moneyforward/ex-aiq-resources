# Expense Rule Validation API Contract

**Version:** 1.0  
**Last Updated:** 2024-01-XX  
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
  "reasons": ["string"]
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

Reason codes follow the format `category:detail` to provide structured error information.

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
  "reasons": ["missing:route"]
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
  "reasons": ["amount:exceeds_max"]
}
```

## Performance Requirements

- **Latency**: P95 response time ≤ 150ms
- **Throughput**: Handle concurrent requests efficiently
- **Availability**: 99.9% uptime

## Security Requirements

- **Authentication**: JWT-based authentication required
- **Authorization**: Validate user permissions for expense categories
- **Input Validation**: Sanitize and validate all input fields
- **Rate Limiting**: Implement appropriate rate limiting

## Monitoring & Observability

EAF should implement:
- Request/response logging with `clause_id` tracking
- Performance metrics (latency, throughput, error rates)
- Audit logging for compliance requirements
- Health check endpoints

## Future Enhancements

This contract will be extended in future phases to include:
- Confidence scoring and selective abstention
- Detailed reason codes with suggested fixes
- Rule classification and risk assessment
- Caching and optimization strategies

## Contact

For questions about this API contract, contact the AIQ team.
