"""
Workflow Models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class WorkflowTrigger(enum.Enum):
    """Workflow trigger enum."""
    RELEASE_CREATED = "release_created"
    RELEASE_UPDATED = "release_updated"
    DELIVERY_FAILED = "delivery_failed"
    TAKEDOWN_REQUEST = "takedown_request"
    REVENUE_THRESHOLD = "revenue_threshold"
    PARTNER_ERROR = "partner_error"
    MANUAL = "manual"


class WorkflowAction(enum.Enum):
    """Workflow action enum."""
    REQUIRE_APPROVAL = "require_approval"
    SEND_NOTIFICATION = "send_notification"
    RETRY_DELIVERY = "retry_delivery"
    PAUSE_DELIVERY = "pause_delivery"
    ESCALATE = "escalate"
    AUTO_RESOLVE = "auto_resolve"
    WEBHOOK_CALL = "webhook_call"


class WorkflowStatus(enum.Enum):
    """Workflow status enum."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"


class WorkflowRule(Base):
    """Workflow rule model for defining automated workflows."""
    __tablename__ = "workflow_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Rule info
    name = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.ACTIVE)
    priority = Column(Integer, default=0)  # Higher number = higher priority
    
    # Trigger configuration
    trigger_event = Column(Enum(WorkflowTrigger), nullable=False)
    trigger_conditions = Column(JSON)  # Conditions that must be met
    
    # Action configuration
    action_type = Column(Enum(WorkflowAction), nullable=False)
    action_config = Column(JSON)  # Action-specific configuration
    
    # Execution settings
    max_executions = Column(Integer, default=-1)  # -1 for unlimited
    execution_count = Column(Integer, default=0)
    cooldown_minutes = Column(Integer, default=0)  # Minimum time between executions
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_executed = Column(DateTime)
    
    # Relationships
    user = relationship("User")
    executions = relationship("WorkflowExecution", back_populates="rule", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<WorkflowRule(id={self.id}, name='{self.name}', trigger='{self.trigger_event}')>"


class ExecutionStatus(enum.Enum):
    """Execution status enum."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REQUIRES_APPROVAL = "requires_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


class WorkflowExecution(Base):
    """Workflow execution model for tracking workflow runs."""
    __tablename__ = "workflow_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("workflow_rules.id"), nullable=False)
    
    # Execution info
    execution_id = Column(String(100), unique=True, nullable=False)
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING)
    
    # Trigger data
    trigger_data = Column(JSON)  # Data that triggered the workflow
    context = Column(JSON)  # Additional context data
    
    # Execution results
    result = Column(JSON)  # Execution results
    error_message = Column(Text)
    error_details = Column(JSON)
    
    # Approval workflow
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(Integer, ForeignKey("users.id"))
    approval_comment = Column(Text)
    approved_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    rule = relationship("WorkflowRule", back_populates="executions")
    approver = relationship("User", foreign_keys=[approved_by])
    
    def __repr__(self):
        return f"<WorkflowExecution(id={self.id}, execution_id='{self.execution_id}', status='{self.status}')>"
