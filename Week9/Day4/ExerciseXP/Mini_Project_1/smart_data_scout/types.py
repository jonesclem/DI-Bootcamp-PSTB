# smart_data_scout/types.py
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional


@dataclass
class ToolDescriptor:
    server_name: str
    tool_name: str
    description: str
    input_schema: Dict[str, Any]


@dataclass
class ToolCallLog:
    step: int
    server_name: str
    tool_name: str
    arguments: Dict[str, Any]
    success: bool
    summary: str
    error: Optional[str] = None


ActionType = Literal["tool", "finish"]


@dataclass
class PlannedAction:
    action: ActionType
    server_name: Optional[str] = None
    tool_name: Optional[str] = None
    arguments: Optional[Dict[str, Any]] = None
    reasoning: Optional[str] = None