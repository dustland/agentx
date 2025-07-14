#!/bin/bash
# Clear Word Add-in Cache on macOS

echo "🧹 Clearing Word Add-in Cache..."

# Kill Word if running
echo "Closing Word..."
pkill -f "Microsoft Word" 2>/dev/null || true

# Clear Office cache directories
echo "Clearing cache directories..."

# Office cache locations on macOS
rm -rf ~/Library/Containers/com.microsoft.Word/Data/Library/Caches/com.microsoft.Word
rm -rf ~/Library/Containers/com.microsoft.Word/Data/Documents/wef
rm -rf ~/Library/Caches/com.microsoft.Office365ServiceV2
rm -rf ~/Library/Caches/Microsoft/Office/16.0/Wef

# Clear add-in specific data
rm -rf ~/Library/Containers/com.microsoft.Word/Data/Library/Application\ Support/Microsoft/Office/16.0/Wef

echo "✅ Cache cleared!"
echo ""
echo "Next steps:"
echo "1. Open Word"
echo "2. Go to Insert > My Add-ins"
echo "3. Click the three dots next to WordX and select 'Remove'"
echo "4. Click 'Upload My Add-in' and select manifest.xml again"
echo ""
echo "This will force Word to reload the manifest with the new settings."