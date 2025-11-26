# Tiny Web Briefing Tool (Serper.dev + Ollama)

This project exposes a tiny HTTP “tool” API that can:

- Search the web
- Fetch readable page content
- Summarize with citations using a local LLM (Ollama)
- Save a Markdown research brief

A small CLI client calls the server end-to-end and writes `brief_YYYY-MM-DD.md`.

## 1. Architecture

- **Server** (FastAPI, HTTP only)
  - `GET /tools` – list tools & input schemas
  - `POST /tools/search_web` – Serper.dev web search
  - `POST /tools/fetch_readable` – fetch + extract main text from URL
  - `POST /tools/summarize_with_citations` – local LLM summarization (Ollama)
  - `POST /tools/save_markdown` – save Markdown file to `output/`

- **CLI client**
  - Command: `python -m cli.brief "your topic"`
  - Flow: `search_web → fetch_readable(3 domains) → summarize_with_citations → save_markdown`
  - Prints the final absolute path of the saved `.md` file.

All server endpoints are authenticated with:

```text
Authorization: Bearer <MCP_HTTP_TOKEN>
```

## 2. Requirements

- Python 3.9+  
- [Ollama](https://ollama.com/) installed and running locally  
- A free [Serper.dev](https://serper.dev/) API key

## 3. Installation

Clone and install dependencies:

```bash
git clone <your-repo-url> web_briefing_tool
cd web_briefing_tool

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

## 4. Configure environment variables

In your shell:

```bash
export MCP_HTTP_TOKEN="dev-secret-token"      # any secret you choose
export SERPER_API_KEY="your-serper-api-key"  # from Serper.dev
# Optional overrides:
# export OLLAMA_MODEL="llama3.2:1b"
# export OLLAMA_BASE_URL="http://localhost:11434"
```

On Windows PowerShell, use:

```powershell
$env:MCP_HTTP_TOKEN="dev-secret-token"
$env:SERPER_API_KEY="your-serper-api-key"
```

## 5. Set up Ollama

1. Install Ollama from their website.
2. Make sure the Ollama server is running (usually automatic).
3. Pull a model (or pick your own and update `OLLAMA_MODEL`):

```bash
ollama pull llama3.2:1b
```

## 6. Run the server

From the project root:

```bash
uvicorn server.main:app --host 0.0.0.0 --port 8000
```

Health check (new terminal, same env):

```bash
curl -H "Authorization: Bearer $MCP_HTTP_TOKEN" http://localhost:8000/
```

You should see a small JSON status payload.

## 7. Run the CLI client

In another terminal (same project, venv + env vars):

```bash
python -m cli.brief "AI regulation in the EU"
```

What happens:

1. CLI → `POST /tools/search_web` (topic query)  
2. CLI → `POST /tools/fetch_readable` for 3 distinct domains  
3. CLI → `POST /tools/summarize_with_citations`  
4. CLI → `POST /tools/save_markdown` with `brief_YYYY-MM-DD.md`  
5. CLI prints the absolute path, for example:

```text
/home/you/web_briefing_tool/output/brief_2025-11-25.md
```

Open the file to see:

- Exactly 5 bullet points, each ≤ 200 characters, with inline citation markers like `[1]`, `[2]`, …  
- A “Sources” section listing the numbered sources.

## 8. HTTP API summary

All requests must include:

```http
Authorization: Bearer <MCP_HTTP_TOKEN>
Content-Type: application/json
```

### GET `/tools`

List available tools and their input schemas.

### POST `/tools/search_web`

Body:

```json
{ "query": "AI regulation in the EU", "k": 5 }
```

Returns top search results (Serper.dev) as:

```json
{ "results": [ { "title": "...", "url": "...", "snippet": "...", "source": "serper.dev" }, ... ] }
```

### POST `/tools/fetch_readable`

Body:

```json
{ "url": "https://example.com/article" }
```

Returns:

```json
{ "url": "...", "title": "...", "text": "Main readable content..." }
```

### POST `/tools/summarize_with_citations`

Body:

```json
{
  "topic": "AI regulation in the EU",
  "docs": [
    { "title": "...", "url": "https://...", "text": "..." },
    { "title": "...", "url": "https://...", "text": "..." }
  ]
}
```

Returns:

```json
{
  "bullets": ["First bullet [1][2]", "..."],
  "sources": [
    { "i": 1, "title": "Source 1", "url": "https://..." },
    { "i": 2, "title": "Source 2", "url": "https://..." }
  ]
}
```

Exactly 5 bullets, each ≤ 200 characters.

### POST `/tools/save_markdown`

Body:

```json
{ "filename": "brief_2025-11-25.md", "content": "# Briefing..." }
```

Returns:

```json
{ "path": "/absolute/path/to/output/brief_2025-11-25.md" }
```

## 9. cURL examples

See `curl_examples.md` for ready-to-run cURL commands for each endpoint.
