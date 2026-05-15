#!/bin/bash
# Activate Safari and reload the active page
osascript -e 'tell application "Safari" to activate' -e 'tell application "Safari" to tell document 1 to reload'
