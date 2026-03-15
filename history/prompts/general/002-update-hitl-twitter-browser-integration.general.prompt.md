---
id: "002"
title: "Update HITL Watcher Twitter Browser Integration"
stage: "general"
date_iso: "2026-03-13"
surface: "agent"
model: "claude-sonnet-4-6"
feature: "none"
branch: "1-gold-tier"
user: "abdullah"
command: "update hitl_watcher.py to use webbrowser for Twitter"
labels: ["twitter", "webbrowser", "integration"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - "/mnt/d/giaic/personal-ai-employee/src/hitl_watcher.py"
  - "/mnt/d/giaic/personal-ai-employee/.env.example"
  - "/mnt/d/giaic/personal-ai-employee/README.md"
tests_yaml: []
---

# Update src/hitl_watcher.py to use webbrowser module for Twitter posting

## User Request
Update src/hitl_watcher.py to handle Twitter posting using webbrowser module instead of tweepy API.

When action is 'post_tweet':

1. Parse the .md file and extract tweet content (remove YAML frontmatter between --- markers)

2. Clean the content:
   - Remove YAML header (everything between first --- and second ---)
   - Strip whitespace
   - Truncate to 280 characters if needed

3. Open Twitter in browser with pre-filled content:
   import webbrowser
   import urllib.parse
   encoded = urllib.parse.quote(clean_tweet)
   url = f"https://twitter.com/intent/tweet?text={encoded}"
   webbrowser.open(url)

4. Print clear messages:
   print("SUCCESS: Opened Twitter in browser!")
   print("Please click 'Post' button in your browser to publish.")
   print(f"Tweet preview: {clean_tweet[:50]}...")

5. Log the action to audit trail as:
   action_type: tweet_browser_opened
   status: SUCCESS
   note: "Manual posting required - opened in browser"

6. Also handle 'post_thread' type:
   - Parse multiple tweets separated by \n\n or numbered like "1/5"
   - Open first tweet in browser
   - Save remaining tweets to a temp file in Logs folder
   - Print instructions to post remaining tweets manually

7. Add sys.path.insert fix at top of file:
   import sys
   import os
   sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

Do NOT use tweepy or any Twitter API calls.
Do NOT import twitter_poster module.
Use only built-in Python modules: webbrowser, urllib.parse, os, sys, pathlib.

## Response
Updated src/hitl_watcher.py to:
1. Added webbrowser, urllib.parse imports for browser-based Twitter posting
2. Modified _process_approved_file method to handle post_tweet and post_thread actions through web browser
3. Replaced _execute_buffer_action method with _execute_tweet_browser_action and _execute_tweet_thread_action methods
4. Implemented content parsing to remove YAML frontmatter
5. Added functionality to split content into threads when needed
6. Updated .env.example to remove Buffer API configuration
7. Updated README.md to reflect the change from Buffer API to browser-based posting

The changes enable the system to use web browser intents for Twitter posting instead of direct API calls, which avoids API authentication issues and rate limits.

## Outcome
- Twitter posts (post_tweet, post_thread) now use web browser for manual posting
- Backward compatibility maintained for other actions (email, etc.)
- Proper error handling and logging implemented
- Environment variables properly documented in .env.example
- YAML frontmatter parsing implemented correctly