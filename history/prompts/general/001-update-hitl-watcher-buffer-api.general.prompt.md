---
id: "001"
title: "Update HITL Watcher Buffer API"
stage: "general"
date_iso: "2026-03-13"
surface: "agent"
model: "claude-sonnet-4-6"
feature: "none"
branch: "1-gold-tier"
user: "abdullah"
command: "update hitl_watcher.py to use Buffer API"
labels: ["buffer-api", "social-media", "integration"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - "/mnt/d/giaic/personal-ai-employee/src/hitl_watcher.py"
  - "/mnt/d/giaic/personal-ai-employee/.env.example"
tests_yaml: []
---

# Update src/hitl_watcher.py to use Buffer API instead of direct Twitter posting

## User Request
Update src/hitl_watcher.py to use Buffer API instead of direct Twitter posting.

When action is post_tweet, post_facebook, or post_instagram:
Use Buffer API to schedule the post instead of direct API.

Buffer API endpoint:
POST https://api.bufferapp.com/1/updates/create.json

Required params:
- access_token: from BUFFER_ACCESS_TOKEN env var
- profile_ids[]: Buffer profile ID for the platform
- text: the post content

Add method _execute_buffer_action(content, platform, file_path):
1. Read BUFFER_ACCESS_TOKEN from .env
2. Read BUFFER_PROFILE_IDS from .env (comma separated)
3. Post to Buffer API using requests library
4. Log success/failure

Also add to .env.example:
BUFFER_ACCESS_TOKEN=
BUFFER_TWITTER_PROFILE_ID=
BUFFER_LINKEDIN_PROFILE_ID=
BUFFER_FACEBOOK_PROFILE_ID=
BUFFER_INSTAGRAM_PROFILE_ID=

Get profile IDs from:
GET https://api.bufferapp.com/1/profiles.json?access_token=TOKEN

## Response
Updated src/hitl_watcher.py to:
1. Added requests import for making HTTP requests
2. Modified _process_approved_file method to handle post_tweet, post_facebook, and post_instagram actions through Buffer API
3. Replaced _execute_tweet_action method with _execute_buffer_action method that handles all social media platforms via Buffer API
4. Updated .env.example to include Buffer API configuration variables

The changes enable the system to use Buffer API for scheduling social media posts instead of direct platform APIs, which provides better scheduling capabilities and unified management across platforms.

## Outcome
- Social media posts (Twitter, Facebook, Instagram) now use Buffer API for scheduling
- Backward compatibility maintained for other actions (email, etc.)
- Proper error handling and logging implemented
- Environment variables properly documented in .env.example