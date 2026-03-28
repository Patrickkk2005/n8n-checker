# n8n Workflow Debugger

Paste your n8n workflow JSON and get a structured analysis report with issues categorized as critical, warning, or suggestion — each with an explanation and a fix.

## How to use

1. Export your workflow from n8n (three-dot menu → Download)
2. Paste the JSON into the text area
3. Click **Scan workflow** for instant static analysis (free, no account needed)
4. Optionally, click **Deep scan with AI** for pattern-level insights (requires your own OpenAI API key)

## What it checks

### Security (Critical)
- Hardcoded secrets (API keys, tokens, passwords) in node parameters
- Webhooks with no authentication
- Execute Command nodes (shell execution risk)

### Reliability (Warning)
- HTTP Request nodes used instead of native service nodes (Slack, Notion, GitHub, etc.)
- No error workflow configured
- No error handling on HTTP/database nodes
- Webhook workflows without a Respond to Webhook node
- AI Agents without memory connected
- Large workflows without batching
- Manual Trigger as the only trigger

### Best Practices (Suggestion)
- Generic/default node names
- No sticky notes in complex workflows
- Oversized workflows that should be decomposed
- Disconnected (orphan) nodes
- setTimeout in Code nodes (use Wait node instead)
- RAG ingestion and retrieval in the same workflow
- AI Agent without Output Parser feeding structured consumers

### AI Deep Scan
With an OpenAI API key, the AI layer catches pattern-level issues that static analysis can't — architectural problems, data flow issues, optimization opportunities, and n8n-specific anti-patterns.

## Privacy

- **Your workflow JSON never leaves your browser** during static analysis
- If you use AI deep scan, the workflow is sent directly from your browser to OpenAI's API — it never passes through any intermediary server
- Your OpenAI API key is stored in your browser's localStorage and is only sent to `api.openai.com`
- This tool has no backend, no analytics, no tracking

## Built with

- Vanilla HTML, CSS, and JavaScript
- Hosted on GitHub Pages
- Fonts: IBM Plex Sans and IBM Plex Mono

## License

MIT
