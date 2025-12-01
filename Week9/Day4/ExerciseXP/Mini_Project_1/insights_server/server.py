# insights_server/server.py
import io
from typing import Dict, Any

import pandas as pd
from mcp.server.fastmcp import FastMCP  # FastMCP helper from the official SDK

mcp = FastMCP("Insights Server", json_response=True)


def _df_basic_profile(df: pd.DataFrame) -> Dict[str, Any]:
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    non_numeric_cols = [c for c in df.columns if c not in numeric_cols]

    summary: Dict[str, Any] = {
        "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
        "columns": list(df.columns),
        "numeric_columns": numeric_cols,
        "non_numeric_columns": non_numeric_cols,
    }

    if numeric_cols:
        desc = df[numeric_cols].describe().to_dict()
        summary["numeric_summary"] = {
            col: {stat: float(val) for stat, val in stats.items()}
            for col, stats in desc.items()
        }
    else:
        summary["numeric_summary"] = {}

    summary["sample_rows"] = df.head(5).to_dict(orient="records")
    return summary


@mcp.tool()
def analyze_csv_snippet(
    csv_text: str,
    delimiter: str = ",",
    question: str | None = None,
) -> Dict[str, Any]:
    """
    Analyze a CSV snippet given as raw text.

    Typically used after csv-editor has:
    - loaded a CSV (from file or URL),
    - filtered/cleaned it,
    - exported a subset as raw text.

    Parameters
    ----------
    csv_text : str
        Raw CSV content.
    delimiter : str
        Column delimiter (default ',').
    question : str | None
        Optional natural language question about the data.

    Returns
    -------
    dict
        Structured profile and optional question hint.
    """
    buf = io.StringIO(csv_text)
    try:
        df = pd.read_csv(buf, delimiter=delimiter)
    except Exception as exc:  # noqa: BLE001
        return {"error": f"Failed to parse CSV: {exc}"}

    profile = _df_basic_profile(df)
    if question:
        profile["question"] = question
        profile["answer_hint"] = (
            "Use this structured summary to answer the question: "
            f"{question!r}."
        )
    return profile


if __name__ == "__main__":
    # Run as stdio MCP server:
    #   python -m insights_server.server
    mcp.run()