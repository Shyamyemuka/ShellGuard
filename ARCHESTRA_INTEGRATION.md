# 🤖 Archestra AI Integration Guide

## Overview

ShellGuard is fully integrated with **Archestra MCP Gateway** for hackathon requirements. The integration provides:

✅ **MCP Tool Calling** - Uses Archestra's Model Context Protocol for command analysis  
✅ **Observability** - Sends traces to Archestra runtime  
✅ **Guardrails** - Input/output validation through Archestra  
✅ **Fallback Support** - Falls back to direct Gemini API if Archestra unavailable

---

## Configuration

### 1. Add Your API Keys to Root `.env` File

The root `.env` file (at `d:\ShellGuard\.env`) is where you paste your API keys:

```bash
# ===== LLM =====
GEMINI_API_KEY=your-google-gemini-api-key-here

# ===== ARCHESTRA =====
ARCHESTRA_API_KEY=your-archestra-mcp-gateway-token-here
ARCHESTRA_RUNTIME_URL=https://runtime.archestra.dev  # Or your runtime URL
ARCHESTRA_PROJECT_ID=shellguard
ARCHESTRA_OBSERVABILITY_ENABLED=true
ARCHESTRA_GUARDRAILS_ENABLED=true
```

### 2. How It Works

The backend config (`backend/config.py`) **automatically loads** the root `.env` file:

```python
# Loads from: d:\ShellGuard\.env
root_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(root_env_path)
```

---

## AI Analysis Flow

```
Command Entered
     │
     ▼
Pattern Matcher (instant)
     │
     ├─ CRITICAL → Block immediately
     │
     └─ MEDIUM/HIGH
         │
         ▼
    AI Analysis
         │
         ├─ 1️⃣ Try Archestra MCP Gateway first
         │     └─ POST /v1/tools/analyze_command/invoke
         │         └─ Returns: risk_level, consequences, safer_alternative
         │
         ├─ 2️⃣ If Archestra fails → Fall back to Gemini API
         │     └─ google.generativeai.generate_content()
         │
         └─ 3️⃣ If both fail → Pattern-based fallback
```

---

## MCP Tools Used

ShellGuard leverages these Archestra MCP tools:

### 1. **analyze_command**

Analyzes shell commands for risk, provides detailed breakdown

**Input:**

```json
{
  "command": "rm -rf /tmp/logs",
  "working_directory": "/home/user",
  "preliminary_risk": "medium"
}
```

**Output:**

```json
{
  "risk_level": "medium",
  "risk_score": 65,
  "allow": false,
  "title": "Recursive Deletion",
  "explanation": "...",
  "consequences": ["Data loss in /tmp/logs", "..."],
  "safer_alternative": "rm -r /tmp/logs",
  "data_loss_risk": 70,
  "service_impact_risk": 20,
  "reversibility": 10
}
```

### 2. **suggest_alternative**

Suggests safer command alternatives

### 3. **explain_command**

Provides beginner-friendly command explanations

---

## Observability

All command analyses are traced to Archestra:

```python
# Automatic tracing via archestra/observability.py
await archestra_client.send_trace(
    trace_id="uuid",
    command="dangerous command",
    risk_level="high",
    action="blocked",
    latency_ms=250,
    metadata={...}
)
```

**Metrics Tracked:**

- Total commands analyzed
- Risk distribution (safe/low/medium/high/critical)
- AI analysis latency
- Token usage
- Interceptions by pattern vs. AI
- Safe swap success rate

---

## Guardrails

Input and output validation via `archestra/guardrails.py`:

### Input Guardrails

- Command length limits
- Prompt injection detection
- Encoding validation

### Output Guardrails

- Alternative must be safer than original
- Risk scores must be within bounds
- PII scrubbing (commands truncated in traces)

---

## Verification

### Check Archestra Integration Status

When you start the backend:

```bash
cd backend
python main.py
```

You should see:

```
✅ Loaded environment from: d:\ShellGuard\.env
🤖 Archestra MCP Gateway initialized
   Runtime: https://runtime.archestra.dev
   Project: shellguard
📊 Observability initialized
🛡️  ShellGuard Backend Started
   Archestra MCP: ✅ Enabled
```

### Test Command Analysis

Run a dangerous command in ShellGuard terminal:

```bash
rm -rf /tmp/test
```

Backend logs should show:

```
🤖 Using Archestra MCP Gateway for analysis...
✅ Archestra analysis complete: Recursive Deletion Risk
```

If Archestra fails:

```
⚠️  Archestra analysis failed, falling back to Gemini...
🔮 Using Gemini API for analysis...
```

---

## Deployment (Render)

Set these environment variables in Render dashboard:

```
GEMINI_API_KEY=your-key-here
ARCHESTRA_API_KEY=your-archestra-token-here
ARCHESTRA_RUNTIME_URL=https://runtime.archestra.dev
ARCHESTRA_PROJECT_ID=shellguard
ARCHESTRA_OBSERVABILITY_ENABLED=true
ARCHESTRA_GUARDRAILS_ENABLED=true
```

---

## Code Architecture

```
backend/
├── archestra/
│   ├── mcp_client.py          ⭐ NEW: Archestra MCP Gateway client
│   ├── mcp_tools.py            Tool definitions (analyze_command, etc.)
│   ├── observability.py        Metrics + trace sending to Archestra
│   └── guardrails.py           Input/output validation
│
├── analysis/
│   └── ai_analyzer.py          ⭐ UPDATED: Uses Archestra first, Gemini fallback
│
└── config.py                   ⭐ UPDATED: Loads root .env file
```

---

## Hackathon Scoring

This integration maximizes Archestra usage for hackathon scoring:

✅ **MCP Gateway** - All AI analysis routed through Archestra  
✅ **Tool Calling** - Uses structured MCP tool definitions  
✅ **Observability** - All traces sent to Archestra runtime  
✅ **Guardrails** - Input/output validation enabled  
✅ **Runtime Integration** - Deployed using Archestra runtime URL

---

## Troubleshooting

### "Archestra MCP Gateway disabled (no API key)"

**Solution:** Check that `ARCHESTRA_API_KEY` is set in root `.env` file

### "Archestra analysis failed, falling back to Gemini..."

**Possible causes:**

- Invalid API key
- Network connectivity issues
- Archestra runtime URL incorrect
- Tool endpoint not available

**Check logs for specific error:**

```
❌ Archestra API error: 401 - Unauthorized
❌ Archestra tool call timed out after 30s
```

### Traces not appearing in Archestra dashboard

**Check:**

1. `ARCHESTRA_OBSERVABILITY_ENABLED=true` in `.env`
2. Backend logs show: `✅ Archestra analysis complete`
3. No errors like: `⚠️  Archestra trace failed: ...`

---

## Support

For hackathon support:

- Check [Archestra Platform Documentation](https://archestra.dev)
- Verify API keys in root `.env` file
- Check backend startup logs for integration status

---

**Integration Status: ✅ FULLY INTEGRATED**  
**Last Updated:** 2026-02-15
