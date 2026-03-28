# n8n Workflow Debugger

Paste your n8n workflow JSON and get a structured analysis report — issues categorized as critical, warning, or suggestion, each with an explanation and a fix.

## How to use

1. Export your workflow from n8n (three-dot menu → Download)
2. Paste the JSON, or use **Paste from clipboard** / **Load JSON file**
3. Click **Scan workflow** for instant static analysis
4. Click **Deep scan with AI** for pattern-level architectural insights

## What it checks

**Security (Critical)** — hardcoded secrets, unauthenticated webhooks, Execute Command nodes

**Reliability (Warning)** — HTTP Request instead of native nodes, no error workflow, no error handling on HTTP/database nodes, webhook without response node, AI Agent without memory, large workflow without batching, Manual Trigger only

**Best Practices (Suggestion)** — generic node names, no sticky notes, oversized workflows, disconnected nodes, setTimeout in Code nodes, RAG ingestion and retrieval in the same workflow, AI Agent without Output Parser

**AI Deep Scan** — pattern-level issues static analysis can't catch: architectural problems, data flow issues, deduplication gaps, suboptimal node chains

