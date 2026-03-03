#!/bin/bash

# Cleanup script for YouTube Human Emulator

echo "🧹 Cleaning up YouTube Human Emulator..."

# Remove old logs
echo "📝 Removing old logs..."
find logs -name "*.log" -type f -mtime +7 -delete
find logs -name "*.log.*" -type f -mtime +7 -delete

# Remove old proxy files
echo "📡 Removing old proxy files..."
find data/proxies -name "working_proxies_*.txt" -type f -mtime +1 -delete
find data/proxies -name "proxy_results_*.json" -type f -mtime +1 -delete

# Remove old session data
echo "💾 Removing old session data..."
find sessions/cookies -name "*.pkl" -type f -mtime +1 -delete
find sessions/profiles -mindepth 1 -maxdepth 1 -type d -mtime +1 -exec rm -rf {} \;

# Remove old stats
echo "📊 Removing old stats..."
find data -name "stats_*.json" -type f -mtime +7 -delete

# Clear temp files
echo "🗑️  Clearing temp files..."
rm -f *.tmp
rm -f *.log
rm -f geckodriver.log

# Create fresh directories
mkdir -p logs data/proxies sessions/cookies sessions/profiles

echo "✅ Cleanup complete!"

# Show disk usage
echo ""
echo "📊 Current disk usage:"
du -sh *