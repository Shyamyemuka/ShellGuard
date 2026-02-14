# 🛡️ ShellGuard - AI Terminal Copilot with Safety Rails

ShellGuard is an AI-powered terminal copilot that intercepts potentially dangerous shell commands before execution, analyzes their risk, explains consequences in plain English, suggests safer alternatives, and maintains a full audit trail.

## Features

- 🖥️ **Web-based Terminal**: Fully functional terminal emulator using xterm.js
- 🔍 **Real-time Interception**: Catches dangerous commands before execution
- 🤖 **AI Analysis**: Deep risk analysis using Google Gemini
- 📊 **Risk Breakdown**: Visual risk scores for data loss, service impact, and reversibility
- 💡 **Safe Alternatives**: AI-suggested safer commands
- 📝 **Audit Trail**: Complete command history and analytics
- 🏗️ **Archestra Integration**: MCP orchestration, guardrails, and observability

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker (optional)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-org/shellguard.git
cd shellguard
```

2. Set up environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Start the backend:
```bash
cd backend
pip install -r requirements.txt
python main.py
```

4. Start the frontend:
```bash
cd frontend
npm install
npm run dev
```

5. Open http://localhost:3000

### Using Docker

```bash
docker-compose up --build
```

## Demo Commands

Try these commands to see ShellGuard in action:

- Safe: `ls -la`, `pwd`, `echo "hello"`
- Risky: `rm -rf /var/logs/*`
- Critical: `chmod 777 /etc/passwd`
- Blocked: `rm -rf /`

## Architecture

- **Frontend**: Next.js 14 + xterm.js + shadcn/ui
- **Backend**: FastAPI + Python PTY
- **AI**: Google Gemini 1.5 Flash
- **Database**: SQLite
- **Orchestration**: Archestra MCP

## License

MIT License
