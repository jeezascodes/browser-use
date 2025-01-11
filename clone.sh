#!/bin/bash

# Create knowledge directory one level up
mkdir -p ../knowledge

# Find all files, excluding specified directories
find . -type f \
    ! -path "*/.github/*" \
    ! -path "*/.venv/*" \
    ! -path "*/.vscode/*" \
    ! -path "*/examples/*" \
    ! -path "*/static/*" \
    ! -path "*/tests/*" \
    ! -path "*/knowledge/*" \
    -print0 | while IFS= read -r -d '' file; do
    # Create new filename by replacing / with _
    new_name=$(echo "$file" | sed 's/^\.\///;s/\//_/g')
    # Copy file to knowledge directory
    cp "$file" "../knowledge/$new_name"
    # Add to file structure (excluding the leading ./)
    echo "${file:2}" >> "../knowledge/file_structure.txt"
done

# Sort file structure
sort "../knowledge/file_structure.txt" -o "../knowledge/file_structure.txt"

echo "Directory structure has been cloned to '../knowledge' folder."