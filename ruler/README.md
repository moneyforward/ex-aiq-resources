# Ruler - Expense Rule Validator

A FastAPI-based rule validation engine for expense submissions, implementing AIQ's validation logic against the Master rulebook.

## Overview

Ruler is the AIQ team's implementation of the expense rule validation engine. It provides:

- **Rule Validation Logic**: Core validation rules based on the Master rulebook
- **Demo Interface**: Interactive web interface to test validation scenarios
- **API Contract**: Clear specification for EAF to implement production APIs

## Project Structure

```
ruler/
├── ruler_server/          # FastAPI application
│   ├── main.py           # Main server and validation logic
│   └── __init__.py       # Package initialization
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

### Production API Contract

For production implementation, see **[API_CONTRACT.md](./API_CONTRACT.md)**. This document defines:

- Request/response format
- Reason codes taxonomy
- Performance requirements
- Security specifications
- Example usage scenarios

**Note**: The production API will be implemented by EAF based on this contract.

## Validation Logic

The engine validates expense submissions against the Master rulebook using:

1. **Required Field Validation**: Ensures all mandatory fields are present
2. **Receipt Requirements**: Validates receipt image requirements
3. **Invoice Validation**: Checks qualified invoice issuer numbers
4. **Amount Constraints**: Enforces min/max amount limits
5. **Per-Person Limits**: Validates per-person maximum amounts

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

## Team Responsibilities

### AIQ (This Project)
- ✅ Rule validation logic and business rules
- ✅ Master rulebook integration
- ✅ API contract design
- ✅ Reason codes taxonomy
- ✅ Demo and testing interface

### EAF (Production Implementation)
- ✅ Production API deployment
- ✅ Performance optimization
- ✅ Security and authentication
- ✅ Monitoring and observability
- ✅ Caching and scaling

## Contributing

1. Follow the existing code structure
2. Update the API contract if validation logic changes
3. Ensure all changes pass validation (`make validate`)
4. Test with the demo interface

## License

Internal MoneyForward project - see project documentation for details.
