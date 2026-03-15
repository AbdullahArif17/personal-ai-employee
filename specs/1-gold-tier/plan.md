# Implementation Plan: Gold Tier Features

**Branch**: `1-gold-tier` | **Date**: 2026-03-02 | **Spec**: [specs/1-gold-tier/spec.md](../specs/1-gold-tier/spec.md)

**Input**: Feature specification from `/specs/1-gold-tier/spec.md`

## Summary

Implementation of Gold tier features for the Personal AI Employee system. This extends the Silver tier capabilities to include advanced automation loops, social media integration (Twitter/X, Facebook, Instagram), business accounting integration (Odoo), and automated weekly business auditing. The system maintains the human-in-the-loop approach and local-first architecture while adding these advanced capabilities.

## Technical Context

**Language/Version**: Python 3.13 with uv package management
**Primary Dependencies**:
- google-api-python-client for Gmail integration
- google-auth-oauthlib for OAuth2 authentication
- linkedin-api library or requests for LinkedIn API v2
- playwright for WhatsApp Web automation
- tweepy or twitter-api-python for Twitter/X integration
- facebook-sdk or requests for Facebook/Instagram via Meta Graph API
- odoo-rpc or requests for Odoo JSON-RPC API
- apscheduler for scheduling the weekly audit
- watchdog for filesystem monitoring
- python-dotenv for environment management
- google-genai for AI processing (existing)

**Storage**: File-based (Obsidian markdown files on local filesystem, extended with external API data)
**Testing**: pytest for unit and integration tests
**Target Platform**: Cross-platform (macOS/Linux/Windows)
**Project Type**: Extension of existing Personal AI Employee application with external API integrations
**Performance Goals**: Ralph loop iteration under 30s, social media post generation under 10s, Odoo operations under 5s, weekly audit under 5 minutes
**Constraints**: All processing occurs locally on user's machine; human approval required for all external communications; credentials in .env file only; rate limiting enforced
**Scale/Scope**: Single-user system supporting up to 1000 emails/week, 5 Twitter posts/day, 3 Facebook/Instagram posts/day, 10 Odoo invoices/day

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ LOCAL-FIRST: All data stays on local machine, Obsidian vault is the single source of truth
- ✅ SECURITY: Credentials in .env file only, never stored in vault or committed to git
- ✅ HUMAN-IN-THE-LOOP: No external action (email send, social post, payment) executes without human moving file to /Approved
- ✅ AGENT SKILLS: AI logic implemented as SKILL.md files that Claude Code can read and follow
- ✅ DRY-RUN DEFAULT: All scripts default to DRY_RUN=true during development
- ✅ PYTHON 3.13+: All scripts use Python 3.13 or higher with uv for package management
- ✅ FAIL SAFE: On any error, scripts log and pause — never silently skip or auto-retry destructive actions
- ✅ AUDITABILITY: Every action the AI takes is logged to /Vault/Logs/YYYY-MM-DD.json
- ✅ RATE LIMITING: Enforced limits (max 5 Twitter posts/day, max 3 Facebook/Instagram posts/day, max 10 Odoo invoices/day)
- ✅ GEMINI MODEL: All AI processing uses gemma-3-27b-it model as specified
- ✅ VAULT PATH: Uses correct vault path D:\giaic\personal-ai-employee\AI_Employee_Vault

## Project Structure

### Documentation (this feature)

```text
specs/1-gold-tier/
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
│   ├── gmail_watcher.py
│   ├── email_mcp.py
│   ├── linkedin_poster.py
│   ├── approved_watcher.py
│   ├── ralph_loop.py          # New: Ralph Wiggum autonomous loop
│   ├── twitter_poster.py      # New: Twitter/X integration
│   ├── social_media_poster.py # New: Facebook/Instagram integration
│   ├── odoo_integration.py    # New: Odoo accounting integration
│   ├── weekly_audit.py        # New: Weekly business audit
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
│   ├── Approved/
│   └── Approved/             # New: For approved actions
└── scripts/
    └── process_tasks_gold.bat # New: Script for Gold tier features
```

**Structure Decision**: Extends existing project structure to house the Gold tier functionality with dedicated source files for each new feature while maintaining backward compatibility with existing Bronze and Silver tier features.

## Component Architecture

### 1. Ralph Wiggum Loop (`src/ralph_loop.py`)
- Monitors Needs_Action folder for tasks
- Processes each task with gemma-3-27b-it AI model
- If task incomplete, retries up to 10 times
- Only stops when task moves to Done
- Logs each iteration attempt

### 2. Twitter/X Poster (`src/twitter_poster.py`)
- Generates tweets using gemma-3-27b-it based on Company_Handbook.md context
- Saves drafts to Pending_Approval folder
- Posts to Twitter/X only after human approval
- Enforces rate limits (max 5 posts per day)
- Logs all activity

### 3. Social Media Poster (`src/social_media_poster.py`)
- Generates Facebook and Instagram posts using gemma-3-27b-it
- Creates platform-appropriate content
- Saves drafts to Pending_Approval folder
- Posts after human approval
- Includes hashtags and emojis
- Enforces rate limits (max 3 posts per day per platform)
- Logs all activity

### 4. Odoo Integration (`src/odoo_integration.py`)
- Connects to local Odoo Community instance via JSON-RPC API
- Creates invoices based on approved requests
- Reads transactions and generates reports
- All entries go to Pending_Approval first
- Human approval required before posting to Odoo
- Integrates with CEO Briefing system

### 5. Weekly Audit (`src/weekly_audit.py`)
- Runs automatically every Sunday night via scheduler
- Reads Done files from past 7 days
- Reads Odoo financial data
- Reads social media activity
- Generates comprehensive audit report
- Saves to vault as AUDIT_YYYYMMDD.md
- Feeds into Monday CEO Briefing

### 6. Approved Folder Watcher (extends existing approved_watcher.py)
- Monitors Approved folder for approved files from Gold tier features
- Executes approved actions (social media posts, Odoo entries)
- Moves processed files to Done folder
- Logs all actions to Logs folder

### 7. Vault Structure Extension
- Maintains existing folder structure
- Updates dashboard to show Gold tier workflow status

### 8. Configuration (`pyproject.toml`, `.env.example`)
- Python project configuration with Gold tier dependencies
- Environment variable template for Twitter, Facebook, Instagram, and Odoo credentials

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Multiple external API integrations | Feature requirement for Gold tier | Would reduce functionality below Gold tier standards |