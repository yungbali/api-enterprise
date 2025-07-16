"""
Workflow schema definitions
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class WorkflowStatus(str, Enum):
    """Workflow status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStepStatus(str, Enum):
    """Workflow step status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStepBase(BaseModel):
    """Base workflow step schema"""
    name: str = Field(..., description="Step name")
    description: Optional[str] = None
    step_type: str = Field(..., description="Type of step (validation, delivery, etc.)")
    order: int = Field(..., description="Order of execution")
    config: Optional[Dict[str, Any]] = {}


class WorkflowStepCreate(WorkflowStepBase):
    """Schema for creating workflow step"""
    pass


class WorkflowStep(BaseModel):
    """Schema for workflow step with execution info"""
    id: str
    workflow_id: str
    status: WorkflowStepStatus = WorkflowStepStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = {}
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class WorkflowBase(BaseModel):
    """Base workflow schema"""
    name: str = Field(..., description="Workflow name")
    description: Optional[str] = None
    workflow_type: str = Field(..., description="Type of workflow (release, delivery, etc.)")
    config: Optional[Dict[str, Any]] = {}


class WorkflowCreate(WorkflowBase):
    """Schema for creating workflow"""
    steps: List[WorkflowStepCreate] = []


class WorkflowUpdate(BaseModel):
    """Schema for updating workflow"""
    name: Optional[str] = None
    description: Optional[str] = None
    workflow_type: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    status: Optional[WorkflowStatus] = None


class Workflow(BaseModel):
    """Schema for workflow with execution info"""
    id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = {}
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class WorkflowExecution(BaseModel):
    """Schema for workflow execution request"""
    workflow_id: str
    context: Optional[Dict[str, Any]] = {}
    priority: Optional[int] = 1
    
    
class WorkflowExecutionResult(BaseModel):
    """Schema for workflow execution result"""
    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = {}
    steps_completed: int = 0
    total_steps: int = 0
    
    class Config:
        from_attributes = True
