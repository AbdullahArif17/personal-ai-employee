<!--
Sync Impact Report:
- Version change: 1.1.0 → 1.2.0
- Modified principles: Added XV, XVI, XVII, XVIII, XIX, XX, XXI for Gold tier rules
- Added sections: Gold tier specific principles
- Templates requiring updates:
  - .specify/templates/plan-template.md: ⚠ pending
  - .specify/templates/spec-template.md: ⚠ pending
  - .specify/templates/tasks-template.md: ⚠ pending
- Follow-up TODOs: None
-->

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

### IX. GMAIL CREDENTIALS (Silver tier)
Gmail API credentials stored in .env only, never in vault. These credentials must never be stored in the Obsidian vault or committed to version control.

### X. WHATSAPP AUTOMATION (Silver tier)
WhatsApp automation via Playwright - always ask human approval before replying. The AI must request human approval before sending any WhatsApp messages.

### XI. LINKEDIN POSTS (Silver tier)
LinkedIn posts go to Pending_Approval folder first, never auto-post. All LinkedIn content must be reviewed by a human before publication.

### XII. EMAIL APPROVAL (Silver tier)
Email replies require human approval for unknown contacts. The system must route emails from unknown contacts to the Pending_Approval folder for human review.

### XIII. WATCHER PATTERNS (Silver tier)
All new watchers follow base_watcher.py pattern. Any new filesystem watchers must inherit from the BaseWatcher class to ensure consistent error handling and logging.

### XIV. RATE LIMITING (Silver tier)
Rate limiting: max 10 emails processed per run, max 3 LinkedIn posts per day. The system must enforce these limits to prevent spam and API abuse.

### XV. ODOO ACCOUNTING (Gold tier)
Odoo accounting integration: all financial entries require human approval before posting. No financial transactions or entries may be automatically posted without explicit human approval in the system.

### XVI. SOCIAL MEDIA DRAFTS (Gold tier)
Social media automation for Twitter, Facebook, and Instagram: AI may draft content only, never auto-posts. All social media content must be reviewed and manually approved before publication.

### XVII. RALPH WIGGUM LOOP (Gold tier)
Ralph Wiggum loop protection: maximum 10 iterations allowed, with each iteration logged. The system must always log each iteration to prevent infinite loops.

### XVIII. DRY-RUN MODE (Gold tier)
All Gold tier features must have dry-run mode enabled by default. No Gold tier functionality may execute without the ability to run in a simulation mode that shows what would happen without taking actual actions.

### XIX. EXTERNAL API CREDENTIALS (Gold tier)
External API credentials for Twitter, Facebook, and Odoo must be stored in .env file only, never in vault or committed to version control. These credentials must never be exposed in the Obsidian vault or committed to any repository.

### XX. WEEKLY BUSINESS AUDIT (Gold tier)
Weekly business audit runs automatically every Sunday night. The system must perform comprehensive checks and generate audit reports without human intervention.

### XXI. DOUBLE APPROVAL FOR FINANCIAL ACTIONS (Gold tier)
Any action touching money requires double human approval. Financial transactions, payments, or monetary transfers must receive approval from two separate human reviewers before execution.

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
- Gmail API credentials stored in .env only, never in vault
- WhatsApp automation requires human approval before replying

### Data Management
- Obsidian vault serves as the single source of truth
- All data processing happens locally
- No cloud storage of personal information unless explicitly approved by user
- Maintain data integrity and backup procedures
- LinkedIn posts go to Pending_Approval folder first, never auto-post
- Email replies require human approval for unknown contacts

### Silver Tier Extensions
- WhatsApp automation via Playwright with human approval requirement
- LinkedIn posts require human approval before publishing
- Rate limiting enforced: max 10 emails per run, max 3 LinkedIn posts per day
- All new watchers must follow base_watcher.py inheritance pattern

### Gold Tier Extensions
- Odoo accounting requires human approval before posting any financial entries
- Social media (Twitter, Facebook, Instagram) AI drafts only, never auto-posts
- Ralph Wiggum loop protection: max 10 iterations with logging
- All Gold tier features must have dry-run mode enabled
- External API credentials (Twitter, Facebook, Odoo) stored in .env only
- Weekly business audit runs automatically every Sunday night
- Double human approval required for any action touching money

## Development Workflow

### Code Review Process
- All changes must follow the principles outlined in this constitution
- Security-sensitive changes require additional review
- Human-in-the-loop approval required for any script that performs external actions
- Silver tier features must implement proper approval flows and rate limiting

### Quality Gates
- All scripts must implement fail-safe mechanisms
- Proper error handling and logging required
- Dry-run capability for all automation scripts
- Audit logging for all actions taken
- Rate limiting enforcement for external communications
- Human approval flows for sensitive actions

## Governance

This constitution supersedes all other practices in the Personal AI Employee project. Any amendments to these principles must be documented with justification and approved by the project maintainer. All implementations must comply with these principles, and any deviation must be explicitly documented and justified. Silver tier extensions must maintain the same security and human-in-the-loop standards as Bronze tier.

**Version**: 1.2.0 | **Ratified**: 2026-02-20 | **Last Amended**: 2026-03-02
