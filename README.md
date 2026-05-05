# ELM MCP — talk to IBM ELM from Bob

> **Stop clicking around DOORS Next. Just tell Bob what you want.**
>
> *"Bob, build me a tracking service end-to-end with requirements, tasks, and tests in ELM."*
> *"Bob, import this Jira epic PDF into DNG."*
> *"Bob, what's the team been doing this week?"*

> ⚠️ Personal passion project. **NOT** an official IBM tool. Use at your own risk. IBM, DOORS Next, ELM, EWM, ETM are trademarks of IBM Corp.

---

## Set up Bob in 3 steps (30 seconds)

You need: a Mac/Linux machine, Python 3.9+, and an ELM account.

### Step 1 — install

Open Terminal. Paste this. Hit Enter.

```bash
curl -fsSL https://raw.githubusercontent.com/brettscharm/elm-mcp/main/install.sh | bash
```

That command:
- Downloads ELM MCP to `~/.elm-mcp`
- Asks you for your ELM URL, username, password (typed at the prompt — never sent anywhere except your own machine)
- Writes Bob's MCP config automatically (`~/.bob/mcp_settings.json`)
- Verifies the whole thing works end-to-end

### Step 2 — fully quit + reopen Bob

**Cmd + Q in Bob, then reopen.** Bob only loads MCP servers at startup; you have to actually quit, not just close the window.

### Step 3 — say hi

In any Bob chat, type:

> *"Connect to ELM and list my projects."*

Bob should respond with your DNG projects. **You're done.** Try one of these next:

- *"Build me a temperature converter web app end-to-end."*
- *"Show me what's in the [Module Name] module."*
- *"What can you do?"* (Bob calls `list_capabilities` and shows you the menu)

---

## Common things you'll ask Bob

| You say | What Bob does |
|---|---|
| *"build me a [thing]"* | Full agentic flow: requirements → tasks → tests → review pause → code |
| *"import this Jira epic [paste text or PDF path]"* | Parses the epic into ELM artifacts (epic + reqs + tests + cross-links) |
| *"show me the reqs in [module]"* | Reads the module from DNG, summarizes |
| *"what's the team doing?"* | Reads the BOB Team Actions module, summarizes who did what |
| *"resume my last build"* | Picks up an in-progress build run from where you left off |
| *"I'm done for today"* | Wraps up your session with a final entry teammates can read |
| *"update yourself"* | Pulls the latest version of ELM MCP from GitHub |
| *"are you connected? what version?"* | Self-diagnoses connection state, version, active runs |

You don't have to memorize these. Bob figures it out from natural language. If you're not sure what to do, just type **`/getting-started`** and Bob asks one question to point you at the right starting point.

---

## When something goes wrong

**Bob can't see ELM MCP after install:**
1. Did you fully quit Bob (Cmd+Q) and reopen?
2. Run `python3 ~/.elm-mcp/setup.py --diagnose` — it tells you what's wrong in plain English

**Bob asks for approval on every single action:**
- Re-run `python3 ~/.elm-mcp/setup.py` — refreshes Bob's allow-list with the current set of safe-to-auto-approve tools
- Quit + reopen Bob

**Module binding fails ("requirements created but not in module"):**
- Your DNG project doesn't have configuration management enabled
- Either ask your DNG admin to enable it, or open the module in DNG and drag the requirements in manually
- Then tell Bob *"continue"* and the build flow picks back up

**Anything else:**
- Tell Bob *"run elm_mcp_health"* — it'll dump connection state, version, last update check, etc.
- Or open an issue: https://github.com/brettscharm/elm-mcp/issues

---

## To update

The simplest way: **say *"update yourself"* in any Bob chat.** That's a single tool call — Bob pulls the latest from GitHub and tells you to restart.

Or in terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/brettscharm/elm-mcp/main/install.sh | bash
```

(Same command as install — re-running it just updates.)

---

## What it actually does (for the curious)

ELM MCP is a Model Context Protocol server. It exposes IBM Engineering Lifecycle Management — DNG (requirements), EWM (work items / tasks / defects), ETM (test management), GCM (global config), and SCM/code-review — as **62 tools and 10 prompts** that any MCP-speaking AI assistant can call. Bob is one such assistant; Claude Code, Cursor, Windsurf are others.

The MCP itself does **zero AI generation**. Every tool is a deterministic API call against ELM. The intelligence — writing requirements, parsing PDFs, picking the right module — comes from whichever AI you connect.

The headline workflow is **`/build-new-project`**:
1. You give Bob a one-line idea
2. Bob interviews you (5 min)
3. Bob proposes requirements; you approve
4. Bob proposes tasks; you approve
5. Bob proposes test cases; you approve
6. **STOP** — you review everything in DNG/EWM/ETM
7. Bob re-pulls current state, writes the actual app code with `# Implements: REQ-005` headers tying every file to the requirement
8. Bob marks tasks resolved, records test results in ETM as it goes
9. Final summary: traceability matrix, all URLs clickable

Every phase has an explicit user-approval gate. Bob can't blast through to writing code without your sign-off at each step.

---

## Bring your own AI assistant

Same server works against any MCP-speaking host. `install.sh` writes the right config for every host it detects:

| AI Assistant | Config file written |
|---|---|
| **IBM Bob** | `~/.bob/mcp_settings.json` (global) + `<project>/.bob/mcp.json` (project-local) |
| **Claude Code** | `~/.claude.json` (global) + `.mcp.json` (project) |
| **VS Code Copilot** | `.vscode/mcp.json` |
| **Cursor** | `~/.cursor/mcp.json` |
| **Windsurf** | `~/.codeium/windsurf/mcp_config.json` |

---

## Manual install (only if `curl | bash` doesn't fit your security policy)

```bash
git clone https://github.com/brettscharm/elm-mcp.git ~/.elm-mcp
cd ~/.elm-mcp
python3 setup.py
```

Same outcome, just two more steps.

For air-gapped / locked-down environments where automatic config-write doesn't work, run `python3 ~/.elm-mcp/setup.py --print-config`. It outputs the JSON ready to paste manually into Bob's `~/.bob/mcp_settings.json` with absolute paths pre-filled for your machine.

---

## Privacy + credentials

- ELM password lives ONLY in `~/.elm-mcp/.env` on your machine
- That file is gitignored; it's never committed
- The MCP authenticates directly with your ELM server using your account; no third-party services involved
- Re-enter credentials anytime by deleting `.env` and re-running `setup.py`

---

## File layout (if you want to inspect the code)

```
~/.elm-mcp/
├── setup.py                  # Installer (this is what install.sh runs)
├── doors_mcp_server.py       # The MCP server itself (62 tools)
├── doors_client.py           # ELM REST client (DNG + EWM + ETM + GCM + SCM)
├── BOB.md                    # Instructions Bob reads automatically
├── README.md                 # This file
├── .env                      # YOUR credentials (gitignored, local only)
└── probe/                    # Live-server probes + research notes
```

---

## Help / issues / contributing

- Issues: https://github.com/brettscharm/elm-mcp/issues
- Email: brett.scharmett@ibm.com (personal capacity, not IBM support)

PRs welcome. The probes in `probe/` document the live ELM API surface; new tools should follow the patterns in `doors_client.py` (GET-with-ETag → modify → PUT-with-If-Match for updates; service-provider-discovery → POST to creation factory for creates).

---

## Share with your team

Copy-paste-ready blurb:

> 🤖 **ELM MCP** — drive IBM DOORS Next, EWM, and ETM from Bob (or any AI assistant) instead of clicking around the web UI.
>
> Install in 30 seconds:
> ```
> curl -fsSL https://raw.githubusercontent.com/brettscharm/elm-mcp/main/install.sh | bash
> ```
> Restart Bob. Say *"connect to ELM and list my projects."*
>
> 62 tools, 10 prompts. Read/write requirements (rich text + tables + images), build full projects end-to-end with traceable code, import Jira epics, see what your team's been up to. Full details: https://github.com/brettscharm/elm-mcp
>
> ⚠️ Personal passion project — NOT an official IBM tool.
