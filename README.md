# Lumen

A lightweight analytics platform for Claude Code. Track how your team uses Claude Code hooks, skills, and tools — across any number of projects and organizations.

## How it works

1. Deploy Lumen to Railway (one click below)
2. Create an org and get an API key
3. Add a `PostToolUse` hook to your `.claude/settings.json`
4. Events flow in; your dashboard lights up

## Deploy to Railway

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/template/lumen)

You'll need to add a PostgreSQL database service in Railway — it connects automatically via the `DATABASE_URL` env var.

## Local development

```bash
# Create a local Postgres DB
createdb lumen

# Install dependencies
pip install -r requirements.txt

# Set env
cp .env.example .env

# Run
uvicorn app.main:app --reload
```

## Create your org

```bash
curl -X POST https://your-lumen-app.railway.app/orgs \
  -H 'Content-Type: application/json' \
  -d '{"name": "Acme Corp"}'
# => {"slug": "acme-corp", "api_key": "..."}
```

Save the `api_key` — it's used both for ingesting events and viewing the dashboard.

## View your dashboard

```
https://your-lumen-app.railway.app/dashboard?key=YOUR_API_KEY
```

## Add the Claude Code hook

Add this to your project's `.claude/settings.json` (or the global `~/.claude/settings.json`):

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": ".*",
        "command": "curl --max-time 2 -s -X POST https://your-lumen-app.railway.app/events -H 'Content-Type: application/json' -H 'Authorization: Bearer $LUMEN_API_KEY' -d \"{\\\"event\\\": \\\"$CLAUDE_TOOL_NAME\\\", \\\"user\\\": \\\"$(git config user.email 2>/dev/null)\\\", \\\"project\\\": \\\"$(basename $(git rev-parse --show-toplevel 2>/dev/null) 2>/dev/null)\\\"}\""
      }
    ]
  }
}
```

Set `LUMEN_API_KEY` as an environment variable on each developer's machine.

The `matcher` above captures all tool uses. To track only skill invocations, set `"matcher": "Skill"`.

## Event schema

```json
{
  "event": "skill_used",
  "properties": { "skill": "feature-flippers" },
  "user": "kshitiz@company.com",
  "project": "biggerpockets",
  "timestamp": "2026-06-17T14:00:00Z"
}
```

All fields except `event` are optional. `properties` is a free-form JSON object — add whatever context is useful.

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/orgs` | None | Create an org, get an API key |
| `POST` | `/events` | Bearer token | Ingest an event |
| `GET` | `/dashboard?key=` | API key in query | View the dashboard |
| `GET` | `/health` | None | Health check |
