"""
Jira Client for elm-mcp
Direct REST API access to Atlassian Jira Cloud, using API-token Basic auth.

This module exists because Atlassian's official MCP server
(https://mcp.atlassian.com/v1/mcp) uses OAuth 2.1 and the OAuth flow does
not complete reliably inside IBM Bob's embedded webview. So instead of
proxying through that MCP server, elm-mcp talks to Jira's REST API
directly using the user's email + API token (stored in .env alongside
the existing ELM credentials).

NOT an official Atlassian product. Use at your own risk.

Required environment variables (set in ~/.elm-mcp/.env):
  JIRA_BASE_URL    — e.g. https://yourorg.atlassian.net
  JIRA_EMAIL       — the email address tied to the API token
  JIRA_API_TOKEN   — generated at id.atlassian.com/manage-profile/security/api-tokens
"""

import os
import re
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import requests


class JiraClient:
    """Thin wrapper over Jira Cloud REST API v3.

    Designed for the elm-mcp /import-jira workflow:
      • get_issue(key)         — pull a single issue
      • search_issues(jql)     — JQL search
      • add_comment(key, body) — post a markdown-ish comment back to Jira
      • add_remote_link(...)   — structured DNG → Jira back-link

    All methods raise RuntimeError on auth/network failures with a clear
    message; the MCP server catches and surfaces them to the user.
    """

    def __init__(self) -> None:
        load_dotenv()
        base = (os.getenv("JIRA_BASE_URL") or "").strip().rstrip("/")
        email = (os.getenv("JIRA_EMAIL") or "").strip()
        token = (os.getenv("JIRA_API_TOKEN") or "").strip()
        if not (base and email and token):
            raise RuntimeError(
                "Jira credentials missing. Set JIRA_BASE_URL, JIRA_EMAIL, "
                "and JIRA_API_TOKEN in your .env file (~/.elm-mcp/.env). "
                "Get a token from "
                "https://id.atlassian.com/manage-profile/security/api-tokens"
            )
        # Normalize: accept user pasting either the bare org host
        # ("yourorg.atlassian.net") or the full https URL.
        if not base.startswith("http://") and not base.startswith("https://"):
            base = "https://" + base
        self.base_url = base
        self.email = email
        self.session = requests.Session()
        self.session.auth = (email, token)
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "elm-mcp/jira-client",
        })

    # ── Public methods ─────────────────────────────────────────

    def get_issue(self, key_or_url: str) -> Dict[str, Any]:
        """Fetch a single issue by key (e.g. 'PROJ-123') or full browse URL
        ('https://yourorg.atlassian.net/browse/PROJ-123'). Returns a slim
        dict with the fields elm-mcp's /import-jira flow actually uses.
        """
        key = self._normalize_key(key_or_url)
        url = f"{self.base_url}/rest/api/3/issue/{key}"
        r = self.session.get(url, params={"fields": "*all"}, timeout=30)
        self._check_response(r, op=f"GET issue {key}")
        data = r.json()
        return self._summarize_issue(data)

    def search_issues(self, jql: str, max_results: int = 25) -> List[Dict[str, Any]]:
        """JQL search. Returns up to `max_results` slim summaries."""
        url = f"{self.base_url}/rest/api/3/search/jql"
        body = {
            "jql": jql,
            "maxResults": max(1, min(int(max_results), 100)),
            "fields": ["summary", "status", "issuetype", "assignee",
                       "priority", "updated"],
        }
        r = self.session.post(url, json=body, timeout=30)
        self._check_response(r, op=f"POST search ({jql!r})")
        out = []
        for issue in r.json().get("issues", []):
            f = issue.get("fields", {})
            out.append({
                "key": issue.get("key"),
                "url": f"{self.base_url}/browse/{issue.get('key')}",
                "summary": f.get("summary", ""),
                "status": _safe_name(f.get("status")),
                "type": _safe_name(f.get("issuetype")),
                "priority": _safe_name(f.get("priority")),
                "assignee": _resolve_user(f.get("assignee")),
                "updated": f.get("updated"),
            })
        return out

    def add_comment(self, key_or_url: str, body_markdown: str) -> Dict[str, Any]:
        """Post a comment on the given issue. `body_markdown` is converted
        to a minimal Atlassian Document Format (ADF) doc covering
        paragraphs, bullet lists, and [text](url) links — which is exactly
        what the elm-mcp /import-jira back-link template produces.
        """
        key = self._normalize_key(key_or_url)
        url = f"{self.base_url}/rest/api/3/issue/{key}/comment"
        adf = _markdown_to_adf(body_markdown)
        r = self.session.post(url, json={"body": adf}, timeout=30)
        self._check_response(r, op=f"POST comment on {key}")
        data = r.json()
        cid = data.get("id")
        return {
            "id": cid,
            "url": f"{self.base_url}/browse/{key}?focusedCommentId={cid}",
        }

    def add_remote_link(self, key_or_url: str, target_url: str,
                        title: str, *, summary: Optional[str] = None,
                        icon_url: Optional[str] = None) -> Dict[str, Any]:
        """Add a structured remote link on the issue — renders in Jira's
        'Links' panel. Best for DNG-requirement → Jira back-links.
        """
        key = self._normalize_key(key_or_url)
        url = f"{self.base_url}/rest/api/3/issue/{key}/remotelink"
        obj: Dict[str, Any] = {"url": target_url, "title": title}
        if summary:
            obj["summary"] = summary
        if icon_url:
            obj["icon"] = {"url16x16": icon_url, "title": title}
        r = self.session.post(url, json={"object": obj}, timeout=30)
        self._check_response(r, op=f"POST remotelink on {key}")
        return r.json() or {"ok": True, "url": f"{self.base_url}/browse/{key}"}

    def whoami(self) -> Dict[str, Any]:
        """Quick auth check. Returns the authenticated user's profile."""
        url = f"{self.base_url}/rest/api/3/myself"
        r = self.session.get(url, timeout=15)
        self._check_response(r, op="GET myself")
        d = r.json()
        return {
            "accountId": d.get("accountId"),
            "displayName": d.get("displayName"),
            "emailAddress": d.get("emailAddress"),
            "base_url": self.base_url,
        }

    # ── Internals ──────────────────────────────────────────────

    @staticmethod
    def _normalize_key(key_or_url: str) -> str:
        s = (key_or_url or "").strip()
        if "/browse/" in s:
            s = s.rstrip("/").split("/browse/")[-1]
            s = s.split("?")[0].split("#")[0]
        return s

    def _check_response(self, r: requests.Response, *, op: str) -> None:
        if r.status_code in (200, 201, 204):
            return
        snippet = (r.text or "")[:300].replace("\n", " ")
        if r.status_code in (401, 403):
            raise RuntimeError(
                f"Jira auth failed on {op}: HTTP {r.status_code}. "
                f"Check JIRA_EMAIL and JIRA_API_TOKEN in .env. "
                f"Server said: {snippet!r}"
            )
        if r.status_code == 404:
            raise RuntimeError(
                f"Jira returned 404 on {op}. Check the issue key / "
                f"JIRA_BASE_URL ({self.base_url}). Server said: {snippet!r}"
            )
        raise RuntimeError(
            f"Jira {op} failed: HTTP {r.status_code}. Server said: {snippet!r}"
        )

    def _summarize_issue(self, data: Dict[str, Any]) -> Dict[str, Any]:
        f = data.get("fields", {}) or {}
        key = data.get("key")
        comments_block = f.get("comment") or {}
        comments_list = comments_block.get("comments", []) if isinstance(
            comments_block, dict) else []
        # Inline first few comments — useful context for the interview.
        comments_preview = []
        for c in comments_list[-5:]:  # last 5
            comments_preview.append({
                "author": _resolve_user(c.get("author")),
                "created": c.get("created"),
                "body": _adf_to_text(c.get("body")),
            })
        return {
            "key": key,
            "id": data.get("id"),
            "url": f"{self.base_url}/browse/{key}",
            "summary": f.get("summary", ""),
            "description": _adf_to_text(f.get("description")),
            "status": _safe_name(f.get("status")),
            "type": _safe_name(f.get("issuetype")),
            "priority": _safe_name(f.get("priority")),
            "assignee": _resolve_user(f.get("assignee")),
            "reporter": _resolve_user(f.get("reporter")),
            "created": f.get("created"),
            "updated": f.get("updated"),
            "labels": f.get("labels", []) or [],
            "parent": _summarize_parent_or_subtask(f.get("parent")),
            "subtasks": [
                _summarize_parent_or_subtask(st)
                for st in (f.get("subtasks", []) or [])
            ],
            "comments_count": comments_block.get("total", len(comments_list)),
            "comments_preview": comments_preview,
            "attachments_count": len(f.get("attachment", []) or []),
        }


# ── Helpers ─────────────────────────────────────────────────────

def _safe_name(obj: Optional[Dict[str, Any]]) -> str:
    if not obj or not isinstance(obj, dict):
        return ""
    return obj.get("name") or obj.get("displayName") or ""


def _resolve_user(u: Optional[Dict[str, Any]]) -> str:
    if not u or not isinstance(u, dict):
        return ""
    return (u.get("displayName") or u.get("emailAddress")
            or u.get("accountId") or "")


def _summarize_parent_or_subtask(item: Optional[Dict[str, Any]]
                                  ) -> Optional[Dict[str, Any]]:
    if not item:
        return None
    f = item.get("fields", {}) or {}
    return {
        "key": item.get("key"),
        "summary": f.get("summary", ""),
        "status": _safe_name(f.get("status")),
        "type": _safe_name(f.get("issuetype")),
    }


# ── Atlassian Document Format (ADF) helpers ────────────────────
#
# Jira REST API v3 uses ADF (a JSON tree) for rich-text fields like
# description and comment bodies. We only need:
#   • Reading ADF → flat markdown-ish text (for showing to the user)
#   • Writing minimal ADF for our back-link comments (paragraphs +
#     bullet lists + [text](url) links)
#
# Not a full ADF implementation — just the subset elm-mcp produces and
# the subset Jira issues commonly contain. Unknown nodes pass through
# as their text content.

def _adf_to_text(node: Any) -> str:
    """Best-effort flatten of ADF to readable markdown."""
    if node is None or node == "":
        return ""
    if isinstance(node, str):
        return node
    if not isinstance(node, dict):
        return ""

    t = node.get("type")
    content = node.get("content", []) or []

    if t == "text":
        text = node.get("text", "")
        for mark in node.get("marks", []) or []:
            mt = mark.get("type")
            if mt == "strong":
                text = f"**{text}**"
            elif mt == "em":
                text = f"*{text}*"
            elif mt == "code":
                text = f"`{text}`"
            elif mt == "strike":
                text = f"~~{text}~~"
            elif mt == "link":
                href = (mark.get("attrs") or {}).get("href", "")
                if href:
                    text = f"[{text}]({href})"
        return text

    if t == "paragraph":
        return "".join(_adf_to_text(c) for c in content) + "\n\n"
    if t == "heading":
        level = (node.get("attrs") or {}).get("level", 1)
        return ("#" * level) + " " + "".join(
            _adf_to_text(c) for c in content) + "\n\n"
    if t == "bulletList":
        return "".join("- " + _adf_to_text(c) for c in content)
    if t == "orderedList":
        return "".join(
            f"{i + 1}. " + _adf_to_text(c) for i, c in enumerate(content))
    if t == "listItem":
        inner = "".join(_adf_to_text(c) for c in content).rstrip("\n")
        return inner + "\n"
    if t == "codeBlock":
        lang = (node.get("attrs") or {}).get("language", "")
        body = "".join(_adf_to_text(c) for c in content)
        return f"```{lang}\n{body}\n```\n\n"
    if t == "blockquote":
        inner = "".join(_adf_to_text(c) for c in content).rstrip("\n")
        # Prefix each line with "> "
        quoted = "\n".join(f"> {ln}" for ln in inner.split("\n"))
        return quoted + "\n\n"
    if t == "hardBreak":
        return "\n"
    if t == "rule":
        return "\n---\n\n"
    if t in ("mediaSingle", "mediaGroup", "media"):
        alt = (node.get("attrs") or {}).get("alt", "[media]")
        return f"![{alt}]\n\n"
    if t in ("mention",):
        attrs = node.get("attrs") or {}
        return f"@{attrs.get('text') or attrs.get('id') or 'unknown'}"
    if t in ("emoji",):
        attrs = node.get("attrs") or {}
        return attrs.get("shortName") or attrs.get("text") or ""
    if t == "doc" or t is None:
        return "".join(_adf_to_text(c) for c in content)
    # Unknown — best effort
    return "".join(_adf_to_text(c) for c in content)


_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def _inline_to_adf(text: str) -> List[Dict[str, Any]]:
    """Convert a single line of text into ADF inline content, recognizing
    [label](url) markdown link syntax. Everything else is plain text.
    """
    out: List[Dict[str, Any]] = []
    pos = 0
    for m in _LINK_RE.finditer(text):
        before = text[pos:m.start()]
        if before:
            out.append({"type": "text", "text": before})
        label, href = m.group(1), m.group(2)
        out.append({
            "type": "text",
            "text": label,
            "marks": [{"type": "link", "attrs": {"href": href}}],
        })
        pos = m.end()
    tail = text[pos:]
    if tail:
        out.append({"type": "text", "text": tail})
    if not out:
        out = [{"type": "text", "text": text or " "}]
    return out


def _markdown_to_adf(md: str) -> Dict[str, Any]:
    """Minimal markdown → ADF for elm-mcp's back-link comments.
    Handles: paragraphs, bullet/numbered lists, [label](url) links,
    **bold** is NOT converted (left as literal — fine for the template).
    """
    blocks: List[Dict[str, Any]] = []
    lines = (md or "").replace("\r\n", "\n").split("\n")
    i = 0
    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()
        if not stripped:
            i += 1
            continue
        # Bullet list
        if stripped.startswith("- ") or stripped.startswith("* "):
            items = []
            while i < len(lines) and lines[i].strip().startswith(("- ", "* ")):
                item_text = lines[i].strip()[2:]
                items.append({
                    "type": "listItem",
                    "content": [{
                        "type": "paragraph",
                        "content": _inline_to_adf(item_text),
                    }],
                })
                i += 1
            blocks.append({"type": "bulletList", "content": items})
            continue
        # Numbered list
        if re.match(r"^\d+\.\s", stripped):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s", lines[i].strip()):
                item_text = re.sub(r"^\d+\.\s", "", lines[i].strip())
                items.append({
                    "type": "listItem",
                    "content": [{
                        "type": "paragraph",
                        "content": _inline_to_adf(item_text),
                    }],
                })
                i += 1
            blocks.append({"type": "orderedList", "content": items})
            continue
        # Plain paragraph
        blocks.append({
            "type": "paragraph",
            "content": _inline_to_adf(stripped),
        })
        i += 1

    if not blocks:
        blocks = [{
            "type": "paragraph",
            "content": [{"type": "text", "text": " "}],
        }]

    return {
        "type": "doc",
        "version": 1,
        "content": blocks,
    }
