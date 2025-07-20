#!/usr/bin/env bash
set -e

echo "Testing toshy-tray service management..."

echo "Starting toshy-tray service..."
systemctl --user start toshy-tray

echo "Checking service status..."
systemctl --user --no-pager status toshy-tray

echo "Stopping toshy-tray service..."
systemctl --user stop toshy-tray

echo "Enabling toshy-tray service..."
systemctl --user enable toshy-tray

echo "Disabling toshy-tray service..."
systemctl --user disable toshy-tray

echo "Verifying toshy-gui can be launched from command line..."
which toshy-gui
if [ $? -eq 0 ]; then
  echo "toshy-gui command is available"
else
  echo "ERROR: toshy-gui command is not available"
  exit 1
fi

echo "Service management tests completed successfully!"
