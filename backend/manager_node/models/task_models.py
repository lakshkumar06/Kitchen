"""Task and prompt models for AI agent orchestration"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator


class TaskPriority(str, Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskType(str, Enum):
    """Types of tasks that can be assigned"""
    BACKEND_API = "backend_api"
    BACKEND_DATABASE = "backend_database"
    BACKEND_AUTH = "backend_auth"
    BACKEND_LOGIC = "backend_logic"
    FRONTEND_UI = "frontend_ui"
    FRONTEND_COMPONENT = "frontend_component"
    FRONTEND_STYLING = "frontend_styling"
    FRONTEND_INTEGRATION = "frontend_integration"


class UserPrompt(BaseModel):
    """Raw user input prompt"""
    content: str = Field(..., description="Original user prompt")
    timestamp: datetime = Field(default_factory=datetime.now)
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")

    @validator('content')
    def content_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()


class TaskBoundary(BaseModel):
    """Defines boundaries and constraints for a task"""
    scope: str = Field(..., description="What the task should accomplish")
    constraints: List[str] = Field(default_factory=list, description="Limitations and restrictions")
    dependencies: List[str] = Field(default_factory=list, description="Required dependencies")
    deliverables: List[str] = Field(..., description="Expected outputs")
    acceptance_criteria: List[str] = Field(..., description="Criteria for task completion")


class ExecutableGoal(BaseModel):
    """Specific, measurable goal within a task"""
    description: str = Field(..., description="Goal description")
    success_metrics: List[str] = Field(..., description="How to measure success")
    estimated_time: Optional[int] = Field(None, description="Estimated time in minutes")
    is_critical: bool = Field(False, description="Whether this goal is critical for task completion")


class AgentTask(BaseModel):
    """Task assigned to a specific agent"""
    task_id: str = Field(..., description="Unique task identifier")
    task_type: TaskType = Field(..., description="Type of task")
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Detailed task description")
    boundaries: TaskBoundary = Field(..., description="Task boundaries and constraints")
    goals: List[ExecutableGoal] = Field(..., description="Executable goals")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Task priority")
    status: TaskStatus = Field(TaskStatus.PENDING, description="Current status")
    assigned_agent: Optional[str] = Field(None, description="Agent assigned to this task")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    due_date: Optional[datetime] = Field(None, description="Task deadline")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional task metadata")


class EnhancedPrompt(BaseModel):
    """Cleaned and structured prompt with role assignments"""
    original_prompt: UserPrompt = Field(..., description="Original user input")
    enhanced_description: str = Field(..., description="Cleaned and clarified description")
    project_context: str = Field(..., description="Project context and background")
    technical_requirements: List[str] = Field(..., description="Technical requirements extracted")
    backend_tasks: List[AgentTask] = Field(default_factory=list, description="Tasks for backend agents")
    frontend_tasks: List[AgentTask] = Field(default_factory=list, description="Tasks for frontend agents")
    cross_cutting_concerns: List[str] = Field(default_factory=list, description="Concerns affecting multiple agents")
    success_criteria: List[str] = Field(..., description="Overall success criteria")
    estimated_timeline: Optional[int] = Field(None, description="Estimated completion time in hours")
    complexity_score: int = Field(..., ge=1, le=10, description="Complexity rating 1-10")
    created_at: datetime = Field(default_factory=datetime.now)


class TaskResult(BaseModel):
    """Result of a completed task"""
    task_id: str = Field(..., description="Task identifier")
    status: TaskStatus = Field(..., description="Final status")
    output: Optional[str] = Field(None, description="Task output/result")
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")
    execution_time: Optional[int] = Field(None, description="Execution time in seconds")
    completed_goals: List[str] = Field(default_factory=list, description="Successfully completed goals")
    failed_goals: List[str] = Field(default_factory=list, description="Failed goals")
    agent_notes: Optional[str] = Field(None, description="Notes from the executing agent")
    completed_at: datetime = Field(default_factory=datetime.now)


class ProjectSession(BaseModel):
    """Overall project session tracking multiple related tasks"""
    session_id: str = Field(..., description="Unique session identifier")
    enhanced_prompt: EnhancedPrompt = Field(..., description="The enhanced prompt for this session")
    all_tasks: List[AgentTask] = Field(default_factory=list, description="All tasks in this session")
    completed_tasks: List[TaskResult] = Field(default_factory=list, description="Completed task results")
    session_status: TaskStatus = Field(TaskStatus.PENDING, description="Overall session status")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def update_timestamp(self):
        """Update the last modified timestamp"""
        self.updated_at = datetime.now()

    def get_pending_tasks(self) -> List[AgentTask]:
        """Get all pending tasks"""
        return [task for task in self.all_tasks if task.status == TaskStatus.PENDING]

    def get_tasks_by_type(self, task_type: TaskType) -> List[AgentTask]:
        """Get tasks by type"""
        return [task for task in self.all_tasks if task.task_type == task_type]