#!/bin/bash

echo "Starting metadata cleanup process..."
echo "Preserving references to Dennis Nedry and vine email addresses"

# Remove EXIF data from images
find . -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" \) -exec echo "Cleaning metadata from {}" \; -exec exiftool -all= {} 2>/dev/null \; || echo "Note: exiftool not found, skipping image metadata cleanup"

# Clean .git directory to remove personal info but preserve example data
if [ -d ".git" ]; then
  echo "Backing up .git/config"
  cp .git/config .git/config.bak
  
  # Update git config to use generic info
  git config --local user.name "GameStopsNow" 
  git config --local user.email "contact@example.com"
  
  echo "Git config updated with generic information"
fi

# Remove potential metadata from document files
find . -type f -name "*.docx" -o -name "*.xlsx" -exec echo "Consider manually checking {}" \;

# Clean up potential hard-coded paths
echo "Cleaning up potential hard-coded paths..."
find . -type f -name "*.py" -o -name "*.ipynb" | xargs grep -l "/Users/" | while read file; do
  # Skip files with Dennis Nedry references
  if grep -q "Dennis Nedry" "$file"; then
    echo "Preserving Dennis Nedry reference in $file"
    continue
  fi
  
  echo "Checking $file for personal paths"
  # Replace personal paths with generic ones
  sed -i.bak 's|/Users/[a-zA-Z0-9_-]*/|/path/to/|g' "$file"
  rm -f "$file.bak"
done

echo "Metadata cleanup complete!"
echo "Note: You may want to manually review files before publishing" 