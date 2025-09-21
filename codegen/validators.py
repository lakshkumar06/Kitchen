"""Specification validators"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field, validator


class EntitySpec(BaseModel):
    """Entity specification validator"""
    name: str = Field(..., min_length=1, max_length=50)
    fields: Dict[str, str] = Field(..., min_items=1)

    @validator('name')
    def validate_name(cls, v):
        """Validate entity name"""
        if not v.isidentifier():
            raise ValueError("Entity name must be a valid Python identifier")
        if v[0].islower():
            raise ValueError("Entity name should start with uppercase letter")
        return v

    @validator('fields')
    def validate_fields(cls, v):
        """Validate entity fields"""
        valid_types = {'str', 'string', 'int', 'integer', 'bool', 'boolean', 'text', 'float'}

        for field_name, field_type in v.items():
            if not field_name.isidentifier():
                raise ValueError(f"Field name '{field_name}' must be a valid Python identifier")
            if field_type.lower() not in valid_types:
                raise ValueError(f"Field type '{field_type}' not supported. Valid types: {valid_types}")

        return v


class ProjectSpec(BaseModel):
    """Complete project specification validator"""
    project_name: str = Field(..., min_length=1, max_length=100)
    entities: List[EntitySpec] = Field(..., min_items=1)

    @validator('project_name')
    def validate_project_name(cls, v):
        """Validate project name"""
        # Remove special characters and make it a valid identifier
        cleaned = ''.join(c for c in v if c.isalnum() or c in ' _-')
        if not cleaned:
            raise ValueError("Project name must contain alphanumeric characters")
        return cleaned

    @validator('entities')
    def validate_unique_entities(cls, v):
        """Ensure entity names are unique"""
        names = [entity.name for entity in v]
        if len(names) != len(set(names)):
            raise ValueError("Entity names must be unique")
        return v


class SpecValidator:
    """Validates project specifications"""

    @staticmethod
    def validate_project_spec(spec_data: Dict[str, Any]) -> ProjectSpec:
        """Validate and return project specification"""
        try:
            return ProjectSpec(**spec_data)
        except Exception as e:
            raise ValueError(f"Invalid project specification: {str(e)}")

    @staticmethod
    def validate_manager_output(manager_output: Dict[str, Any]) -> bool:
        """Validate manager output structure"""
        required_fields = {
            'backend_engineer_prompt': {
                'role', 'domain_description', 'project_context',
                'required_technologies', 'code_requirements',
                'core_deliverables', 'integration_requirements', 'constraints'
            },
            'frontend_engineer_prompt': {
                'role', 'domain_description', 'project_context',
                'required_technologies', 'code_requirements',
                'core_deliverables', 'api_integration_requirements', 'constraints'
            }
        }

        for prompt_type, fields in required_fields.items():
            if prompt_type not in manager_output:
                raise ValueError(f"Missing {prompt_type} in manager output")

            prompt = manager_output[prompt_type]
            missing_fields = fields - set(prompt.keys())
            if missing_fields:
                raise ValueError(f"Missing fields in {prompt_type}: {missing_fields}")

        return True

    @staticmethod
    def extract_entities_from_prompts(backend_prompt: Dict[str, Any], frontend_prompt: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract entity specifications from manager prompts"""
        # This is a simplified extraction - in practice, you might want to
        # parse the prompts more intelligently to extract entity information
        entities = []

        # Look for entity mentions in deliverables
        backend_deliverables = backend_prompt.get('core_deliverables', [])
        for deliverable in backend_deliverables:
            if 'model' in deliverable.lower() or 'entity' in deliverable.lower():
                # Extract entity name (simplified)
                words = deliverable.split()
                for word in words:
                    if word.isalpha() and word[0].isupper() and len(word) > 2:
                        entities.append({
                            'name': word,
                            'fields': {
                                'id': 'int',
                                'name': 'str',
                                'description': 'text'
                            }
                        })
                        break

        # If no entities found, create a default one
        if not entities:
            project_context = backend_prompt.get('project_context', '')
            project_name = 'Item'  # Default name

            # Try to extract from project context
            if 'user' in project_context.lower():
                project_name = 'User'
            elif 'product' in project_context.lower():
                project_name = 'Product'
            elif 'task' in project_context.lower():
                project_name = 'Task'

            entities.append({
                'name': project_name,
                'fields': {
                    'id': 'int',
                    'name': 'str',
                    'description': 'text',
                    'created_at': 'str'
                }
            })

        return entities


# Global validator instance
spec_validator = SpecValidator()