# SKILL: Approval Process

## Purpose
This skill enables the AI Employee to handle tasks that require human approval before execution.

## Process
1. Identify tasks that require human approval based on predetermined criteria
2. Move these tasks to the Pending_Approval folder
3. Create clear approval requests with necessary context
4. Monitor for human approval actions
5. Move approved tasks to the Approved folder for execution
6. Handle rejected tasks appropriately

## Approval Criteria

### Automatic Approval Requirements
Any task meeting these criteria should be moved to Pending_Approval:

- **Financial Transactions**: Any task involving spending money
  - Amount > $50 (customizable threshold)
  - Transfer of funds
  - Subscription payments
  - Purchase orders

- **Communication**: Any task involving external communication
  - Sending emails to new contacts
  - Posting on social media
  - Sharing personal information
  - Making reservations on behalf of user

- **System Changes**: Any task modifying system configurations
  - Changing security settings
  - Installing/uninstalling software
  - Modifying system files
  - Granting permissions to applications

- **Privacy**: Any task involving personal/sensitive information
  - Sharing personal documents
  - Accessing medical records
  - Viewing financial information
  - Disclosing personal schedules

### Approval Process Steps

#### Step 1: Identification
- Scan task content for approval triggers
- Check against approval criteria
- Flag tasks that require approval

#### Step 2: Preparation
- Create approval request with full context
- Preserve original task information
- Add reason for requiring approval
- Include estimated time/resources needed

#### Step 3: Submission
- Move task file to Pending_Approval folder
- Create notification if applicable
- Update dashboard to reflect pending approval status

#### Step 4: Monitoring
- Periodically check for human action
- Wait for file to be moved to Approved folder
- Handle timeouts appropriately

#### Step 5: Execution
- When approved, move to Approved folder
- Proceed with task execution
- Update dashboard and logs

## Approval Request Format

Each approval request should include:

```
---
approval_required: true
approval_reason: "[Specific reason for approval]"
approval_threshold: "[financial_amount, privacy_level, etc.]"
original_folder: "Needs_Action"
submitted_by: "AI_Employee"
submitted_at: "[ISO timestamp]"
estimated_completion: "[Time estimate]"
priority: "[high/medium/low]"
---

# Approval Request: [Brief Description]

## Original Task
[Original task content]

## Why Approval Is Needed
[Explanation of why this requires human approval]

## Estimated Impact
- Time required: [estimate]
- Resources needed: [estimate]
- Potential risks: [if any]

## Recommended Action
[What the AI suggests, but with clear indication this requires approval]

## Approval Options
- **Approve**: Move file to Approved folder to authorize
- **Reject**: Move file back to Needs_Action with feedback
- **Modify**: Make changes and resubmit
```

## Human Action Instructions

### For User (Human Approver)
1. Review the approval request in the Pending_Approval folder
2. Determine if you approve the requested action
3. To approve: Move the file to the Approved folder
4. To reject: Move the file back to Needs_Action with comments
5. To modify: Edit the file with changes and resubmit

### For AI Employee
1. Monitor Pending_Approval folder for changes
2. When file moves to Approved, proceed with execution
3. When file returns to Needs_Action, reprocess with changes
4. Update dashboard and logs accordingly

## Timeout Handling

If a task remains in Pending_Approval for longer than the specified time:

1. **Default Timeout**: 7 days (configurable)
2. **Notification**: Send reminder to user after 3 days
3. **Escalation**: After timeout, move to Needs_Action with timeout notice
4. **Logging**: Record timeout in system logs

## Error Handling

### Failed Approvals
- If unable to move files between folders, log error and retry
- If approval criteria are unclear, escalate to user
- If system encounters unexpected state, pause and notify user

### Invalid Approvals
- If a file is moved to Approved folder without proper review, log for audit
- Verify approval requests match approved actions
- Maintain audit trail of all approval-related actions

## Special Cases

### Emergency Approvals
For urgent tasks:
- Allow expedited approval process
- Enable immediate notification to user
- Provide emergency approval pathway

### Batch Approvals
For multiple related tasks:
- Allow bulk approval decisions
- Group related tasks together
- Maintain individual tracking within batch

## Security Considerations
- All approval actions are logged
- Maintain audit trail of approval decisions
- Verify file integrity before and after approval
- Protect against unauthorized approval bypasses

## Validation Checklist
Before processing approval-required tasks:
- [x] Approval criteria correctly identified
- [x] Proper context provided to human approver
- [x] Audit trail maintained
- [x] Timeout handling configured
- [x] User instructions clear and accessible
- [x] Error handling implemented