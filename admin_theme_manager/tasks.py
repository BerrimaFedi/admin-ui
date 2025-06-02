# admin_theme_manager/tasks.py
import os
import subprocess
from celery import shared_task
from django.conf import settings
from admin_theme_manager.models import AdminTheme
from .utils import css_color_to_srgb, calculate_contrast_ratio
import cssutils
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import models


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


# @shared_task
# def analyze_ui_suggestions(theme_id):
#     try:
#         theme = AdminTheme.objects.get(pk=theme_id)
#         css_file_path = os.path.join(settings.BASE_DIR, 'admin_theme_manager', 'static', 'theming', theme.css_url)

#         if not os.path.exists(css_file_path):
#             return f"CSS file not found for theme '{theme.name}' at '{css_file_path}'."

#         with open(css_file_path, 'r', encoding='utf-8') as f:
#             css = f.read()

#         stylesheet = cssutils.parseString(css)
#         contrast_issues = []
#         color_used_without_other_indicators = []
#         processed_pairs = set()

#         for rule in stylesheet.cssRules:
#             if rule.type == rule.STYLE_RULE:
#                 declarations = rule.style.getProperties()
#                 colors = {}
#                 text_decoration = False
#                 font_weight = False
#                 for prop in declarations:
#                     if prop.name in ['color', 'background-color']:
#                         colors[prop.name] = prop.value
#                     if prop.name == 'text-decoration':
#                         text_decoration = True
#                     if prop.name == 'font-weight' and prop.value in ['bold', '700', '800', '900']:
#                         font_weight = True

#                 if 'color' in colors and not (text_decoration or font_weight):
#                     color_used_without_other_indicators.append(f"Rule '{rule.selectorText}' uses color '{colors['color']}' without text decoration or bold font-weight.")

#                 if 'color' in colors and 'background-color' in colors:
#                     color1 = colors['color']
#                     color2 = colors['background-color']
#                     pair = tuple(sorted((color1, color2)))
#                     if pair not in processed_pairs:
#                         ratio = calculate_contrast_ratio(color1, color2)
#                         if ratio < 4.5:
#                             contrast_issues.append({
#                                 'selector': rule.selectorText,
#                                 'color1': color1,
#                                 'color2': color2,
#                                 'ratio': round(ratio, 2),
#                                 'message': f"Low contrast ({ratio:.2f}) between '{color1}' and '{color2}'."
#                             })
#                         processed_pairs.add(pair)
#                 elif 'color' in colors and 'background-color' not in colors:
#                     body_bg = None
#                     for r in stylesheet.cssRules:
#                         if r.type == r.STYLE_RULE and r.selectorText.lower() == 'body':
#                             body_bg = r.style.getPropertyValue('background-color')
#                             break
#                     if body_bg:
#                         ratio = calculate_contrast_ratio(colors['color'], body_bg)
#                         if ratio < 4.5:
#                             contrast_issues.append({
#                                 'selector': rule.selectorText,
#                                 'color1': colors['color'],
#                                 'color2': body_bg,
#                                 'ratio': round(ratio, 2),
#                                 'message': f"Low contrast ({ratio:.2f}) between text color '{colors['color']}' and assumed body background '{body_bg}'."
#                             })
#                 elif 'background-color' in colors and 'color' not in colors:
#                     body_color = None
#                     for r in stylesheet.cssRules:
#                         if r.type == r.STYLE_RULE and r.selectorText.lower() == 'body':
#                             body_color = r.style.getPropertyValue('color')
#                             break
#                     if body_color:
#                         ratio = calculate_contrast_ratio(body_color, colors['background-color'])
#                         if ratio < 4.5:
#                             contrast_issues.append({
#                                 'selector': rule.selectorText,
#                                 'color1': body_color,
#                                 'color2': colors['background-color'],
#                                 'ratio': round(ratio, 2),
#                                 'message': f"Low contrast ({ratio:.2f}) between assumed body text color '{body_color}' and background '{colors['background-color']}'."
#                             })

#         suggestions = {
#             "color_contrast_issues": contrast_issues,
#             "accessibility_warnings": {
#                 "color_reliance_warnings": color_used_without_other_indicators,
#                 "other_suggestions": "More comprehensive accessibility analysis requires advanced tools or DOM analysis (placeholder)."
#             }
#         }

#         theme.ui_suggestions = suggestions
#         theme.save()
#         return f"UI analysis completed for theme '{theme.name}'. Issues found: {len(contrast_issues)}"
@shared_task
def analyze_ui_suggestions(theme_id):
    print(f"Analyzing theme ID: {theme_id}")
    try:
        theme = AdminTheme.objects.get(pk=theme_id)
        print(f"Found theme: {theme.name}")
        # css_file_path = os.path.join(settings.BASE_DIR, 'admin_theme_manager', 'static', 'theming', theme.css_url)
        # with open(css_file_path, 'r', encoding='utf-8') as f:
        #     css = f.read()
        # stylesheet = cssutils.parseString(css)
        # ... rest of your analysis code commented out ...
        suggestions = {"message": "Analysis temporarily disabled for debugging"}
        theme.ui_suggestions = suggestions
        theme.save()
        return f"UI analysis (simplified) completed for theme '{theme.name}'."
    except AdminTheme.DoesNotExist:
        return f"Theme with ID {theme_id} not found."
    except Exception as e:
        import traceback
        print(f"Error during UI analysis for theme_id {theme_id}: {e}")
        traceback.print_exc()
        return f"Error during UI analysis for theme_id {theme_id}: {e}"
    except AdminTheme.DoesNotExist:
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
    # analyze_ui_suggestions.delay(instance.id) # Comment out the Celery task for now