---
name: pixel-pick
description: Interactive coordinate picker - click on an image to get exact pixel coordinates. Useful for mapping UI element positions. Invoke with /pixel-pick <image-path>.
lifecycle: experimental
---

# Pixel Pick Skill

Interactive tool to click on an image and get exact pixel coordinates.

## Usage

```
/pixel-pick /path/to/image.png
/pixel-pick /path/to/image.png --output coords.json
```

## Process

1. **Create interactive picker script**
   ```python
   #!/usr/bin/env python3
   """Click on image to get coordinates."""
   import sys
   from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
   from PyQt6.QtGui import QPixmap, QMouseEvent
   from PyQt6.QtCore import Qt

   class PixelPicker(QMainWindow):
       def __init__(self, image_path):
           super().__init__()
           self.setWindowTitle(f"Pixel Picker - {image_path}")
           self.coords = []

           self.label = QLabel()
           self.pixmap = QPixmap(image_path)
           self.label.setPixmap(self.pixmap)
           self.setCentralWidget(self.label)
           self.resize(self.pixmap.size())

       def mousePressEvent(self, event: QMouseEvent):
           x, y = event.pos().x(), event.pos().y()
           print(f"Clicked: ({x}, {y})")
           self.coords.append((x, y))

   if __name__ == '__main__':
       app = QApplication(sys.argv)
       picker = PixelPicker(sys.argv[1])
       picker.show()
       app.exec()
   ```

2. **Run the picker**
   ```bash
   python3 pixel_pick.py /path/to/image.png
   ```

3. **Click on elements to get coordinates**
   - Each click prints (x, y) to terminal
   - Coordinates are relative to image top-left

## Output Format

```
Clicked: (384, 208)
Clicked: (418, 208)
Clicked: (452, 208)
```

## Generating Layout Code

After collecting coordinates, generate code:

```python
# Convert clicks to _box() calls
coords = [(384, 208), (418, 208), (452, 208)]
for i, (x, y) in enumerate(coords):
    print(f'"BUTTON_{i}": _box({x}, {y}, 28, 20),')
```

## Tips

- Click top-left corner of each button
- Note the pattern/spacing for similar buttons
- Use grid overlay (/align-debug) first for reference
