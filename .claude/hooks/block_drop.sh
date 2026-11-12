#!/bin/bash
INPUT=$(cat)

# To learn about the json input format 
echo "$INPUT" >> "$CLAUDE_PROJECT_DIR/.claude/hooks/hook-input.log"
echo "---" >> "$CLAUDE_PROJECT_DIR/.claude/hooks/hook-input.log"

# Try common field names across Bash/PowerShell tool schemas
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // .tool_input.script // .tool_input.code // empty')

if echo "$COMMAND" | grep -iq "drop" && echo "$COMMAND" | grep -iq "table"; then
  echo "Blocked: dropping tables is not allowed" >&2
  exit 2
fi
exit 0
