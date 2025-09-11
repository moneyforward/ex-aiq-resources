"""
FastAPI server for the Expense Rule Validator.
This server exposes validation endpoints and serves the demo interface.
"""

import os
import tomllib
from pathlib import Path
from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

from ruler_server.validator import evaluate_rule, get_rule_by_id, validate_rulebook_schema
from ruler_server.demo_utils import build_demo_options

# Configuration
CONFIG_PATH = Path("config.toml")
DEMO_DIR = Path("static")

app = FastAPI(title="Expense Rule Validator API", version="1.0.0")

# Data models
class EvaluateRequest(BaseModel):
    clause_id: str
    inputs: List[Dict[str, Any]]

class ValidationResponse(BaseModel):
    clause_id: str
    status: str  # "OK" or "NG"
    reasons: List[str]
    standardized_reasons: List[str]
    suggested_fixes: List[Dict[str, Any]]
    total_issues: int
    error_count: int
    warning_count: int

# Global rulebook data
_rulebook_data = None
_schema_data = None

def load_rulebook() -> Dict[str, Any]:
    """Load the rulebook data, caching it for performance."""
    global _rulebook_data
    if _rulebook_data is None:
        try:
            import json
            with open("expense_rulebook.json", "r", encoding="utf-8") as f:
                _rulebook_data = json.load(f)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load rulebook: {e}")
    return _rulebook_data

def load_schema() -> Dict[str, Any]:
    """Load the JSON schema, caching it for performance."""
    global _schema_data
    if _schema_data is None:
        try:
            import json
            with open("expense_rulebook.schema.json", "r", encoding="utf-8") as f:
                _schema_data = json.load(f)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load schema: {e}")
    return _schema_data

# API Endpoints

@app.get("/health")
def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "expense-rule-validator"}

@app.get("/rules")
def get_all_rules() -> List[Dict[str, Any]]:
    """Get all rules from the rulebook."""
    data = load_rulebook()
    return data.get("rules", [])

@app.get("/rules/{clause_id}")
def get_rule(clause_id: str) -> Dict[str, Any]:
    """Get a specific rule by clause_id."""
    data = load_rulebook()
    rule = get_rule_by_id(data, clause_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule

@app.get("/rules/{clause_id}/demo_options")
def demo_options(clause_id: str) -> Dict[str, Any]:
    """Get demo input options for a specific rule."""
    data = load_rulebook()
    rule = get_rule_by_id(data, clause_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    return {
        "clause_id": clause_id, 
        "options": build_demo_options(rule),
        "rule": rule  # Include the full rule data for frontend logic
    }

@app.post("/rules/evaluate", response_model=ValidationResponse)
def evaluate(req: EvaluateRequest) -> ValidationResponse:
    """Evaluate a rule against given input data."""
    data = load_rulebook()
    rule = get_rule_by_id(data, req.clause_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Convert inputs to dict format expected by validator
    given = {i["key"]: i["value"] for i in req.inputs}
    
    # Use the validator module
    result = evaluate_rule(rule, given)
    
    return ValidationResponse(
        clause_id=result["clause_id"],
        status=result["status"],
        reasons=result["reasons"],
        standardized_reasons=result.get("standardized_reasons", []),
        suggested_fixes=result.get("suggested_fixes", []),
        total_issues=result.get("total_issues", 0),
        error_count=result.get("error_count", 0),
        warning_count=result.get("warning_count", 0)
    )

@app.get("/validate-rulebook")
def validate_rulebook() -> Dict[str, Any]:
    """Validate the entire rulebook against its schema."""
    rulebook = load_rulebook()
    schema = load_schema()
    
    errors = validate_rulebook_schema(rulebook, schema)
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "rule_count": len(rulebook.get("rules", [])),
        "schema_version": schema.get("$schema", "unknown")
    }

@app.get("/reasons")
def get_reasons_taxonomy() -> Dict[str, Any]:
    """Get the complete reasons taxonomy with suggested fixes templates."""
    try:
        from output_schema.reason_processor import ReasonProcessor
        processor = ReasonProcessor()
        return {
            "taxonomy": processor.get_all_reasons(),
            "metadata": processor.reasons_data.get("metadata", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load reasons taxonomy: {e}")

@app.get("/reasons/{reason_code}")
def get_reason_info(reason_code: str) -> Dict[str, Any]:
    """Get information about a specific reason code."""
    try:
        from output_schema.reason_processor import ReasonProcessor
        processor = ReasonProcessor()
        reason_info = processor.get_reason_info(reason_code)
        if not reason_info:
            raise HTTPException(status_code=404, detail="Reason code not found")
        return reason_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get reason info: {e}")

# Demo Interface Endpoints

@app.get("/")
def index() -> HTMLResponse:
    """Serve the main demo page."""
    return HTMLResponse(
        """
        <html>
          <head><title>Expense Rule Validator Demo</title></head>
          <body>
            <h1>Expense Rule Validator Demo</h1>
            <p>Open <a href="/demo">/demo</a> for the interactive page.</p>
            <p>API documentation available at <a href="/docs">/docs</a></p>
          </body>
        </html>
        """
    )

@app.get("/demo")
def demo_page() -> FileResponse:
    """Serve the demo HTML page."""
    index_html = DEMO_DIR / "index.html"
    if not index_html.exists():
        raise HTTPException(status_code=404, detail="Demo not built")
    return FileResponse(index_html)

# Server configuration

def load_server_config() -> tuple[str, int]:
    """Load server configuration from config.toml or environment variables."""
    host = os.getenv("HOST", "0.0.0.0")
    port_env = os.getenv("PORT")
    port: int | None = int(port_env) if port_env and port_env.isdigit() else None
    
    if tomllib and CONFIG_PATH.exists():
        try:
            with CONFIG_PATH.open("rb") as f:
                cfg = tomllib.load(f)
            srv = cfg.get("server", {})
            host = str(srv.get("host", host))
            if port is None:
                p = srv.get("port")
                if isinstance(p, int):
                    port = p
        except Exception:
            pass
    
    if port is None:
        port = 8810
    
    return host, port

def run():
    """Run the server using uvicorn."""
    import uvicorn
    host, port = load_server_config()
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    run()


