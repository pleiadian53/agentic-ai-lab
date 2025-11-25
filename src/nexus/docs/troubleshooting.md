# Nexus Research Agent - Troubleshooting Guide

## PDF Generation Issues

### Issue: PDF Not Generated or "View PDF" Button Missing

**Symptoms:**
- Research report completes successfully
- Markdown file exists in `output/research_reports/<topic>/`
- No PDF file present
- Web interface shows only "View Markdown" button

**Common Causes:**

#### 1. LaTeX Syntax Errors in Generated Report

The Writer agent may generate LaTeX documents with syntax errors, particularly when using advanced models like GPT-4.5 or GPT-5.

**Example Error:**
```latex
\labeleq:feas_compute_growth  # ❌ Wrong
\label{eq:feas_compute_growth}  # ✅ Correct
```

**How to Diagnose:**
```bash
# Try to compile the report manually
cd output/research_reports/<topic_directory>/
mamba run -n agentic-ai tectonic report_*.md
```

**Common LaTeX Errors:**
- `\labeleq:` instead of `\label{eq:}`
- Missing closing braces `}`
- Undefined control sequences
- Missing packages in preamble
- Mismatched `\begin{...}` and `\end{...}`

**How to Fix:**
1. Open the markdown file (it's actually LaTeX)
2. Look for the error line number from tectonic output
3. Fix the syntax error
4. Recompile manually:
   ```bash
   cd output/research_reports/<topic_directory>/
   mamba run -n agentic-ai tectonic report_*.md
   ```
5. Refresh the web interface

#### 2. Full LaTeX Document vs Markdown

**Issue:** Writer agent generates a complete LaTeX document instead of markdown with embedded math.

**Detection:**
```bash
head -5 output/research_reports/<topic>/report_*.md
```

If you see:
```latex
\documentclass[11pt,article]{article}
\usepackage{amsmath,amssymb,amsfonts}
...
```

This is a **full LaTeX document**, not markdown.

**Solution:**
- This is actually intentional for academic reports with heavy math
- Compile with LaTeX engine (tectonic) instead of pandoc
- The PDF generation code should detect this automatically (future improvement)

#### 3. Missing LaTeX Engine

**Error:** `xelatex not found` or `tectonic not found`

**Solution:**
```bash
# Check if tectonic is installed
mamba run -n agentic-ai tectonic --version

# If not installed, add to environment
mamba activate agentic-ai
mamba install -c conda-forge tectonic
```

---

## Manual PDF Generation

If automatic PDF generation fails, you can generate PDFs manually:

### For LaTeX Documents (starts with `\documentclass`)

```bash
cd output/research_reports/<topic_directory>/
mamba run -n agentic-ai tectonic report_*.md
```

### For Markdown Documents (starts with `#` headings)

```bash
cd output/research_reports/<topic_directory>/
mamba run -n agentic-ai pandoc report_*.md \
  -o report_*.pdf \
  --pdf-engine=tectonic \
  -V geometry:margin=1in \
  -V fontsize=11pt
```

---

## Model-Specific Issues

### GPT-4.5 / GPT-5 LaTeX Generation

**Issue:** Advanced models may generate more sophisticated LaTeX but with occasional syntax errors.

**Common Patterns:**
- Typos in LaTeX commands (e.g., `\labeleq` instead of `\label`)
- Complex equation environments that tectonic doesn't support
- Missing package declarations

**Mitigation Strategies:**

1. **Add LaTeX validation to Writer agent** (future improvement)
2. **Use simpler LaTeX in prompts** for Writer agent
3. **Post-process LaTeX** to fix common errors automatically

### GPT-4o vs GPT-4.5/5 Differences

| Model | LaTeX Quality | Syntax Errors | Recommendation |
|-------|---------------|---------------|----------------|
| GPT-4o | Good | Rare | Default for production |
| GPT-4.5 | Excellent | Occasional | Use with validation |
| GPT-5 | Excellent | Occasional | Use with validation |

---

## Debugging Checklist

When PDF generation fails:

- [ ] Check if markdown file exists
- [ ] Check file size (should be > 10 KB for full report)
- [ ] Try manual compilation with tectonic
- [ ] Check tectonic error output for specific line numbers
- [ ] Look for LaTeX syntax errors at reported lines
- [ ] Verify LaTeX packages are available
- [ ] Check if it's LaTeX or markdown format
- [ ] Review Writer agent output in logs

---

## Prevention: Automatic Error Fixing 

As of the latest version, Nexus automatically fixes common LaTeX errors before PDF compilation:

**Auto-fixed Errors:**
- `\labeleq:` → `\label{eq:}` 
- `\begineq:` → `\begin{eq:}`
- Missing closing braces in `\label`
- Commas after `\label` in equations

When auto-fixes are applied, you'll see log messages like:
```
 Auto-fixed 1 LaTeX error(s):
   - Fixed \labeleq: → \label{eq:}
```

### Future Improvements

### Additional LaTeX Validation

Planned validation step after Writer agent:

```python
def validate_latex(content: str) -> tuple[bool, list[str]]:
    """
    Validate LaTeX syntax before PDF generation.
    
    Returns:
        (is_valid, list_of_errors)
    """
    common_errors = [
        (r'\\labeleq:', r'\\label{eq:'),  # Fix label syntax
        (r'\\begineq:', r'\\begin{eq:'),  # Fix begin syntax
        # Add more patterns...
    ]
    
    errors = []
    for pattern, replacement in common_errors:
        if re.search(pattern, content):
            errors.append(f"Found '{pattern}', should be '{replacement}'")
    
    return len(errors) == 0, errors
```

### Automatic Error Correction

```python
def fix_common_latex_errors(content: str) -> str:
    """Auto-fix common LaTeX syntax errors."""
    fixes = [
        (r'\\labeleq:(\w+)', r'\\label{eq:\1}'),
        (r'\\begineq:(\w+)', r'\\begin{eq:\1}'),
        # Add more patterns...
    ]
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content)
    
    return content
```

### Better Error Reporting

Enhance PDF generation to:
1. Detect LaTeX vs markdown automatically
2. Show specific error line and context
3. Suggest fixes for common errors
4. Retry with auto-fixes applied

---

## Related Documentation

- [Installation Guide](installation.md) - LaTeX engine setup
- [Research Agent README](../agents/research/README.md) - Usage guide
- [Configuration](../agents/research/server/config.py) - Output paths

---

## Getting Help

If you encounter issues not covered here:

1. Check the log file in `output/research_reports/<topic>/`
2. Try manual PDF generation to see full error output
3. Review the generated LaTeX/markdown for obvious errors
4. Open an issue with the error message and report file
