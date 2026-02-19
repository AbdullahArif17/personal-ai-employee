# Personal AI Employee - Bronze Tier Specification

## Overview
A local automation system where Claude Code acts as an AI employee that monitors an Obsidian markdown vault, processes incoming tasks, and writes structured outputs — all running on the user's local machine.

## Scope

### In Scope
- Local Obsidian vault monitoring and processing
- File-based task management system
- Dashboard for monitoring and status updates
- Company Handbook for AI behavior rules
- Filesystem watcher for detecting new tasks
- Agent skill files for defining AI behavior
- Claude Code integration for task processing

### Out of Scope (Bronze tier limitations)
- No Gmail or WhatsApp integration (Silver tier)
- No MCP servers (Silver tier)
- No external API calls
- No payments or social media integration
- No cloud synchronization

## Features

### 1. Obsidian Vault Structure
Create a structured Obsidian vault with the following folders:
- `/Inbox` - Incoming tasks and files to be processed
- `/Needs_Action` - Tasks that need processing by Claude Code
- `/Done` - Completed tasks with responses/output
- `/Logs` - System logs and activity records
- `/Pending_Approval` - Tasks awaiting human approval
- `/Approved` - Approved tasks ready for execution

### 2. Dashboard.md
A live summary file showing:
- Count of pending items in each status
- Recent activity log
- Current system status
- Quick links to important sections

### 3. Company_Handbook.md
Rules of engagement for the AI including:
- Expected tone and communication style
- Approval thresholds for different types of actions
- Contact list and escalation procedures
- Guidelines for handling various task types

### 4. Filesystem Watcher
A Python script that:
- Monitors the `/Inbox` folder for new files
- When a new file appears, copies it to `/Needs_Action`
- Creates a metadata `.md` sidecar file with timestamp and initial status
- Logs the detection event to `/Logs`

### 5. Agent SKILL.md Files
Markdown skill files that Claude Code reads to understand how to process tasks:
- `triage_skill.md` - Instructions for categorizing and prioritizing tasks
- `dashboard_update_skill.md` - Instructions for updating Dashboard.md
- `response_formatting_skill.md` - Instructions for formatting responses
- `approval_process_skill.md` - Instructions for handling approval workflows

### 6. Claude Code Integration
Claude Code will:
- Read files in `/Needs_Action` folder
- Process each item following instructions in SKILL.md files
- Write responses or action plans to `/Done` folder
- Update Dashboard.md with current status
- Move processed items appropriately between folders

## User Story
As a user, I drag a text file into my `/Inbox` folder. The watcher detects it, creates a task file in `/Needs_Action`. I run Claude Code and it reads the task, follows the SKILL.md instructions, writes a response plan in `/Done`, and updates my Dashboard.md — all automatically.

## Acceptance Criteria

### Functional Requirements
- [ ] Obsidian vault structure is created with all required folders
- [ ] Dashboard.md is automatically updated with current status
- [ ] Company_Handbook.md contains comprehensive rules
- [ ] Filesystem watcher detects new files and moves them appropriately
- [ ] Metadata sidecar files are created with proper information
- [ ] SKILL.md files provide clear instructions for Claude Code
- [ ] Claude Code can process tasks following the skill instructions
- [ ] All actions are logged to the `/Logs` folder

### Non-functional Requirements
- [ ] All processing happens locally on the user's machine
- [ ] No external network calls are made by default
- [ ] System is secure with no sensitive data leaving the local machine
- [ ] System handles errors gracefully and logs them appropriately
- [ ] Dashboard updates occur in near real-time

## Technical Requirements
- Python 3.13+ with uv for package management (as per constitution)
- File system monitoring using watchdog library
- Markdown file parsing and generation
- Local-only processing with no external dependencies
- Human-in-the-loop for approval workflows

## Constraints
- All data remains on the local machine
- No cloud storage or external API calls
- Approval required for any external action
- Fail-safe mechanisms prevent unintended actions
- Comprehensive logging for audit trail

## Assumptions
- User has Claude Code installed and configured
- User has Obsidian installed and configured
- User understands basic file management
- User provides clear instructions in Company_Handbook.md

## Clarifications

### Session 2026-02-20
- Q: How should the filesystem watcher monitor the Inbox folder? → A: File-based monitoring (using Python watchdog library)
- Q: What should happen to files when moved from Inbox to Needs_Action? → A: Copy the file to /Needs_Action with metadata sidecar
- Q: Which Python version and package manager should be used? → A: Python 3.13+ with uv (as per constitution)
- Q: What approval mechanism should be used for external actions? → A: Human approval required for all external actions
- Q: What format should the dashboard and logs use? → A: Markdown format (.md)