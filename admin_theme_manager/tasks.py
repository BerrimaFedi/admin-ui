# admin_theme_manager/tasks.py
import os
import subprocess
from celery import shared_task
from django.conf import settings
from admin_theme_manager.models import AdminTheme
from .utils import calculate_contrast_ratio
import cssutils
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import models
from pathlib import Path
import json


def is_css_variable(color_value):
    return color_value.startswith('var(--')


@shared_task
def compile_scss(scss_filepath, css_filepath):
    try:
        subprocess.run(['sass', scss_filepath, css_filepath], check=True, capture_output=True, text=True)
        return f"SCSS compiled successfully: {css_filepath}"
    except subprocess.CalledProcessError as e:
        return f"Error compiling SCSS for {scss_filepath}: {e.stderr}"


@shared_task
def deploy_static_assets():
    try:
        subprocess.run(['python', 'manage.py', 'collectstatic', '--noinput'], check=True, capture_output=True, text=True)
        return "Static assets deployed successfully."
    except subprocess.CalledProcessError as e:
        return f"Error deploying static assets: {e.stderr}"


@shared_task
def analyze_ui_suggestions(theme_id):
    print(f"Analyzing theme ID: {theme_id}")
    try:
        theme = AdminTheme.objects.get(pk=theme_id)
        print(f"Found theme: {theme.name}")

        css_file_path = Path(settings.BASE_DIR) / 'admin_theme_manager' / 'static' / theme.css_url
        print(f"Attempting to open CSS file: {css_file_path}")

        if not css_file_path.exists():
            print(f"CSS file NOT found: {css_file_path}")
            return f"CSS file not found for theme '{theme.name}' at '{css_file_path}'."

        with open(css_file_path, 'r', encoding='utf-8') as f:
            css = f.read()
        print(f"Successfully read CSS content from {css_file_path}. Length: {len(css)} characters.")

        stylesheet = cssutils.parseString(css)
        contrast_issues = []
        color_used_without_other_indicators = []
        processed_pairs = set()

        for rule in stylesheet.cssRules:
            if rule.type == rule.STYLE_RULE:
                declarations = rule.style.getProperties()
                colors = {}
                text_decoration = False
                font_weight = False
                for prop in declarations:
                    if prop.name in ['color', 'background-color']:
                        colors[prop.name] = prop.value
                    if prop.name == 'text-decoration':
                        text_decoration = True
                    if prop.name == 'font-weight' and prop.value in ['bold', '700', '800', '900']:
                        font_weight = True

                if 'color' in colors and not (text_decoration or font_weight):
                    if not is_css_variable(colors['color']):
                        color_used_without_other_indicators.append(f"Rule '{rule.selectorText}' uses color '{colors.get('color', 'N/A')}' without text decoration or bold font-weight.")
                    else:
                        color_used_without_other_indicators.append(f"Rule '{rule.selectorText}' uses color variable '{colors.get('color', 'N/A')}' without text decoration or bold font-weight (cannot determine actual color).")

                if 'color' in colors and 'background-color' in colors:
                    color1 = colors['color']
                    color2 = colors['background-color']
                    if not (is_css_variable(color1) or is_css_variable(color2)):
                        pair = tuple(sorted((color1, color2)))
                        if pair not in processed_pairs:
                            ratio = calculate_contrast_ratio(color1, color2)
                            if ratio < 4.5:
                                contrast_issues.append({
                                    'selector': rule.selectorText,
                                    'color1': color1,
                                    'color2': color2,
                                    'ratio': round(ratio, 2),
                                    'message': f"Low contrast ({ratio:.2f}) between '{color1}' and '{color2}'."
                                })
                            processed_pairs.add(pair)
                    else:
                        contrast_issues.append({
                            'selector': rule.selectorText,
                            'color1': color1,
                            'color2': color2,
                            'ratio': 1.0,  # Indicate potential issue, but inaccurate
                            'message': f"Cannot accurately calculate contrast for '{rule.selectorText}' due to CSS variables: '{color1}' vs '{color2}'."
                        })
                elif 'color' in colors and 'background-color' not in colors:
                    if not is_css_variable(colors['color']):
                        body_bg = None
                        for r in stylesheet.cssRules:
                            if r.type == r.STYLE_RULE and r.selectorText.lower() == 'body':
                                body_bg = r.style.getPropertyValue('background-color')
                                break
                        if not body_bg:
                            body_bg = 'white'
                            print(f"Debug: No explicit body background found for '{rule.selectorText}', assuming default '{body_bg}'.")

                        if body_bg and not is_css_variable(body_bg):
                            ratio = calculate_contrast_ratio(colors['color'], body_bg)
                            if ratio < 4.5:
                                contrast_issues.append({
                                    'selector': rule.selectorText,
                                    'color1': colors['color'],
                                    'color2': body_bg,
                                    'ratio': round(ratio, 2),
                                    'message': f"Low contrast ({ratio:.2f}) between text color '{colors['color']}' and assumed body background '{body_bg}'."
                                })
                        elif body_bg:
                            contrast_issues.append({
                                'selector': rule.selectorText,
                                'color1': colors['color'],
                                'color2': body_bg,
                                'ratio': 1.0,  # Indicate potential issue
                                'message': f"Cannot accurately calculate contrast for '{rule.selectorText}' (text color '{colors['color']}') as background '{body_bg}' involves a CSS variable."
                            })
                        else:
                            contrast_issues.append({
                                'selector': rule.selectorText,
                                'color1': colors['color'],
                                'color2': 'white (assumed)',
                                'ratio': 1.0,  # Indicate potential issue
                                'message': f"Cannot accurately calculate contrast for '{rule.selectorText}' (text color '{colors['color']}') as body background couldn't be determined."
                            })
                    else:
                        body_bg = None
                        for r in stylesheet.cssRules:
                            if r.type == r.STYLE_RULE and r.selectorText.lower() == 'body':
                                body_bg = r.style.getPropertyValue('background-color')
                                break
                        contrast_issues.append({
                            'selector': rule.selectorText,
                            'color1': colors['color'],
                            'color2': body_bg if body_bg else 'white (assumed)',
                            'ratio': 1.0,  # Indicate potential issue
                            'message': f"Cannot accurately calculate contrast for '{rule.selectorText}' (text color '{colors['color']}' is a variable)."
                        })
                elif 'background-color' in colors and 'color' not in colors:
                    if not is_css_variable(colors['background-color']):
                        body_color = None
                        for r in stylesheet.cssRules:
                            if r.type == r.STYLE_RULE and r.selectorText.lower() == 'body':
                                body_color = r.style.getPropertyValue('color')
                                break
                        if not body_color:
                            body_color = 'black'
                            print(f"Debug: No explicit body text color found for '{rule.selectorText}', assuming default '{body_color}'.")

                        if body_color and not is_css_variable(body_color):
                            ratio = calculate_contrast_ratio(body_color, colors['background-color'])
                            if ratio < 4.5:
                                contrast_issues.append({
                                    'selector': rule.selectorText,
                                    'color1': body_color,
                                    'color2': colors['background-color'],
                                    'ratio': round(ratio, 2),
                                    'message': f"Low contrast ({ratio:.2f}) between assumed body text color '{body_color}' and background '{colors['background-color']}'."
                                })
                        elif body_color:
                            contrast_issues.append({
                                'selector': rule.selectorText,
                                'color1': body_color,
                                'color2': colors['background-color'],
                                'ratio': 1.0,  # Indicate potential issue
                                'message': f"Cannot accurately calculate contrast for '{rule.selectorText}' (background '{colors['background-color']}') as text color '{body_color}' involves a CSS variable."
                            })
                        else:
                            contrast_issues.append({
                                'selector': rule.selectorText,
                                'color1': 'black (assumed)',
                                'color2': colors['background-color'],
                                'ratio': 1.0,  # Indicate potential issue
                                'message': f"Cannot accurately calculate contrast for '{rule.selectorText}' (background '{colors['background-color']}') as body text color couldn't be determined."
                            })
                    else:
                        body_color = None
                        for r in stylesheet.cssRules:
                            if r.type == r.STYLE_RULE and r.selectorText.lower() == 'body':
                                body_color = r.style.getPropertyValue('color')
                                break
                        contrast_issues.append({
                            'selector': rule.selectorText,
                            'color1': body_color if body_color else 'black (assumed)',
                            'color2': colors['background-color'],
                            'ratio': 1.0,  # Indicate potential issue
                            'message': f"Cannot accurately calculate contrast for '{rule.selectorText}' (background '{colors['background-color']}' is a variable)."
                        })

        suggestions = {
            "color_contrast_issues": contrast_issues,
            "accessibility_warnings": {
                "color_reliance_warnings": color_used_without_other_indicators,
                "other_suggestions": "More comprehensive accessibility analysis requires advanced tools or DOM analysis (placeholder)."
            }
        }
        print(f"Generated suggestions (JSON): {suggestions}")

        # Generate textual report for accessibility_report
        report_lines = []
        report_text = ""  # Initialize report_text

        if contrast_issues:
            report_lines.append("Color Contrast Issues:")
            for issue in contrast_issues:
                report_lines.append(f"- In '{issue['selector']}', the contrast ratio between '{issue['color1']}' and '{issue['color2']}' is {issue['ratio']:.2f}. {issue['message']}")

        if color_used_without_other_indicators:
            report_lines.append("\nAccessibility Warnings:")
            report_lines.append("- Color is used without additional visual indicators:")
            for warning in color_used_without_other_indicators:
                report_lines.append(f"  - {warning}")

        if not report_lines:
            report_text = "No significant accessibility issues found during automated analysis."
        else:
            report_text = "\n".join(report_lines)

        theme.ui_suggestions = suggestions
        theme.accessibility_report = report_text
        # Prevent the post_save signal from being triggered again
        theme.save(update_fields=['ui_suggestions', 'accessibility_report'])

        print(f"UI analysis completed for theme '{theme.name}'. Issues found: {len(contrast_issues) + len(color_used_without_other_indicators)}")
        return f"UI analysis completed for theme '{theme.name}'. Issues found: {len(contrast_issues) + len(color_used_without_other_indicators)}"

    except AdminTheme.DoesNotExist:
        print(f"Theme with ID {theme_id} not found.")
        return f"Theme with ID {theme_id} not found."
    except Exception as e:
        import traceback
        print(f"Error during UI analysis for theme_id {theme_id}: {e}")
        traceback.print_exc()
        return f"Error during UI analysis for theme_id {theme_id}: {e}"


@receiver(pre_save, sender=AdminTheme)
def pre_save_admin_theme_css_url(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_css_url = sender.objects.get(pk=instance.pk).css_url
        except sender.DoesNotExist:
            instance._old_css_url = None
    else:
        instance._old_css_url = None


@receiver(post_save, sender=AdminTheme)
def trigger_ui_analysis(sender, instance, created, **kwargs):
    print(f"AdminTheme saved! ID: {instance.id}, Created: {created}, CSS URL: {instance.css_url}")
    analyze_ui_suggestions.delay(instance.id)