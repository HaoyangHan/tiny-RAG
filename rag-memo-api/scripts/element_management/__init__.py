"""
Element Management Scripts Package for TinyRAG v1.4.

This package contains scripts and utilities for managing element templates
and automatic provisioning in the TinyRAG system.
"""

from pathlib import Path

# Package metadata
__version__ = "1.4.0"
__description__ = "Element Management Scripts for TinyRAG"
__author__ = "TinyRAG Team"

# Script paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent

# Available scripts
AVAILABLE_SCRIPTS = {
    "insert_element_templates": "Insert element templates into database",
    "remove_script_elements": "Remove elements inserted by scripts",
    "generate_retrieval_prompts": "Generate retrieval prompts for elements",
    "provision_project": "Provision templates to existing projects",
    "manage_templates": "Manage existing templates",
    "system_status": "Check system health and statistics"
}

def get_script_path(script_name: str) -> Path:
    """Get the full path to a script."""
    return SCRIPT_DIR / f"{script_name}.py"

def list_available_scripts() -> dict:
    """List all available scripts with descriptions."""
    return AVAILABLE_SCRIPTS.copy()

__all__ = [
    "__version__",
    "__description__", 
    "__author__",
    "SCRIPT_DIR",
    "PROJECT_ROOT",
    "AVAILABLE_SCRIPTS",
    "get_script_path",
    "list_available_scripts"
] 