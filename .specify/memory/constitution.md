# Personal AI Employee Constitution

## Core Principles

### I. LOCAL-FIRST
All sensitive data stays on local machine. Obsidian vault is the single source of truth.

### II. SECURITY
All credentials in .env file only. Never stored in vault or committed to git.

### III. HUMAN-IN-THE-LOOP
No external action (email send, payment, social post) executes without a human moving a file to /Approved.

### IV. AGENT SKILLS
All AI logic must be implemented as SKILL.md files that Claude Code can read and follow.

### V. DRY-RUN DEFAULT
All watcher and action scripts default to DRY_RUN=true during development.

### VI. PYTHON 3.13+
All scripts use Python 3.13 or higher with uv for package management.

### VII. FAIL SAFE
On any error, scripts log and pause — they never silently skip or auto-retry destructive actions.

### VIII. AUDITABILITY
Every action the AI takes is logged to /Vault/Logs/YYYY-MM-DD.json.

## Additional Constraints

### Technology Stack
- Use Python 3.13+ for all automation scripts
- Use uv for Python package management
- Use Claude Code for AI interaction and skill management
- Store all personal data locally in Obsidian vault format

### Security Requirements
- All sensitive credentials must be stored in .env files and never committed to version control
- Implement strict access controls for all external APIs
- Encrypt all sensitive data at rest
- Log all actions for audit trail

### Data Management
- Obsidian vault serves as the single source of truth
- All data processing happens locally
- No cloud storage of personal information unless explicitly approved by user
- Maintain data integrity and backup procedures

## Development Workflow

### Code Review Process
- All changes must follow the principles outlined in this constitution
- Security-sensitive changes require additional review
- Human-in-the-loop approval required for any script that performs external actions

### Quality Gates
- All scripts must implement fail-safe mechanisms
- Proper error handling and logging required
- Dry-run capability for all automation scripts
- Audit logging for all actions taken

## Governance

This constitution supersedes all other practices in the Personal AI Employee project. Any amendments to these principles must be documented with justification and approved by the project maintainer. All implementations must comply with these principles, and any deviation must be explicitly documented and justified.

**Version**: 1.0.0 | **Ratified**: 2026-02-20 | **Last Amended**: 2026-02-20
