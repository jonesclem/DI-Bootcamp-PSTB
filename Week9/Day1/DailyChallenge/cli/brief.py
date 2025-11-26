# cli/brief.py
import argparse
import os
from urllib.parse import urlparse
from datetime import date

import requests


def call_server(method: str, base_url: str, path: str, token: str, json=None):
    url = base_url.rstrip("/") + path
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    resp = requests.request(method, url, headers=headers, json=json, timeout=60)
    resp.raise_for_status()
    return resp.json()


def choose_three_domains(results):
    chosen = []
    seen_domains = set()
    for r in results:
        url = r.get("url")
        if not url:
            continue
        domain = urlparse(url).netloc
        if domain and domain not in seen_domains:
            seen_domains.add(domain)
            chosen.append(r)
        if len(chosen) == 3:
            break
    return chosen


def main():
    parser = argparse.ArgumentParser(
        description="Tiny web briefing client (search → fetch → summarize → save)"
    )
    parser.add_argument("topic", help="Topic to brief on (quoted)")
    parser.add_argument(
        "--server-url",
        default="http://localhost:8000",
        help="Base URL of the tool server (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("MCP_HTTP_TOKEN", ""),
        help="Bearer token (default: MCP_HTTP_TOKEN env)",
    )
    args = parser.parse_args()

    if not args.token:
        raise SystemExit("Error: MCP_HTTP_TOKEN env or --token is required")

    base_url = args.server_url
    token = args.token
    topic = args.topic

    # 1) search_web
    search_payload = {"query": topic, "k": 5}
    search_resp = call_server(
        "POST", base_url, "/tools/search_web", token, json=search_payload
    )
    results = search_resp.get("results", [])
    if not results:
        raise SystemExit("No search results returned")

    selected_results = choose_three_domains(results)
    if not selected_results:
        raise SystemExit("Could not select any domains from results")

    # 2) fetch_readable for 3 domains
    docs = []
    for r in selected_results:
        url = r["url"]
        fetch_payload = {"url": url}
        fetch_resp = call_server(
            "POST", base_url, "/tools/fetch_readable", token, json=fetch_payload
        )
        docs.append(
            {
                "title": fetch_resp["title"],
                "url": fetch_resp["url"],
                "text": fetch_resp["text"],
            }
        )

    # 3) summarize_with_citations
    summarize_payload = {"topic": topic, "docs": docs}
    summary_resp = call_server(
        "POST", base_url, "/tools/summarize_with_citations", token, json=summarize_payload
    )

    bullets = summary_resp.get("bullets", [])
    sources = summary_resp.get("sources", [])

    # 4) Build Markdown
    today = date.today().isoformat()
    filename = f"brief_{today}.md"

    md_lines = []
    md_lines.append(f"# Briefing: {topic}")
    md_lines.append("")
    md_lines.append(f"_Generated on {today}_")
    md_lines.append("")
    for b in bullets:
        md_lines.append(f"- {b}")
    md_lines.append("")
    md_lines.append("## Sources")
    for s in sorted(sources, key=lambda x: x.get("i", 0)):
        i = s.get("i")
        title = s.get("title", "")
        url = s.get("url", "")
        md_lines.append(f"- [{i}] {title} — {url}")

    content = "\n".join(md_lines)

    # 5) save_markdown
    save_payload = {"filename": filename, "content": content}
    save_resp = call_server(
        "POST", base_url, "/tools/save_markdown", token, json=save_payload
    )
    path = save_resp.get("path", filename)

    print(path)


if __name__ == "__main__":
    main()