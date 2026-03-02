# Implementation Plan: Silver Tier Features

**Branch**: `1-silver-tier` | **Date**: 2026-03-02 | **Spec**: [specs/1-silver-tier/spec.md](../specs/1-silver-tier/spec.md)

**Input**: Feature specification from `/specs/1-silver-tier/spec.md`

## Summary

Implementation of Silver tier features for the Personal AI Employee system, adding Gmail integration, email automation, LinkedIn posting capabilities, and enhanced human-in-the-loop workflows. The system will extend the existing Bronze tier foundation with external API integrations while maintaining local-first architecture and human approval requirements for all external communications.

## Technical Context

**Language/Version**: Python 3.13 with uv package management
**Primary Dependencies**:
- google-api-python-client for Gmail integration
- google-auth-oauthlib for OAuth2 authentication
- linkedin-api library or requests for LinkedIn API v2
- playwright for WhatsApp Web automation
- watchdog for filesystem monitoring
- python-dotenv for environment management
- google-genai for AI processing (existing)

**Storage**: File-based (Obsidian markdown files on local filesystem, extended with external API data)
**Testing**: pytest for unit and integration tests
**Target Platform**: Cross-platform (macOS/Linux/Windows)
**Project Type**: Extension of existing Personal AI Employee application with external API integrations
**Performance Goals**: Gmail sync every 5 minutes, LinkedIn post generation under 10 seconds, email processing under 30 seconds
**Constraints**: All processing must occur locally; human approval required for all external actions; credentials in .env only; rate limiting enforced
**Scale/Scope**: Single-user system supporting up to 1000 emails/week and 3 LinkedIn posts/day

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ LOCAL-FIRST: All data stays on local machine, Obsidian vault as single source of truth
- ✅ SECURITY: Credentials in .env file only, never committed to git
- ✅ HUMAN-IN-THE-LOOP: External actions require human moving file to /Approved
- ✅ AGENT SKILLS: AI logic implemented as SKILL.md files for Gemini processing
- ✅ DRY-RUN DEFAULT: Scripts default to DRY_RUN=true during development
- ✅ PYTHON 3.13+: All scripts use Python 3.13+ with uv for package management
- ✅ FAIL SAFE: Scripts log and pause on errors, no silent retries
- ✅ AUDITABILITY: Actions logged to /Vault/Logs/YYYY-MM-DD.json
- ✅ GMAIL CREDENTIALS (Silver tier): Gmail API credentials stored in .env only, never in vault
- ✅ WHATSAPP AUTOMATION (Silver tier): WhatsApp automation via Playwright - always ask human approval before replying
- ✅ LINKEDIN POSTS (Silver tier): LinkedIn posts go to Pending_Approval folder first, never auto-post
- ✅ EMAIL APPROVAL (Silver tier): Email replies require human approval for unknown contacts
- ✅ WATCHER PATTERNS (Silver tier): All new watchers follow base_watcher.py pattern
- ✅ RATE LIMITING (Silver tier): max 10 emails processed per run, max 3 LinkedIn posts per day

## Project Structure

### Documentation (this feature)

```text
specs/1-silver-tier/
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
│   ├── ai_processor.py
│   ├── gmail_watcher.py          # New: Gmail integration
│   ├── email_mcp.py              # New: Email processing server
│   ├── linkedin_poster.py        # New: LinkedIn posting
│   └── dashboard_updater.py
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
│   └── Approved/                 # New: For approved actions
└── scripts/
    └── process_tasks.bat
```

**Structure Decision**: Extends existing project structure to house the Silver tier functionality with dedicated source files for each new feature while maintaining backward compatibility with existing Bronze tier features.

## Component Architecture

### 1. Gmail Watcher (`src/gmail_watcher.py`)
- Monitors Gmail for unread emails using google-api-python-client
- Authenticates with OAuth2 using credentials from .env
- Saves each email as .md file in Needs_Action folder
- Includes: sender, subject, date, email body snippet
- Marks emails as read after processing
- Implements rate limiting to stay within API quotas

### 2. Email MCP Server (`src/email_mcp.py`)
- Drafts email replies using Gemini AI based on original email content
- Saves draft replies to Pending_Approval folder
- Waits for human approval before sending
- Sends emails only after file moved to Approved folder
- Logs all sent emails to Logs folder

### 3. LinkedIn Poster (`src/linkedin_poster.py`)
- Generates weekly business posts using Gemini AI
- Uses trending topics in user's industry for content
- Saves post drafts to Pending_Approval folder
- Posts to LinkedIn only after human approval
- Enforces rate limit of max 3 posts per day

### 4. Approved Folder Watcher (extends existing base_watcher.py)
- Monitors Approved folder for approved files
- Executes approved actions automatically (send email, post to LinkedIn)
- Moves processed files to Done folder
- Logs all actions to Logs folder

### 5. Vault Structure Extension
- Maintains existing folder structure
- Adds Approved folder for approved actions
- Updates dashboard to show new workflow status

### 6. Configuration (`pyproject.toml`, `.env.example`)
- Python project configuration with Silver tier dependencies
- Environment variable template for Gmail, LinkedIn, and other API credentials

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| | | |