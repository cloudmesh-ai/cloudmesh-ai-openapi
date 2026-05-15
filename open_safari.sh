#!/bin/bash
# Try multiple ways to open Safari
if open -a "Safari" "$1"; then
    exit 0
fi

if open -b com.apple.Safari "$1"; then
    exit 0
fi

if osascript -e "tell application \"Safari\" to open location \"$1\""; then
    exit 0
fi

echo "Failed to open Safari"
exit 1
