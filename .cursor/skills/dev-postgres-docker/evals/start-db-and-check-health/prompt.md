---
tags: [dev-postgres-docker]
max_turns: 15
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Shell]
---

my integration tests are failing with connection refused on 5432 — can you get the dev postgres from our docker-compose running and confirm it's healthy before I rerun pytest?