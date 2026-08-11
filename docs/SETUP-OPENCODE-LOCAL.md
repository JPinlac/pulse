# PULSE on OpenCode with a Local Model (Apple Silicon)

Zero-subscription setup: OpenCode as the CLI, a local model as the brain. Written for a Mac with ≥32GB unified memory (tested target: M5 Pro 48GB). Nothing leaves the machine.

## 1. Serve a local model

Install [LM Studio](https://lmstudio.ai) (friendliest local server on Apple silicon; MLX-native).

- Download a model. Recommended: **Muse Glimmer 30B, 4-bit MLX** (~20GB — distilled specifically for local agentic tool use, Apache 2.0). Alternative if you want faster generations: **Qwen3.6-35B-A3B, 4-bit**.
- Start the local server (Developer tab → Start Server). Note the model id LM Studio displays — you'll paste it into the config below.
- Give the model as much context as memory allows (PULSE sessions are long); 32k minimum.

## 2. Install OpenCode

```bash
curl -fsSL https://opencode.ai/install | bash
# or: npm install -g opencode-ai
```

(If either fails, use the current instructions at https://opencode.ai/docs.)

## 3. Point OpenCode at the local model

Create `~/.config/opencode/opencode.json` (global config — keeps the repo's own `opencode.json` machine-agnostic):

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "lmstudio/YOUR-MODEL-ID",
  "small_model": "lmstudio/YOUR-MODEL-ID",
  "provider": {
    "lmstudio": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "LM Studio (local)",
      "options": { "baseURL": "http://127.0.0.1:1234/v1" },
      "models": {
        "YOUR-MODEL-ID": { "name": "Local PULSE model" }
      }
    }
  }
}
```

Replace both `YOUR-MODEL-ID` occurrences with the id from LM Studio's server page. A copy of this block lives at `docs/opencode.local.example.json`.

## 4. Get PULSE

```bash
git clone <repo-url> pulse
cd pulse
opencode
```

The repo's `AGENTS.md` + `opencode.json` load the engine rules automatically — including from subdirectories like `pulse-vault/`.

## 5. First session

In OpenCode, type:

```
/pulse
```

With an empty vault, the agent bootstraps starter Maps by asking about your efforts (`/efforts bootstrap` runs automatically). From then on the loop is:

```
/pulse    ← start of session
  ...talk, plan, capture...
/close    ← end of session
```

## Troubleshooting

- **Agent ignores commands like `/pulse`**: local models vary in instruction discipline. Say it in words — "run the pulse skill: read `.claude/skills/pulse/SKILL.md` and follow it."
- **Slow responses**: lower the context length in LM Studio, or switch to the A3B model.
- **Rules didn't load**: confirm you launched `opencode` inside the repo (or a subdirectory of it).
