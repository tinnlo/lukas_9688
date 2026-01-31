#!/bin/bash

# Script to fix YAML frontmatter in product_index.md files
# Removes empty lines within the YAML section (between --- markers)
#
# Usage:
#   cd scripts && ./fix_yaml_frontmatter.sh           # From scripts directory
#   bash scripts/fix_yaml_frontmatter.sh              # From repo root

# Get repo root (parent of scripts directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
PRODUCT_LIST_DIR="$REPO_ROOT/product_list"

# Counter for tracking
fixed_count=0

# Find all product_index.md files
find "$PRODUCT_LIST_DIR" -name "product_index.md" -type f | while read file; do
    # Check if file has empty lines in YAML frontmatter
    has_empty=$(awk '/^---$/ {count++} count==1 && NF==0 {print "yes"; exit}' "$file")
    
    if [ "$has_empty" = "yes" ]; then
        echo "Fixing: $file"
        
        # Create a temporary file
        temp_file="${file}.tmp"
        
        # Process the file: remove empty lines only within YAML frontmatter
        awk '
        /^---$/ {
            marker_count++
            print
            next
        }
        marker_count == 1 && NF == 0 {
            # Skip empty lines in YAML frontmatter
            next
        }
        {
            print
        }
        ' "$file" > "$temp_file"
        
        # Replace original with fixed version
        mv "$temp_file" "$file"
        
        ((fixed_count++))
    fi
done

echo "Fixed $fixed_count files"
