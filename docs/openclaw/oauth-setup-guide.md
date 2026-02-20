# OpenClaw: Using Subscription OAuth Instead of the API

**Why this matters:** Using OpenClaw with a direct API key is expensive. A single
"hello" message to Claude Opus or GPT models can consume 50,000+ context tokens
due to system prompts and memory files loaded on every turn. At API rates
($15–$25 per million output tokens), costs accumulate fast — easily $25+/day
for active use. OAuth subscription authentication routes requests through your
existing ChatGPT Pro or Gemini subscription instead, at a fraction of the cost.

---

## Provider Landscape (as of February 2026)

| Provider | OAuth Allowed? | Notes |
|---|---|---|
| **OpenAI (ChatGPT Pro)** | ✅ Yes | OpenAI explicitly permits this via Codex CLI OAuth |
| **Google (Gemini)** | ✅ Yes | Supported via Gemini CLI OAuth plugin |
| **Anthropic (Claude)** | ❌ Banned | Blocked on January 9, 2026; violates Claude ToS |

Anthropic's policy: *"Using OAuth tokens obtained through Claude Free, Pro, or
Max accounts in any other product, tool, or service — including the Agent SDK —
is not permitted."* Setup-tokens via `claude setup-token` remain technically
functional but carry the same enforcement risk under their Terms of Service.

---

## Option 1: OpenAI Codex OAuth (Recommended)

Requires an active **ChatGPT Pro** subscription. OpenAI has publicly confirmed
this use case is permitted.

### Step 1 — Run the onboarding wizard

```bash
openclaw onboard --auth-choice codex-cli --skip-channels --skip-skills --skip-daemon
```

- `--auth-choice codex-cli` uses the Codex CLI's OAuth flow, which handles the
  browser callback automatically without requiring manual URL pasting.
- The `--skip-*` flags bypass channel and skill setup so you only touch auth.

When prompted for onboarding mode, select **QuickStart**.

A browser window will open to OpenAI's login page. Sign in with your ChatGPT Pro
account. The terminal completes automatically after authentication — you do not
need to copy or paste any URLs.

### Step 2 — Set the Codex model as primary

```bash
openclaw models set openai-codex/gpt-5.3-codex
```

> **Note on naming:** `openai-codex/gpt-5.3-codex` means GPT-5.3 accessed via
> the Codex OAuth path. The `-codex` suffix refers to the *access route* (ChatGPT
> subscription), not a code-specialized model variant. Capability is identical to
> the API-accessed version.

### Step 3 — Remove the API key

If you previously set `OPENAI_API_KEY` in `~/.openclaw/.env`, clear it so it
cannot be used as a fallback:

```bash
echo "" > ~/.openclaw/.env
```

If the key was set as a shell environment variable (e.g. in `~/.zshrc`), remove
that line and reload your shell:

```bash
# Remove the export line from ~/.zshrc, then:
source ~/.zshrc
```

### Step 4 — Verify

```bash
openclaw models status
```

Look for the `openai-codex` OAuth profile with an expiry timestamp. If you see
an API key listed instead of an OAuth profile, the switch did not complete.

---

## Option 2: Google Gemini CLI OAuth

Requires a Google account. Works with free-tier Gemini access as well as paid
Google AI Pro/Ultra subscriptions.

### Step 1 — Enable the bundled plugin

```bash
openclaw plugins enable google-gemini-cli-auth
```

### Step 2 — Authenticate

```bash
openclaw models auth login --provider google-gemini-cli --set-default
```

A browser window opens for Google OAuth. Sign in with your Google account. The
`--set-default` flag automatically sets the authenticated Gemini model as your
primary.

### Step 3 — Verify

```bash
openclaw models status
```

You should see a `google-gemini-cli` OAuth profile.

---

## Locking Out API Fallback

With OAuth configured, OpenClaw may still fall back to an API key if one is
present in the environment. To make subscription-only operation strict:

1. Clear `~/.openclaw/.env` (see Step 3 above).
2. Check for keys set at the shell level:
   ```bash
   grep -n "OPENAI_API_KEY\|ANTHROPIC_API_KEY\|GEMINI_API_KEY" ~/.zshrc ~/.zprofile
   ```
3. Remove any lines found and reload the shell.

After this, any accidental use of an API-key provider will fail loudly rather
than silently billing you.

---

## Token Refresh

OAuth tokens expire periodically. OpenClaw handles refresh automatically at
runtime — when a stored token is near expiry, it refreshes silently using the
stored refresh token. You generally do not need to re-run the login flow.

If a token becomes invalid (e.g. you revoked access from your OpenAI account
settings), re-run the relevant onboard command to get a fresh token:

```bash
# OpenAI Codex
openclaw onboard --auth-choice codex-cli --skip-channels --skip-skills --skip-daemon

# Gemini
openclaw models auth login --provider google-gemini-cli --set-default
```

---

## Choosing a Model After OAuth Setup

```bash
# List available models (configured ones)
openclaw models list

# Switch model for the current session (in chat)
/model openai-codex/gpt-5.3-codex

# Set a permanent default
openclaw models set openai-codex/gpt-5.3-codex
```

Avoid selecting any `openai/*` or `anthropic/*` model while OAuth-only operation
is intended — those providers route through API keys, not subscription OAuth.

---

## Troubleshooting

**"No provider plugins found"** when running `openclaw models auth login --provider openai-codex`  
→ Use the onboard wizard instead: `openclaw onboard --auth-choice codex-cli`

**OAuth browser callback fails / terminal gets stuck asking to paste URL**  
→ The `openai-codex` auth choice uses a localhost callback that may not bind
  correctly. Use `codex-cli` instead — it completes the callback without
  requiring manual URL pasting.

**"Token exchange failed" (400 error)**  
→ The authorization code expired before it was submitted (codes are single-use
  and short-lived). Re-run the onboard command to get a fresh code.

**Model still showing API key in `openclaw models status`**  
→ The primary model may still be pointing at `openai/gpt-5.2` (API provider).
  Run `openclaw models set openai-codex/gpt-5.3-codex` to switch.

**"You exceeded your current quota"**  
→ OpenClaw is still using the API key. Check that `~/.openclaw/.env` is empty
  and that no `OPENAI_API_KEY` is set in your shell environment.
