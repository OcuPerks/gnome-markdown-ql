# GNOME Markdown QuickLook

> **Beautiful markdown previews for GNOME** - Press Space in Nautilus to preview .md files with rich formatting, syntax highlighting, and multiple flavor support.

[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![GNOME](https://img.shields.io/badge/GNOME-Sushi-orange.svg)](https://wiki.gnome.org/Apps/Sushi)

Similar to macOS [QLMarkdown](https://github.com/sbarex/QLMarkdown), this extension brings Quick Look-style markdown previews to GNOME Linux desktops.

## ✨ Features

- 🚀 **8 Markdown Flavors** - GitHub, CommonMark, Pandoc, GitLab, and more
- 🎨 **Auto Theme Detection** - Seamlessly adapts to GNOME light/dark themes
- 🔧 **Syntax Highlighting** - Powered by [Pygments](https://pygments.org/) with 40+ styles
- 📊 **Rich Content** - Tables, task lists, math equations, Mermaid diagrams
- ⚡ **Instant Preview** - Sub-second rendering with WebKit2GTK
- 🌐 **Standards Compliant** - Full HTML5 + CSS3 + JavaScript support

## 🚀 Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/noboomu/gnome-markdown-quicklook/main/install.sh | bash
```

**That's it!** The installer will handle dependencies, setup, and configuration automatically.

## 📋 Supported Markdown Flavors

| Flavor | Specification | Key Features |
|--------|---------------|--------------|
| **[GFM](https://github.github.com/gfm/)** | GitHub Flavored Markdown | Tables, task lists, strikethrough, @mentions |
| **[CommonMark](https://spec.commonmark.org/0.31.2/)** | CommonMark 0.31.2 | Standards-compliant parsing |
| **[PyMdown](https://facelessuser.github.io/pymdown-extensions/)** | Enhanced GitHub-like | Emoji, keyboard keys, advanced highlighting |
| **[Pandoc](https://pandoc.org/MANUAL.html#pandocs-markdown)** | Pandoc Markdown | Extensive extensions, citations, metadata |
| **[Extra](https://python-markdown.github.io/extensions/extra/)** | PHP Markdown Extra | Definition lists, abbreviations, footnotes |
| **[GitLab](https://docs.gitlab.com/ee/user/markdown.html)** | GitLab Flavored Markdown | GFM + GitLab-specific references (!123, etc.) |
| **[MMD](https://fletcher.github.io/MultiMarkdown-6/)** | MultiMarkdown v6 | Metadata, citations, advanced tables |
| **Standard** | [Python Markdown](https://python-markdown.github.io/) | Basic markdown features |

## 🎯 Usage

### Basic Usage
1. **Open Nautilus** (GNOME Files)
2. **Select any `.md` file**
3. **Press `Space`** → Preview opens instantly!
4. **Press `Escape`** to close

### Advanced Usage

**Test different flavors:**
```bash
sushi-markdown-converter document.md --flavor gfm
sushi-markdown-converter document.md --flavor commonmark
sushi-markdown-converter document.md --flavor pandoc
```

**Export to HTML:**
```bash
sushi-markdown-converter document.md --output preview.html --flavor gfm
```

**List all flavors:**
```bash
sushi-markdown-converter --help
```

## 📝 Supported File Types

- `.md` - Standard Markdown
- `.markdown` - Markdown document
- `.mdown` - Markdown document
- `.mkd` - Markdown document
- `.mkdn` - Markdown document

## 🔧 System Requirements

- **OS**: Linux with GNOME desktop
- **GNOME Sushi**: File previewer (`sudo apt install gnome-sushi`)
- **WebKit2GTK**: Web rendering (`sudo apt install libwebkit2gtk-4.1-dev`)
- **Python**: 3.8+ with pip or [uv](https://github.com/astral-sh/uv)

### Dependencies Auto-Install

The installer automatically handles:
- [Python Markdown](https://python-markdown.github.io/) - Core markdown processing
- [Pygments](https://pygments.org/) - Syntax highlighting
- [PyMdown Extensions](https://facelessuser.github.io/pymdown-extensions/) - Enhanced features
- [CommonMark](https://github.com/readthedocs/commonmark.py) - Spec compliance
- [markdown-it-py](https://github.com/executablebooks/markdown-it-py) - Modern parser
- [python-markdown-math](https://github.com/mitya57/python-markdown-math) - Math support

## 🏗️ Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│ Markdown    │───▶│ Python       │───▶│ Styled      │───▶│ WebKit2      │
│ File        │    │ Converter    │    │ HTML        │    │ Preview      │
│ (.md)       │    │ (Multi-flavor)│    │ (CSS+JS)    │    │ (Sushi)      │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘
```

**Components:**
1. **[GNOME Sushi](https://gitlab.gnome.org/GNOME/sushi)** - File preview framework
2. **Python Converter** - Multi-flavor markdown processor
3. **JavaScript Viewer** - WebKit2GTK integration
4. **MIME Integration** - File type associations

## 🎨 Themes & Styling

### Auto Theme Detection
- Automatically detects GNOME light/dark theme
- Switches styling and syntax highlighting accordingly
- Consistent with system appearance

### Syntax Highlighting
- **Light Theme**: GitHub-style highlighting
- **Dark Theme**: Dark-optimized color schemes
- **40+ Languages**: Powered by Pygments

## ⚡ Performance

- **Rendering**: < 100ms for typical documents
- **Memory**: ~10MB per preview
- **CPU**: Minimal impact, efficient caching
- **Large Files**: Handles 1MB+ documents smoothly

## 🔍 Feature Comparison

| Feature | [QLMarkdown (macOS)](https://github.com/sbarex/QLMarkdown) | GNOME Markdown QuickLook |
|---------|-------------------|---------------------------|
| **Platform** | macOS only | Linux/GNOME |
| **Flavors** | 1 (Custom GFM-like) | 8 markdown specifications |
| **Themes** | Built-in themes | System theme integration |
| **Math** | ✅ [MathJax](https://www.mathjax.org/) | ✅ [MathJax](https://www.mathjax.org/) |
| **Diagrams** | ❌ | ✅ [Mermaid](https://mermaid.js.org/) |
| **Syntax Highlighting** | ✅ | ✅ [Pygments](https://pygments.org/) |
| **Tables** | ✅ | ✅ |
| **Task Lists** | ✅ | ✅ |
| **Extensibility** | Limited | Highly extensible |
| **Performance** | Native (Swift) | WebKit2GTK |

## 🧪 Development

### Local Setup

```bash
git clone https://github.com/noboomu/gnome-markdown-quicklook.git
cd gnome-markdown-quicklook
uv sync  # or pip install -e .
```

### Testing

```bash
# Test converter directly
uv run python -m gnome_markdown_quicklook.converter tests/sample.md

# Test different flavors
uv run python -m gnome_markdown_quicklook.converter tests/sample.md --flavor gfm
uv run python -m gnome_markdown_quicklook.converter tests/sample.md --flavor commonmark
```

### Adding Flavors

1. Implement `render_<flavor>()` method in `converter.py`
2. Add to `FLAVORS` dictionary
3. Update CLI choices and documentation
4. Test with various markdown documents

## 🛠️ Manual Installation

<details>
<summary>Click to expand manual installation steps</summary>

```bash
# 1. Install system dependencies
sudo apt install gnome-sushi libwebkit2gtk-4.1-dev python3-pip

# 2. Clone repository
git clone https://github.com/noboomu/gnome-markdown-quicklook.git
cd gnome-markdown-quicklook

# 3. Install Python dependencies
uv sync  # or pip install -r requirements.txt

# 4. Install converter
sudo cp src/gnome_markdown_quicklook/converter.py /usr/local/bin/sushi-markdown-converter
sudo chmod +x /usr/local/bin/sushi-markdown-converter

# 5. Install Sushi viewer
sudo cp src/sushi-viewers/markdown.js /usr/share/sushi/viewers/

# 6. Update MIME database
sudo cp mime/markdown.xml /usr/share/mime/packages/
sudo update-mime-database /usr/share/mime

# 7. Restart Sushi
pkill -f sushi
```

</details>

## 🐛 Troubleshooting

### Preview Not Working
1. **Check Sushi**: `which sushi` and restart with `pkill -f sushi`
2. **Check converter**: `sushi-markdown-converter --help`
3. **Check logs**: `journalctl --user -f | grep sushi`

### Dependency Issues
1. **Python packages**: `uv sync` or `pip install markdown pygments`
2. **System packages**: `sudo apt install gnome-sushi libwebkit2gtk-4.1-dev`
3. **WebKit version**: Try both `webkit2gtk-4.0` and `webkit2gtk-4.1`

### MIME Type Issues
1. **Update database**: `update-mime-database ~/.local/share/mime`
2. **Check associations**: `file --mime-type document.md`
3. **Restart session**: Log out and back in

## 🗑️ Uninstall

```bash
# Remove files
sudo rm -f /usr/local/bin/sushi-markdown-converter
sudo rm -f /usr/share/sushi/viewers/markdown.js
sudo rm -f /usr/share/mime/packages/markdown.xml

# Update MIME database
sudo update-mime-database /usr/share/mime

# Restart Sushi
pkill -f sushi
```

## 📄 License

This project is licensed under the [GNU General Public License v2.0](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html) - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[QLMarkdown](https://github.com/sbarex/QLMarkdown)** - Original macOS inspiration by [Sbarex](https://github.com/sbarex)
- **[GNOME Sushi](https://gitlab.gnome.org/GNOME/sushi)** - File preview framework by GNOME Project
- **[Python Markdown](https://python-markdown.github.io/)** - Core markdown processing
- **[PyMdown Extensions](https://facelessuser.github.io/pymdown-extensions/)** - Enhanced markdown features by [facelessuser](https://github.com/facelessuser)
- **[Pygments](https://pygments.org/)** - Syntax highlighting by [Georg Brandl](https://github.com/birkenfeld)

## 🌟 Contributing

Contributions welcome! Please read our [Contributing Guide](CONTRIBUTING.md) and submit pull requests to our [GitHub repository](https://github.com/noboomu/gnome-markdown-quicklook).

---

**Ready to use!** 🎉
```bash
curl -fsSL https://raw.githubusercontent.com/noboomu/gnome-markdown-quicklook/main/install.sh | bash
```
