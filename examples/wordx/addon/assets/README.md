# WordX Add-in Icons

This directory contains the icons for the WordX Office.js add-in.

## Icon Files

- `icon-16.svg` - 16x16 icon for ribbon and taskpane
- `icon-32.svg` - 32x32 icon for ribbon and taskpane
- `icon-80.svg` - 80x80 icon for ribbon and taskpane

## Converting to PNG

For production use, you may need PNG versions of these icons. You can convert the SVG files to PNG using:

### Using ImageMagick

```bash
convert icon-16.svg icon-16.png
convert icon-32.svg icon-32.png
convert icon-80.svg icon-80.png
```

### Using Inkscape

```bash
inkscape icon-16.svg --export-png=icon-16.png
inkscape icon-32.svg --export-png=icon-32.png
inkscape icon-80.svg --export-png=icon-80.png
```

### Using Online Tools

- [Convertio](https://convertio.co/svg-png/)
- [CloudConvert](https://cloudconvert.com/svg-to-png)

## Icon Design

The WordX icons feature:

- Purple background (#667eea) representing the Dustland brand
- White document lines representing text/content
- Green checkmark circle (#48bb78) representing AI processing and quality assurance

## Usage in Manifest

The icons are referenced in the `manifest.xml` file:

```xml
<bt:Images>
  <bt:Image id="WordX.tpicon_16x16" DefaultValue="https://localhost:7778/assets/icon-16.png"/>
<bt:Image id="WordX.tpicon_32x32" DefaultValue="https://localhost:7778/assets/icon-32.png"/>
<bt:Image id="WordX.tpicon_80x80" DefaultValue="https://localhost:7778/assets/icon-80.png"/>
</bt:Images>
```

## Customization

To customize the icons:

1. Edit the SVG files with your preferred design
2. Maintain the same dimensions (16x16, 32x32, 80x80)
3. Convert to PNG if needed
4. Update the manifest.xml references
