# Example PDFs - Local Storage Only

⚠️ **IMPORTANT: PDFs in this directory are NOT committed to git**

## Policy

This directory is for **local storage only** of example Zendesk and Jira ticket exports used for testing and development.

**Why PDFs are excluded:**
- PDFs may contain **customer PII** (names, emails, internal details)
- Zendesk tickets may contain **sensitive support conversations**
- Jira exports may contain **proprietary technical information**

## Protection

All PDFs are automatically excluded from git via `.gitignore`:
```
*.pdf
```

This ensures customer data is never accidentally committed to the repository.

## Usage

### For Development
1. Download Zendesk ticket PDFs to this directory for testing
2. Use them with `claude_interactive.py` or other analysis scripts
3. PDFs remain local and are never pushed to GitHub

### For Testing
Example workflow:
```bash
# Download a Zendesk ticket PDF
mv ~/Downloads/redislabs.zendesk.com_tickets_*.pdf docs/examples/pdfs/

# Analyze with claude_interactive.py
python3 src/claude_interactive.py docs/examples/pdfs/redislabs.zendesk.com_tickets_*.pdf

# PDFs stay local, never committed
git status  # Won't show PDFs as untracked
```

## What Gets Committed

✅ **DO commit:**
- This README
- Example markdown files (anonymized/sanitized)
- Code and scripts

❌ **NEVER commit:**
- PDF files (automatically blocked by .gitignore)
- Any files with real customer names, emails, or PII
- Zendesk/Jira exports with actual customer data

## Anonymization

If you need to share example data:
1. Export the Jira ticket to markdown
2. **Manually anonymize** all customer-specific information:
   - Replace real customer names with "Example Corp", "Customer A", etc.
   - Remove specific email addresses
   - Generalize technical details if needed
3. Commit the anonymized markdown file
4. **Never** commit the original PDF

---

**Remember:** When in doubt, don't commit it. Customer privacy is paramount.
