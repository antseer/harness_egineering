# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a **research and documentation repository** for Harness Engineering — an emerging AI/LLM engineering discipline. It contains no executable source code, tests, or CI/CD pipelines. There is no build system.

The core thesis: `Agent = Model + Harness` — improving the harness (tools, orchestration, guardrails, feedback loops) often yields higher ROI than switching to a larger model.

## Content Structure

- **English research reports**: `harness_engineering_research_report.md` (57-paper academic synthesis), `RESEARCH_FINDINGS.md` (90+ source practice-oriented findings)
- **Chinese translations**: `*_zh.md` variants of the above, plus `HARNESS_ENGINEERING_实践指南.md` (7-week implementation roadmap with code examples)
- **Session log**: `SESSION_2026-03-29.md` documents what was produced and key findings
- **`claude.sh`**: Shell script to resume a specific Claude Code session (not general-purpose)
- **`logs/`**: MCP Puppeteer server logs (auto-generated, not manually maintained)

## Working with This Repository

- All deliverables are Markdown files. When editing, preserve bilingual conventions: technical terms use English on first mention with Chinese annotation, all URLs and paper titles stay in original language.
- The `.claude/settings.local.json` whitelists research domains (Anthropic, OpenAI, arXiv, Semantic Scholar, etc.) for web fetching during research sessions.
- This repository is not git-initialized.
