#!/bin/bash
# Post-install script for Playwright
echo "Installing Playwright browsers..."
playwright install chromium
playwright install-deps chromium
echo "Playwright installation complete!"
