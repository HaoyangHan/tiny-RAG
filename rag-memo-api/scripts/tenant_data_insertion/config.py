"""
Configuration for tenant-specific element insertion scripts.

This module contains all configuration settings for connecting to MongoDB
and setting up default values for element insertion.
"""

import os
from typing import Dict, Any
from models.enums import TenantType

# Database Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "tinyrag")

# Default User and Project Configuration
DEFAULT_USER_ID = "6859036f0cfc8f1bb0f21c76"  # Test user from memories

# Default Project IDs for each tenant type
# You should update these with actual project IDs from your database
DEFAULT_PROJECT_IDS: Dict[TenantType, str] = {
    TenantType.HR: "60f4d2e5e8b4a12345678901",  # Example HR project ID
    TenantType.CODING: "60f4d2e5e8b4a12345678902",  # Example coding project ID
    TenantType.FINANCIAL_REPORT: "685e40b69bf4ff7e5e03c1ad",  # Real financial project ID (test1)
    TenantType.DEEP_RESEARCH: "60f4d2e5e8b4a12345678904",  # Example research project ID
    TenantType.QA_GENERATION: "60f4d2e5e8b4a12345678905",  # Example QA project ID
    TenantType.RAW_RAG: "60f4d2e5e8b4a12345678906",  # Example raw RAG project ID
}

# LLM Configuration for element templates
DEFAULT_LLM_CONFIG: Dict[str, Any] = {
    "temperature": 0.7,
    "max_tokens": 2000,
    "model": "gpt-4o-mini"
}

# Element Insertion Settings
DRY_RUN = False  # Set to True to test without actually inserting
LOG_LEVEL = "INFO"
CHECK_DUPLICATES = True  # Check for duplicate element names before inserting

# Element Tags Configuration
COMMON_TAGS = ["manual", "predefined", "v1.4"]

# Tenant-specific tag prefixes
TENANT_TAG_PREFIXES: Dict[TenantType, str] = {
    TenantType.HR: "hr",
    TenantType.CODING: "dev",
    TenantType.FINANCIAL_REPORT: "finance",
    TenantType.DEEP_RESEARCH: "research",
    TenantType.QA_GENERATION: "qa",
    TenantType.RAW_RAG: "rag",
}

# Logging Configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": LOG_LEVEL,
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": LOG_LEVEL,
            "propagate": False
        }
    }
} 