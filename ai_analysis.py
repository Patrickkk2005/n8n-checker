import json
import os
import urllib.request
import urllib.error

SYSTEM_PROMPT = """You are an expert n8n workflow analyzer. You review n8n workflow JSON and find issues that static analysis can't catch — patterns, anti-patterns, architectural problems, and optimization opportunities.

IMPORTANT RULES:
- The static rule engine already ran. The user will tell you which rule IDs were already flagged. Do NOT repeat those findings.
- Focus on PATTERN-LEVEL insights: workflow architecture, data flow issues, potential race conditions, missing validation, suboptimal node chains that could be simplified, and n8n-specific best practices.
- Return ONLY valid JSON in this exact format:

{
  "findings": [
    {
      "severity": "warning" | "suggestion",
      "title": "Short descriptive title",
      "description": "What's wrong and why it matters.",
      "fix": "Specific actionable fix instructions.",
      "nodeNames": ["Node1", "Node2"],
      "ruleId": "ai-pattern-name"
    }
  ]
}

NEVER return severity "critical" — only static checks produce critical findings (they're deterministic and reliable). AI findings are always "warning" or "suggestion".

Examples of things you should catch:
- A workflow fetches data from Service A, transforms it, then writes to Service B — but there's no deduplication, so re-runs create duplicates
- An If node checks a condition but both branches lead to the same subsequent node, making the condition pointless
- A workflow processes items one by one with HTTP requests when the API supports batch operations
- An AI Agent uses web search as a tool but the workflow could use the native n8n HTTP Request as a tool instead (faster, cheaper)
- Sensitive data flows through a logging or notification node unredacted
- A scheduled workflow runs every minute but the task it performs only needs hourly execution
- Credentials are correctly managed but the same credential is used across many workflows (single point of failure — note this as a suggestion)
- A workflow uses the Code node for simple operations that could be done with native nodes (Edit Fields, Filter, Sort, etc.)
- Webhook workflows that do heavy processing synchronously instead of responding immediately and processing async

If the workflow looks clean and well-structured, return {"findings": []} — don't invent problems."""


def _get_config():
    api_key = os.environ.get('OPENAI_API_KEY', '')
    model = os.environ.get('OPENAI_MODEL', '')
    if not api_key or not model:
        try:
            import config
            api_key = api_key or getattr(config, 'OPENAI_API_KEY', '')
            model = model or getattr(config, 'OPENAI_MODEL', 'gpt-4o-mini')
        except ImportError:
            if not api_key:
                raise RuntimeError('OpenAI API key not configured. Set the OPENAI_API_KEY environment variable.')
    model = model or 'gpt-4o-mini'
    if not api_key or api_key == 'YOUR_KEY_HERE':
        raise RuntimeError('OpenAI API key not configured. Set the OPENAI_API_KEY environment variable.')
    return api_key, model


def deep_analyze(workflow_json, static_findings):
    api_key, model = _get_config()

    already_flagged = json.dumps([f.get('ruleId') for f in static_findings])
    user_message = (
        f"Analyze this n8n workflow JSON and return findings as a JSON array.\n\n"
        f"Static analysis already found these issues (do not repeat them):\n{already_flagged}\n\n"
        f"Workflow JSON:\n{json.dumps(workflow_json)}"
    )

    payload = json.dumps({
        'model': model,
        'max_tokens': 2000,
        'temperature': 0.3,
        'messages': [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': user_message},
        ],
        'response_format': {'type': 'json_object'},
    }).encode()

    req = urllib.request.Request(
        'https://api.openai.com/v1/chat/completions',
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        },
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 401:
            raise RuntimeError('Invalid API key. Check config.py.')
        if e.code == 429:
            raise RuntimeError('Rate limited by OpenAI. Wait a moment and try again.')
        try:
            body = json.loads(e.read().decode())
            msg = body.get('error', {}).get('message') or f'API error ({e.code})'
        except Exception:
            msg = f'API error ({e.code})'
        raise RuntimeError(msg)
    except urllib.error.URLError:
        raise RuntimeError('Could not reach OpenAI API. Check your internet connection.')

    try:
        content = data['choices'][0]['message']['content']
        parsed = json.loads(content)
    except (KeyError, json.JSONDecodeError):
        raise RuntimeError('Failed to parse AI response. Try again.')

    ai_findings = parsed.get('findings', [])

    for f in ai_findings:
        if f.get('severity') == 'critical':
            f['severity'] = 'warning'
        f['isAI'] = True

    return ai_findings