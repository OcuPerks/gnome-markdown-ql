# GNOME Markdown Quick Look Test

This is a test file to verify that our GNOME Markdown Quick Look extension is working correctly.

## Features Demonstration

### Code Syntax Highlighting

Here's some Python code:

```python
def fibonacci(n):
    """Generate Fibonacci sequence up to n."""
    a, b = 0, 1
    sequence = []
    while a < n:
        sequence.append(a)
        a, b = b, a + b
    return sequence

# Test the function
print(fibonacci(100))
```

And some JavaScript:

```javascript
const markdownRenderer = {
    convertToHTML(text) {
        // Simple markdown to HTML conversion
        return text
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
            .replace(/\*(.*)\*/gim, '<em>$1</em>');
    }
};
```

### Tables

| Feature | Status | Notes |
|---------|--------|-------|
| Syntax Highlighting | ✅ | Using Pygments |
| Tables | ✅ | GitHub-style tables |
| Math | ✅ | MathJax support |
| Themes | ✅ | Light/Dark mode |
| Images | ✅ | Local image support |

### Mathematical Expressions

Inline math: $E = mc^2$

Block math:
$$
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
$$

### Lists and Formatting

- **Bold text**
- *Italic text*
- `Inline code`
- ~~Strikethrough text~~

1. First ordered item
2. Second ordered item
   - Nested unordered item
   - Another nested item

### Blockquotes

> This is a blockquote.
> 
> It can span multiple lines and contain other markdown:
> 
> - List items
> - **Bold text**
> - `Code snippets`

### Links and Images

[GitHub Repository](https://github.com/sbarex/QLMarkdown)

![Markdown Logo](https://markdown-here.com/img/icon256.png)

### Horizontal Rule

---

## Task List

- [x] Create markdown converter
- [x] Implement Sushi viewer
- [x] Add syntax highlighting
- [x] Support tables and math
- [ ] Add emoji support
- [ ] Add mermaid diagram support
- [ ] Add custom themes

## Conclusion

If you can see this file properly formatted with syntax highlighting, tables, and math equations, then the GNOME Markdown Quick Look extension is working correctly!

For more information about markdown syntax, visit the [Markdown Guide](https://www.markdownguide.org/).