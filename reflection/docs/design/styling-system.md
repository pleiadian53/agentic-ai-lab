# Styling System Design

Documentation for the custom HTML/CSS styling system used in Jupyter notebooks.

## Overview

The `print_html()` function provides a consistent, professional styling system for displaying content in Jupyter notebooks. Instead of relying on default pandas/matplotlib outputs, we use custom CSS to create a polished, presentation-ready interface.

## Design Philosophy

### Goals
1. **Visual Consistency** - All outputs share a unified design language
2. **Readability** - Clear hierarchy, proper spacing, readable typography
3. **Professional Appearance** - Suitable for demos, presentations, and reports
4. **Accessibility** - Good contrast, clear labels, responsive design

### Non-Goals
- Not trying to replace Jupyter's default styling globally
- Not a full UI framework (just for content display)
- Not customizable per-call (consistent styling is intentional)

## Architecture

### Function Signature

```python
def print_html(
    content: Any,
    title: str | None = None,
    is_image: bool = False
) -> None
```

### Content Type Detection

The function automatically detects and formats different content types:

| Content Type | Detection | Rendering |
|-------------|-----------|-----------|
| **Image** | `is_image=True` and `isinstance(content, str)` | Base64-encoded `<img>` tag |
| **DataFrame** | `isinstance(content, pd.DataFrame)` | HTML table via `df.to_html()` |
| **Series** | `isinstance(content, pd.Series)` | Convert to DataFrame, then table |
| **String** | `isinstance(content, str)` | `<pre><code>` block |
| **Other** | Fallback | `str(content)` in `<pre><code>` |

## CSS Design

### Card Container (`.pretty-card`)

```css
.pretty-card {
  font-family: ui-sans-serif, system-ui;
  border: 2px solid transparent;
  border-radius: 14px;
  padding: 14px 16px;
  margin: 10px 0;
  background: linear-gradient(#fff, #fff) padding-box,
              linear-gradient(135deg, #3b82f6, #9333ea) border-box;
  color: #111;
  box-shadow: 0 4px 12px rgba(0,0,0,.08);
}
```

**Design Decisions:**
- **Gradient Border**: Creates visual interest without being distracting (blue to purple, 135° diagonal)
- **Border Radius**: 14px provides modern, friendly appearance
- **Shadow**: Subtle depth (4px blur, 12px spread, 8% opacity)
- **Padding**: 14px vertical, 16px horizontal for comfortable spacing
- **System Fonts**: Uses native UI fonts for performance and consistency

### Title (`.pretty-title`)

```css
.pretty-title {
  font-weight: 700;
  margin-bottom: 8px;
  font-size: 14px;
  color: #111;
}
```

**Design Decisions:**
- **Bold Weight**: Clear visual hierarchy
- **Small Size**: 14px keeps it subtle but readable
- **Bottom Margin**: 8px separates from content
- **Dark Color**: High contrast for readability

### Code Blocks

```css
.pretty-card pre,
.pretty-card code {
  background: #f3f4f6;
  color: #111;
  padding: 8px;
  border-radius: 8px;
  display: block;
  overflow-x: auto;
  font-size: 13px;
  white-space: pre-wrap;
}
```

**Design Decisions:**
- **Light Gray Background**: Distinguishes code from regular text
- **Word Wrap**: `pre-wrap` allows long lines to wrap
- **Horizontal Scroll**: `overflow-x: auto` for very long lines
- **Smaller Font**: 13px for code readability
- **Rounded Corners**: Consistent with card design

### Tables (`.pretty-table`)

```css
.pretty-card table.pretty-table {
  border-collapse: collapse;
  width: 100%;
  font-size: 13px;
  color: #111;
}

.pretty-card table.pretty-table th,
.pretty-card table.pretty-table td {
  border: 1px solid #e5e7eb;
  padding: 6px 8px;
  text-align: left;
}

.pretty-card table.pretty-table th {
  background: #f9fafb;
  font-weight: 600;
}
```

**Design Decisions:**
- **Collapsed Borders**: Clean, professional appearance
- **Light Borders**: `#e5e7eb` (gray-200) subtle but visible
- **Header Background**: Very light gray (`#f9fafb`) distinguishes headers
- **Compact Padding**: 6px vertical, 8px horizontal for data density
- **Left Alignment**: Standard for tabular data

### Images

```css
.pretty-card img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
}
```

**Design Decisions:**
- **Responsive**: `max-width: 100%` prevents overflow
- **Aspect Ratio**: `height: auto` maintains proportions
- **Rounded Corners**: Consistent with overall design

## Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| **Blue** | `#3b82f6` | Gradient start (primary brand) |
| **Purple** | `#9333ea` | Gradient end (accent) |
| **Dark Gray** | `#111` | Text, high contrast |
| **Light Gray** | `#f3f4f6` | Code background |
| **Very Light Gray** | `#f9fafb` | Table headers |
| **Border Gray** | `#e5e7eb` | Table borders |
| **White** | `#fff` | Card background |

## Implementation Details

### Base64 Image Encoding

```python
def image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")
```

**Why Base64?**
- Embeds images directly in HTML (no external file dependencies)
- Works in any Jupyter environment (local, cloud, exported)
- Self-contained notebooks

### HTML Escaping

```python
from html import escape as _escape
rendered = f"<pre><code>{_escape(content)}</code></pre>"
```

**Why Escape?**
- Prevents XSS vulnerabilities
- Ensures special characters (`<`, `>`, `&`) display correctly
- Safe for user-generated content

### CSS Injection

```python
css = """<style>...</style>"""
card = f'<div class="pretty-card">{title_html}{rendered}</div>'
display(HTML(css + card))
```

**Why Inject CSS Each Time?**
- **Isolation**: Styles only affect the specific card
- **No Global Pollution**: Doesn't interfere with other notebook cells
- **Portability**: Works in exported HTML
- **Simplicity**: No separate CSS file to manage

**Trade-off**: Slight duplication of CSS in notebook output (acceptable for educational use)

## Usage Examples

### Basic DataFrame Display

```python
import pandas as pd
from reflection import utils

df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'score': [95, 87, 92]
})

utils.print_html(df, title="Student Scores")
```

### Image Display

```python
utils.print_html(
    content="chart_v1.png",
    title="Generated Chart (V1)",
    is_image=True
)
```

### Code Display

```python
code = """
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [4, 5, 6])
plt.savefig('output.png')
"""

utils.print_html(code, title="Generated Code")
```

## Customization Guide

### Changing Colors

To modify the gradient colors, edit the `background` property:

```css
background: linear-gradient(#fff, #fff) padding-box,
            linear-gradient(135deg, #YOUR_COLOR_1, #YOUR_COLOR_2) border-box;
```

### Adjusting Spacing

Modify padding/margin values:

```css
.pretty-card {
  padding: 20px;      /* Increase internal spacing */
  margin: 15px 0;     /* Increase vertical spacing between cards */
}
```

### Font Changes

Update the font family:

```css
.pretty-card {
  font-family: 'Your Font', system-ui;
}
```

## Performance Considerations

### CSS Duplication
- Each call injects ~2KB of CSS
- For 100 cells: ~200KB (negligible)
- Trade-off: Simplicity vs. slight size increase

### Base64 Images
- Images are ~33% larger when base64-encoded
- Trade-off: Portability vs. file size
- Acceptable for educational notebooks with few images

### Rendering Speed
- HTML rendering is fast (< 1ms per call)
- No noticeable performance impact

## Future Enhancements

Potential improvements (not currently implemented):

1. **Theme Support** - Light/dark mode toggle
2. **Custom Colors** - Per-call color customization
3. **Animation** - Subtle fade-in effects
4. **Icons** - Add icons to titles
5. **Collapsible Cards** - Expand/collapse for long content
6. **Export Optimization** - Deduplicate CSS in exported HTML

## See Also

- [API Reference - utils.md](../api/utils.md)
- [Getting Started Guide](../guides/getting-started.md)
- [Jupyter Documentation](../../docs/libraries/JUPYTER.md)
