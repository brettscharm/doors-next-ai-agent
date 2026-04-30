#!/usr/bin/env bash
#
# ELM MCP — one-command installer.
#
# Run this from any terminal:
#
#   curl -fsSL https://raw.githubusercontent.com/brettscharm/elm-mcp/main/install.sh | bash
#
# It clones the repo to a stable location, runs setup.py to wire up your
# AI host (IBM Bob, Claude Code, Cursor, VS Code, Windsurf), and prompts
# for your ELM credentials. Re-running it later updates the clone in
# place and re-runs setup. Idempotent.
#
# NOT an official IBM product. Personal passion project. Use at your
# own risk.

set -euo pipefail

REPO_URL="https://github.com/brettscharm/elm-mcp.git"
INSTALL_DIR="${ELM_MCP_DIR:-$HOME/.elm-mcp}"

# ── Pretty output ────────────────────────────────────────────
if [ -t 1 ]; then
  BOLD=$'\033[1m'; DIM=$'\033[2m'; GREEN=$'\033[92m'; RED=$'\033[91m'; RESET=$'\033[0m'
else
  BOLD=""; DIM=""; GREEN=""; RED=""; RESET=""
fi
say()  { printf "%s\n" "$*"; }
ok()   { printf "  ${GREEN}OK${RESET}  %s\n" "$*"; }
fail() { printf "  ${RED}FAIL${RESET}  %s\n" "$*"; exit 1; }
step() { printf "\n${BOLD}%s${RESET}\n" "$*"; }

say "${BOLD}ELM MCP installer${RESET}"
say "${DIM}Personal passion project — not an official IBM product. Use at your own risk.${RESET}"

# ── Prerequisites ────────────────────────────────────────────
step "[1/4] Checking prerequisites"
command -v git >/dev/null 2>&1 || fail "git is not installed."
ok "git: $(git --version)"

PY=""
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1; then
    if "$candidate" -c "import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)" 2>/dev/null; then
      PY="$candidate"; break
    fi
  fi
done
[ -n "$PY" ] || fail "Python 3.9+ is required. Install from https://www.python.org/downloads/ and re-run."
ok "$PY: $($PY --version 2>&1)"

# ── Clone or update ──────────────────────────────────────────
step "[2/4] Clone or update the repo at $INSTALL_DIR"
if [ -d "$INSTALL_DIR/.git" ]; then
  ok "Existing clone found — pulling latest"
  git -C "$INSTALL_DIR" fetch --quiet origin
  git -C "$INSTALL_DIR" reset --hard --quiet origin/main
  ok "Updated: $(git -C "$INSTALL_DIR" rev-parse --short HEAD)"
elif [ -e "$INSTALL_DIR" ]; then
  fail "$INSTALL_DIR exists but isn't a git checkout. Move/delete it and re-run."
else
  git clone --quiet "$REPO_URL" "$INSTALL_DIR"
  ok "Cloned: $(git -C "$INSTALL_DIR" rev-parse --short HEAD)"
fi

# ── Run setup.py ─────────────────────────────────────────────
step "[3/4] Running setup.py (deps + AI host config + smoke test)"
cd "$INSTALL_DIR"
"$PY" setup.py

# ── Done ─────────────────────────────────────────────────────
step "[4/4] Done — and here's the manual-fallback info"
PY_ABS=$(command -v "$PY")
SERVER_ABS="$INSTALL_DIR/doors_mcp_server.py"
say ""
say "  ${GREEN}✓${RESET} ELM MCP installed at: ${BOLD}$INSTALL_DIR${RESET}"
say "  ${GREEN}✓${RESET} Configs written to every AI host detected."
say "  ${GREEN}✓${RESET} Now: ${BOLD}fully quit and reopen your AI assistant${RESET} (Cmd+Q on macOS), then say:"
say "    ${BOLD}\"Connect to ELM and list my projects\"${RESET}"
say ""
say "${BOLD}If your AI doesn't see the MCP server after restart${RESET} (e.g. some IBM Bob"
say "deployments don't auto-load configs), paste the JSON below into the right"
say "config file for your host. The two paths in it are already filled in for"
say "your machine."
say ""
say "${BOLD}Where the file goes${RESET} (create it if missing):"
say "  • IBM Bob (recommended):  ${BOLD}~/.bob/mcp_settings.json${RESET}"
say "  • Claude Code:            ${BOLD}~/.claude.json${RESET}"
say "  • VS Code:                ${BOLD}<your-project>/.vscode/mcp.json${RESET}  (uses 'servers' key, not 'mcpServers')"
say "  • Cursor:                 ${BOLD}~/.cursor/mcp.json${RESET}"
say "  • Windsurf:               ${BOLD}~/.codeium/windsurf/mcp_config.json${RESET}"
say ""
say "${BOLD}JSON to paste${RESET} (top-level key 'mcpServers' for Bob/Claude/Cursor/Windsurf;"
say "VS Code uses 'servers' instead):"
say ""
cat <<JSON
{
  "mcpServers": {
    "doors-next": {
      "command": "$PY_ABS",
      "args": [
        "$SERVER_ABS"
      ],
      "alwaysAllow": [
        "connect_to_elm", "list_projects", "get_modules",
        "get_module_requirements", "save_requirements",
        "search_requirements", "get_artifact_types", "get_link_types",
        "get_attribute_definitions", "list_baselines",
        "compare_baselines", "extract_pdf",
        "list_global_configurations", "list_global_components",
        "get_global_config_details", "query_work_items",
        "scm_list_projects", "scm_list_changesets",
        "scm_get_changeset", "scm_get_workitem_changesets",
        "review_get", "review_list_open", "generate_chart",
        "update_elm_mcp"
      ]
    }
  }
}
JSON
say ""
say "${BOLD}Your filled-in paths (you can also copy these directly):${RESET}"
say "  Python interpreter:  ${BOLD}$PY_ABS${RESET}"
say "  Server script:       ${BOLD}$SERVER_ABS${RESET}"
say ""
say "  ${DIM}To update later: re-run this same curl command, or:${RESET}"
say "    ${DIM}cd \"$INSTALL_DIR\" && git pull && $PY setup.py${RESET}"
say "  ${DIM}Or just talk to your AI: \"update yourself\" (uses the update_elm_mcp tool).${RESET}"
say ""
