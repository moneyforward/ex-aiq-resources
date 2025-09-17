"""
Reason Processor Module

This module provides utilities for processing expense rule validation reasons
and generating suggested fixes with variable substitution.
"""

import json
from typing import Dict, List, Optional, Any
from pathlib import Path


class ReasonProcessor:
    """Processes expense rule validation reasons and generates suggested fixes."""
    
    def __init__(self, reasons_file_path: Optional[str] = None):
        """
        Initialize the ReasonProcessor.
        
        Args:
            reasons_file_path: Path to the reasons.json file. 
                             If None, uses default path in output_schema directory.
        """
        if reasons_file_path is None:
            # Get the directory where this file is located
            current_dir = Path(__file__).parent
            reasons_file_path = current_dir / "reasons.json"
        
        self.reasons_file_path = Path(reasons_file_path)
        self.reasons_data = self._load_reasons()
    
    def _load_reasons(self) -> Dict[str, Any]:
        """Load the reasons data from the JSON file."""
        try:
            with open(self.reasons_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Reasons file not found: {self.reasons_file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in reasons file: {e}")
    
    def get_reason_info(self, reason_code: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific reason code.
        
        Args:
            reason_code: The reason code to look up
            
        Returns:
            Dictionary containing reason information or None if not found
        """
        # Handle field-specific reason codes (e.g., "missing_field:receipt_images")
        if ":" in reason_code:
            base_reason = reason_code.split(":")[0]
            return self.reasons_data.get("reason_taxonomy", {}).get(base_reason)
        
        return self.reasons_data.get("reason_taxonomy", {}).get(reason_code)
    
    def get_all_reasons(self) -> Dict[str, Any]:
        """
        Get all reasons from the taxonomy.
        
        Returns:
            Dictionary containing all reasons
        """
        return self.reasons_data.get("reason_taxonomy", {})
    
    def generate_suggested_fix(self, reason_code: str, variables: Dict[str, Any]) -> Optional[str]:
        """
        Generate a suggested fix by substituting variables in the template.
        
        Args:
            reason_code: The reason code to generate fix for
            variables: Dictionary of variable names and values to substitute
            
        Returns:
            Generated suggested fix string or None if reason not found
        """
        reason_info = self.get_reason_info(reason_code)
        if not reason_info:
            return None
        
        template = reason_info.get("suggested_fix", "")
        if not template:
            return None
        
        try:
            # Substitute variables in the template
            return template.format(**variables)
        except KeyError:
            # If a required variable is missing, return the template as-is
            return template
    
    def get_reason_severity(self, reason_code: str) -> Optional[str]:
        """
        Get the severity level for a reason code.
        
        Args:
            reason_code: The reason code to look up
            
        Returns:
            Severity level ('error' or 'warning') or None if not found
        """
        reason_info = self.get_reason_info(reason_code)
        return reason_info.get("severity") if reason_info else None
    
    def get_reasons_by_severity(self, severity: str) -> List[str]:
        """
        Get all reason codes for a specific severity level.
        
        Args:
            severity: Severity level ('error' or 'warning')
            
        Returns:
            List of reason codes with the specified severity
        """
        reasons = self.get_all_reasons()
        return [
            code for code, info in reasons.items() 
            if info.get("severity") == severity
        ]
    
    def validate_reason_code(self, reason_code: str) -> bool:
        """
        Check if a reason code exists in the taxonomy.
        
        Args:
            reason_code: The reason code to validate
            
        Returns:
            True if the reason code exists, False otherwise
        """
        # Handle field-specific reason codes (e.g., "missing_field:receipt_images")
        if ":" in reason_code:
            base_reason = reason_code.split(":")[0]
            return base_reason in self.get_all_reasons()
        
        return reason_code in self.get_all_reasons()
    
    def get_required_variables(self, reason_code: str) -> List[str]:
        """
        Get the list of required variables for a reason code.
        
        Args:
            reason_code: The reason code to look up
            
        Returns:
            List of required variable names or empty list if not found
        """
        reason_info = self.get_reason_info(reason_code)
        return reason_info.get("variables", []) if reason_info else []
    
    def format_validation_result(self, reason_codes: List[str], 
                                variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format validation results with reasons and suggested fixes.
        TRULY GENERIC - handles field-specific reasons automatically.
        
        Args:
            reason_codes: List of reason codes from validation
            variables: Dictionary of variables for substitution
            
        Returns:
            Dictionary with formatted validation results
        """
        results = []
        
        for reason_code in reason_codes:
            # Create variables specific to this reason
            reason_variables = variables.copy()
            
            # Handle field-specific reasons by setting field-specific variables
            if ":" in reason_code:
                field_name = reason_code.split(":", 1)[1]
                reason_variables["field_name"] = field_name
                
                # Generate field-specific context if not already provided
                if "field_context" not in reason_variables:
                    # Try to create a meaningful context
                    reason_variables["field_context"] = " This field is required for proper expense validation and processing."
            
            # Get the base reason info (handle field-specific codes)
            base_reason = reason_code.split(":")[0] if ":" in reason_code else reason_code
            reason_info = self.get_reason_info(base_reason)
            
            if reason_info:
                # Generate suggested fix with reason-specific variables
                suggested_fix = self.generate_suggested_fix(base_reason, reason_variables)
                
                # Process description with reason-specific variables
                description = reason_info.get("description", "")
                if description and reason_variables:
                    try:
                        description = description.format(**reason_variables)
                    except (KeyError, ValueError):
                        # If variable substitution fails, keep original description
                        pass
                
                results.append({
                    "code": reason_code,
                    "label": reason_info.get("label", ""),
                    "description": description,
                    "severity": reason_info.get("severity", "error"),
                    "suggested_fix": suggested_fix,
                    "required_variables": reason_info.get("variables", [])
                })
        
        return {
            "reasons": results,
            "total_count": len(results),
            "error_count": len([r for r in results if r["severity"] == "error"]),
            "warning_count": len([r for r in results if r["severity"] == "warning"])
        }
    
    def reload_reasons(self):
        """Reload the reasons data from the file."""
        self.reasons_data = self._load_reasons()


# Convenience functions for common operations
def get_reason_processor() -> ReasonProcessor:
    """Get a default ReasonProcessor instance."""
    return ReasonProcessor()


def generate_fix(reason_code: str, variables: Dict[str, Any]) -> Optional[str]:
    """
    Generate a suggested fix for a reason code.
    
    Args:
        reason_code: The reason code
        variables: Variables for substitution
        
    Returns:
        Generated suggested fix or None
    """
    processor = get_reason_processor()
    return processor.generate_suggested_fix(reason_code, variables)


def format_reasons(reason_codes: List[str], variables: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a list of reason codes with suggested fixes.
    
    Args:
        reason_codes: List of reason codes
        variables: Variables for substitution
        
    Returns:
        Formatted validation results
    """
    processor = get_reason_processor()
    return processor.format_validation_result(reason_codes, variables)


if __name__ == "__main__":
    # Example usage
    processor = ReasonProcessor()
    
    # Example: Generate a suggested fix
    variables = {
        "field_name": "receipt_images",
        "category": "TRAVEL",
        "amount": 5000,
        "currency": "JPY",
        "threshold": 1000
    }
    
    fix = processor.generate_suggested_fix("missing_receipt_images", variables)
    print(f"Suggested fix: {fix}")
    
    # Example: Format validation results
    reason_codes = ["missing_receipt_images", "missing_pre_approval"]
    results = processor.format_validation_result(reason_codes, variables)
    print(f"Validation results: {json.dumps(results, indent=2)}")
