# SKILL: Dashboard Update

## Purpose
This skill enables the AI Employee to update the Dashboard.md file with current status information.

## Process
1. Read the current Dashboard.md file
2. Count files in each vault folder (Inbox, Needs_Action, etc.)
3. Collect recent activity information
4. Update statistics and status information
5. Write the updated dashboard back to Dashboard.md

## Data Collection Points

### File Counts
- Count files in `Inbox/` folder
- Count files in `Needs_Action/` folder
- Count files in `Done/` folder
- Count files in `Pending_Approval/` folder
- Count files in `Approved/` folder
- Count files in `Logs/` folder

### Recent Activity
- Last 10 processed tasks (from Done folder)
- Last 5 actions taken by AI
- Most recent error (if any)
- System status updates

### Statistics
- Total processed tasks (cumulative)
- Today's activity count
- Success rate percentage
- Error count

## Update Process

### 1. Read Current Dashboard
- Load the existing Dashboard.md content
- Parse current status information

### 2. Collect Fresh Data
- Scan vault folders for file counts
- Read recent log files for activity
- Calculate updated statistics

### 3. Update Status Table
- Update the status overview table with current counts
- Format the table consistently

### 4. Update Recent Activity Section
- Add new activities chronologically
- Limit to most recent entries to prevent bloat
- Format as a list with timestamps

### 5. Update System Status
- Update filesystem watcher status
- Update Claude Code integration status
- Update last run timestamp
- Update DRY_RUN mode status

### 6. Update Statistics
- Recalculate cumulative totals
- Update daily/weekly/monthly metrics
- Update success/error rates

## Formatting Guidelines

### Table Format
Use markdown tables with consistent column headers:
```markdown
| Folder | Count | Description |
|--------|-------|-------------|
| Inbox | [count] | New tasks waiting to be processed |
```

### Activity Format
List recent activities with timestamps:
```markdown
## Recent Activity
- [timestamp]: [activity description]
- [timestamp]: [activity description]
```

### Status Format
Maintain consistent status section format:
```markdown
## System Status
- Filesystem watcher: **[status]**
- Claude Code integration: **[status]**
- Last run: **[timestamp]**
- DRY_RUN mode: **[status]**
```

## Error Handling
- If unable to read a folder, show count as "Error"
- If unable to update dashboard, log the error and continue
- Preserve existing dashboard content if update fails
- Attempt to maintain formatting consistency even if individual sections fail

## Frequency Recommendations
- Update dashboard after processing each task batch
- Update dashboard when starting/stopping the watcher
- Update dashboard during periodic system checks
- Update dashboard when requested manually

## Safety Checks
- Always backup current dashboard before updating
- Validate file paths before counting
- Handle missing folders gracefully
- Preserve manual additions to dashboard that aren't in the template sections