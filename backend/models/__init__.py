"""Data models for Workflow Intelligence Platform API."""

from .requests import (
    WorkspaceGenerationRequest,
    InsightGenerationRequest,
)
from .responses import (
    WorkspaceGenerationResponse,
    AnalyticsResponse,
    InsightResponse,
    HealthCheckResponse,
)

__all__ = [
    "WorkspaceGenerationRequest",
    "InsightGenerationRequest",
    "WorkspaceGenerationResponse",
    "AnalyticsResponse",
    "InsightResponse",
    "HealthCheckResponse",
]
