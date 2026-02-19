# SKILL: Response Formatting

## Purpose
This skill enables the AI Employee to format responses and outputs according to consistent standards.

## Process
1. Analyze the input task and requirements
2. Determine appropriate response format based on task type
3. Apply formatting guidelines consistently
4. Validate output against formatting standards
5. Prepare response for storage in the appropriate folder

## Standard Response Formats

### Task Completion Response
```
# Task Completion Report

**Task**: [Original task description]
**Status**: [Completed/Partially completed/Pending]
**Date**: [YYYY-MM-DD]
**Time Taken**: [Duration if applicable]

## Summary
[Brief summary of what was done]

## Details
[Detailed explanation of actions taken]

## Next Steps
[If applicable, outline any follow-up actions needed]

## Attachments/References
[Any relevant files, links, or references]
```

### Research Response
```
# Research Report

**Topic**: [Research topic]
**Date**: [YYYY-MM-DD]
**Status**: [Complete/In Progress]

## Executive Summary
[Brief summary of key findings]

## Findings
### [Category 1]
[Detailed findings]

### [Category 2]
[Detailed findings]

## Sources
[List of sources used in research]

## Recommendations
[Actionable recommendations based on research]
```

### Scheduling Response
```
# Scheduling Confirmation

**Event**: [Event name]
**Date**: [YYYY-MM-DD]
**Time**: [HH:MM]
**Location**: [Physical or virtual location]
**Status**: [Confirmed/Pending/Rescheduled]

## Details
[Event details]

## Preparation
[Items to prepare before event]

## Follow-up
[Actions to take after event]
```

## Formatting Guidelines

### Markdown Standards
- Use ATX-style headers (e.g., `# Header 1`, `## Header 2`)
- Use consistent heading hierarchy
- Use hyphens for unordered lists (`- item`)
- Use 1-3 levels of headings maximum for readability
- Bold important information using `**bold**`
- Italicize emphasis using `*italic*`

### Metadata Headers
For all responses, include metadata in YAML front matter:
```
---
task_id: [unique identifier]
original_task: [summary of original request]
status: [completed/in-progress/deferred]
priority: [high/medium/low]
tags: [list, of, relevant, tags]
created_date: [YYYY-MM-DD]
completion_date: [YYYY-MM-DD or null]
estimated_time: [time estimate if applicable]
actual_time: [actual time taken if applicable]
---

# Main Content
```

### Content Structure
1. **Header Section**: Clear title and metadata
2. **Summary Section**: Brief overview of the response
3. **Detail Section**: In-depth information
4. **Action Section**: Next steps or required actions
5. **Reference Section**: Sources or attachments

## Special Formatting Requirements

### For Email Drafts
- Use plain text or simple markdown
- Include clear subject line
- Separate body into paragraphs
- Add signature if appropriate
- Include any required legal disclaimers

### For Lists and Enumerations
- Use ordered lists for steps (`1. First step`)
- Use unordered lists for items (`- Item 1`)
- Keep list items concise and parallel in structure
- Limit lists to 10 items when possible

### For Tables
- Use markdown table format with headers
- Align content appropriately (numbers right, text left)
- Keep tables to 5 columns maximum for readability
- Add table caption above the table

## Error Handling
- If formatting requirements are unclear, use the closest matching format
- If content doesn't fit standard formats, create an appropriate custom format
- Always maintain readability and clarity
- When in doubt, choose simpler formatting over complex structures

## Validation Checklist
Before finalizing any response:
- [ ] Headers follow consistent hierarchy
- [ ] Metadata is complete and accurate
- [ ] Content is well-organized
- [ ] Formatting enhances readability
- [ ] All required sections are included
- [ ] File is saved in appropriate output folder