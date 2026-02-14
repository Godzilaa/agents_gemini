---
name: festival-event-agent
description: Detects and explains real-world disruptions (festivals, rallies, road closures) in Bengaluru using Google Search.
---
# Goal
Identify human-driven urban disruptions to explain traffic for the IRL Replay app.

# Instructions
1. Use the @google-search tool via the event_scanner.py script.
2. Cross-reference search results with the user's location.
3. Output: [Event Name] | [Location] | [Closure Advice].

# Constraints
- Use verified sources (news, official police tweets).
