# admin_theme_manager/utils.py
import re

def srgb_to_linear(color_channel):
    """Converts an sRGB color channel value (0-1) to a linear RGB value."""
    if color_channel <= 0.03928:
        return color_channel / 12.92
    else:
        return ((color_channel + 0.055) / 1.055) ** 2.4

def hex_to_rgb(hex_color):
    """Converts a hex color string (e.g., '#FF0000') to RGB (0-1 tuple)."""
    hex_color = hex_color.lstrip('#')
    # Handle shorthand hex colors (e.g., #F00 -> #FF0000)
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def rgb_string_to_rgb(rgb_string):
    """Converts an rgb() or rgba() string to RGB (0-1 tuple)."""
    # Use regex to extract numbers, handling rgba and potential percentages
    match = re.match(r'rgba?\((\d+%?)\s*,\s*(\d+%?)\s*,\s*(\d+%?)(?:,\s*[\d.]+)?\)', rgb_string)
    if not match:
        raise ValueError(f"Invalid RGB string format: {rgb_string}")

    values = []
    for i in range(1, 4): # R, G, B
        val = match.group(i)
        if val.endswith('%'):
            values.append(float(val.strip('%')) / 100.0)
        else:
            values.append(int(val) / 255.0)
    return tuple(values)


def get_color_rgb_normalized(css_color):
    """
    Converts various CSS color formats to a normalized RGB tuple (0-1 range).
    Handles hex, rgb(), rgba(), and a basic set of named colors.
    """
    css_color_lower = css_color.lower().strip()

    # Named colors (expand this dictionary as needed)
    named_colors = {
        'black': (0, 0, 0), 'white': (1, 1, 1), 'red': (1, 0, 0),
        'green': (0, 0.5, 0), 'blue': (0, 0, 1), 'yellow': (1, 1, 0),
        'cyan': (0, 1, 1), 'magenta': (1, 0, 1), 'gray': (0.5, 0.5, 0.5),
        'lightgray': (0.827, 0.827, 0.827), 'darkgray': (0.662, 0.662, 0.662),
        'orange': (1, 0.647, 0), 'purple': (0.5, 0, 0.5), 'brown': (0.647, 0.165, 0.165),
        'lime': (0, 1, 0), 'navy': (0, 0, 0.5), 'teal': (0, 0.5, 0.5),
        'aqua': (0, 1, 1), 'fuchsia': (1, 0, 1), 'maroon': (0.5, 0, 0),
        'olive': (0.5, 0.5, 0), 'silver': (0.753, 0.753, 0.753), 'gold': (1, 0.843, 0),
        'transparent': (0, 0, 0, 0) # Special case, might need different handling for contrast
    }

    if css_color_lower in named_colors:
        return named_colors[css_color_lower]
    elif css_color_lower.startswith('#'):
        if len(css_color) in [4, 7]: # #RGB or #RRGGBB
            return hex_to_rgb(css_color)
    elif css_color_lower.startswith('rgb(') or css_color_lower.startswith('rgba('):
        return rgb_string_to_rgb(css_color)

    # Fallback for unparseable colors
    print(f"Warning: Could not parse CSS color '{css_color}'. Returning default (black).")
    return (0, 0, 0) # Default to black if color can't be parsed

def rgb_to_luminance(r, g, b):
    """Calculates the relative luminance of an RGB color."""
    lr = srgb_to_linear(r)
    lg = srgb_to_linear(g)
    lb = srgb_to_linear(b)
    return 0.2126 * lr + 0.7152 * lg + 0.0722 * lb

def calculate_contrast_ratio(color1_css, color2_css):
    """Calculates the contrast ratio between two CSS colors based on WCAG 2.0 formula."""
    try:
        rgb1 = get_color_rgb_normalized(color1_css)
        rgb2 = get_color_rgb_normalized(color2_css)

        # Handle transparent for contrast calculation (assume it's against white or black)
        # For simplicity, if one is transparent, we might assume it's against the other's background
        # or a default, but for strict WCAG, transparency needs more complex blending.
        # For now, let's treat it as black if it's transparent for contrast.
        if len(rgb1) == 4 and rgb1[3] == 0: # rgba with alpha 0
            lum1 = rgb_to_luminance(0, 0, 0) # Treat transparent as black for luminance
        else:
            lum1 = rgb_to_luminance(rgb1[0], rgb1[1], rgb1[2])

        if len(rgb2) == 4 and rgb2[3] == 0: # rgba with alpha 0
            lum2 = rgb_to_luminance(0, 0, 0) # Treat transparent as black for luminance
        else:
            lum2 = rgb_to_luminance(rgb2[0], rgb2[1], rgb2[2])


        # Add a small epsilon to avoid division by zero if luminance is 0
        lum1_adjusted = lum1 + 0.05
        lum2_adjusted = lum2 + 0.05

        if lum1_adjusted > lum2_adjusted:
            return lum1_adjusted / lum2_adjusted
        else:
            return lum2_adjusted / lum1_adjusted

    except Exception as e:
        print(f"Error calculating contrast for '{color1_css}' vs '{color2_css}': {e}")
        # Fallback to a safe, non-failing value
        return 1.0 # Minimum contrast ratio (no contrast)

if __name__ == '__main__':
    print(f"Contrast between white and black: {calculate_contrast_ratio('white', 'black')}")
    print(f"Contrast between red and green: {calculate_contrast_ratio('red', 'green')}")
    print(f"Contrast between #333 and #eee: {calculate_contrast_ratio('#333', '#eee')}")
    print(f"Contrast between rgb(255, 0, 0) and rgb(0, 255, 0): {calculate_contrast_ratio('rgb(255, 0, 0)', 'rgb(0, 255, 0)')}")
    print(f"Contrast between #F00 and #0F0 (shorthand hex): {calculate_contrast_ratio('#F00', '#0F0')}")
    print(f"Contrast between rgba(255, 255, 255, 0.5) and black: {calculate_contrast_ratio('rgba(255, 255, 255, 0.5)', 'black')}")
    print(f"Contrast between transparent and white: {calculate_contrast_ratio('transparent', 'white')}")
    print(f"Contrast between unknowncolor and white: {calculate_contrast_ratio('unknowncolor', 'white')}")
