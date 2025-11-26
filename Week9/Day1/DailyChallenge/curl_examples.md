# cURL examples for Tiny Tool API

All commands assume:

```bash
export MCP_HTTP_TOKEN="dev-secret-token"
BASE_URL="http://localhost:8000"
```

---

## 1. Root health check

```bash
curl -X GET   -H "Authorization: Bearer $MCP_HTTP_TOKEN"   "$BASE_URL/"
```

---

## 2. GET /tools

```bash
curl -X GET   -H "Authorization: Bearer $MCP_HTTP_TOKEN"   -H "Content-Type: application/json"   "$BASE_URL/tools"
```

---

## 3. POST /tools/search_web

```bash
curl -X POST   -H "Authorization: Bearer $MCP_HTTP_TOKEN"   -H "Content-Type: application/json"   -d '{
    "query": "AI regulation in the EU",
    "k": 5
  }'   "$BASE_URL/tools/search_web"
```

---

## 4. POST /tools/fetch_readable

Replace the URL with one of the URLs from `search_web`:

```bash
curl -X POST   -H "Authorization: Bearer $MCP_HTTP_TOKEN"   -H "Content-Type: application/json"   -d '{
    "url": "https://example.com/some-article"
  }'   "$BASE_URL/tools/fetch_readable"
```

---

## 5. POST /tools/summarize_with_citations

Example with two short docs:

```bash
curl -X POST   -H "Authorization: Bearer $MCP_HTTP_TOKEN"   -H "Content-Type: application/json"   -d '{
    "topic": "AI regulation in the EU",
    "docs": [
      {
        "title": "EU AI Act overview",
        "url": "https://example.com/eu-ai-act",
        "text": "The EU AI Act is a comprehensive framework for regulating artificial intelligence systems in the European Union..."
      },
      {
        "title": "Risk-based approach to AI",
        "url": "https://example.com/risk-based-ai",
        "text": "The EU AI Act classifies AI systems by risk level, with stricter rules for high-risk applications..."
      }
    ]
  }'   "$BASE_URL/tools/summarize_with_citations"
```

Expected response shape:

```json
{
  "bullets": [
    "Short bullet with [1]",
    "Another point with [1][2]",
    "... 3 more bullets ..."
  ],
  "sources": [
    { "i": 1, "title": "EU AI Act overview", "url": "https://example.com/eu-ai-act" },
    { "i": 2, "title": "Risk-based approach to AI", "url": "https://example.com/risk-based-ai" }
  ]
}
```

---

## 6. POST /tools/save_markdown

```bash
curl -X POST   -H "Authorization: Bearer $MCP_HTTP_TOKEN"   -H "Content-Type: application/json"   -d '{
    "filename": "brief_2025-11-25.md",
    "content": "# Briefing: AI regulation in the EU\n\n- Bullet 1 [1]\n\n## Sources\n- [1] Example source — https://example.com"
  }'   "$BASE_URL/tools/save_markdown"
```

Example response:

```json
{
  "path": "/absolute/path/to/your/project/output/brief_2025-11-25.md"
}
```
