# Ruler - Expense Rule Validator

A FastAPI-based rule validation engine for expense submissions, implementing AIQ's validation logic against the Master rulebook with a comprehensive, generic validation system.

## Overview

Ruler is the AIQ team's implementation of the expense rule validation engine. It provides:

- **Generic Rule Validation Logic**: Metadata-driven validation system that automatically processes all rule types
- **Comprehensive Reason Taxonomy**: 35 standardized reason codes with detailed descriptions and suggested fixes
- **Dynamic Suggested Fixes**: Context-aware error messages with variable substitution
- **Demo Interface**: Interactive web interface to test validation scenarios
- **API Contract**: Clear specification for EAF to implement production APIs

## Project Structure

```
ruler/
├── ruler_server/          # FastAPI application
│   ├── main.py           # Main server and API endpoints
│   └── validator.py      # Generic validation engine
├── output_schema/         # Validation output structure
│   ├── reasons.json      # 16 standardized reason codes with taxonomy
│   ├── reasons.schema.json # JSON schema for reason validation
│   ├── reason_processor.py # Enhanced reason processor (completely generic)
│   └── README.md         # Output schema documentation
├── static/                # Demo web interface
│   └── index.html        # React + Tailwind demo page
├── expense_rulebook.json # Master rulebook (AIQ source of truth)
├── expense_rulebook.schema.json # JSON schema for validation
├── config.toml           # Server configuration
├── pyproject.toml        # Python project configuration
├── Dockerfile            # Container configuration
├── Makefile              # Development commands
├── API_CONTRACT.md       # Production API contract for EAF
└── README.md             # This file
```

## Key Features

### 🎯 **Generic Validation System**
- **Metadata-Driven**: All validation logic comes from rule definitions, no hardcoded conditions
- **Recursive Processing**: Automatically handles nested validation rules at any depth
- **Type-Agnostic**: Supports `required`, `format`, `range`, `date_validation`, `business_rule`, `field_type`, `amount_constraint`, and `accommodation_dates` types
- **Completely Generic**: No manual reason processing - everything handled dynamically by the reason processor

### 🔧 **Centralized Configuration**
- **Single Source of Truth**: All allowed values defined in one place
- **No Duplication**: Eliminates code duplication and maintenance issues
- **Easy Updates**: Change values once, updates everywhere automatically

### 📊 **Comprehensive Reason Taxonomy**
- **16 Standardized Reasons**: Consolidated and optimized reason codes covering all validation scenarios
- **Dynamic Suggested Fixes**: Context-aware error messages with variable substitution
- **Severity Levels**: Error and warning classifications
- **Variable Support**: Templates support dynamic values like amounts, dates, field names, and field contexts
- **Field-Specific Processing**: Automatically handles field-specific reason codes (e.g., `missing_field:receipt_images`)

### 🚀 **Smart Variable Override System**
- **Rule-Specific Limits**: Automatically uses rule-specific values instead of defaults
- **Most Restrictive**: For amount limits, automatically selects the most restrictive value
- **Generic Mapping**: Works with any rule structure without hardcoding

### 🧠 **Enhanced Reason Processor**
- **Completely Generic**: No manual reason processing - everything handled dynamically
- **Field-Specific Handling**: Automatically processes field-specific reason codes (e.g., `missing_field:receipt_images`)
- **Variable Substitution**: Processes both descriptions and suggested fixes with dynamic variables
- **Unified Processing**: Single method handles all reason types uniformly

## Quick Start

### Prerequisites

- Python 3.8+
- pip or uv

### Local Development

1. **Install dependencies:**
   ```bash
   make install
   ```

2. **Run the server:**
   ```bash
   make run
   ```

3. **Open demo page:**
   - Navigate to http://localhost:8810/demo
   - Test validation scenarios for different expense rules

### Docker

1. **Build image:**
   ```bash
   make docker-build
   ```

2. **Run container:**
   ```bash
   make docker-run
   ```

## API Endpoints

### Development Endpoints

- `GET /` - Welcome page
- `GET /demo` - Interactive demo interface
- `GET /rules` - List all available rules
- `GET /rules/{clause_id}/demo_options` - Get demo options for a rule
- `POST /rules/evaluate` - Evaluate a rule against inputs
- `GET /reasons` - Get full reason taxonomy
- `GET /reasons/{reason_code}` - Get specific reason information

### Production API Contract

For production implementation, see **[API_CONTRACT.md](./API_CONTRACT.md)**. This document defines:

- Request/response format
- Reason codes taxonomy
- Performance requirements
- Security specifications
- Example usage scenarios

**Note**: The production API will be implemented by EAF based on this contract.

## Validation Logic

The engine validates expense submissions against the Master rulebook using a completely generic, metadata-driven approach:

### **1. Required Field Validation**
- Automatically detects missing required fields
- Uses field metadata for intelligent error messages
- Supports nested field structures

### **2. Generic Rule Processing**
- **Amount Constraints**: `max_amount_jpy`, `per_person_max_amount_jpy`, `per_person_min_amount_jpy`
- **Dynamic Formulas**: `per_night_cap`, `per_person_cap` with variable calculations
- **Frequency Constraints**: `max_occurrences_per_period` with scope and period
- **Special Thresholds**: Custom validation rules with field mappings

### **3. Smart Variable Override**
```python
# Rule-specific values automatically override defaults
"validation_rules": {
  "amount_constraints": {
    "per_person_max_amount_jpy": 5000  # → variables["limit"] = 5000
  }
}
```

### **4. Recursive Validation**
- Processes nested validation rules at any depth
- Automatically discovers all constraint types
- No hardcoded field names or special cases

## Output Schema

### **Reason Taxonomy Structure**
```json
{
  "code": "amount_exceeds_limit",
  "label": "Amount Exceeds Limit",
  "description": "The expense amount exceeds the allowed limit for this category",
  "suggested_fix": "The amount {amount} {currency} exceeds the limit of {limit} {currency} for {category} expenses. Please reduce the amount or obtain additional approval.",
  "variables": ["amount", "currency", "limit", "category"],
  "severity": "error"
}
```

### **Variable Substitution**
- **Dynamic Values**: System automatically populates variables
- **Context-Aware**: Uses actual rule constraints and field values
- **User-Friendly**: Shows specific amounts, field names, and limits

## Development

### Available Commands

```bash
make install          # Install package in development mode
make run             # Start development server
make validate        # Validate rulebook against schema
make docker-build    # Build Docker image
make docker-run      # Run Docker container
make clean           # Clean build artifacts
```

### Configuration

Server settings are configured in `config.toml`:
- Default port: 8810
- Default host: 0.0.0.0
- Override with `HOST` and `PORT` environment variables

### **Centralized Configuration**
```python
# All allowed values defined in one place
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
```

## Contributing

1. Follow the existing code structure
2. Update the API contract if validation logic changes
3. Ensure all changes pass validation (`make validate`)
4. Test with the demo interface
5. **Use centralized configuration** for any new allowed values
6. **Follow the generic validation pattern** for new rule types

## License

Internal MoneyForward project - see project documentation for details.
