# admin_theme_manager/utils.py
from colormath.color_objects import sRGBColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

def css_color_to_srgb(css_color):
    """Converts a CSS color string (e.g., 'red', '#FF0000', 'rgb(255, 0, 0)') to an sRGBColor object."""
    try:
        if css_color.startswith('#'):
            hex_color = css_color.lstrip('#')
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            return sRGBColor(r, g, b)
        elif css_color.startswith('rgb('):
            values = css_color[4:-1].split(',')
            if len(values) == 3:
                r = int(values[0].strip()) / 255.0
                g = int(values[1].strip()) / 255.0
                b = int(values[2].strip()) / 255.0
                return sRGBColor(r, g, b)
        elif css_color.lower() in sRGBColor.get_named_colors():
            return sRGBColor.get_named_colors()[css_color.lower()]
        return None
    except ValueError:
        return None

def calculate_contrast_ratio(color1_css, color2_css):
    """Calculates the contrast ratio between two CSS colors based on WCAG 2.0 formula."""
    srgb1 = css_color_to_srgb(color1_css)
    srgb2 = css_color_to_srgb(color2_css)

    if srgb1 and srgb2:
        lum1 = srgb1.get_luminance()
        lum2 = srgb2.get_luminance()

        if lum1 > lum2:
            return (lum1 + 0.05) / (lum2 + 0.05)
        else:
            return (lum2 + 0.05) / (lum1 + 0.05)
    return 0.0

if __name__ == '__main__':
    print(f"Contrast between white and black: {calculate_contrast_ratio('white', 'black')}")
    print(f"Contrast between red and green: {calculate_contrast_ratio('red', 'green')}")
    print(f"Contrast between #333 and #eee: {calculate_contrast_ratio('#333', '#eee')}")