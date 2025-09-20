"""Agent models and role definitions for AI orchestration"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field, validator

from .task_models import TaskType, TaskStatus, AgentTask


class AgentRole(str, Enum):
    """Available agent roles in the system"""
    MANAGER = "manager"
    BACKEND_ENGINEER = "backend_engineer"
    FRONTEND_ENGINEER = "frontend_engineer"


class AgentStatus(str, Enum):
    """Agent availability status"""
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"


class AgentCapability(BaseModel):
    """Specific capability of an agent"""
    name: str = Field(..., description="Capability name")
    description: str = Field(..., description="Capability description")
    proficiency_level: int = Field(..., ge=1, le=5, description="Proficiency level 1-5")
    supported_task_types: List[TaskType] = Field(..., description="Task types this capability supports")


class AgentProfile(BaseModel):
    """Complete profile of an agent including capabilities and constraints"""
    role: AgentRole = Field(..., description="Agent's primary role")
    specializations: List[str] = Field(default_factory=list, description="Areas of specialization")
    capabilities: List[AgentCapability] = Field(..., description="Agent capabilities")
    max_concurrent_tasks: int = Field(3, ge=1, description="Maximum concurrent tasks")
    preferred_task_types: List[TaskType] = Field(..., description="Preferred task types")
    constraints: List[str] = Field(default_factory=list, description="Agent limitations")
    communication_style: str = Field("professional", description="Communication preferences")


class BackendEngineerProfile(AgentProfile):
    """Specialized profile for backend engineer agents"""
    role: AgentRole = Field(AgentRole.BACKEND_ENGINEER, const=True)
    preferred_task_types: List[TaskType] = Field(
        default=[
            TaskType.BACKEND_API,
            TaskType.BACKEND_DATABASE,
            TaskType.BACKEND_AUTH,
            TaskType.BACKEND_LOGIC
        ]
    )

    def __init__(self, **data):
        super().__init__(**data)
        if not self.capabilities:
            self.capabilities = [
                AgentCapability(
                    name="API Development",
                    description="RESTful API design and implementation",
                    proficiency_level=5,
                    supported_task_types=[TaskType.BACKEND_API]
                ),
                AgentCapability(
                    name="Database Design",
                    description="Database schema design and optimization",
                    proficiency_level=4,
                    supported_task_types=[TaskType.BACKEND_DATABASE]
                ),
                AgentCapability(
                    name="Authentication Systems",
                    description="User authentication and authorization",
                    proficiency_level=4,
                    supported_task_types=[TaskType.BACKEND_AUTH]
                ),
                AgentCapability(
                    name="Business Logic",
                    description="Core application logic implementation",
                    proficiency_level=5,
                    supported_task_types=[TaskType.BACKEND_LOGIC]
                )
            ]


class FrontendEngineerProfile(AgentProfile):
    """Specialized profile for frontend engineer agents"""
    role: AgentRole = Field(AgentRole.FRONTEND_ENGINEER, const=True)
    preferred_task_types: List[TaskType] = Field(
        default=[
            TaskType.FRONTEND_UI,
            TaskType.FRONTEND_COMPONENT,
            TaskType.FRONTEND_STYLING,
            TaskType.FRONTEND_INTEGRATION
        ]
    )

    def __init__(self, **data):
        super().__init__(**data)
        if not self.capabilities:
            self.capabilities = [
                AgentCapability(
                    name="UI Development",
                    description="User interface design and implementation",
                    proficiency_level=5,
                    supported_task_types=[TaskType.FRONTEND_UI]
                ),
                AgentCapability(
                    name="Component Architecture",
                    description="Reusable component design and development",
                    proficiency_level=5,
                    supported_task_types=[TaskType.FRONTEND_COMPONENT]
                ),
                AgentCapability(
                    name="Styling and Design",
                    description="CSS, responsive design, and styling systems",
                    proficiency_level=4,
                    supported_task_types=[TaskType.FRONTEND_STYLING]
                ),
                AgentCapability(
                    name="API Integration",
                    description="Frontend-backend integration and state management",
                    proficiency_level=4,
                    supported_task_types=[TaskType.FRONTEND_INTEGRATION]
                )
            ]


class Agent(BaseModel):
    """Active agent instance in the system"""
    agent_id: str = Field(..., description="Unique agent identifier")
    profile: AgentProfile = Field(..., description="Agent profile and capabilities")
    status: AgentStatus = Field(AgentStatus.AVAILABLE, description="Current status")
    current_tasks: List[str] = Field(default_factory=list, description="Currently assigned task IDs")
    completed_tasks_count: int = Field(0, description="Total completed tasks")
    average_completion_time: Optional[float] = Field(None, description="Average task completion time in minutes")
    success_rate: float = Field(1.0, ge=0.0, le=1.0, description="Task success rate")
    last_active: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, any] = Field(default_factory=dict, description="Additional agent metadata")

    @validator('current_tasks')
    def validate_task_limit(cls, v, values):
        if 'profile' in values and len(v) > values['profile'].max_concurrent_tasks:
            raise ValueError(f"Cannot exceed max concurrent tasks limit")
        return v

    def can_handle_task(self, task: AgentTask) -> bool:
        """Check if agent can handle a specific task"""
        if self.status != AgentStatus.AVAILABLE:
            return False

        if len(self.current_tasks) >= self.profile.max_concurrent_tasks:
            return False

        # Check if agent has capability for this task type
        for capability in self.profile.capabilities:
            if task.task_type in capability.supported_task_types:
                return True

        return False

    def assign_task(self, task_id: str) -> bool:
        """Assign a task to this agent"""
        if len(self.current_tasks) >= self.profile.max_concurrent_tasks:
            return False

        self.current_tasks.append(task_id)
        if len(self.current_tasks) >= self.profile.max_concurrent_tasks:
            self.status = AgentStatus.BUSY

        self.last_active = datetime.now()
        return True

    def complete_task(self, task_id: str, success: bool = True) -> bool:
        """Mark a task as completed"""
        if task_id not in self.current_tasks:
            return False

        self.current_tasks.remove(task_id)
        self.completed_tasks_count += 1

        # Update success rate
        if success:
            self.success_rate = (
                (self.success_rate * (self.completed_tasks_count - 1) + 1.0) /
                self.completed_tasks_count
            )
        else:
            self.success_rate = (
                (self.success_rate * (self.completed_tasks_count - 1)) /
                self.completed_tasks_count
            )

        # Update status if no longer at capacity
        if len(self.current_tasks) < self.profile.max_concurrent_tasks:
            self.status = AgentStatus.AVAILABLE

        self.last_active = datetime.now()
        return True

    def get_workload_score(self) -> float:
        """Calculate current workload as a score (0.0 = available, 1.0 = at capacity)"""
        return len(self.current_tasks) / self.profile.max_concurrent_tasks


class AgentPool(BaseModel):
    """Pool of available agents"""
    agents: Dict[str, Agent] = Field(default_factory=dict, description="Available agents by ID")
    created_at: datetime = Field(default_factory=datetime.now)

    def add_agent(self, agent: Agent) -> bool:
        """Add an agent to the pool"""
        if agent.agent_id in self.agents:
            return False
        self.agents[agent.agent_id] = agent
        return True

    def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent from the pool"""
        if agent_id not in self.agents:
            return False
        del self.agents[agent_id]
        return True

    def get_available_agents(self, task_type: Optional[TaskType] = None) -> List[Agent]:
        """Get available agents, optionally filtered by task type"""
        available = [
            agent for agent in self.agents.values()
            if agent.status == AgentStatus.AVAILABLE
        ]

        if task_type:
            available = [
                agent for agent in available
                if any(task_type in cap.supported_task_types for cap in agent.profile.capabilities)
            ]

        # Sort by workload (ascending) then by success rate (descending)
        return sorted(available, key=lambda a: (a.get_workload_score(), -a.success_rate))

    def find_best_agent_for_task(self, task: AgentTask) -> Optional[Agent]:
        """Find the best available agent for a specific task"""
        suitable_agents = [
            agent for agent in self.agents.values()
            if agent.can_handle_task(task)
        ]

        if not suitable_agents:
            return None

        # Score agents based on multiple factors
        def agent_score(agent: Agent) -> float:
            score = 0.0

            # Prefer agents with higher success rate
            score += agent.success_rate * 0.4

            # Prefer agents with lower current workload
            score += (1.0 - agent.get_workload_score()) * 0.3

            # Prefer agents with matching specialization
            if task.task_type in agent.profile.preferred_task_types:
                score += 0.3

            return score

        return max(suitable_agents, key=agent_score)