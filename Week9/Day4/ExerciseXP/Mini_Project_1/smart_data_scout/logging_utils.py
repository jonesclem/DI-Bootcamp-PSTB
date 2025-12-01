# smart_data_scout/logging_utils.py
import json
import logging
from typing import Any, Dict

from .types import ToolCallLog

logger = logging.getLogger("smart_data_scout")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


def log_tool_call(log: ToolCallLog) -> None:
    safe_args = {k: v for k, v in log.arguments.items() if "key" not in k.lower()}
    payload: Dict[str, Any] = {
        "step": log.step,
        "server": log.server_name,
        "tool": log.tool_name,
        "success": log.success,
        "summary": log.summary,
        "arguments": safe_args,
    }
    if log.error:
        payload["error"] = log.error

    logger.info("MCP TOOL CALL: %s", json.dumps(payload, ensure_ascii=False))