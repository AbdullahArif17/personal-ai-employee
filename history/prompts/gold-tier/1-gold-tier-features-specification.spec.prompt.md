---
id: 1
title: "Gold tier features specification"
stage: "spec"
date_iso: "2026-03-06"
surface: "agent"
model: "claude-sonnet-4-6"
feature: "gold-tier"
branch: "1-gold-tier"
user: "abdullah"
command: "/sp.specify"
labels: ["specification", "gold-tier", "ai-employee", "automation"]
links:
  spec: "specs/1-gold-tier/spec.md"
  ticket: null
  adr: null
  pr: null
files_yaml:
  - "specs/1-gold-tier/spec.md"
  - "specs/1-gold-tier/checklists/requirements.md"
tests_yaml: []
prompt_text: |
  Add Gold tier features to Personal AI Employee:

  1. RALPH WIGGUM LOOP (src/ralph_loop.py)
     Autonomous task completion loop:
     - Read tasks from Needs_Action folder
     - Process each task with Gemini AI
     - If task incomplete, retry up to 10 times
     - Only stop when task moves to Done
     - Log each iteration
     - Use gemma-3-27b-it model

  2. TWITTER/X INTEGRATION (src/twitter_poster.py)
     - Generate tweets using Gemini AI
     - Read business context from Company_Handbook.md
     - Save drafts to Pending_Approval folder
     - Post to Twitter after human approval
     - Use Twitter API v2
     - Log all activity

  3. FACEBOOK & INSTAGRAM (src/social_media_poster.py)
     - Generate posts using Gemini AI
     - Create content for both Facebook and Instagram
     - Save drafts to Pending_Approval folder
     - Post after human approval
     - Use Meta Graph API
     - Include hashtags and emojis

  4. ODOO ACCOUNTING (src/odoo_integration.py)
     - Connect to local Odoo Community instance
     - Create invoices via JSON-RPC API
     - Read transactions and generate reports
     - All entries saved to Pending_Approval first
     - Human approval required before posting
     - Integrate with CEO Briefing

  5. WEEKLY BUSINESS AUDIT (src/weekly_audit.py)
     - Runs every Sunday night via scheduler
     - Reads all Done files from past 7 days
     - Reads Odoo financial data
     - Reads social media activity
     - Generates comprehensive audit report
     - Saves to Vault as AUDIT_YYYYMMDD.md
     - Feeds into Monday CEO Briefing

  Vault path: D:\giaic\personal-ai-employee\AI_Employee_Vault
  Use gemma-3-27b-it for all AI tasks
  All credentials from .env file

response_text: |
  Successfully created the Gold tier features specification for the Personal AI Employee. The specification includes:

  1. Ralph Wiggum Loop - Autonomous task completion with retry mechanism
  2. Twitter/X integration - AI-generated content with human approval workflow
  3. Facebook & Instagram integration - Platform-specific content generation
  4. Odoo accounting integration - Invoice creation and financial reporting
  5. Weekly business audit - Automated reporting system

  The spec includes comprehensive user scenarios, functional requirements, success criteria, and entity definitions. All features maintain the human-in-the-loop approach for approvals while automating routine tasks.

outcome: "Specification created successfully with all Gold tier features documented comprehensively."
evaluation: "The specification is complete, testable, and ready for the planning phase."
---
