# Implementation Plan: Personal AI Employee

**Branch**: `ai-employee-core` | **Date**: 2026-02-20 | **Spec**: [specs/ai_employee/spec.md](../specs/ai_employee/spec.md)

**Input**: Feature specification from `/specs/ai_employee/spec.md`

## Summary

Implementation of a Bronze-tier Personal AI Employee system that monitors an Obsidian vault, processes tasks automatically, and maintains structured outputs. The system will use Python 3.13 with a filesystem watcher to detect new files, Claude Code for AI processing, and maintain a structured vault with designated folders for different workflow stages.

## Technical Context

**Language/Version**: Python 3.13 with uv package management
**Primary Dependencies**: python-watchdog, python-dotenv, claude CLI
**Storage**: File-based (Obsidian markdown files on local filesystem)
**Testing**: pytest for unit and integration tests
**Target Platform**: Cross-platform (macOS/Linux/Windows)
**Project Type**: Single application with file processing capabilities
**Performance Goals**: Real-time file monitoring with sub-second response time for new files
**Constraints**: All processing must occur locally; no external network calls by default; human approval required for external actions
**Scale/Scope**: Single-user local system supporting up to 1000 files in vault

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ LOCAL-FIRST: All data stays on local machine, Obsidian vault as single source of truth
- ✅ SECURITY: Credentials in .env file only, never committed to git
- ✅ HUMAN-IN-THE-LOOP: External actions require human moving file to /Approved
- ✅ AGENT SKILLS: AI logic implemented as SKILL.md files for Claude Code
- ✅ DRY-RUN DEFAULT: Scripts default to DRY_RUN=true during development
- ✅ PYTHON 3.13+: All scripts use Python 3.13+ with uv for package management
- ✅ FAIL SAFE: Scripts log and pause on errors, no silent retries
- ✅ AUDITABILITY: Actions logged to /Vault/Logs/YYYY-MM-DD.json

## Project Structure

### Documentation (this feature)

```text
specs/ai_employee/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
personal-ai-employee/
├── .env.example
├── .gitignore
├── README.md
├── pyproject.toml
├── src/
│   ├── base_watcher.py
│   └── filesystem_watcher.py
├── AI_Employee_Vault/
│   ├── Dashboard.md
│   ├── Company_Handbook.md
│   ├── skills/
│   │   ├── SKILL_triage.md
│   │   └── SKILL_dashboard_update.md
│   ├── Inbox/
│   ├── Needs_Action/
│   ├── Done/
│   ├── Logs/
│   ├── Pending_Approval/
│   └── Approved/
└── scripts/
    └── run_claude.sh
```

**Structure Decision**: Single project structure chosen to house the AI employee core functionality with dedicated source files, vault structure, and helper scripts.

## Component Architecture

### 1. Filesystem Watcher (`src/filesystem_watcher.py`)
- Monitors `/AI_Employee_Vault/Inbox` using python-watchdog
- Copies new files to `/Needs_Action` with metadata sidecar
- Creates JSON log entries in `/Logs`
- Implements fail-safe mechanisms to pause on errors

### 2. Vault Structure (`AI_Employee_Vault/`)
- Organized folder structure with dedicated workflow states
- Dashboard.md for status reporting
- Company_Handbook.md for AI behavior rules
- Skills folder containing SKILL.md files for Claude Code

### 3. AI Processing Scripts (`scripts/run_claude.sh`)
- Shell script to trigger Claude Code processing
- Can be scheduled with cron/Task Scheduler
- Handles dry-run mode for development

### 4. Configuration (`pyproject.toml`, `.env.example`)
- Python project configuration with dependencies
- Environment variable template for credentials

### 5. Build & Deployment
- PM2 configuration to keep watcher running
- Cross-platform setup for easy deployment

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| | | |