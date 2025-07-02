#!/usr/bin/env python3
"""
Enhanced Markdown to HTML converter for GNOME Sushi extension
Supports multiple markdown flavors and proper formatting
"""

import argparse
import sys
import re
from pathlib import Path
from typing import Dict, Any, Optional, Union
import subprocess
import json

# Core markdown libraries
import markdown
from markdown.extensions import codehilite, toc, tables, nl2br, sane_lists
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.toc import TocExtension
from markdown.extensions.tables import TableExtension

# Additional flavor support
try:
    import pymdown.extensions.superfences
    import pymdown.extensions.tasklist
    import pymdown.extensions.emoji
    import pymdown.extensions.magiclink
    import pymdown.extensions.highlight
    import pymdown.extensions.inlinehilite
    import pymdown.extensions.snippets
    import pymdown.extensions.keys
    import pymdown.extensions.smartsymbols
    import pymdown.extensions.betterem
    import pymdown.extensions.caret
    import pymdown.extensions.mark
    import pymdown.extensions.tilde
    PYMDOWN_AVAILABLE = True
except ImportError:
    PYMDOWN_AVAILABLE = False

try:
    import commonmark
    COMMONMARK_AVAILABLE = True
except ImportError:
    COMMONMARK_AVAILABLE = False

try:
    from markdown_it import MarkdownIt
    from markdown_it.extensions.gfm import gfm_plugin
    MARKDOWN_IT_AVAILABLE = True
except ImportError:
    MARKDOWN_IT_AVAILABLE = False


class MarkdownRenderer:
    """Enhanced markdown renderer supporting multiple flavors."""
    
    FLAVORS = {
        'standard': 'Standard Python Markdown',
        'gfm': 'GitHub Flavored Markdown',
        'commonmark': 'CommonMark specification',
        'pymdown': 'PyMdown Extensions (GitHub-like)',
        'pandoc': 'Pandoc (external)',
        'gitlab': 'GitLab Flavored Markdown',
        'extra': 'Markdown Extra',
        'mmd': 'MultiMarkdown (via pandoc)'
    }
    
    def __init__(self, flavor: str = "gfm", theme: str = "auto", 
                 enable_math: bool = True, enable_mermaid: bool = True):
        self.flavor = flavor
        self.theme = theme
        self.enable_math = enable_math
        self.enable_mermaid = enable_mermaid
        
        # Validate flavor
        if flavor not in self.FLAVORS:
            print(f"Warning: Unknown flavor '{flavor}', using 'gfm'", file=sys.stderr)
            self.flavor = 'gfm'
    
    def _get_pygments_style(self) -> str:
        """Get appropriate pygments style for theme."""
        theme = self.theme
        if theme == "auto":
            theme = self._detect_system_theme()
            
        if theme == "dark":
            return "github-dark"
        else:
            return "default"
    
    def _detect_system_theme(self) -> str:
        """Detect system theme (light/dark)."""
        try:
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                theme_name = result.stdout.strip().strip("'\"").lower()
                if "dark" in theme_name:
                    return "dark"
        except:
            pass
        return "light"
    
    def render_commonmark(self, content: str) -> str:
        """Render using CommonMark specification."""
        if not COMMONMARK_AVAILABLE:
            return self.render_standard(content)
        
        parser = commonmark.Parser()
        renderer = commonmark.HtmlRenderer()
        ast = parser.parse(content)
        return renderer.render(ast)
    
    def render_markdown_it(self, content: str) -> str:
        """Render using markdown-it-py with GFM plugin."""
        if not MARKDOWN_IT_AVAILABLE:
            return self.render_standard(content)
        
        md = MarkdownIt().use(gfm_plugin)
        return md.render(content)
    
    def render_pandoc(self, content: str, format_type: str = "gfm") -> str:
        """Render using pandoc (external)."""
        try:
            cmd = [
                'pandoc', 
                '-f', format_type,
                '-t', 'html5',
                '--standalone',
                '--highlight-style', 'github' if self._detect_system_theme() == 'light' else 'github-dark',
                '--mathjax' if self.enable_math else '--no-highlight'
            ]
            
            result = subprocess.run(
                cmd,
                input=content,
                text=True,
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Extract body content from pandoc's full HTML
                html = result.stdout
                if '<body>' in html and '</body>' in html:
                    body_start = html.find('<body>') + 6
                    body_end = html.find('</body>')
                    return html[body_start:body_end].strip()
                return html
            else:
                print(f"Pandoc error: {result.stderr}", file=sys.stderr)
                return self.render_standard(content)
                
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            print(f"Pandoc not available: {e}", file=sys.stderr)
            return self.render_standard(content)
    
    def render_pymdown(self, content: str) -> str:
        """Render using PyMdown Extensions for GitHub-like experience."""
        if not PYMDOWN_AVAILABLE:
            return self.render_gfm(content)
        
        extensions = [
            'pymdown.extensions.superfences',
            'pymdown.extensions.tasklist',
            'pymdown.extensions.emoji',
            'pymdown.extensions.magiclink',
            'pymdown.extensions.highlight',
            'pymdown.extensions.inlinehilite',
            'pymdown.extensions.keys',
            'pymdown.extensions.smartsymbols',
            'pymdown.extensions.betterem',
            'pymdown.extensions.caret',
            'pymdown.extensions.mark',
            'pymdown.extensions.tilde',
            'markdown.extensions.tables',
            'markdown.extensions.footnotes',
            'markdown.extensions.attr_list',
            'markdown.extensions.def_list',
            'markdown.extensions.abbr',
            'markdown.extensions.toc'
        ]
        
        extension_configs = {
            'pymdown.extensions.highlight': {
                'css_class': 'highlight',
                'use_pygments': True,
                'pygments_style': self._get_pygments_style()
            },
            'pymdown.extensions.superfences': {
                'custom_fences': [
                    {
                        'name': 'mermaid',
                        'class': 'mermaid',
                        'format': lambda src, language, css_class, options, md, **kwargs: f'<div class="mermaid">{src}</div>'
                    }
                ]
            },
            'pymdown.extensions.tasklist': {
                'custom_checkbox': True
            },
            'markdown.extensions.toc': {
                'anchorlink': True
            }
        }
        
        md = markdown.Markdown(
            extensions=extensions,
            extension_configs=extension_configs
        )
        
        return md.convert(content)
    
    def render_gfm(self, content: str) -> str:
        """Render GitHub Flavored Markdown."""
        extensions = [
            TableExtension(),
            CodeHiliteExtension(
                css_class="highlight",
                use_pygments=True,
                noclasses=False,
                pygments_style=self._get_pygments_style()
            ),
            TocExtension(anchorlink=True),
            'markdown.extensions.fenced_code',
            'markdown.extensions.footnotes',
            'markdown.extensions.attr_list',
            'markdown.extensions.def_list',
            'markdown.extensions.abbr',
            'markdown.extensions.nl2br',
            'markdown.extensions.sane_lists'
        ]
        
        # Add task list support manually
        if PYMDOWN_AVAILABLE:
            extensions.append('pymdown.extensions.tasklist')
        
        md = markdown.Markdown(extensions=extensions)
        html = md.convert(content)
        
        # Manual task list conversion if pymdown not available
        if not PYMDOWN_AVAILABLE:
            html = self._convert_task_lists(html)
        
        # Convert @mentions and #issues (basic GitHub-like)
        html = self._convert_github_references(html)
        
        return html
    
    def render_gitlab(self, content: str) -> str:
        """Render GitLab Flavored Markdown."""
        # GitLab is similar to GFM with some additions
        html = self.render_gfm(content)
        
        # Add GitLab-specific features
        html = self._convert_gitlab_references(html)
        
        return html
    
    def render_extra(self, content: str) -> str:
        """Render Markdown Extra."""
        extensions = [
            'markdown.extensions.extra',  # This includes tables, footnotes, etc.
            CodeHiliteExtension(
                css_class="highlight",
                use_pygments=True,
                noclasses=False,
                pygments_style=self._get_pygments_style()
            ),
            TocExtension(anchorlink=True)
        ]
        
        md = markdown.Markdown(extensions=extensions)
        return md.convert(content)
    
    def render_standard(self, content: str) -> str:
        """Render using standard Python Markdown."""
        extensions = [
            TableExtension(),
            CodeHiliteExtension(
                css_class="highlight",
                use_pygments=True,
                noclasses=False,
                pygments_style=self._get_pygments_style()
            ),
            TocExtension(anchorlink=True),
            'markdown.extensions.fenced_code',
            'markdown.extensions.footnotes'
        ]
        
        md = markdown.Markdown(extensions=extensions)
        return md.convert(content)
    
    def _convert_task_lists(self, html: str) -> str:
        """Convert task list syntax manually."""
        # Convert [ ] and [x] to checkboxes
        html = re.sub(r'<li>\[ \]', '<li><input type="checkbox" class="task-list-item-checkbox" disabled>', html)
        html = re.sub(r'<li>\[x\]', '<li><input type="checkbox" class="task-list-item-checkbox" checked disabled>', html)
        html = re.sub(r'<li>\[X\]', '<li><input type="checkbox" class="task-list-item-checkbox" checked disabled>', html)
        return html
    
    def _convert_github_references(self, html: str) -> str:
        """Convert GitHub-style references."""
        # Convert @username mentions
        html = re.sub(r'@(\w+)', r'<a href="https://github.com/\1" class="mention">@\1</a>', html)
        # Convert #123 issue references  
        html = re.sub(r'#(\d+)', r'<a href="#issue-\1" class="issue-link">#\1</a>', html)
        return html
    
    def _convert_gitlab_references(self, html: str) -> str:
        """Convert GitLab-style references."""
        # Similar to GitHub but with GitLab specifics
        html = re.sub(r'@(\w+)', r'<a href="#user-\1" class="mention">@\1</a>', html)
        html = re.sub(r'#(\d+)', r'<a href="#issue-\1" class="issue-link">#\1</a>', html)
        html = re.sub(r'!(\d+)', r'<a href="#mr-\1" class="mr-link">!\1</a>', html)  # Merge requests
        return html
    
    def get_css_styles(self) -> str:
        """Generate CSS styles for the rendered HTML."""
        theme = self.theme
        if theme == "auto":
            theme = self._detect_system_theme()
        
        # Enhanced CSS with better styling
        base_css = """
        <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
            font-size: 16px;
            word-wrap: break-word;
        }
        
        h1, h2, h3, h4, h5, h6 {
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
        }
        
        h1 { 
            font-size: 2em; 
            border-bottom: 1px solid #eaecef; 
            padding-bottom: 10px; 
            margin-top: 0;
        }
        h2 { 
            font-size: 1.5em; 
            border-bottom: 1px solid #eaecef; 
            padding-bottom: 8px; 
        }
        h3 { font-size: 1.25em; }
        h4 { font-size: 1em; }
        h5 { font-size: 0.875em; }
        h6 { font-size: 0.85em; color: #6a737d; }
        
        p { margin-bottom: 16px; }
        
        blockquote {
            padding: 0 1em;
            margin: 0 0 16px 0;
            border-left: 0.25em solid #dfe2e5;
            background-color: #f6f8fa;
            color: #6a737d;
        }
        
        ul, ol { 
            margin-bottom: 16px; 
            padding-left: 2em; 
        }
        li { 
            margin-bottom: 4px; 
        }
        
        /* Task lists */
        .task-list-item {
            list-style-type: none;
        }
        .task-list-item input[type="checkbox"] {
            margin: 0 6px 2px -20px;
            vertical-align: middle;
        }
        
        code {
            padding: 2px 4px;
            font-size: 85%;
            background-color: rgba(27,31,35,0.05);
            border-radius: 6px;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
        }
        
        pre {
            padding: 16px;
            overflow: auto;
            line-height: 1.45;
            background-color: #f6f8fa;
            border-radius: 6px;
            margin-bottom: 16px;
            font-size: 85%;
        }
        
        pre code {
            background-color: transparent;
            padding: 0;
            font-size: 100%;
            border-radius: 0;
        }
        
        table {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 16px;
            display: block;
            overflow: auto;
        }
        
        th, td {
            padding: 6px 13px;
            border: 1px solid #dfe2e5;
            text-align: left;
        }
        
        th {
            font-weight: 600;
            background-color: #f6f8fa;
        }
        
        tr:nth-child(2n) {
            background-color: #f6f8fa;
        }
        
        img {
            max-width: 100%;
            height: auto;
            margin: 10px 0;
            border-radius: 6px;
        }
        
        a {
            color: #0366d6;
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
        
        .mention {
            font-weight: 600;
            color: #0366d6;
        }
        
        .issue-link, .mr-link {
            font-weight: 600;
        }
        
        hr {
            height: 0.25em;
            margin: 24px 0;
            background-color: #e1e4e8;
            border: 0;
        }
        
        .highlight {
            margin-bottom: 16px;
        }
        
        .toc {
            background-color: #f6f8fa;
            border: 1px solid #d0d7de;
            border-radius: 6px;
            padding: 16px;
            margin-bottom: 16px;
        }
        
        .toc ul {
            list-style: none;
            margin: 0;
            padding-left: 16px;
        }
        
        .toc > ul {
            padding-left: 0;
        }
        
        /* Mermaid diagrams */
        .mermaid {
            text-align: center;
            margin: 16px 0;
        }
        
        /* Keyboard keys */
        .keys kbd {
            background-color: #fafbfc;
            border: 1px solid #c6cbd1;
            border-bottom-color: #959da5;
            border-radius: 3px;
            box-shadow: inset 0 -1px 0 #959da5;
            color: #444d56;
            display: inline-block;
            font-size: 11px;
            line-height: 10px;
            padding: 3px 5px;
            vertical-align: middle;
        }
        """
        
        # Dark theme modifications
        if theme == "dark":
            dark_css = """
            body { 
                background-color: #0d1117; 
                color: #e6edf3; 
            }
            h1, h2 { 
                border-bottom-color: #30363d; 
            }
            h6 { 
                color: #8b949e; 
            }
            blockquote { 
                border-left-color: #656c76; 
                background-color: #161b22;
                color: #8b949e;
            }
            code { 
                background-color: rgba(240,246,252,0.15); 
            }
            pre { 
                background-color: #161b22; 
            }
            th, td { 
                border-color: #30363d; 
            }
            th { 
                background-color: #21262d; 
            }
            tr:nth-child(2n) { 
                background-color: #161b22; 
            }
            a { 
                color: #58a6ff; 
            }
            .mention {
                color: #58a6ff;
            }
            hr { 
                background-color: #30363d; 
            }
            .toc { 
                background-color: #161b22; 
                border-color: #30363d; 
            }
            .keys kbd {
                background-color: #21262d;
                border-color: #30363d;
                border-bottom-color: #6e7681;
                box-shadow: inset 0 -1px 0 #6e7681;
                color: #e6edf3;
            }
            """
            base_css += dark_css
        
        base_css += "</style>"
        return base_css
    
    def render_content(self, content: str) -> str:
        """Render markdown content using the specified flavor."""
        try:
            # Choose renderer based on flavor
            if self.flavor == 'commonmark':
                html_body = self.render_commonmark(content)
            elif self.flavor == 'gfm':
                html_body = self.render_gfm(content)
            elif self.flavor == 'pymdown':
                html_body = self.render_pymdown(content)
            elif self.flavor == 'pandoc':
                html_body = self.render_pandoc(content, 'gfm')
            elif self.flavor == 'mmd':
                html_body = self.render_pandoc(content, 'markdown_mmd')
            elif self.flavor == 'gitlab':
                html_body = self.render_gitlab(content)
            elif self.flavor == 'extra':
                html_body = self.render_extra(content)
            else:  # standard
                html_body = self.render_standard(content)
            
            # Get CSS styles
            css = self.get_css_styles()
            
            # Add MathJax if math is enabled and detected
            math_js = ""
            if self.enable_math and ("$" in content or "\\(" in content or "\\[" in content):
                math_js = """
                <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
                <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
                <script>
                  MathJax = {
                    tex: {
                      inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
                      displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
                    }
                  };
                </script>
                """
            
            # Add Mermaid if diagrams are enabled and detected
            mermaid_js = ""
            if self.enable_mermaid and ("```mermaid" in content or '<div class="mermaid">' in html_body):
                mermaid_js = """
                <script src="https://unpkg.com/mermaid@10/dist/mermaid.min.js"></script>
                <script>mermaid.initialize({startOnLoad:true, theme: 'neutral'});</script>
                """
            
            # Construct full HTML
            html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Markdown Preview</title>
    {css}
    {math_js}
    {mermaid_js}
</head>
<body>
    {html_body}
</body>
</html>"""
            
            return html
            
        except Exception as e:
            print(f"✗ Render error: {e}", file=sys.stderr)
            return f"<html><body><h1>Error</h1><p>Failed to render markdown: {str(e)}</p></body></html>"
    
    def render_file(self, file_path: Path) -> str:
        """Render a markdown file to HTML."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"✓ Read file: {len(content)} chars", file=sys.stderr)
            return self.render_content(content)
            
        except Exception as e:
            print(f"✗ File error: {e}", file=sys.stderr)
            return f"<html><body><h1>Error</h1><p>Failed to read file: {str(e)}</p></body></html>"


def main():
    """Command line interface for the markdown converter."""
    parser = argparse.ArgumentParser(description="Convert Markdown to HTML with multiple flavor support")
    parser.add_argument("file", help="Markdown file to convert")
    parser.add_argument("--flavor", "-f", 
                       choices=list(MarkdownRenderer.FLAVORS.keys()), 
                       default="gfm",
                       help="Markdown flavor to use")
    parser.add_argument("--theme", choices=["light", "dark", "auto"], default="auto",
                       help="Theme for rendering")
    parser.add_argument("--no-math", action="store_true", help="Disable math rendering")
    parser.add_argument("--no-mermaid", action="store_true", help="Disable mermaid diagrams")
    parser.add_argument("--output", "-o", help="Output HTML file (default: stdout)")
    parser.add_argument("--list-flavors", action="store_true", 
                       help="List available markdown flavors")
    
    args = parser.parse_args()
    
    if args.list_flavors:
        print("Available markdown flavors:")
        for flavor, description in MarkdownRenderer.FLAVORS.items():
            print(f"  {flavor:12} - {description}")
        return
    
    # Create renderer
    renderer = MarkdownRenderer(
        flavor=args.flavor,
        theme=args.theme,
        enable_math=not args.no_math,
        enable_mermaid=not args.no_mermaid
    )
    
    # Render file
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File '{file_path}' not found", file=sys.stderr)
        sys.exit(1)
    
    print(f"✓ Using {args.flavor} flavor", file=sys.stderr)
    html = renderer.render_file(file_path)
    
    # Output result
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✓ HTML written to {args.output}", file=sys.stderr)
    else:
        print(html)


if __name__ == "__main__":
    main()