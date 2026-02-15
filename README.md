# 🛡️ ShellGuard - AI Terminal Copilot with Safety Rails

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)

> An intelligent terminal safety layer that intercepts dangerous shell commands before execution, analyzes their risk using AI, explains consequences in plain English, suggests safer alternatives, and maintains a complete audit trail.

**ShellGuard** acts as a safety copilot between you and your terminal, preventing catastrophic mistakes while helping you learn safer command-line practices. Unlike traditional command-line restrictions, ShellGuard uses AI to understand command intent and context, providing educational feedback alongside protection.

---

## 🎯 Problem Statement

Every engineer has a horror story about a mistyped or copy-pasted command that caused damage:

- `rm -rf /` instead of `rm -rf ./`
- Running untrusted scripts from the internet with `curl | bash`
- Accidentally deleting production data
- Breaking system permissions with overly permissive `chmod` commands

Traditional solutions either:

- Block commands entirely (restrictive, frustrating)
- Offer no protection (dangerous)
- Require complex configuration (time-consuming)

**ShellGuard solves this by:**

1. **Intercepting** commands before execution
2. **Analyzing** risk using pattern matching + AI
3. **Explaining** what the command does and why it's dangerous
4. **Suggesting** safer alternatives
5. **Logging** everything for audit and learning

### 🏖️ **Sandbox Protection for Deployment**

When deployed, ShellGuard runs in **sandbox mode** by default:

- Terminal sessions run in an isolated directory (`/tmp/shellguard_sandbox`)
- Your application code and environment variables are protected
- Users can safely test dangerous commands without affecting the server
- Perfect for demos, hackathons, and learning environments

✅ **Deploy publicly without worrying** - the sandbox keeps your deployment safe!

---

## ✨ Key Features

### 🖥️ **Web-Based Terminal Emulator**

- Full-featured terminal in your browser using **xterm.js**
- Real PTY (pseudo-terminal) backend with actual shell session
- Supports ANSI colors, escape sequences, scrollback, copy/paste
- Dynamic resizing and JetBrains Mono/Fira Code fonts

### 🔍 **Real-Time Command Interception**

- Captures commands **before** execution
- Zero-latency pass-through for safe commands (<5ms)
- Two-tier analysis architecture:
  - **Tier 1**: Instant pattern matching (no API calls)
  - **Tier 2**: Deep AI analysis for nuanced risks

### 🤖 **AI-Powered Risk Analysis**

- **Google Gemini 1.5 Flash** for fast, accurate analysis
- Structured risk assessment with:
  - Risk level: Critical / High / Medium / Low / Safe
  - Risk score: 0-100 numerical rating
  - Data loss risk percentage
  - Service impact risk percentage
  - Reversibility rating
- Context-aware analysis (working directory, user, shell type)
- Command breakdown with flag-by-flag explanation

### 📊 **Visual Risk Breakdown**

- Interactive warning overlay with:
  - Color-coded risk badges
  - Consequence mapping (bullet points of what could happen)
  - Risk bars (data loss, service impact, irreversibility)
  - Affected scope description
  - Command part-by-part breakdown

### 💡 **Intelligent Safer Alternatives**

- AI-generated safer commands that achieve the same goal
- Side-by-side comparison of original vs. safe alternative
- Explanation of why the alternative is safer
- One-click "Use Safe Alternative" button

### 📝 **Complete Audit Trail**

- Full command history with timestamps
- Logs every command: safe, warned, approved, cancelled, blocked
- Session statistics dashboard showing:
  - Total commands entered
  - Interception rate
  - Safe swap rate
  - Blocked commands count
- SQLite persistence (survives restarts)

### 🏗️ **Deep Archestra Integration**

- **MCP (Model Context Protocol)** agent orchestration
- **3 MCP Tools**: `analyze_command`, `suggest_alternative`, `explain_command`
- **Security Guardrails**:
  - Alternative safety validation
  - Prompt injection prevention
  - PII scrubbing
  - Catastrophic command hard blocks
- **Observability**: Traces, metrics, latency tracking

### 🔒 **Hard Command Blocks**

Certain catastrophic commands are **immediately blocked** without AI delay:

- `rm -rf /` (filesystem destruction)
- Fork bombs `:(){ :|:& };:`
- Writing to block devices `dd if=/dev/zero of=/dev/sda`
- Piping remote scripts to sudo `curl ... | sudo bash`
- Making entire filesystem world-writable `chmod -R 777 /`

---

## 🏛️ System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                          │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────────┐  │
│  │  xterm.js    │  │  Warning    │  │  Analysis Panel      │  │
│  │  Terminal    │  │  Overlay    │  │  (Risk Breakdown)    │  │
│  │  Emulator    │  │  Component  │  │                      │  │
│  └──────┬───────┘  └─────────────┘  └──────────────────────┘  │
└─────────┼──────────────────────────────────────────────────────┘
          │ WebSocket (bidirectional)
┌─────────▼──────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ WebSocket Handler → Command Interceptor                  │  │
│  └────────┬─────────────────────┬───────────────────────────┘  │
│           │ (safe)              │ (risky)                       │
│           ▼                     ▼                               │
│  ┌─────────────────┐   ┌─────────────────────────────────────┐ │
│  │  PTY Manager    │   │  ARCHESTRA MCP ORCHESTRATION        │ │
│  │  (bash/zsh)     │   │  ┌────────────────────────────────┐ │ │
│  └─────────────────┘   │  │ Risk Analyzer Agent            │ │ │
│                        │  │ Alternative Suggester Agent    │ │ │
│                        │  │ Command Explainer Agent        │ │ │
│                        │  │ Guardrails + Observability     │ │ │
│                        │  └────────────────────────────────┘ │ │
│                        └─────────────────────────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           DATA LAYER (SQLite + Patterns)                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### How Command Interception Works

1. **Keystroke Buffering**: User types in browser → buffered on backend
2. **Enter Detection**: When user presses Enter → command extracted
3. **Quick Pattern Check** (Tier 1, <10ms):
   - Safe → execute immediately in PTY
   - Medium/High risk → send to AI
   - Critical → hard block
4. **AI Analysis** (Tier 2, 1-3s):
   - MCP `analyze_command` tool invoked
   - Gemini returns structured risk assessment
   - MCP `suggest_alternative` tool generates safer option
5. **Guardrails Applied**: Alternative validated, output sanitized
6. **Warning Displayed**: User sees overlay with analysis
7. **User Decision**:
   - ✅ Approve → execute original
   - 🔄 Use Safe → execute alternative
   - ❌ Cancel → abort
8. **Logging**: Full interaction logged to SQLite

---

## 📦 Project Structure

```
ShellGuard/
├── backend/                     # Python FastAPI backend
│   ├── main.py                  # Entry point + WebSocket routes
│   ├── config.py                # Environment configuration
│   ├── core/                    # Core terminal functionality
│   │   ├── terminal.py          # PTY session manager (Linux/macOS)
│   │   ├── terminal_windows.py  # PTY alternative for Windows
│   │   ├── interceptor.py       # Command interception logic
│   │   ├── session.py           # ShellGuard session handler
│   │   └── buffer.py            # Command line input buffer
│   ├── analysis/                # Risk analysis modules
│   │   ├── pattern_matcher.py   # Fast pattern-based detection
│   │   ├── ai_analyzer.py       # Google Gemini integration
│   │   ├── risk_scorer.py       # Risk score computation
│   │   └── alternative_generator.py  # Safer alternatives
│   ├── archestra/               # Archestra integration
│   │   ├── mcp_tools.py         # MCP tool definitions
│   │   ├── guardrails.py        # Security guardrails
│   │   └── observability.py     # Metrics and tracing
│   ├── data/                    # Data layer
│   │   ├── database.py          # SQLite setup and queries
│   │   ├── models.py            # Data models
│   │   ├── patterns.py          # Dangerous command patterns
│   │   └── seed.py              # Demo data seeding
│   ├── api/                     # API routes
│   │   ├── websocket_handler.py # WebSocket message routing
│   │   ├── routes.py            # REST API (history, stats)
│   │   └── schemas.py           # Pydantic schemas
│   └── tests/                   # Backend tests
│
├── frontend/                    # Next.js 14 frontend
│   ├── src/
│   │   ├── app/                 # Next.js app router
│   │   │   ├── page.tsx         # Main terminal page
│   │   │   ├── dashboard/       # Analytics dashboard
│   │   │   └── globals.css      # Global styles
│   │   ├── components/          # React components
│   │   │   ├── terminal/        # Terminal components
│   │   │   ├── warning/         # Warning overlay
│   │   │   ├── panels/          # Analysis/history panels
│   │   │   └── shared/          # Shared UI components
│   │   ├── hooks/               # React hooks
│   │   │   ├── useTerminalSocket.ts
│   │   │   ├── useCommandHistory.ts
│   │   │   └── useSessionStats.ts
│   │   ├── lib/                 # Utilities
│   │   │   ├── websocket.ts
│   │   │   ├── api.ts
│   │   │   └── utils.ts
│   │   └── types/               # TypeScript types
│   ├── package.json
│   └── Dockerfile
│
├── docs/
│   └── SRS.md                   # Software Requirements Specification
├── docker-compose.yml           # Docker orchestration
├── .env.example                 # Environment variables template
└── README.md                    # This file
```

---

## 🚀 Getting Started

### Prerequisites

| Requirement               | Version | Purpose                  |
| ------------------------- | ------- | ------------------------ |
| **Python**                | 3.11+   | Backend runtime          |
| **Node.js**               | 20+     | Frontend build           |
| **pip**                   | Latest  | Python package manager   |
| **npm**                   | Latest  | Node package manager     |
| **Docker** (optional)     | Latest  | Containerized deployment |
| **Google Gemini API Key** | -       | AI analysis              |

### Installation

#### Option 1: Local Development

1. **Clone the repository**

   ```bash
   git clone https://github.com/Shyamyemuka/ShellGuard.git
   cd ShellGuard
   ```

2. **Set up environment variables**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your Google Gemini API key:

   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   BACKEND_PORT=8000
   FRONTEND_PORT=3000
   WEBSOCKET_URL=ws://localhost:8000/ws/terminal
   ```

3. **Start the backend**

   ```bash
   cd backend
   pip install -r requirements.txt
   python main.py
   ```

   Backend will start on `http://localhost:8000`

4. **Start the frontend** (in a new terminal)

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   Frontend will start on `http://localhost:3000`

5. **Open the app**

   Navigate to `http://localhost:3000` in your browser

#### Option 2: Docker Deployment

```bash
docker-compose up --build
```

Access the app at `http://localhost:3000`

---

## 🎮 Usage Guide

### Basic Terminal Usage

- Type commands as you normally would in a terminal
- Safe commands execute instantly with no interruption
- Dangerous commands trigger the warning overlay

### Understanding the Warning Overlay

When a risky command is detected, you'll see:

**Header**

- 🛡️ ShellGuard logo
- Risk level badge (color-coded)

**Command Display**

- Your command highlighted in monospace

**Risk Analysis**

- **Title**: Short description (e.g., "Recursive Force Delete")
- **Explanation**: What the command does and why it's dangerous
- **Consequences**: Bullet points of potential outcomes

**Risk Breakdown Bars**

- 📊 Data Loss Risk: 0-100%
- 🔧 Service Impact Risk: 0-100%
- 🔄 Irreversibility: 0-100% (higher = harder to undo)

**Safer Alternative** (when available)

- Green-highlighted alternative command
- Explanation of why it's safer

**Action Buttons**

- ✅ **Approve**: Execute the original risky command
- 🔄 **Use Safe Alternative**: Execute the suggested safer command
- ❌ **Cancel**: Abort, don't execute anything

### Keyboard Shortcuts

| Key      | Action                               |
| -------- | ------------------------------------ |
| `Enter`  | Approve and execute original command |
| `S`      | Use safe alternative                 |
| `Escape` | Cancel                               |

### Example Workflows

#### Workflow 1: Learning from Mistakes

```bash
# You type:
$ rm -rf /var/log/*

# ShellGuard intercepts and shows:
⚠️ HIGH RISK: Recursive Force Delete
- Permanently deletes all files in /var/log
- No confirmation, no undo
- System logs will be lost
- May break log rotation

Safer Alternative:
$ find /var/log -type f -name "*.log" -mtime +30 -delete

✅ Approve  🔄 Use Safe  ❌ Cancel
```

#### Workflow 2: Blocking Catastrophic Commands

```bash
# You type:
$ rm -rf /

# ShellGuard IMMEDIATELY blocks:
⛔ BLOCKED: Recursive Force Delete on Root Filesystem
This command is catastrophically dangerous and cannot be approved.

❌ Cancel (only option)
```

#### Workflow 3: Understanding Complex Commands

```bash
# You type:
$ docker system prune -a --volumes

# ShellGuard warns and breaks down:
⚠️ MEDIUM RISK: Container and Volume Cleanup

Command Breakdown:
- docker system prune: Remove unused Docker data
- -a: Remove ALL unused images (not just dangling)
- --volumes: Also remove volumes

Consequences:
- Deleted images must be re-downloaded
- Data in volumes will be permanently lost
- May break local development environments

Safer Alternative:
$ docker system prune --volumes
(Removes -a flag to preserve tagged images)
```

---

## 📊 Analytics Dashboard

Access `/dashboard` to view:

- **Summary Cards**
  - Total commands analyzed
  - Total interceptions
  - Safe swap rate %
  - Average risk score

- **Risk Distribution Chart**
  - Pie chart: commands by risk level

- **Interception Timeline**
  - Line chart: command volume over time

- **Top Dangerous Commands**
  - Ranked list of most-intercepted patterns

- **Recent Interceptions**
  - Table of last 20 intercepted commands

---

## 🔌 API Reference

### WebSocket API

**Endpoint**: `ws://localhost:8000/ws/terminal`

**Client → Server Messages**:

```typescript
{
  "type": "input",
  "data": string  // Keystroke data
}

{
  "type": "resize",
  "cols": number,
  "rows": number
}
```

**Server → Client Messages**:

```typescript
// Terminal output
{
  "type": "output",
  "data": string
}

// Command warning
{
  "type": "warning",
  "command": string,
  "analysis": AIAnalysis
}

// Analysis in progress
{
  "type": "analyzing"
}
```

### REST API

#### `GET /api/stats`

Get session and all-time statistics

**Response**:

```json
{
  "session": {
    "total_commands": 45,
    "safe_commands": 38,
    "warnings_issued": 7,
    "approved": 2,
    "safe_swaps": 4,
    "cancelled": 1,
    "blocked": 0,
    "interception_rate": 15.6,
    "safe_swap_rate": 57.1
  },
  "all_time": { ... }
}
```

#### `GET /api/history`

Get command history (paginated)

**Query Params**:

- `limit`: Number of entries (default: 50)
- `offset`: Pagination offset
- `risk_level`: Filter by risk (safe/low/medium/high/critical)

**Response**:

```json
[
  {
    "id": "uuid",
    "command": "rm -rf /tmp/old",
    "timestamp": "2025-02-14T12:34:56Z",
    "risk_level": "medium",
    "action": "safe_swap",
    "alternative_used": "rm -r /tmp/old",
    "analysis": { ... }
  }
]
```

---

## 🛡️ Dangerous Command Patterns

ShellGuard detects **50+ dangerous patterns** across these categories:

### Critical (Immediate Block)

- `rm -rf /` — Root filesystem deletion
- `:(){ :|:& };:` — Fork bomb
- `dd if=/dev/zero of=/dev/sda` — Overwriting disk
- `> /dev/sda` — Redirecting to block device
- `chmod -R 777 /` — Making filesystem world-writable
- `curl ... | sudo bash` — Piping remote script to root

### High Risk (AI Analysis)

- `rm -rf` — Recursive force delete
- `DROP TABLE`, `TRUNCATE` — Database destruction
- `kill -9`, `killall` — Force process termination
- `shutdown`, `reboot`, `halt` — Service disruption
- `chmod 777` — Dangerous permissions

### Medium Risk (AI Analysis)

- `apt remove`, `yum remove` — Package removal
- `iptables -F`, `ufw disable` — Firewall changes
- `systemctl stop` — Service management
- `docker system prune` — Container cleanup
- `git push --force` — Force push

### Low Risk (Usually passes)

- `chmod` (non-recursive, non-777)
- `kill` (without -9)
- Configuration file edits

---

## 🔐 Security & Privacy

### Data Storage

- All command history stored **locally** in SQLite
- No command data sent to third parties (except AI API for analysis)
- Database file: `backend/data/shellguard.db`

### API Key Security

- Google Gemini API key stored in `.env` (not committed to Git)
- API calls made server-side only
- Guardrails prevent prompt injection attacks

### Guardrails

- **Input**: Command length limits, injection prevention, encoding validation
- **Output**: Alternative safety validation, PII scrubbing, risk score bounds
- **Hard Blocks**: Catastrophic commands blocked without AI (no API exposure)

### Observability

- All MCP tool invocations traced via Archestra
- Latency metrics tracked
- Token usage monitored

---

## 🧪 Testing

### Running Backend Tests

```bash
cd backend
pytest tests/
```

### Test Coverage

- `test_pattern_matcher.py`: Pattern detection accuracy
- `test_interceptor.py`: Command interception logic
- `test_risk_scorer.py`: Risk score calculations

---

## 🛠️ Technology Stack

| Component               | Technology               | Purpose                      |
| ----------------------- | ------------------------ | ---------------------------- |
| **Frontend Framework**  | Next.js 14 (App Router)  | React-based UI framework     |
| **Terminal Emulator**   | xterm.js 5.3 + FitAddon  | Browser-based terminal       |
| **UI Components**       | shadcn/ui + Tailwind CSS | Pre-built, styled components |
| **Icons**               | Lucide React             | Consistent icon set          |
| **Backend Framework**   | FastAPI (Python 3.11+)   | Async WebSocket API          |
| **Terminal Backend**    | Python `pty` module      | Real shell PTY sessions      |
| **WebSocket**           | FastAPI WebSocket        | Bidirectional real-time      |
| **AI/LLM**              | Google Gemini 1.5 Flash  | Fast risk analysis           |
| **Agent Orchestration** | Archestra MCP SDK        | AI agent management          |
| **Security**            | Archestra Guardrails     | Command safety enforcement   |
| **Observability**       | Archestra Observability  | Metrics and tracing          |
| **Database**            | SQLite 3                 | Embedded, zero-config        |
| **Deployment**          | Docker + docker-compose  | Containerized deployment     |

---

## 📝 Configuration

### Environment Variables

**Backend** (`.env` in root):

```env
# Required
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional
BACKEND_PORT=8000
LOG_LEVEL=INFO
DATABASE_PATH=backend/data/shellguard.db
MAX_COMMAND_LENGTH=10000
AI_TIMEOUT_SECONDS=5
```

**Frontend** (`.env.local` in frontend/):

```env
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/terminal
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Customizing Risk Patterns

Edit `backend/data/patterns.py` to add/modify dangerous patterns:

```python
PATTERNS = {
    "critical": [
        {
            "pattern": r"rm\s+-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*\s+/",
            "title": "Root Filesystem Deletion",
            "block": True  # Hard block
        }
    ],
    "high": [
        {
            "pattern": r"rm\s+-rf",
            "title": "Recursive Force Delete",
            "block": False  # AI analysis
        }
    ],
    # ... more patterns
}
```

---

## 🤝 Contributing

Contributions are welcome! Here's how to help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for frontend (strict mode)
- Add tests for new features
- Update documentation as needed

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: "Cannot connect to WebSocket"

- **Solution**: Ensure backend is running on port 8000
- Check `NEXT_PUBLIC_WS_URL` in frontend `.env.local`

**Issue**: "Google API key invalid"

- **Solution**: Verify `GOOGLE_API_KEY` in backend `.env`
- Get a key from: https://ai.google.dev/

**Issue**: "PTY not working on Windows"

- **Solution**: Use WSL (Windows Subsystem for Linux)
- Or use `terminal_windows.py` (limited functionality)

**Issue**: "Commands not being intercepted"

- **Solution**: Check browser console for WebSocket errors
- Ensure `interceptor.py` is active in backend logs

---

## 📜 License

This project is licensed under the **MIT License**.

See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Archestra** — For sponsoring the hackathon and providing the MCP platform
- **Google Gemini** — For the AI analysis API
- **xterm.js** — For the excellent terminal emulator
- **FastAPI** — For the modern, fast Python web framework
- **Next.js** — For the powerful React framework
- **shadcn/ui** — For beautiful, accessible components

---

## 📬 Contact

**Team Penna**

- GitHub: [@Shyamyemuka](https://github.com/Shyamyemuka)
- Repository: [ShellGuard](https://github.com/Shyamyemuka/ShellGuard)

---

## 🎓 Learn More

### Why ShellGuard?

ShellGuard was built for the **Hack All February Series** (Archestra-sponsored hackathon) to solve a real problem: **terminal commands are unforgiving**.

Unlike code that can be reviewed and tested, terminal commands execute instantly and irreversibly. ShellGuard brings:

- **Safety** without sacrificing speed for safe commands
- **Education** through explanations and alternatives
- **Transparency** via complete audit trails
- **Intelligence** using AI to understand intent

### Use Cases

1. **Junior Developers**: Learn command-line safety in a forgiving environment
2. **System Administrators**: Prevent accidental production damage
3. **Security Teams**: Audit and enforce command policies
4. **DevOps Engineers**: Add safety rails to automation workflows
5. **Educators**: Teach Linux/shell scripting with built-in guardrails

---

## 🚀 Future Roadmap

- [ ] **Multi-user support** with role-based access control
- [ ] **Custom rule authoring UI** for pattern management
- [ ] **Native CLI tool** (zsh/bash plugin)
- [ ] **Mobile interface** for remote server management
- [ ] **SIEM integration** for enterprise compliance
- [ ] **Command suggestion autocomplete** (proactive safety)
- [ ] **Machine learning** to learn user-specific patterns
- [ ] **Collaborative mode** for pair programming

---

**Built with ❤️ by Team Penna for Hack All February 2025**
