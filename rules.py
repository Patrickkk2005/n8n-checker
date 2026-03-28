import re

# ── Domain knowledge ──────────────────────────────────────────────────────────

NATIVE_NODE_DOMAINS = {
    'api.slack.com': {'node': 'Slack', 'type': 'n8n-nodes-base.slack'},
    'hooks.slack.com': {'node': 'Slack', 'type': 'n8n-nodes-base.slack'},
    'slack.com/api': {'node': 'Slack', 'type': 'n8n-nodes-base.slack'},
    'sheets.googleapis.com': {'node': 'Google Sheets', 'type': 'n8n-nodes-base.googleSheets'},
    'docs.googleapis.com': {'node': 'Google Docs', 'type': 'n8n-nodes-base.googleDocs'},
    'www.googleapis.com/drive': {'node': 'Google Drive', 'type': 'n8n-nodes-base.googleDrive'},
    'gmail.googleapis.com': {'node': 'Gmail', 'type': 'n8n-nodes-base.gmail'},
    'www.googleapis.com/calendar': {'node': 'Google Calendar', 'type': 'n8n-nodes-base.googleCalendar'},
    'api.notion.com': {'node': 'Notion', 'type': 'n8n-nodes-base.notion'},
    'api.github.com': {'node': 'GitHub', 'type': 'n8n-nodes-base.github'},
    'api.telegram.org': {'node': 'Telegram', 'type': 'n8n-nodes-base.telegram'},
    'api.openai.com': {'node': 'OpenAI / AI Agent', 'type': 'n8n-nodes-base.openAi or @n8n/n8n-nodes-langchain.openAi'},
    'api.anthropic.com': {'node': 'Anthropic / AI Agent', 'type': '@n8n/n8n-nodes-langchain.lmChatAnthropic'},
    'api.airtable.com': {'node': 'Airtable', 'type': 'n8n-nodes-base.airtable'},
    'api.stripe.com': {'node': 'Stripe', 'type': 'n8n-nodes-base.stripe'},
    'graph.microsoft.com': {'node': 'Microsoft (Teams/Outlook/OneDrive)', 'type': 'n8n-nodes-base.microsoftTeams / microsoftOutlook / microsoftOneDrive'},
    'api.hubspot.com': {'node': 'HubSpot', 'type': 'n8n-nodes-base.hubspot'},
    'api.trello.com': {'node': 'Trello', 'type': 'n8n-nodes-base.trello'},
    'api.clickup.com': {'node': 'ClickUp', 'type': 'n8n-nodes-base.clickUp'},
    'api.asana.com': {'node': 'Asana', 'type': 'n8n-nodes-base.asana'},
    'api.sendgrid.com': {'node': 'SendGrid', 'type': 'n8n-nodes-base.sendGrid'},
    'api.twilio.com': {'node': 'Twilio', 'type': 'n8n-nodes-base.twilio'},
    'api.dropboxapi.com': {'node': 'Dropbox', 'type': 'n8n-nodes-base.dropbox'},
    'content.dropboxapi.com': {'node': 'Dropbox', 'type': 'n8n-nodes-base.dropbox'},
    'api.monday.com': {'node': 'Monday.com', 'type': 'community node or credential-only'},
    'api.linear.app': {'node': 'Linear', 'type': 'n8n-nodes-base.linear'},
    'api.pipedrive.com': {'node': 'Pipedrive', 'type': 'n8n-nodes-base.pipedrive'},
    'discord.com/api': {'node': 'Discord', 'type': 'n8n-nodes-base.discord'},
    'discordapp.com/api': {'node': 'Discord', 'type': 'n8n-nodes-base.discord'},
    'api.mailchimp.com': {'node': 'Mailchimp', 'type': 'n8n-nodes-base.mailchimp'},
    'api.paypal.com': {'node': 'PayPal', 'type': 'n8n-nodes-base.payPal'},
    'api.shopify.com': {'node': 'Shopify', 'type': 'n8n-nodes-base.shopify'},
    'api.todoist.com': {'node': 'Todoist', 'type': 'n8n-nodes-base.todoist'},
    'api.zendesk.com': {'node': 'Zendesk', 'type': 'n8n-nodes-base.zendesk'},
    'api.freshdesk.com': {'node': 'Freshdesk', 'type': 'n8n-nodes-base.freshdesk'},
    'login.salesforce.com': {'node': 'Salesforce', 'type': 'n8n-nodes-base.salesforce'},
    'api.jira.com': {'node': 'Jira Software', 'type': 'n8n-nodes-base.jira'},
    'atlassian.net': {'node': 'Jira Software', 'type': 'n8n-nodes-base.jira'},
}

DEFAULT_NODE_NAMES = {
    'Slack', 'HTTP Request', 'If', 'Switch', 'Code', 'Merge', 'Set',
    'Edit Fields', 'Filter', 'Webhook', 'Wait', 'Gmail', 'Telegram',
    'Notion', 'GitHub', 'Airtable', 'Postgres', 'MySQL', 'MongoDB',
    'Redis', 'Google Sheets', 'Stripe', 'HubSpot', 'Discord',
    'Schedule Trigger', 'Split In Batches', 'Loop Over Items',
    'Function', 'Sort', 'Limit', 'Compare Datasets', 'Aggregate',
    'Remove Duplicates', 'Summarize', 'Rename Keys', 'Split Out',
    'Date & Time', 'Crypto', 'Compression', 'XML', 'HTML',
    'Respond to Webhook', 'Execute Workflow', 'Error Trigger',
    'Manual Trigger', 'n8n Form Trigger', 'Chat Trigger',
    'AI Agent', 'OpenAI Chat Model', 'Anthropic Chat Model',
    'Window Buffer Memory',
}

ERROR_PRONE_NODE_TYPES = {
    'n8n-nodes-base.httpRequest',
    'n8n-nodes-base.postgres',
    'n8n-nodes-base.mysql',
    'n8n-nodes-base.mongoDb',
    'n8n-nodes-base.redis',
    'n8n-nodes-base.supabase',
    'n8n-nodes-base.slack',
    'n8n-nodes-base.gmail',
    'n8n-nodes-base.stripe',
    'n8n-nodes-base.salesforce',
    'n8n-nodes-base.hubspot',
    'n8n-nodes-base.shopify',
    'n8n-nodes-base.graphql',
    'n8n-nodes-base.ftp',
    'n8n-nodes-base.ssh',
}

TRIGGER_NODE_TYPES = {
    'n8n-nodes-base.manualTrigger',
    'n8n-nodes-base.scheduleTrigger',
    'n8n-nodes-base.webhook',
    'n8n-nodes-base.emailReadImap',
    'n8n-nodes-base.rssFeedReadTrigger',
    'n8n-nodes-base.errorTrigger',
    'n8n-nodes-base.executeWorkflowTrigger',
    'n8n-nodes-base.formTrigger',
    'n8n-nodes-base.localFileTrigger',
    '@n8n/n8n-nodes-langchain.chatTrigger',
    '@n8n/n8n-nodes-langchain.mcpTrigger',
}

SECRET_PATTERNS = [
    (re.compile(r'sk-[a-zA-Z0-9\-_]{20,}'), 'OpenAI API key'),
    (re.compile(r'xoxb-[a-zA-Z0-9\-]+'), 'Slack bot token'),
    (re.compile(r'xoxp-[a-zA-Z0-9\-]+'), 'Slack user token'),
    (re.compile(r'xoxs-[a-zA-Z0-9\-]+'), 'Slack session token'),
    (re.compile(r'ghp_[a-zA-Z0-9]{36,}'), 'GitHub personal access token'),
    (re.compile(r'gho_[a-zA-Z0-9]{36,}'), 'GitHub OAuth token'),
    (re.compile(r'ghs_[a-zA-Z0-9]{36,}'), 'GitHub app token'),
    (re.compile(r'ghu_[a-zA-Z0-9]{36,}'), 'GitHub user token'),
    (re.compile(r'Bearer\s+[a-zA-Z0-9\-_.]{20,}'), 'Bearer token'),
    (re.compile(r'AKIA[0-9A-Z]{16}'), 'AWS access key'),
    (re.compile(r'key-[a-zA-Z0-9]{20,}'), 'API key'),
]

_BASE64_RE = re.compile(r'^[A-Za-z0-9+/=]{40,}$')
_SENSITIVE_FIELDS = {'password', 'apikey', 'token', 'secret', 'authorization'}
_STRUCTURED_CONSUMER_TYPES = {
    'n8n-nodes-base.if',
    'n8n-nodes-base.switch',
    'n8n-nodes-base.set',
    'n8n-nodes-base.filter',
    'n8n-nodes-base.editFields',
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def _deep_scan_for_secrets(obj, path=''):
    findings = []
    if obj is None:
        return findings
    if isinstance(obj, str):
        # Skip n8n expressions like ={{ ... }}
        if '={{' in obj and '}}' in obj:
            return findings
        for pattern, label in SECRET_PATTERNS:
            if pattern.search(obj):
                findings.append({'value': label, 'path': path})
        # Check base64 in sensitive field names
        field_name = path.split('.')[-1].lower() if path else ''
        if field_name in _SENSITIVE_FIELDS:
            if _BASE64_RE.match(obj.strip()):
                findings.append({'value': 'base64 token in sensitive field', 'path': path})
        return findings
    if isinstance(obj, list):
        for i, item in enumerate(obj):
            findings.extend(_deep_scan_for_secrets(item, f'{path}[{i}]'))
        return findings
    if isinstance(obj, dict):
        for key, val in obj.items():
            new_path = f'{path}.{key}' if path else key
            findings.extend(_deep_scan_for_secrets(val, new_path))
    return findings


def _get_nodes_by_type(nodes, node_type):
    return [n for n in nodes if n.get('type') == node_type]


def _is_trigger_node(node):
    node_type = node.get('type', '')
    return node_type in TRIGGER_NODE_TYPES or 'trigger' in node_type.lower()


def _get_connected_node_ids(connections):
    connected = set()
    for source_name, outputs in connections.items():
        connected.add(source_name)
        if not isinstance(outputs, dict):
            continue
        for key, groups in outputs.items():
            if not isinstance(groups, list):
                continue
            for group in groups:
                if isinstance(group, list):
                    for conn in group:
                        if isinstance(conn, dict) and conn.get('node'):
                            connected.add(conn['node'])
    return connected


def _has_memory_connected(agent_name, connections):
    all_conns = connections.get(agent_name, {})
    if isinstance(all_conns, dict):
        for key, groups in all_conns.items():
            if 'memory' in key or key == 'ai_memory':
                if isinstance(groups, list):
                    for group in groups:
                        if isinstance(group, list) and len(group) > 0:
                            return True
    # Also check if any node connects TO this agent via a memory output
    for source_name, outputs in connections.items():
        if not isinstance(outputs, dict):
            continue
        for key, groups in outputs.items():
            if 'memory' not in key:
                continue
            if isinstance(groups, list):
                for group in groups:
                    if isinstance(group, list):
                        for conn in group:
                            if isinstance(conn, dict) and conn.get('node') == agent_name:
                                return True
    return False


def _has_output_parser_connected(agent_name, connections):
    all_conns = connections.get(agent_name, {})
    if not isinstance(all_conns, dict):
        return False
    for key, groups in all_conns.items():
        if 'outputParser' in key or key == 'ai_outputParser':
            if isinstance(groups, list):
                for group in groups:
                    if isinstance(group, list) and len(group) > 0:
                        return True
    return False


def _get_downstream_nodes(node_name, connections):
    downstream = []
    outputs = connections.get(node_name, {})
    if not isinstance(outputs, dict) or 'main' not in outputs:
        return downstream
    for group in outputs['main']:
        if isinstance(group, list):
            for conn in group:
                if isinstance(conn, dict) and conn.get('node'):
                    downstream.append(conn['node'])
    return downstream


# ── Main analysis function ────────────────────────────────────────────────────

def analyze_workflow(workflow):
    findings = []
    nodes = workflow.get('nodes', [])
    connections = workflow.get('connections', {})
    settings = workflow.get('settings', {})
    node_map = {n['name']: n for n in nodes if 'name' in n}

    # 1. hardcoded-secrets
    for node in nodes:
        secrets = _deep_scan_for_secrets(node.get('parameters', {}))
        if secrets:
            name = node.get('name', '')
            findings.append({
                'severity': 'critical',
                'title': f"Hardcoded secret detected in node '{name}'",
                'description': (
                    f"Found {', '.join(s['value'] for s in secrets)} in the node parameters. "
                    "Hardcoded secrets in workflow JSON can be exposed if the workflow is shared, exported, or stored in version control."
                ),
                'fix': (
                    "Move this credential to n8n's credential manager (Settings \u2192 Credentials \u2192 Add). "
                    "Then reference it in the node's Authentication section instead of pasting the key directly into parameters."
                ),
                'nodeNames': [name],
                'ruleId': 'hardcoded-secrets',
            })

    # 2. webhook-no-auth
    for node in _get_nodes_by_type(nodes, 'n8n-nodes-base.webhook'):
        auth = node.get('parameters', {}).get('authentication')
        if not auth or auth == 'none':
            name = node.get('name', '')
            findings.append({
                'severity': 'critical',
                'title': 'Webhook has no authentication',
                'description': (
                    f"The webhook node '{name}' accepts requests without any authentication. "
                    "Anyone who discovers the webhook URL can trigger this workflow."
                ),
                'fix': (
                    "In the webhook node's settings, set Authentication to Header Auth, Basic Auth, or JWT. "
                    "This prevents unauthorized parties from triggering your workflow if they discover the URL."
                ),
                'nodeNames': [name],
                'ruleId': 'webhook-no-auth',
            })

    # 3. execute-command-enabled
    for node in _get_nodes_by_type(nodes, 'n8n-nodes-base.executeCommand'):
        name = node.get('name', '')
        findings.append({
            'severity': 'critical',
            'title': 'Execute Command node is used',
            'description': (
                f"The node '{name}' runs shell commands directly on the host machine. "
                "This is a significant security risk, especially if the workflow can be triggered externally."
            ),
            'fix': (
                "This node runs shell commands and is disabled by default in n8n v2.0 for security reasons. "
                "Consider using the Code node or SSH node instead. "
                "If you must use it, ensure the workflow is not publicly triggerable."
            ),
            'nodeNames': [name],
            'ruleId': 'execute-command-enabled',
        })

    # 4. http-request-instead-of-native
    for node in _get_nodes_by_type(nodes, 'n8n-nodes-base.httpRequest'):
        url = node.get('parameters', {}).get('url', '')
        for domain, info in NATIVE_NODE_DOMAINS.items():
            if domain in url:
                name = node.get('name', '')
                findings.append({
                    'severity': 'warning',
                    'title': f"HTTP Request used instead of native {info['node']} node",
                    'description': (
                        f"The node '{name}' makes an HTTP request to {domain}, but n8n has a dedicated "
                        f"{info['node']} node that handles authentication, pagination, error handling, and rate limiting automatically."
                    ),
                    'fix': (
                        f"Replace this HTTP Request node with the native {info['node']} node. "
                        "Native nodes handle authentication, pagination, error handling, and rate limiting automatically \u2014 "
                        "and they're easier to configure."
                    ),
                    'nodeNames': [name],
                    'ruleId': 'http-request-instead-of-native',
                })
                break

    # 5. no-error-workflow
    if not settings.get('errorWorkflow'):
        findings.append({
            'severity': 'warning',
            'title': 'No error workflow configured',
            'description': (
                "This workflow has no error workflow set. If any node fails, the error will be silently swallowed "
                "(unless you check executions manually). In production, you need to know when things break."
            ),
            'fix': (
                "Create a separate error-handling workflow that starts with an Error Trigger node, then sends a "
                "notification (Slack, email, etc.) with the error details and execution ID. "
                "In your main workflow's settings, set 'Error Workflow' to point to this handler."
            ),
            'nodeNames': [],
            'ruleId': 'no-error-workflow',
        })

    # 6. no-error-handling-on-http
    for node in nodes:
        if node.get('type') not in ERROR_PRONE_NODE_TYPES:
            continue
        params = node.get('parameters', {})
        continue_on_fail = params.get('options', {}).get('continueOnFail')
        on_error = params.get('onError')
        node_conns = connections.get(node.get('name', ''), {})
        main_outputs = node_conns.get('main', []) if isinstance(node_conns, dict) else []
        has_error_branch = (
            len(main_outputs) > 1 and
            isinstance(main_outputs[1], list) and
            len(main_outputs[1]) > 0
        )
        if not continue_on_fail and on_error != 'continueErrorOutput' and not has_error_branch:
            name = node.get('name', '')
            findings.append({
                'severity': 'warning',
                'title': f"No error handling on '{name}'",
                'description': (
                    "This node calls an external service but has no error handling configured. "
                    "If the service is down, returns an error, or times out, the entire workflow will fail."
                ),
                'fix': (
                    "In this node's settings, enable 'Continue On Fail' or add an error output branch "
                    "to handle failures gracefully instead of crashing the entire workflow."
                ),
                'nodeNames': [name],
                'ruleId': 'no-error-handling-on-http',
            })

    # 7. webhook-no-response
    webhook_triggers = _get_nodes_by_type(nodes, 'n8n-nodes-base.webhook')
    if webhook_triggers:
        has_respond_node = any(n.get('type') == 'n8n-nodes-base.respondToWebhook' for n in nodes)
        all_webhooks_last_node = all(
            n.get('parameters', {}).get('responseMode') == 'lastNode'
            for n in webhook_triggers
        )
        if not has_respond_node and not all_webhooks_last_node:
            findings.append({
                'severity': 'warning',
                'title': 'Webhook workflow has no Respond to Webhook node',
                'description': (
                    "This workflow is triggered by a webhook but never sends a response back to the caller. "
                    "The caller will wait until timeout."
                ),
                'fix': (
                    "Add a 'Respond to Webhook' node at the end of your workflow to send a response back to the caller. "
                    "Without it, the caller receives no response and the request may time out."
                ),
                'nodeNames': [n.get('name', '') for n in webhook_triggers],
                'ruleId': 'webhook-no-response',
            })

    # 8. ai-agent-no-memory
    agent_nodes = [n for n in nodes if n.get('type') == '@n8n/n8n-nodes-langchain.agent']
    for agent in agent_nodes:
        if not _has_memory_connected(agent.get('name', ''), connections):
            name = agent.get('name', '')
            findings.append({
                'severity': 'warning',
                'title': 'AI Agent has no memory connected',
                'description': (
                    f"The AI Agent '{name}' has no memory sub-node connected. "
                    "Without memory, the agent has no conversation context and treats every message as brand new."
                ),
                'fix': (
                    "Connect a Memory node (Window Buffer Memory for simple use, Redis or Postgres Chat Memory for persistence) "
                    "to your AI Agent. Without memory, the agent has no conversation context and treats every message as brand new."
                ),
                'nodeNames': [name],
                'ruleId': 'ai-agent-no-memory',
            })

    # 9. large-dataset-no-batching
    total_node_count = len(nodes)
    has_data_source = any(
        n.get('type') == 'n8n-nodes-base.httpRequest' or n.get('type') in ERROR_PRONE_NODE_TYPES
        for n in nodes
    )
    has_batching = any(n.get('type') == 'n8n-nodes-base.splitInBatches' for n in nodes)
    if total_node_count > 8 and has_data_source and not has_batching:
        findings.append({
            'severity': 'warning',
            'title': 'Large workflow with no batching',
            'description': (
                f"This workflow has {total_node_count} nodes and pulls data from external sources, but doesn't use batching. "
                "Processing large datasets without batching can cause memory issues and hit API rate limits."
            ),
            'fix': (
                "If this workflow processes many items, add a 'Loop Over Items' (Split in Batches) node after your data source "
                "to process records in chunks of 10\u201350. This prevents memory issues and respects API rate limits."
            ),
            'nodeNames': [],
            'ruleId': 'large-dataset-no-batching',
        })

    # 10. manual-trigger-only
    trigger_nodes = [n for n in nodes if _is_trigger_node(n)]
    all_manual = (
        len(trigger_nodes) > 0 and
        all(n.get('type') == 'n8n-nodes-base.manualTrigger' for n in trigger_nodes)
    )
    if all_manual:
        findings.append({
            'severity': 'warning',
            'title': 'Only trigger is Manual Trigger',
            'description': (
                "This workflow can only be started manually. "
                "In production, workflows should be triggered automatically via schedules, webhooks, or service events."
            ),
            'fix': (
                "Manual Trigger is for development/testing only. For production, replace it with an appropriate trigger: "
                "Schedule Trigger (for cron jobs), Webhook (for HTTP events), or a service-specific trigger "
                "(e.g., Gmail Trigger, n8n Form Trigger)."
            ),
            'nodeNames': [n.get('name', '') for n in trigger_nodes],
            'ruleId': 'manual-trigger-only',
        })

    # 11. generic-node-names
    generic_nodes = []
    for n in nodes:
        name = n.get('name', '')
        if name in DEFAULT_NODE_NAMES:
            generic_nodes.append(n)
        else:
            # Check numbered defaults like "HTTP Request1", "Slack2"
            numbered = re.sub(r'\d+$', '', name)
            if numbered in DEFAULT_NODE_NAMES:
                generic_nodes.append(n)
    if generic_nodes:
        sample_names = '", "'.join(n.get('name', '') for n in generic_nodes[:3])
        findings.append({
            'severity': 'suggestion',
            'title': f'Generic node names detected ({len(generic_nodes)} nodes)',
            'description': (
                f'{len(generic_nodes)} nodes still have default names like "{sample_names}". '
                "Generic names make workflows hard to understand and debug."
            ),
            'fix': (
                "Rename these nodes to describe what they do: "
                "'Slack' \u2192 'Notify team on failure', "
                "'HTTP Request' \u2192 'Fetch user profile from CRM', "
                "'If' \u2192 'Check if admin user'. "
                "This makes workflows self-documenting."
            ),
            'nodeNames': [n.get('name', '') for n in generic_nodes],
            'ruleId': 'generic-node-names',
        })

    # 12. no-sticky-notes
    non_sticky_non_trigger = [
        n for n in nodes
        if n.get('type') != 'n8n-nodes-base.stickyNote' and not _is_trigger_node(n)
    ]
    has_sticky_notes = any(n.get('type') == 'n8n-nodes-base.stickyNote' for n in nodes)
    if len(non_sticky_non_trigger) >= 5 and not has_sticky_notes:
        findings.append({
            'severity': 'suggestion',
            'title': 'No sticky notes in a complex workflow',
            'description': (
                f"This workflow has {len(non_sticky_non_trigger)} nodes but no sticky notes to document its logic. "
                "Complex workflows without documentation become hard to maintain."
            ),
            'fix': (
                "Add sticky notes to document your workflow's logic, especially around complex branching, "
                "business rules, or API-specific quirks. Future-you will thank you."
            ),
            'nodeNames': [],
            'ruleId': 'no-sticky-notes',
        })

    # 13. mega-workflow
    if len(non_sticky_non_trigger) > 15:
        count = len(non_sticky_non_trigger)
        findings.append({
            'severity': 'suggestion',
            'title': 'Large workflow \u2014 consider decomposition',
            'description': (
                f"This workflow has {count} nodes. "
                "Large monolithic workflows are harder to debug, test, and maintain."
            ),
            'fix': (
                f"This workflow has {count} nodes. Consider breaking it into smaller, reusable sub-workflows "
                "connected with the 'Execute Sub-workflow' node. Each sub-workflow should handle one concern "
                "(e.g., data fetching, transformation, notification)."
            ),
            'nodeNames': [],
            'ruleId': 'mega-workflow',
        })

    # 14. disconnected-nodes
    connected_names = _get_connected_node_ids(connections)
    disconnected = [
        n for n in nodes
        if not _is_trigger_node(n)
        and n.get('type') != 'n8n-nodes-base.stickyNote'
        and n.get('name', '') not in connected_names
    ]
    if disconnected:
        node_list = ', '.join(n.get('name', '') for n in disconnected)
        findings.append({
            'severity': 'suggestion',
            'title': 'Disconnected nodes found',
            'description': (
                f"{len(disconnected)} node(s) are not connected to any other node and will never execute."
            ),
            'fix': (
                f"These nodes are not connected to anything and will never execute: {node_list}. "
                "Remove them or connect them to the workflow."
            ),
            'nodeNames': [n.get('name', '') for n in disconnected],
            'ruleId': 'disconnected-nodes',
        })

    # 15. code-node-settimeout
    code_nodes = [
        n for n in nodes
        if n.get('type') in ('n8n-nodes-base.code', 'n8n-nodes-base.function')
    ]
    _timeout_re = re.compile(r'setTimeout|setInterval|new\s+Promise.*setTimeout')
    for node in code_nodes:
        params = node.get('parameters', {})
        code = params.get('jsCode') or params.get('code') or ''
        if _timeout_re.search(code):
            name = node.get('name', '')
            findings.append({
                'severity': 'suggestion',
                'title': 'setTimeout used in Code node',
                'description': (
                    f"The Code node '{name}' uses setTimeout/setInterval. "
                    "These can cause execution timeouts and don't integrate with n8n's workflow engine."
                ),
                'fix': (
                    "Instead of setTimeout for delays, use the n8n Wait node. "
                    "It's designed for rate limiting and pausing execution, properly integrates with the workflow engine, "
                    "and doesn't risk execution timeouts."
                ),
                'nodeNames': [name],
                'ruleId': 'code-node-settimeout',
            })

    # 16. rag-same-workflow
    vector_store_nodes = [n for n in nodes if 'vectorStore' in (n.get('type') or '')]
    if vector_store_nodes:
        has_insert = any(
            n.get('parameters', {}).get('mode') in ('insert', 'upsert')
            for n in vector_store_nodes
        )
        has_retrieve = any(
            n.get('parameters', {}).get('mode') in ('retrieve', 'load') or
            not n.get('parameters', {}).get('mode')
            for n in vector_store_nodes
        )
        if has_insert and has_retrieve:
            findings.append({
                'severity': 'suggestion',
                'title': 'RAG ingestion and retrieval in same workflow',
                'description': (
                    "This workflow both writes to and reads from a vector store. "
                    "Combining ingestion and retrieval in one workflow couples two independent concerns."
                ),
                'fix': (
                    "Split your RAG pipeline into two separate workflows: one for ingestion "
                    "(document loading \u2192 splitting \u2192 embedding \u2192 vector store insert) "
                    "and one for retrieval (query \u2192 vector store search \u2192 AI Agent). "
                    "This lets you re-ingest without affecting queries and vice versa."
                ),
                'nodeNames': [n.get('name', '') for n in vector_store_nodes],
                'ruleId': 'rag-same-workflow',
            })

    # 17. ai-agent-no-output-parser
    for agent in agent_nodes:
        downstream = _get_downstream_nodes(agent.get('name', ''), connections)
        has_structured_consumer = any(
            node_map.get(name, {}).get('type') in _STRUCTURED_CONSUMER_TYPES
            for name in downstream
        )
        if has_structured_consumer and not _has_output_parser_connected(agent.get('name', ''), connections):
            name = agent.get('name', '')
            findings.append({
                'severity': 'suggestion',
                'title': 'AI Agent without Output Parser',
                'description': (
                    f"The AI Agent '{name}' feeds into nodes that expect structured data, "
                    "but has no Output Parser connected. "
                    "This can lead to unpredictable behavior when downstream nodes try to parse freeform text."
                ),
                'fix': (
                    "Your AI Agent feeds into nodes that expect structured data, but has no Output Parser connected. "
                    "Add a Structured Output Parser to reliably get JSON responses from the LLM "
                    "instead of unpredictable freeform text."
                ),
                'nodeNames': [name],
                'ruleId': 'ai-agent-no-output-parser',
            })

    return findings
