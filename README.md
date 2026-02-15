# 🛡️ ShellGuard

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)

> An intelligent terminal safety layer that intercepts dangerous shell commands before execution, uses AI to analyze risk, and suggests safer alternatives.

**ShellGuard** prevents catastrophic terminal mistakes while helping you learn safer command-line practices. It intercepts risky commands, explains consequences in plain English, and maintains a complete audit trail.

---

## ✨ Key Features

- **🖥️ Web-Based Terminal** — Full-featured browser terminal with xterm.js
- **🔍 Real-Time Interception** — Captures commands before execution (<5ms for safe commands)
- **🤖 AI Risk Analysis** — Google Gemini powered risk assessment with structured scoring
- **💡 Safer Alternatives** — AI-generated safe commands that achieve the same goal
- **📝 Audit Trail** — Complete command history with timestamps and actions
- **🏗️ Archestra MCP Integration** — Agent orchestration with guardrails and observability
- **🔒 Hard Blocks** — Catastrophic commands (like `rm -rf /`) blocked instantly
- **🏖️ Sandbox Mode** — Isolated execution environment for safe deployment

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Google Gemini API key ([get one here](https://ai.google.dev/))

### Installation

1. **Clone and configure**

   ```bash
   git clone https://github.com/Shyamyemuka/ShellGuard.git
   cd ShellGuard
   cp .env.example .env
   # Add your GOOGLE_API_KEY to .env
   ```

2. **Start backend**

   ```bash
   cd backend
   pip install -r requirements.txt
   python main.py
   ```

3. **Start frontend** (new terminal)

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Open** `http://localhost:3000`

### Docker (Alternative)

```bash
docker-compose up --build
```

---

## 🎮 How It Works

1. **Type** a command in the terminal
2. **Safe commands** execute instantly (<5ms)
3. **Risky commands** trigger AI analysis (1-3s)
4. **Warning overlay** shows risks and safer alternatives
5. **Choose** to approve, use safe alternative, or cancel
6. **All actions** logged for audit trail

### Example

```bash
$ rm -rf /var/log/*
```

ShellGuard intercepts and shows:

- ⚠️ **HIGH RISK**: Recursive Force Delete
- **Consequences**: Permanent deletion, no undo, system logs lost
- **Safer Alternative**: `find /var/log -type f -mtime +30 -delete`
- **Actions**: ✅ Approve | 🔄 Use Safe | ❌ Cancel

---

## 📚 Documentation

- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** — Production deployment instructions
- **[Archestra Integration](ARCHESTRA_INTEGRATION.md)** — MCP setup and guardrails
- **[Render Deployment](RENDER_DEPLOY.md)** — Deploy to Render.com
- **[SRS Document](SRS.md)** — Full requirements specification

---

## 🛠️ Tech Stack

| Component      | Technology                         |
| -------------- | ---------------------------------- |
| Frontend       | Next.js 14, xterm.js, Tailwind CSS |
| Backend        | FastAPI, Python 3.11+              |
| AI             | Google Gemini 1.5 Flash            |
| Agent Platform | Archestra MCP                      |
| Database       | SQLite 3                           |
| Deployment     | Docker, docker-compose             |

---

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built with ❤️ by **Team Penna** for Hack All February 2025.

Special thanks to:

- **Archestra** for the MCP platform
- **Google Gemini** for AI analysis
- **xterm.js** for the terminal emulator

---

**Repository**: [github.com/Shyamyemuka/ShellGuard](https://github.com/Shyamyemuka/ShellGuard)
