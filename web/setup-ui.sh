#!/bin/bash

# VibeX UI Setup Script
# This script updates dependencies and installs all required shadcn/ui components

echo "🚀 Setting up VibeX..."

# Update all dependencies to latest versions
echo "📦 Updating dependencies to latest versions..."
pnpm update --latest

# Install any missing dependencies
echo "📦 Installing dependencies..."
pnpm install

# Install shadcn/ui components
components=(
  "button"
  "card"
  "tabs"
  "badge"
  "select"
  "textarea"
  "toast"
  "dialog"
  "dropdown-menu"
  "label"
  "skeleton"
  "separator"
  "scroll-area"
  "avatar"
  "progress"
  "alert"
  "input"
)

echo "🎨 Installing shadcn/ui components..."

for component in "${components[@]}"; do
  echo "Installing $component..."
  pnpm dlx shadcn@latest add "$component" --yes
done

echo "✅ UI components setup complete!"
echo ""
echo "🎯 Next steps:"
echo "  1. Run 'pnpm dev' to start the development server"
echo "  2. Open http://localhost:7777 in your browser"
echo ""