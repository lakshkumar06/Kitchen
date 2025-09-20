"""JSON schemas for validation and API communication"""

from typing import Dict, Any

# JSON Schema for enhanced prompt structure used by Gemini API
ENHANCED_PROMPT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "enhanced_description": {
            "type": "string",
            "description": "Cleaned and clarified description of the user's request"
        },
        "project_context": {
            "type": "string",
            "description": "Context about the project and its requirements"
        },
        "technical_requirements": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of technical requirements extracted from the prompt"
        },
        "backend_tasks": {
            "type": "array",
            "items": {"$ref": "#/definitions/task"},
            "description": "Tasks to be assigned to backend engineers"
        },
        "frontend_tasks": {
            "type": "array",
            "items": {"$ref": "#/definitions/task"},
            "description": "Tasks to be assigned to frontend engineers"
        },
        "cross_cutting_concerns": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Concerns that affect multiple components"
        },
        "success_criteria": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Criteria for overall project success"
        },
        "estimated_timeline": {
            "type": "integer",
            "minimum": 1,
            "description": "Estimated completion time in hours"
        },
        "complexity_score": {
            "type": "integer",
            "minimum": 1,
            "maximum": 10,
            "description": "Complexity rating from 1-10"
        }
    },
    "required": [
        "enhanced_description",
        "project_context",
        "technical_requirements",
        "success_criteria",
        "complexity_score"
    ],
    "definitions": {
        "task": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Task title"
                },
                "description": {
                    "type": "string",
                    "description": "Detailed task description"
                },
                "task_type": {
                    "type": "string",
                    "enum": [
                        "backend_api",
                        "backend_database",
                        "backend_auth",
                        "backend_logic",
                        "frontend_ui",
                        "frontend_component",
                        "frontend_styling",
                        "frontend_integration"
                    ]
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "default": "medium"
                },
                "boundaries": {
                    "$ref": "#/definitions/task_boundary"
                },
                "goals": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/executable_goal"},
                    "minItems": 1
                }
            },
            "required": ["title", "description", "task_type", "boundaries", "goals"]
        },
        "task_boundary": {
            "type": "object",
            "properties": {
                "scope": {
                    "type": "string",
                    "description": "What the task should accomplish"
                },
                "constraints": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Limitations and restrictions"
                },
                "dependencies": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Required dependencies"
                },
                "deliverables": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Expected outputs"
                },
                "acceptance_criteria": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Criteria for task completion"
                }
            },
            "required": ["scope", "deliverables", "acceptance_criteria"]
        },
        "executable_goal": {
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "Goal description"
                },
                "success_metrics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "How to measure success"
                },
                "estimated_time": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Estimated time in minutes"
                },
                "is_critical": {
                    "type": "boolean",
                    "default": false,
                    "description": "Whether this goal is critical for task completion"
                }
            },
            "required": ["description", "success_metrics"]
        }
    }
}

# Schema for agent communication messages
AGENT_MESSAGE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "message_id": {
            "type": "string",
            "description": "Unique message identifier"
        },
        "sender_id": {
            "type": "string",
            "description": "ID of the sending agent"
        },
        "recipient_id": {
            "type": "string",
            "description": "ID of the receiving agent"
        },
        "message_type": {
            "type": "string",
            "enum": [
                "task_assignment",
                "task_completion",
                "task_status_update",
                "error_report",
                "coordination_request",
                "information_request"
            ]
        },
        "payload": {
            "type": "object",
            "description": "Message payload specific to message type"
        },
        "timestamp": {
            "type": "string",
            "format": "date-time",
            "description": "Message timestamp"
        },
        "priority": {
            "type": "string",
            "enum": ["low", "medium", "high", "urgent"],
            "default": "medium"
        }
    },
    "required": ["message_id", "sender_id", "recipient_id", "message_type", "payload", "timestamp"]
}

# Schema for task results
TASK_RESULT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "task_id": {
            "type": "string",
            "description": "Task identifier"
        },
        "status": {
            "type": "string",
            "enum": ["completed", "failed", "blocked"]
        },
        "output": {
            "type": "string",
            "description": "Task output or result"
        },
        "errors": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Any errors encountered"
        },
        "execution_time": {
            "type": "integer",
            "minimum": 0,
            "description": "Execution time in seconds"
        },
        "completed_goals": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Successfully completed goals"
        },
        "failed_goals": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Failed goals"
        },
        "agent_notes": {
            "type": "string",
            "description": "Notes from the executing agent"
        }
    },
    "required": ["task_id", "status"]
}

# Gemini API prompt template for processing user input
GEMINI_PROMPT_TEMPLATE = """
You are a technical project manager AI that specializes in breaking down user requests into structured, executable tasks for software development teams.

Your job is to:
1. Clean and clarify the user's request
2. Extract technical requirements
3. Identify project context and constraints
4. Break down the work into specific tasks for backend and frontend engineers
5. Set clear boundaries and success criteria

User Request: {user_prompt}

Please analyze this request and provide a structured response in the following JSON format:

{{
  "enhanced_description": "A clear, detailed description of what the user wants to accomplish",
  "project_context": "Background information about the project, technology stack, and constraints",
  "technical_requirements": ["List of specific technical requirements"],
  "backend_tasks": [
    {{
      "title": "Task title",
      "description": "Detailed description of what needs to be done",
      "task_type": "backend_api|backend_database|backend_auth|backend_logic",
      "priority": "low|medium|high|critical",
      "boundaries": {{
        "scope": "What this task should accomplish",
        "constraints": ["Any limitations or restrictions"],
        "dependencies": ["Required dependencies or prerequisites"],
        "deliverables": ["Expected outputs"],
        "acceptance_criteria": ["How to verify completion"]
      }},
      "goals": [
        {{
          "description": "Specific goal within the task",
          "success_metrics": ["How to measure success"],
          "estimated_time": 60,
          "is_critical": true
        }}
      ]
    }}
  ],
  "frontend_tasks": [
    {{
      "title": "Task title",
      "description": "Detailed description of what needs to be done",
      "task_type": "frontend_ui|frontend_component|frontend_styling|frontend_integration",
      "priority": "low|medium|high|critical",
      "boundaries": {{
        "scope": "What this task should accomplish",
        "constraints": ["Any limitations or restrictions"],
        "dependencies": ["Required dependencies or prerequisites"],
        "deliverables": ["Expected outputs"],
        "acceptance_criteria": ["How to verify completion"]
      }},
      "goals": [
        {{
          "description": "Specific goal within the task",
          "success_metrics": ["How to measure success"],
          "estimated_time": 60,
          "is_critical": false
        }}
      ]
    }}
  ],
  "cross_cutting_concerns": ["Issues that affect multiple components"],
  "success_criteria": ["Overall criteria for project success"],
  "estimated_timeline": 8,
  "complexity_score": 5
}}

Guidelines:
- Be specific and actionable in task descriptions
- Ensure tasks are independent where possible
- Consider dependencies between backend and frontend work
- Set realistic time estimates
- Include proper error handling and testing considerations
- Focus on deliverable outcomes

Provide only the JSON response, no additional text.
"""

def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """
    Basic JSON schema validation
    In production, use jsonschema library for complete validation
    """
    try:
        # Basic validation - check required fields exist
        if 'required' in schema:
            for field in schema['required']:
                if field not in data:
                    return False

        # Basic type checking for top-level fields
        if 'properties' in schema:
            for field, field_schema in schema['properties'].items():
                if field in data:
                    field_type = field_schema.get('type')
                    if field_type == 'string' and not isinstance(data[field], str):
                        return False
                    elif field_type == 'integer' and not isinstance(data[field], int):
                        return False
                    elif field_type == 'array' and not isinstance(data[field], list):
                        return False
                    elif field_type == 'object' and not isinstance(data[field], dict):
                        return False

        return True
    except Exception:
        return False