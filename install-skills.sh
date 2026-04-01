#!/usr/bin/env bash
# Install Harness Engineering skills to ~/.claude/skills/ for global availability
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SRC="$SCRIPT_DIR/.claude/skills"
SKILLS_DST="$HOME/.claude/skills"

if [ ! -d "$SKILLS_SRC" ]; then
  echo "Error: skills source directory not found at $SKILLS_SRC"
  exit 1
fi

mkdir -p "$SKILLS_DST"

installed=0
for skill_dir in "$SKILLS_SRC"/harness-*; do
  skill_name="$(basename "$skill_dir")"
  mkdir -p "$SKILLS_DST/$skill_name"
  cp "$skill_dir/SKILL.md" "$SKILLS_DST/$skill_name/SKILL.md"
  echo "  Installed: $skill_name"
  installed=$((installed + 1))
done

echo ""
echo "Done. $installed skills installed to $SKILLS_DST"
echo "Skills are now available globally in all Claude Code projects."
