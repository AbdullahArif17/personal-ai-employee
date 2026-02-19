# SKILL: Triage and Task Categorization

## Purpose
This skill enables the AI Employee to categorize and prioritize incoming tasks from the Inbox folder.

## Process
1. Read the content of the new file in Needs_Action folder
2. Analyze the content to determine task category and priority
3. Apply appropriate tags and metadata
4. Update the task file with categorization information
5. Prepare for next processing step

## Categories
- **Personal**: Private matters, family, health
- **Professional**: Work-related tasks, career development
- **Financial**: Budget, investments, bills
- **Administrative**: Appointments, reminders, organization
- **Informational**: Research requests, fact-finding

## Priority Levels
- **High**: Deadline within 24 hours, urgent matters
- **Medium**: Deadline within 7 days, important tasks
- **Low**: Routine tasks, long-term planning
- **Backlog**: Ideas, future considerations

## Categorization Steps
1. **Read Task Content**: Examine the entire content of the incoming task
2. **Identify Keywords**: Look for terms that indicate category
3. **Determine Urgency**: Assess deadlines and importance
4. **Assign Category**: Select the most appropriate category
5. **Set Priority**: Assign priority based on urgency and importance
6. **Apply Tags**: Add relevant tags for filtering and searching
7. **Update Metadata**: Add categorization information to the task

## Decision Rules
- If task contains "urgent", "ASAP", or "immediate", set priority to High
- If task has a date within 24 hours, set priority to High
- If task is marked with high priority by sender, respect that designation
- If task affects safety or security, elevate to High priority
- If task is routine maintenance, set to Low priority

## Output Format
After categorization, add the following metadata to the task file:
```
---
Category: [category]
Priority: [priority]
Tags: [tag1, tag2, ...]
Due Date: [YYYY-MM-DD or null]
Dependencies: [list of dependent tasks or null]
---

Original task content continues here...
```

## Approval Thresholds
- If task involves spending money > $100, escalate to Pending Approval
- If task involves sharing personal information, escalate to Pending Approval
- If task is outside defined comfort zone, escalate to Pending Approval