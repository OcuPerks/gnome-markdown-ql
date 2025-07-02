/*
 * Enhanced Markdown viewer for GNOME Sushi with print support
 * Supports multiple markdown flavors and proper formatting
 */

const {Gio, GLib, GObject, Gdk} = imports.gi;

var WebKit2;
try {
    imports.gi.versions.WebKit2 = '4.1';
    WebKit2 = imports.gi.WebKit2;
} catch(e) {
    log('WebKit2 4.1 not available: ' + e.message);
}

function _isAvailable() {
    return WebKit2 !== undefined;
}

const Renderer = imports.ui.renderer;

// Path to our markdown converter script
const CONVERTER_PATH = '/usr/local/bin/sushi-markdown-converter';
const USER_CONVERTER_PATH = GLib.get_home_dir() + '/.local/bin/sushi-markdown-converter';

var Klass = _isAvailable() ? GObject.registerClass({
    Implements: [Renderer.Renderer],
    Properties: {
        fullscreen: GObject.ParamSpec.boolean('fullscreen', '', '',
                                              GObject.ParamFlags.READABLE,
                                              false),
        ready: GObject.ParamSpec.boolean('ready', '', '',
                                         GObject.ParamFlags.READABLE,
                                         false)
    },
}, class MarkdownRenderer extends WebKit2.WebView {
    get ready() {
        return !!this._ready;
    }

    get fullscreen() {
        return !!this._fullscreen;
    }

    _init(file) {
        super._init();
        
        this._file = file;
        this._ready = false;

        // Enable custom context menu with print option
        this.connect('context-menu', (view, contextMenu, event, hitTestResult) => {
            this._setupContextMenu(contextMenu);
            return false; // Allow context menu to show
        });

        // Add keyboard shortcuts
        this.connect('key-press-event', (widget, event) => {
            let keyval = event.get_keyval()[1];
            let state = event.get_state()[1];
            
            // Ctrl+P for print
            if ((state & Gdk.ModifierType.CONTROL_MASK) && keyval === Gdk.KEY_p) {
                this._printDocument();
                return true;
            }
            
            return false;
        });

        // Configure WebKit settings
        let settings = this.get_settings();
        settings.enable_javascript = true;
        settings.enable_webgl = false;
        settings.enable_plugins = false;
        settings.enable_java = false;
        settings.auto_load_images = true;
        settings.enable_smooth_scrolling = true;
        settings.enable_media_stream = false;
        settings.enable_html5_database = false;
        settings.enable_html5_local_storage = false;
        
        // Set up error handling
        this.connect('load-failed', (view, loadEvent, uri, error) => {
            log('Markdown load failed: ' + error.message);
            this._showError('Failed to load markdown content: ' + error.message);
        });

        this.connect('load-changed', (view, loadEvent) => {
            if (loadEvent === WebKit2.LoadEvent.FINISHED) {
                this._ready = true;
                this.notify('ready');
                this._injectPrintStyles();
            }
        });

        // Start conversion process
        this._convertAndLoad();
    }

    _setupContextMenu(contextMenu) {
        // Clear existing menu items
        contextMenu.remove_all();
        
        // Add print option
        let printItem = new WebKit2.ContextMenuItem.from_stock_action(WebKit2.ContextMenuAction.CUSTOM);
        printItem.set_stock_action(WebKit2.ContextMenuAction.PRINT);
        contextMenu.append(printItem);
        
        // Add separator
        contextMenu.append(new WebKit2.ContextMenuItem.separator());
        
        // Add copy option for selected text
        let copyItem = new WebKit2.ContextMenuItem.from_stock_action(WebKit2.ContextMenuAction.COPY);
        contextMenu.append(copyItem);
        
        // Add select all
        let selectAllItem = new WebKit2.ContextMenuItem.from_stock_action(WebKit2.ContextMenuAction.SELECT_ALL);
        contextMenu.append(selectAllItem);
    }

    _printDocument() {
        try {
            let printOperation = WebKit2.PrintOperation.new(this);
            printOperation.run_dialog(null);
        } catch (e) {
            log('Print operation failed: ' + e.message);
            // Fallback: try to trigger browser print
            this.run_javascript('window.print();', null, null);
        }
    }

    _injectPrintStyles() {
        // Inject print-specific CSS
        let printCSS = `
        @media print {
            body {
                max-width: none !important;
                margin: 0 !important;
                padding: 20mm !important;
                font-size: 12pt !important;
                line-height: 1.5 !important;
                color: black !important;
                background: white !important;
            }
            
            h1, h2, h3, h4, h5, h6 {
                page-break-after: avoid;
                color: black !important;
            }
            
            pre, blockquote {
                page-break-inside: avoid;
                border: 1px solid #ccc !important;
                background: #f9f9f9 !important;
            }
            
            table {
                page-break-inside: avoid;
            }
            
            img {
                max-width: 100% !important;
                page-break-inside: avoid;
            }
            
            .highlight {
                background: #f5f5f5 !important;
                border: 1px solid #ddd !important;
            }
            
            a {
                color: black !important;
                text-decoration: none !important;
            }
            
            a[href]:after {
                content: " (" attr(href) ")";
                font-size: 0.8em;
                color: #666;
            }
        }`;
        
        this.run_javascript(`
            var style = document.createElement('style');
            style.textContent = \`${printCSS}\`;
            document.head.appendChild(style);
        `, null, null);
    }

    _getConverterPath() {
        // Check user path first, then system path
        let userFile = Gio.File.new_for_path(USER_CONVERTER_PATH);
        if (userFile.query_exists(null)) {
            return USER_CONVERTER_PATH;
        }
        
        let systemFile = Gio.File.new_for_path(CONVERTER_PATH);
        if (systemFile.query_exists(null)) {
            return CONVERTER_PATH;
        }
        
        return null;
    }

    _detectMarkdownFlavor(filename) {
        // Try to detect the best flavor based on filename and content
        let basename = filename.toLowerCase();
        
        if (basename.includes('readme') || basename.includes('github')) {
            return 'gfm';
        } else if (basename.includes('gitlab')) {
            return 'gitlab';
        } else if (basename.endsWith('.mmd')) {
            return 'mmd';
        } else {
            return 'gfm'; // Default to GFM as it's most common
        }
    }

    _convertAndLoad() {
        try {
            let converterPath = this._getConverterPath();
            let theme = this._getSystemTheme();
            let flavor = this._detectMarkdownFlavor(this._file.get_basename());
            
            if (converterPath) {
                this._convertWithPython(converterPath, theme, flavor);
            } else {
                this._convertWithPandoc(theme);
            }
        } catch (e) {
            log('Markdown conversion error: ' + e.message);
            this._showError('Failed to convert markdown: ' + e.message);
        }
    }

    _convertWithPython(converterPath, theme, flavor) {
        // Use our enhanced Python converter
        let subprocess = new Gio.Subprocess({
            argv: [converterPath, this._file.get_path(), '--theme', theme, '--flavor', flavor],
            flags: Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_PIPE
        });
        
        subprocess.init(null);
        
        subprocess.communicate_utf8_async(null, null, (proc, result) => {
            try {
                let [, stdout, stderr] = proc.communicate_utf8_finish(result);
                
                if (proc.get_successful()) {
                    this._loadHTML(stdout);
                } else {
                    log('Python converter error: ' + stderr);
                    this._convertWithPandoc(theme);
                }
            } catch (e) {
                log('Python converter subprocess error: ' + e.message);
                this._convertWithPandoc(theme);
            }
        });
    }

    _convertWithPandoc(theme) {
        // Fallback to pandoc
        let highlightStyle = theme === 'dark' ? 'zenburn' : 'pygments';
        let subprocess = new Gio.Subprocess({
            argv: [
                'pandoc', 
                this._file.get_path(), 
                '-f', 'gfm',
                '-t', 'html5', 
                '--standalone', 
                '--highlight-style=' + highlightStyle,
                '--mathjax'
            ],
            flags: Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_PIPE
        });
        
        try {
            subprocess.init(null);
            
            subprocess.communicate_utf8_async(null, null, (proc, result) => {
                try {
                    let [, stdout, stderr] = proc.communicate_utf8_finish(result);
                    
                    if (proc.get_successful()) {
                        let styledHTML = this._addCustomStyling(stdout, theme);
                        this._loadHTML(styledHTML);
                    } else {
                        log('Pandoc error: ' + stderr);
                        this._showBasicMarkdown();
                    }
                } catch (e) {
                    log('Pandoc subprocess error: ' + e.message);
                    this._showBasicMarkdown();
                }
            });
        } catch (e) {
            log('Failed to start pandoc: ' + e.message);
            this._showBasicMarkdown();
        }
    }

    _showBasicMarkdown() {
        // Last resort: show formatted raw markdown
        try {
            let [, contents] = this._file.load_contents(null);
            let markdownText = new TextDecoder().decode(contents);
            
            let html = this._createBasicHTML(markdownText, this._getSystemTheme());
            this._loadHTML(html);
        } catch (e) {
            this._showError('Failed to load markdown file: ' + e.message);
        }
    }

    _createBasicHTML(markdownText, theme) {
        let css = this._getBasicCSS(theme);
        let escapedText = GLib.markup_escape_text(markdownText, -1);
        
        return `<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Markdown Preview</title>
    ${css}
</head>
<body>
    <div class="markdown-notice">
        <p><strong>Basic Markdown View</strong> - For full rendering, install the markdown converter.</p>
        <p><em>Press Ctrl+P to print</em></p>
    </div>
    <pre class="markdown-raw">${escapedText}</pre>
</body>
</html>`;
    }

    _addCustomStyling(html, theme) {
        let css = this._getBasicCSS(theme);
        
        // Insert our CSS into pandoc's HTML
        if (html.includes('<head>')) {
            return html.replace('<head>', '<head>' + css);
        } else if (html.includes('<style>')) {
            return html.replace('<style>', css + '<style>');
        } else {
            return css + html;
        }
    }

    _getBasicCSS(theme) {
        let isDark = theme === 'dark';
        
        return `<style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
            font-size: 16px;
            background-color: ${isDark ? '#0d1117' : '#ffffff'};
            color: ${isDark ? '#e6edf3' : '#24292f'};
            word-wrap: break-word;
        }
        
        .markdown-notice {
            background-color: ${isDark ? '#1f2937' : '#f3f4f6'};
            border: 1px solid ${isDark ? '#374151' : '#d1d5db'};
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        
        .markdown-raw {
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            font-size: 13px;
            line-height: 1.5;
            background-color: ${isDark ? '#161b22' : '#f6f8fa'};
            border: 1px solid ${isDark ? '#30363d' : '#d0d7de'};
            border-radius: 6px;
            padding: 16px;
            overflow-x: auto;
        }
        
        h1, h2, h3, h4, h5, h6 {
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
        }
        
        h1 { 
            font-size: 2em; 
            border-bottom: 1px solid ${isDark ? '#30363d' : '#eaecef'}; 
            padding-bottom: 10px; 
        }
        
        h2 { 
            font-size: 1.5em; 
            border-bottom: 1px solid ${isDark ? '#30363d' : '#eaecef'}; 
            padding-bottom: 8px; 
        }
        
        /* Print styles */
        @media print {
            body {
                max-width: none !important;
                margin: 0 !important;
                padding: 20mm !important;
                font-size: 12pt !important;
                color: black !important;
                background: white !important;
            }
            
            .markdown-notice {
                display: none !important;
            }
            
            h1, h2, h3, h4, h5, h6 {
                page-break-after: avoid;
                color: black !important;
                border-color: black !important;
            }
            
            pre, blockquote {
                page-break-inside: avoid;
                border: 1px solid #ccc !important;
                background: #f9f9f9 !important;
            }
        }
        </style>`;
    }

    _getSystemTheme() {
        try {
            let subprocess = new Gio.Subprocess({
                argv: ['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'],
                flags: Gio.SubprocessFlags.STDOUT_PIPE
            });
            
            subprocess.init(null);
            let [, stdout] = subprocess.communicate_utf8(null);
            
            if (subprocess.get_successful()) {
                let themeName = stdout.trim().replace(/'/g, '').toLowerCase();
                if (themeName.includes('dark')) {
                    return 'dark';
                }
            }
        } catch (e) {
            log('Failed to detect theme: ' + e.message);
        }
        
        return 'light';
    }

    _loadHTML(html) {
        this.load_html(html, this._file.get_uri());
    }

    _showError(message) {
        let theme = this._getSystemTheme();
        let css = this._getBasicCSS(theme);
        
        let errorHTML = `<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Error</title>
    ${css}
</head>
<body>
    <h1>Markdown Preview Error</h1>
    <p>${GLib.markup_escape_text(message, -1)}</p>
    <p>Please check that:</p>
    <ul>
        <li>The markdown file is valid and readable</li>
        <li>The markdown converter is properly installed</li>
        <li>Required dependencies are available</li>
    </ul>
    <p><em>Press Ctrl+P to print this error report</em></p>
</body>
</html>`;
        
        this._loadHTML(errorHTML);
    }

    static {
        if (WebKit2) {
            WebKit2.WebContext.get_default().set_sandbox_enabled(true);
        }
    }

    get moveOnClick() {
        return false;
    }
}) : undefined;

// Register MIME types for markdown files
var mimeTypes = [];
if (_isAvailable()) {
    mimeTypes = [
        'text/markdown',
        'text/x-markdown',
        'application/x-markdown',
        'text/x-web-markdown'
    ];
}