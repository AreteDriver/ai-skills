---
name: align-debug
description: Overlay coordinate grid on screenshots for visual debugging. Helps align UI elements by showing pixel coordinates. Invoke with /align-debug <image-path>.
---

# Align Debug Skill

Overlay a coordinate grid on images to help with UI element alignment.

## Usage

```
/align-debug /path/to/screenshot.png
/align-debug /path/to/screenshot.png --grid 50   # Custom grid size
/align-debug /path/to/screenshot.png --output /tmp/debug.png
```

## Process

1. **Load image and create grid overlay**
   ```python
   from PIL import Image, ImageDraw, ImageFont

   img = Image.open(image_path)
   draw = ImageDraw.Draw(img)
   grid_size = 100  # pixels

   # Draw vertical lines with coordinates
   for x in range(0, img.width, grid_size):
       draw.line([(x, 0), (x, img.height)], fill='red', width=1)
       draw.text((x + 2, 2), str(x), fill='yellow')

   # Draw horizontal lines with coordinates
   for y in range(0, img.height, grid_size):
       draw.line([(0, y), (img.width, y)], fill='red', width=1)
       draw.text((2, y + 2), str(y), fill='yellow')

   output_path = '/tmp/align_debug.png'
   img.save(output_path)
   ```

2. **Display the result**
   - Show the gridded image to user
   - Report image dimensions

## Output

- Grid-overlaid image saved to /tmp/align_debug.png
- Image dimensions reported
- Ready for visual inspection

## Example Script

Save as `align_debug.py`:

```python
#!/usr/bin/env python3
"""Overlay coordinate grid on image for alignment debugging."""
import sys
from PIL import Image, ImageDraw, ImageFont

def add_grid(image_path, grid_size=100, output_path='/tmp/align_debug.png'):
    img = Image.open(image_path).convert('RGBA')
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Draw grid lines
    for x in range(0, img.width, grid_size):
        draw.line([(x, 0), (x, img.height)], fill=(255, 0, 0, 128), width=1)
        draw.text((x + 2, 2), str(x), fill=(255, 255, 0, 200))

    for y in range(0, img.height, grid_size):
        draw.line([(0, y), (img.width, y)], fill=(255, 0, 0, 128), width=1)
        draw.text((2, y + 2), str(y), fill=(255, 255, 0, 200))

    result = Image.alpha_composite(img, overlay)
    result.save(output_path)
    print(f"Grid overlay saved to {output_path}")
    print(f"Image size: {img.width}x{img.height}")
    return output_path

if __name__ == '__main__':
    image_path = sys.argv[1]
    grid_size = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    add_grid(image_path, grid_size)
```
