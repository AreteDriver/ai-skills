---
name: g13-layout
description: Interactive G13 button position editor. Click on device image to set button coordinates. Invoke with /g13-layout.
---

# G13 Layout Skill

Interactive tool for positioning G13 button overlays on the device image.

## Usage

```
/g13-layout                    # Open position editor
/g13-layout --export           # Export to g13_layout.py
/g13-layout --verify           # Verify current positions
```

## Process

1. **Launch the calibration tool**
   ```bash
   cd /home/arete/projects/G13_Linux
   python3 tools/g13_calibrate.py
   ```

2. **Click on button corners**
   - Click top-left of each button
   - Tool records coordinates
   - Preview shows button overlay

3. **Export positions**
   - Generates g13_layout.py code
   - Copy to resources/g13_layout.py

## Button Order

Click buttons in this order for organized output:
1. M1, M2, M3, MR (M-key row)
2. G1-G7 (Row 1)
3. G8-G14 (Row 2)
4. G15-G19 (Row 3)
5. G20-G22 (Row 4)
6. LEFT, DOWN, STICK (thumb area)

## Calibration Script

Save as `tools/g13_calibrate.py`:

```python
#!/usr/bin/env python3
"""Interactive G13 button position calibrator."""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QTextEdit
from PyQt6.QtGui import QPixmap, QMouseEvent, QPainter, QPen, QColor
from PyQt6.QtCore import Qt

BUTTON_ORDER = [
    "M1", "M2", "M3", "MR",
    "G1", "G2", "G3", "G4", "G5", "G6", "G7",
    "G8", "G9", "G10", "G11", "G12", "G13", "G14",
    "G15", "G16", "G17", "G18", "G19",
    "G20", "G21", "G22",
    "LEFT", "DOWN", "STICK"
]

BUTTON_SIZES = {
    "M": (28, 18), "G": (38, 28), "LEFT": (28, 22),
    "DOWN": (28, 22), "STICK": (35, 35)
}

class Calibrator(QMainWindow):
    def __init__(self, image_path):
        super().__init__()
        self.positions = {}
        self.current_idx = 0
        self.image_path = image_path

        self.setWindowTitle("G13 Button Calibrator")
        self.pixmap = QPixmap(image_path)

        layout = QVBoxLayout()
        self.label = QLabel()
        self.label.setPixmap(self.pixmap)
        self.label.mousePressEvent = self.on_click

        self.status = QLabel(f"Click on: {BUTTON_ORDER[0]}")
        self.output = QTextEdit()
        self.output.setMaximumHeight(200)

        layout.addWidget(self.status)
        layout.addWidget(self.label)
        layout.addWidget(self.output)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def on_click(self, event: QMouseEvent):
        if self.current_idx >= len(BUTTON_ORDER):
            return

        x, y = event.pos().x(), event.pos().y()
        btn_name = BUTTON_ORDER[self.current_idx]

        # Determine size based on button type
        if btn_name.startswith("M"):
            w, h = BUTTON_SIZES["M"]
        elif btn_name in ("LEFT", "DOWN", "STICK"):
            w, h = BUTTON_SIZES[btn_name]
        else:
            w, h = BUTTON_SIZES["G"]

        self.positions[btn_name] = (x, y, w, h)
        self.current_idx += 1

        # Update display
        self.update_preview()

        if self.current_idx < len(BUTTON_ORDER):
            self.status.setText(f"Click on: {BUTTON_ORDER[self.current_idx]}")
        else:
            self.status.setText("Done! Copy the output below.")
            self.generate_output()

    def update_preview(self):
        pixmap = QPixmap(self.image_path)
        painter = QPainter(pixmap)
        painter.setPen(QPen(QColor(0, 255, 0), 2))

        for name, (x, y, w, h) in self.positions.items():
            painter.drawRect(x, y, w, h)
            painter.drawText(x + 2, y + 12, name)

        painter.end()
        self.label.setPixmap(pixmap)

    def generate_output(self):
        lines = ['G13_BUTTON_POSITIONS = {']
        for name in BUTTON_ORDER:
            if name in self.positions:
                x, y, w, h = self.positions[name]
                lines.append(f'    "{name}": _box({x}, {y}, {w}, {h}),')
        lines.append('}')
        self.output.setText('\n'.join(lines))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    img = Path(__file__).parent.parent / "src/g13_linux/gui/resources/images/g13_device.png"
    cal = Calibrator(str(img))
    cal.show()
    app.exec()
```

## Verification

After updating positions, verify with:
```bash
python3 -m src.g13_linux.gui.main
```

Check that all buttons align with physical button locations in the image.
