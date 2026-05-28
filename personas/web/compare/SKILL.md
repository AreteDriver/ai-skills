---
name: compare
description: Side-by-side image comparison with difference highlighting. Useful for visual regression testing and UI changes. Invoke with /compare <image1> <image2>.
---

# Compare Skill

Compare two images side-by-side with difference highlighting.

## Usage

```
/compare before.png after.png
/compare before.png after.png --output diff.png
/compare before.png after.png --threshold 10
```

## Process

1. **Load and compare images**
   ```python
   from PIL import Image, ImageChops, ImageDraw

   img1 = Image.open(image1_path).convert('RGB')
   img2 = Image.open(image2_path).convert('RGB')

   # Compute difference
   diff = ImageChops.difference(img1, img2)

   # Highlight differences
   diff_enhanced = diff.point(lambda x: min(x * 10, 255))
   ```

2. **Create comparison output**
   - Side-by-side view
   - Difference overlay
   - Stats on changed pixels

## Example Script

```python
#!/usr/bin/env python3
"""Compare two images and highlight differences."""
import sys
from PIL import Image, ImageChops, ImageDraw

def compare_images(img1_path, img2_path, output_path='/tmp/compare.png'):
    img1 = Image.open(img1_path).convert('RGB')
    img2 = Image.open(img2_path).convert('RGB')

    # Resize if different sizes
    if img1.size != img2.size:
        img2 = img2.resize(img1.size)

    # Compute difference
    diff = ImageChops.difference(img1, img2)

    # Count different pixels
    diff_data = list(diff.getdata())
    changed = sum(1 for px in diff_data if sum(px) > 30)
    total = len(diff_data)
    pct = (changed / total) * 100

    # Create side-by-side with diff
    width = img1.width * 3 + 20
    height = img1.height
    result = Image.new('RGB', (width, height), (30, 30, 30))

    result.paste(img1, (0, 0))
    result.paste(img2, (img1.width + 10, 0))

    # Enhanced diff (boost visibility)
    diff_enhanced = diff.point(lambda x: min(x * 5, 255))
    result.paste(diff_enhanced, (img1.width * 2 + 20, 0))

    # Add labels
    draw = ImageDraw.Draw(result)
    draw.text((10, 10), "BEFORE", fill='white')
    draw.text((img1.width + 20, 10), "AFTER", fill='white')
    draw.text((img1.width * 2 + 30, 10), f"DIFF ({pct:.1f}%)", fill='red')

    result.save(output_path)
    print(f"Comparison saved to {output_path}")
    print(f"Changed pixels: {changed}/{total} ({pct:.2f}%)")
    return output_path

if __name__ == '__main__':
    compare_images(sys.argv[1], sys.argv[2])
```

## Output

- Three-panel image: BEFORE | AFTER | DIFF
- Percentage of changed pixels
- Visual highlight of differences
