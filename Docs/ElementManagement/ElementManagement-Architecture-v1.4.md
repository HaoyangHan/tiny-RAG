# Element Management Architecture v1.4

## Overview

The Element Management system provides a comprehensive framework for managing tenant-specific element templates and project elements in TinyRAG. This system supports automatic template provisioning, dual prompt architecture, and intelligent LLM-based prompt summarization.

## Architecture Components

### 1. Database Schemas

#### ElementTemplate Schema
Default templates for each tenant type that serve as blueprints for project elements.

```python
class ElementTemplate(BaseDocument):
    """
    Template definitions for elements by tenant type.
    These are default templates that get copied to projects.
    """
    name: str                           # Template name
    description: str                    # Template description  
    tenant_type: TenantType            # Associated tenant type
    task_type: TaskType                # Task processing approach
    element_type: ElementType          # Type of element (prompt, MCP, etc.)
    
    # Dual Prompt System
    generation_prompt: str             # Full detailed prompt for generation
    retrieval_prompt: Optional[str]    # Summarized prompt for retrieval
    
    # Template Configuration
    variables: List[str]               # Template variables
    execution_config: Dict[str, Any]   # LLM execution parameters
    
    # Metadata
    is_system_default: bool = True     # Created by system vs user
    version: str = "1.0.0"            # Template version
    tags: List[str]                    # Searchable tags
    
    # Status and Access
    status: ElementStatus = ElementStatus.ACTIVE
    created_by: str                    # Creator user ID
```

#### Enhanced Element Schema  
Project-specific elements created from templates or by users.

```python
class Element(BaseDocument):
    """Enhanced project element with dual prompt support."""
    
    # Basic Information (existing)
    name: str
    description: Optional[str]
    project_id: str
    tenant_type: TenantType
    task_type: TaskType
    element_type: ElementType
    
    # Dual Prompt System (NEW)
    generation_prompt: str             # Full detailed prompt
    retrieval_prompt: Optional[str]    # Summarized prompt for retrieval
    
    # Source and Type (NEW)
    is_default_element: bool = False   # Created from template vs user-created
    template_id: Optional[str] = None  # Source template ID if from template
    
    # Template Configuration
    variables: List[str]
    execution_config: Dict[str, Any]
    
    # Existing fields...
    status: ElementStatus
    tags: List[str]
    owner_id: str
```

#### TenantConfiguration Schema
Tenant-specific settings and configurations.

```python
class TenantConfiguration(BaseDocument):
    """Configuration settings for tenant types."""
    
    tenant_type: TenantType            # Tenant identifier
    display_name: str                  # Human-readable name
    description: str                   # Tenant description
    
    # Default Settings
    default_task_type: TaskType        # Default task processing
    default_llm_config: Dict[str, Any] # Default LLM settings
    
    # Template Management
    auto_provision_templates: bool = True  # Auto-copy templates to new projects
    template_count: int = 0            # Number of available templates
    
    # Customization
    allowed_element_types: List[ElementType]  # Supported element types
    custom_settings: Dict[str, Any]    # Tenant-specific settings
    
    # Status
    is_active: bool = True
    created_by: str
```

### 2. Core Services

#### ElementTemplateService
Manages element templates and automatic provisioning.

```python
class ElementTemplateService:
    """Service for managing element templates."""
    
    async def create_template(self, template_data: Dict[str, Any]) -> ElementTemplate
    async def get_templates_by_tenant(self, tenant_type: TenantType) -> List[ElementTemplate]
    async def provision_templates_to_project(self, project_id: str, tenant_type: TenantType) -> List[Element]
    async def update_template(self, template_id: str, updates: Dict[str, Any]) -> ElementTemplate
    async def delete_template(self, template_id: str) -> bool
```

#### PromptSummarizationService
Handles LLM-based prompt summarization for retrieval prompts.

```python
class PromptSummarizationService:
    """Service for generating retrieval prompts from generation prompts."""
    
    async def summarize_prompt(self, generation_prompt: str, context: Dict[str, Any]) -> str
    async def batch_summarize_prompts(self, prompts: List[str]) -> List[str]
    async def regenerate_retrieval_prompt(self, element_id: str) -> Element
```

### 3. Management Scripts

#### Enhanced Insertion Scripts
- **Template Insertion**: Insert element templates into the system
- **Project Provisioning**: Auto-copy templates when projects are created
- **Bulk Operations**: Mass template management operations

#### Removal and Cleanup Scripts
- **Element Removal**: Remove elements by script insertion tracking
- **Template Cleanup**: Clean up unused or outdated templates
- **Project Reset**: Reset project elements to default templates

## Operations and Workflows

### 1. Template Management

#### Creating Templates
```bash
# Insert all tenant templates
python scripts/element_management/insert_element_templates.py

# Insert specific tenant templates
python scripts/element_management/insert_element_templates.py --tenant hr

# Dry run mode
python scripts/element_management/insert_element_templates.py --dry-run
```

#### Managing Templates
```bash
# List all templates
python scripts/element_management/manage_templates.py list

# Update template
python scripts/element_management/manage_templates.py update --template-id <id> --field <field> --value <value>

# Remove template
python scripts/element_management/manage_templates.py remove --template-id <id>
```

### 2. Project Element Provisioning

#### Automatic Provisioning
When a new project is created, the system automatically:
1. Identifies the project's tenant type
2. Retrieves all active templates for that tenant
3. Creates project elements from each template
4. Generates retrieval prompts using LLM summarization
5. Sets `is_default_element=True` and links to template

#### Manual Provisioning
```bash
# Provision templates to existing project
python scripts/element_management/provision_project.py --project-id <id>

# Provision specific templates
python scripts/element_management/provision_project.py --project-id <id> --template-ids <id1,id2>
```

### 3. Prompt Management

#### Dual Prompt System
- **Generation Prompt**: Full, detailed prompt with complete context and instructions
- **Retrieval Prompt**: Concise, LLM-summarized version optimized for retrieval and indexing

#### LLM Summarization
```bash
# Generate retrieval prompts for all elements missing them
python scripts/element_management/generate_retrieval_prompts.py

# Regenerate retrieval prompts for specific elements
python scripts/element_management/generate_retrieval_prompts.py --element-ids <id1,id2>

# Batch process by tenant
python scripts/element_management/generate_retrieval_prompts.py --tenant hr
```

### 4. Cleanup and Removal

#### Script-Inserted Element Removal
```bash
# Remove all script-inserted elements
python scripts/element_management/remove_script_elements.py

# Remove by tenant type
python scripts/element_management/remove_script_elements.py --tenant hr

# Remove by insertion batch
python scripts/element_management/remove_script_elements.py --batch-id <id>
```

#### Template Cleanup
```bash
# Remove unused templates
python scripts/element_management/cleanup_templates.py --unused

# Remove outdated versions
python scripts/element_management/cleanup_templates.py --outdated

# Archive old templates
python scripts/element_management/cleanup_templates.py --archive
```

## Configuration and Settings

### Environment Variables
```bash
# LLM Configuration for Summarization
SUMMARIZATION_LLM_PROVIDER=openai
SUMMARIZATION_LLM_MODEL=gpt-4o-mini
SUMMARIZATION_LLM_TEMPERATURE=0.3
SUMMARIZATION_LLM_MAX_TOKENS=500

# Element Management Settings
AUTO_PROVISION_TEMPLATES=true
ENABLE_RETRIEVAL_PROMPT_GENERATION=true
DEFAULT_TEMPLATE_VERSION=1.0.0
```

### Configuration Files
- `config/element_templates.yaml`: Template definitions
- `config/tenant_settings.yaml`: Tenant-specific configurations  
- `config/summarization_prompts.yaml`: LLM summarization prompts

## API Endpoints

### Template Management API
```python
# GET /api/v1/element-templates/
# GET /api/v1/element-templates/{tenant_type}
# POST /api/v1/element-templates/
# PUT /api/v1/element-templates/{template_id}
# DELETE /api/v1/element-templates/{template_id}
```

### Element Management API
```python
# POST /api/v1/elements/{element_id}/regenerate-retrieval-prompt
# POST /api/v1/projects/{project_id}/provision-templates
# GET /api/v1/elements/by-source/{template_id}
```

## Monitoring and Analytics

### Metrics Tracked
- Template usage statistics
- Element creation patterns
- Prompt summarization performance
- Project provisioning success rates

### Logging
- Template creation and updates
- Element provisioning operations
- LLM summarization requests
- Error tracking and debugging

## Best Practices

### Template Design
1. **Clear Naming**: Use descriptive, consistent naming conventions
2. **Variable Definition**: Clearly define all template variables
3. **Version Control**: Maintain template versions for tracking changes
4. **Testing**: Validate templates before deployment

### Prompt Engineering
1. **Generation Prompts**: Include complete context and detailed instructions
2. **Retrieval Prompts**: Focus on key concepts and searchable terms
3. **Variable Usage**: Design flexible prompts with clear variable substitution
4. **Performance**: Balance detail with LLM token limits

### System Management
1. **Regular Cleanup**: Periodically remove unused templates and elements
2. **Monitoring**: Track template usage and element performance
3. **Backup**: Maintain backups of template configurations
4. **Documentation**: Keep template documentation updated

## Security Considerations

### Access Control
- Template creation requires admin privileges
- Element management respects project permissions
- LLM summarization uses secure API calls

### Data Protection
- Sensitive data handling in prompts
- Audit trails for template modifications
- Secure storage of API keys and configurations

## Future Enhancements

### Planned Features
- Template versioning and rollback
- A/B testing for prompt effectiveness
- Automated template optimization
- Multi-language template support
- Template sharing between tenants 