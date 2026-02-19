# Data Model: Personal AI Employee

## Overview

The Personal AI Employee system uses a file-based data model where information is stored in markdown files and structured directories. This approach aligns with the local-first principle and integrates well with Obsidian.

## Core Entities

### 1. Task Entity

**Definition**: Represents a unit of work to be processed by the AI Employee

**Attributes**:
- `id`: Unique identifier (derived from filename)
- `title`: Task title (first line of content or filename)
- `content`: Full task content (markdown format)
- `status`: Current status (new, needs_action, processing, done, pending_approval, approved)
- `created_at`: Timestamp when task was created
- `updated_at`: Timestamp when task was last updated
- `category`: Task category (personal, professional, financial, administrative, informational)
- `priority`: Priority level (high, medium, low, backlog)
- `tags`: List of associated tags
- `due_date`: Optional deadline
- `attempts`: Number of processing attempts
- `processed`: Boolean indicating if processing is complete

**File Location**: Stored in appropriate folder based on status
- New tasks: `AI_Employee_Vault/Inbox/`
- Processing: `AI_Employee_Vault/Needs_Action/`
- Completed: `AI_Employee_Vault/Done/`
- Pending approval: `AI_Employee_Vault/Pending_Approval/`
- Approved: `AI_Employee_Vault/Approved/`

**Metadata File**: Associated JSON file with additional attributes
- Located in same folder as the task file
- Named `{task_filename_without_extension}_metadata.json`

### 2. Metadata Entity

**Definition**: Stores additional information about tasks that is not part of the main content

**Attributes**:
- `original_path`: Path where the file was initially detected
- `copied_at`: Timestamp when file was copied to current location
- `status`: Current processing status
- `processed`: Boolean indicating if processing is complete
- `attempts`: Number of processing attempts
- `category`: Assigned category
- `priority`: Assigned priority
- `dependencies`: List of dependent tasks
- `estimated_time`: Estimated processing time
- `actual_time`: Actual processing time
- `approval_required`: Boolean indicating if human approval is needed
- `approval_reason`: Reason for requiring approval

**File Format**: JSON
**Location**: Same folder as the associated task file
**Naming Convention**: `{task_base_name}_metadata.json`

### 3. Log Entry Entity

**Definition**: Records system actions and events for audit and debugging

**Attributes**:
- `timestamp`: ISO format timestamp of the event
- `action`: Type of action (FILE_COPIED, PROCESSING_START, ERROR, etc.)
- `message`: Description of the event
- `dry_run`: Boolean indicating if this was a dry run
- `task_id`: Optional reference to the associated task

**File Format**: JSON
**Location**: `AI_Employee_Vault/Logs/`
**Naming Convention**: `{YYYY-MM-DD}.json`
**Structure**: Array of log entries

### 4. Dashboard Entity

**Definition**: Aggregates system status and metrics for user visibility

**Attributes**:
- `last_updated`: Timestamp of last update
- `folder_counts`: Dictionary of file counts by folder
- `recent_activity`: List of recent system activities
- `system_status`: Current status of system components
- `statistics`: Various system metrics

**File Format**: Markdown with YAML frontmatter
**Location**: `AI_Employee_Vault/Dashboard.md`

### 5. Skill Entity

**Definition**: Contains instructions for AI processing in specific areas

**Attributes**:
- `name`: Skill name
- `purpose`: Description of the skill's purpose
- `process`: Step-by-step process instructions
- `formatting`: Output formatting guidelines
- `validation`: Quality checks and validation rules

**File Format**: Markdown
**Location**: `AI_Employee_Vault/skills/`
**Naming Convention**: `SKILL_{skill_name}.md`

## Folder Structure

### Primary Directories

```
AI_Employee_Vault/
├── Dashboard.md                 # System status dashboard
├── Company_Handbook.md          # AI behavior rules
├── skills/                      # AI skill files
│   ├── SKILL_triage.md          # Task categorization instructions
│   ├── SKILL_dashboard_update.md # Dashboard update instructions
│   ├── SKILL_response_formatting.md # Response formatting instructions
│   └── SKILL_approval_process.md # Approval process instructions
├── Inbox/                       # New tasks to be processed
├── Needs_Action/                # Tasks ready for AI processing
├── Done/                        # Completed tasks
├── Logs/                        # System logs
├── Pending_Approval/            # Tasks awaiting human approval
└── Approved/                    # Approved tasks for execution
```

### Relationships

1. **Task → Metadata**: One-to-one relationship
   - Each task file has one associated metadata file

2. **Task → Log Entry**: One-to-many relationship
   - Each task may generate multiple log entries

3. **Skill → Task**: Many-to-many relationship
   - Tasks may be processed using multiple skills
   - Skills may be applied to multiple tasks

4. **Folder → Task**: One-to-many relationship
   - Each folder contains multiple tasks
   - Each task exists in exactly one folder

## Data Lifecycle

### Task Lifecycle
1. **Creation**: Task enters `Inbox/` folder
2. **Detection**: Filesystem watcher detects new file
3. **Processing Initiation**: Task copied to `Needs_Action/` with metadata
4. **AI Processing**: Claude Code processes task using skills
5. **Completion**: Task moved to `Done/` or `Pending_Approval/`
6. **Approval**: If required, human approves in `Pending_Approval/`
7. **Execution**: Approved tasks moved to `Approved/` and executed
8. **Archival**: Completed tasks remain in `Done/` or `Approved/`

### Log Lifecycle
1. **Generation**: Events generate log entries in real-time
2. **Aggregation**: Daily log files collect events by date
3. **Retention**: Log files may be archived or rotated based on policy
4. **Cleanup**: Old logs may be purged according to retention policy

## File Format Specifications

### Markdown Files
- Standard markdown format (CommonMark)
- YAML frontmatter for metadata (optional)
- UTF-8 encoding
- Unix line endings preferred

### JSON Files
- Valid JSON format
- UTF-8 encoding
- Human-readable indentation (2 spaces)
- Consistent field naming (snake_case)

### Naming Conventions
- Folders: lowercase with underscores
- Files: descriptive names with appropriate extensions
- Dates: YYYY-MM-DD format
- Timestamps: ISO 8601 format

## Constraints and Validation

### File System Constraints
- All paths must be valid for the target operating system
- File names must avoid reserved characters
- Maximum path length considerations
- Case sensitivity differences across platforms

### Data Integrity Constraints
- Each task must have a corresponding metadata file
- Status transitions must follow valid patterns
- Required fields in log entries must be present
- Dashboard updates must maintain structural integrity

### Security Constraints
- No sensitive information in filenames
- Metadata files should not contain confidential data
- Log entries should not contain sensitive content
- Skill files should be validated before use

## Performance Considerations

### File Access Patterns
- Minimize file system operations
- Batch operations when possible
- Cache frequently accessed information
- Use efficient file traversal algorithms

### Storage Optimization
- Compress log files when appropriate
- Archive old tasks based on retention policy
- Deduplicate common content when possible
- Optimize for the expected volume of tasks

## Backup and Recovery

### Backup Strategy
- Regular backups of the entire vault directory
- Version control for skill files and configuration
- Separate backup for log files if needed
- Point-in-time recovery capabilities

### Recovery Procedures
- Restore from backup in case of corruption
- Rebuild dashboard from current state
- Resume processing from last known good state
- Audit trail reconstruction from logs