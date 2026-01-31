#!/bin/bash

# Script to fix YAML frontmatter in product_index.md files
# Removes empty lines within the YAML section (between --- markers)

# Counter for tracking
fixed_count=0

# Find all product_index.md files
find /Users/lxt/Movies/TikTok/WZ/lukas_9688/product_list -name "product_index.md" -type f | while read file; do
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
