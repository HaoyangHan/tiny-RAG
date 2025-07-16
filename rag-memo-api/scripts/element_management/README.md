# Element Management System - TinyRAG v1.4.2

This directory contains the comprehensive Element Management System for TinyRAG, providing automated template provisioning, dual prompt architecture, and intelligent element management with **simplified, essential-only models**.

## 🌟 Key Features

- **📝 Element Templates**: Pre-defined templates for automatic project provisioning
- **🔄 Dual Prompt System**: Generation prompts for detailed context, retrieval prompts for search optimization
- **🤖 LLM Summarization**: Automatic generation of retrieval prompts using AI
- **🎯 Smart Provisioning**: Automatic template deployment to new projects
- **🗑️ Safe Removal**: Tracked removal of script-inserted elements
- **⚡ Simplified Architecture**: Essential-only attributes, no over-engineering

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

## 📊 System Architecture (Simplified v1.4.2)

### Database Schemas (Essential Only)

#### **ElementTemplate** 
**Core Fields:**
- `name`, `description`, `tenant_type`, `element_type`, `task_type`
- `generation_prompt`, `retrieval_prompt` (dual prompt system)
- `variables`, `execution_config`
- `version`, `tags`, `status`
- `is_system_default`, `created_by`

#### **Element** (Enhanced)
**Core Fields:**
- `name`, `description`, `project_id`, `tenant_type`, `element_type`, `task_type`
- `template` (ElementContent with dual prompts)
- `is_default_element`, `template_id`, `insertion_batch_id` (tracking)
- `tags`, `status`, `owner_id`

#### **TenantConfiguration** 
**Core Fields:**
- `tenant_type`, `display_name`, `description`
- `default_task_type`, `default_llm_config`
- `auto_provision_templates`, `allowed_element_types`
- `is_active`, `created_by`

### Services
- **ElementTemplateService**: Template management and provisioning
- **PromptSummarizationService**: LLM-based prompt generation

### Key Features
- **Dual Prompt Architecture**: Separate prompts for generation and retrieval
- **Template Tracking**: Links between templates and created elements
- **Batch Management**: Tracked insertion/removal operations
- **Auto-Provisioning**: Automatic template deployment to projects

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

## 📖 Documentation

For detailed documentation, see:
- **[V1.4.2 Final Architecture](../../Docs/ElementManagement/V1.4.2-Final-Architecture.md)**: Complete system design
- **[Element Generation Flow](../../Docs/ElementManagement/Element-Generation-Flow.md)**: Generation workflow
- **[Tenant-Project Relations](../../Docs/ElementManagement/Tenant-Project-Relations.md)**: Relationship mappings
- **[Operations Guide](../../Docs/ElementManagement/ElementManagement-Operations-Guide.md)**: Detailed operations

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

## 🏗️ Architecture Principles (v1.4.2)

### Simplified Design Philosophy
- **Essential Only**: No over-engineered analytics or complex tracking
- **Clear Relationships**: Simple tenant → project → element hierarchy
- **Dual Prompt Focus**: Generation vs retrieval prompt optimization
- **Safe Operations**: Batch tracking for all script operations
- **Legacy Compatible**: Preserves existing functionality

### Database Design
- **Minimal Attributes**: Only essential fields for core functionality
- **Proper Indexing**: Optimized for common query patterns
- **Clear Relationships**: Template → Element tracking with batch IDs
- **Version Control**: Simple semantic versioning without complex changelogs

## 🤝 Contributing

When adding new functionality:
1. Follow the **essential-only** principle - avoid over-engineering
2. Maintain clear relationships between models
3. Add comprehensive tests for new features
4. Update documentation with examples
5. Ensure backward compatibility with legacy scripts

## 📜 Legacy Support

The legacy tenant insertion scripts are preserved for backward compatibility:
- All existing `tenant_*_elements.py` scripts continue to work
- Legacy configuration in `config.py` is maintained
- Existing insertion batch tracking is preserved
- Clear migration path to new simplified system

---

**v1.4.2 Focus**: Essential-only architecture with dual prompt system, template provisioning, and safe script management. Ready for v1.4.3 development! 