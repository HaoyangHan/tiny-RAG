# Element Management System - TinyRAG v1.4

This directory contains the comprehensive Element Management System for TinyRAG, providing automated template provisioning, dual prompt architecture, and intelligent element management.

## 🌟 Key Features

- **📝 Element Templates**: Pre-defined templates for automatic project provisioning
- **🔄 Dual Prompt System**: Generation prompts for detailed context, retrieval prompts for search optimization
- **🤖 LLM Summarization**: Automatic generation of retrieval prompts using AI
- **🎯 Smart Provisioning**: Automatic template deployment to new projects
- **🗑️ Safe Removal**: Tracked removal of script-inserted elements
- **📊 Analytics**: Template usage tracking and performance metrics

## 📁 Directory Structure

### Core Scripts
- **`insert_element_templates.py`** - Insert element templates into database
- **`remove_script_elements.py`** - Remove script-inserted elements safely
- **`generate_retrieval_prompts.py`** - Generate retrieval prompts using LLM
- **`provision_project.py`** - Provision templates to existing projects

### Legacy Scripts (Preserved for Compatibility)
- **`base_inserter.py`** - Base functionality for legacy scripts
- **`config.py`** - Legacy configuration and environment setup
- **`tenant_*_elements.py`** - Legacy tenant-specific insertion scripts
- **`insert_all.py`** - Legacy script to run all tenant insertions

## 🚀 Quick Start

### Prerequisites

1. **Start TinyRAG Services**:
   ```bash
   cd ../.. && docker-compose up -d
   ```

2. **Environment Setup**:
   ```bash
   export MONGODB_URL="mongodb://localhost:27017"
   export SUMMARIZATION_LLM_PROVIDER="openai"
   export SUMMARIZATION_LLM_MODEL="gpt-4o-mini"
   export OPENAI_API_KEY="your-api-key"
   ```

### Basic Operations

#### 1. Insert Element Templates
```bash
# Dry run - see what would be inserted
python insert_element_templates.py --dry-run

# Insert all tenant templates
python insert_element_templates.py

# Insert templates for specific tenant
python insert_element_templates.py --tenant hr

# Force update existing templates
python insert_element_templates.py --force-update
```

#### 2. Provision Templates to Projects
```bash
# Dry run for project provisioning
python provision_project.py --project-id PROJECT_ID --dry-run

# Provision all templates to project
python provision_project.py --project-id PROJECT_ID

# Provision with custom prefix
python provision_project.py --project-id PROJECT_ID --prefix "Custom_"
```

#### 3. Generate Retrieval Prompts
```bash
# Generate for all elements missing retrieval prompts
python generate_retrieval_prompts.py

# Generate for specific tenant
python generate_retrieval_prompts.py --tenant hr

# Regenerate all (overwrite existing)
python generate_retrieval_prompts.py --regenerate-all
```

#### 4. Remove Script Elements
```bash
# List all script-inserted elements
python remove_script_elements.py --list

# Dry run removal
python remove_script_elements.py --dry-run

# Remove all script-inserted elements
python remove_script_elements.py --force

# Remove by tenant
python remove_script_elements.py --tenant hr --force
```

## 🔧 Advanced Usage

### Template Management
```bash
# Insert specific tenant templates with custom settings
python insert_element_templates.py --tenant coding --force-update --debug

# Provision multiple projects with batch tracking
for project in proj1 proj2 proj3; do
  python provision_project.py --project-id $project --prefix "Batch_"
done
```

### Prompt Optimization
```bash
# Generate retrieval prompts with custom batch size
python generate_retrieval_prompts.py --batch-size 10 --show-progress

# Validate prompt quality for specific element
python generate_retrieval_prompts.py --validate ELEMENT_ID

# Process specific elements only
python generate_retrieval_prompts.py --element-ids id1,id2,id3
```

### Cleanup Operations
```bash
# Remove elements from specific batch
python remove_script_elements.py --batch-id batch_20241201_143022 --force

# Remove default elements from project
python remove_script_elements.py --project-id PROJECT_ID --default-only --force

# Dry run with detailed output
python remove_script_elements.py --dry-run --debug
```

## 📊 System Architecture

### Database Schemas
- **ElementTemplate**: Default templates for tenant types
- **Element** (Enhanced): Project elements with dual prompt support
- **TenantConfiguration**: Tenant-specific settings and analytics

### Services
- **ElementTemplateService**: Template management and provisioning
- **PromptSummarizationService**: LLM-based prompt generation
- **Element Management APIs**: RESTful template management

### Key Features
- **Dual Prompt Architecture**: Separate prompts for generation and retrieval
- **Template Tracking**: Links between templates and created elements
- **Batch Management**: Tracked insertion/removal operations
- **Auto-Provisioning**: Automatic template deployment to projects
- **Usage Analytics**: Template performance and usage metrics

## 🛡️ Safety Features

### Data Protection
- **Dry-run Mode**: Test operations without making changes
- **Batch Tracking**: All script operations are tracked for safe removal
- **Duplicate Prevention**: Prevents duplicate templates and elements
- **Validation**: Comprehensive data validation before insertion
- **Rollback Support**: Safe removal of script-inserted data

### Error Handling
- **Graceful Failures**: Operations continue despite individual failures
- **Detailed Logging**: Comprehensive logging for debugging
- **Progress Tracking**: Real-time progress updates for long operations
- **Recovery Options**: Tools to recover from partial failures

## 📈 Monitoring & Analytics

### Usage Tracking
- Template usage counts and success rates
- Element creation and performance metrics
- Project provisioning statistics
- LLM summarization performance

### Health Checks
```bash
# Check template system health
python -c "
from services.element_template_service import get_template_service
import asyncio
async def check():
    service = get_template_service()
    # Add health check logic
asyncio.run(check())
"
```

## 🔧 Configuration

### Environment Variables
```bash
# Database Configuration
MONGODB_URL="mongodb://localhost:27017"
MONGODB_DATABASE="tinyrag"

# LLM Configuration for Summarization
SUMMARIZATION_LLM_PROVIDER="openai"
SUMMARIZATION_LLM_MODEL="gpt-4o-mini"
SUMMARIZATION_LLM_TEMPERATURE="0.3"
SUMMARIZATION_LLM_MAX_TOKENS="500"

# Element Management Settings
AUTO_PROVISION_TEMPLATES="true"
ENABLE_RETRIEVAL_PROMPT_GENERATION="true"
DEFAULT_TEMPLATE_VERSION="1.0.0"
```

### Template Customization
Templates can be customized by:
1. Modifying template definitions in `insert_element_templates.py`
2. Creating tenant-specific template files
3. Using the template management API
4. Importing templates from configuration files

## 📖 Documentation

For detailed documentation, see:
- **[Architecture Guide](../../Docs/ElementManagement/ElementManagement-Architecture-v1.4.md)**: System design and components
- **[Operations Guide](../../Docs/ElementManagement/ElementManagement-Operations-Guide.md)**: Detailed operations and troubleshooting
- **[API Documentation](../../Docs/TinyRAG-v1.4-API-Documentation.md)**: REST API endpoints

## 🐛 Troubleshooting

### Common Issues

1. **Templates Not Appearing in Projects**
   ```bash
   # Check if templates exist
   python insert_element_templates.py --tenant hr --dry-run
   
   # Force provision templates
   python provision_project.py --project-id PROJECT_ID --force
   ```

2. **Retrieval Prompt Generation Failing**
   ```bash
   # Check LLM configuration
   echo $OPENAI_API_KEY
   
   # Test with debug mode
   python generate_retrieval_prompts.py --debug
   ```

3. **Element Removal Not Working**
   ```bash
   # List script elements first
   python remove_script_elements.py --list
   
   # Use force removal with debug
   python remove_script_elements.py --force --debug
   ```

### Debug Mode
Enable detailed logging for all scripts:
```bash
export LOG_LEVEL=DEBUG
python script_name.py --debug
```

## 🤝 Contributing

When adding new functionality:
1. Follow the existing patterns for error handling and logging
2. Add comprehensive tests for new features
3. Update documentation and examples
4. Ensure backward compatibility with legacy scripts

## 📜 Legacy Support

The legacy tenant insertion scripts are preserved for backward compatibility:
- All existing `tenant_*_elements.py` scripts continue to work
- Legacy configuration in `config.py` is maintained
- Existing insertion batch tracking is preserved
- Migration path provided for upgrading to new system 