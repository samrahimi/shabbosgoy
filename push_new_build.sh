#!/bin/bash
# push_new_build.sh
# Script to increment minor version, build, update release notes, and push to GitHub

set -e  # Exit on error
set -x  # Print commands and their arguments as they are executed

echo "Starting version bump and release process..."

# 1. Increment minor version in pyproject.toml
echo "Incrementing minor version in pyproject.toml..."
CURRENT_VERSION=$(grep -oP 'version = "\K[^"]+' pyproject.toml)
echo "Current version: $CURRENT_VERSION"

# Split version into major.minor.patch
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

# Increment minor version
NEW_MINOR=$((MINOR + 1))
NEW_VERSION="$MAJOR.$NEW_MINOR.$PATCH"
echo "New version: $NEW_VERSION"

# Update pyproject.toml with new version
sed -i "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml
echo "Updated pyproject.toml with new version: $NEW_VERSION"

# 2. Build the new version
echo "Building new version with python3 -m build..."
python3 -m build

# 3. Update RELEASES.md in dist directory
echo "Updating release notes..."
mkdir -p dist
RELEASE_FILE="dist/RELEASES.md"

# Create RELEASES.md if it doesn't exist
if [ ! -f "$RELEASE_FILE" ]; then
    echo "# Release History" > "$RELEASE_FILE"
    echo "" >> "$RELEASE_FILE"
    echo "Creating new RELEASES.md file"
fi

# Add new release entry
CURRENT_DATE=$(date +"%Y-%m-%d")
{
    echo "## $NEW_VERSION ($CURRENT_DATE)"
    echo ""
    echo "- Version bump to $NEW_VERSION"
    echo ""
} >> "$RELEASE_FILE"

echo "Updated $RELEASE_FILE with new version information"

# 4. Push to GitHub
echo "Pushing changes to GitHub..."
git add pyproject.toml "$RELEASE_FILE" dist/*
git commit -m "Bump version to $NEW_VERSION and update release artifacts"
git push origin HEAD

echo "Version bump and release process completed successfully!"
