# Tool Selection Guide

**Last Updated:** November 21, 2025
**Version:** 2.0 (Post-Refactoring)

---

## Quick Decision Tree

**Start here** → What do you need to do?

```
┌─ Need Impact Score? ─────────────────────────────────┐
│                                                       │
│  → From Zendesk PDF?                                 │
│     ✓ Use: intelligent_estimator.py                  │
│                                                       │
│  → From Jira Excel (many tickets)?                   │
│     ✓ Use: calculate_jira_scores.py                  │
│                                                       │
│  → Manual entry (no file)?                           │
│     ✓ Use: estimate_impact_score.py                  │
│                                                       │
└───────────────────────────────────────────────────────┘

┌─ Need to Create Jira Ticket? ────────────────────────┐
│                                                       │
│  → From Zendesk PDF?                                 │
│     ✓ Use: create_jira_from_zendesk.py               │
│                                                       │
│  → RCA ticket?                                       │
│     ✓ Use: create_rca.py                             │
│                                                       │
│  → RCA with auto-generated content from PDFs?       │
│     ✓ Use: generate_rca_form.py OR                   │
│            generate_complete_rca.py                  │
│                                                       │
└───────────────────────────────────────────────────────┘
```

---

## All Tools (12 Total)

### 🎯 Core Libraries (4) - Used by Other Scripts

| Script | Purpose | Direct Use? |
|--------|---------|-------------|
| `impact_score_calculator.py` | Core scoring logic | ❌ Library only |
| `universal_ticket_parser.py` | Multi-format parsing | ❌ Library only |
| `jira_impact_score_processor.py` | Excel processing engine | ❌ Library only |
| `jira_creator.py` | Jira ticket creation logic | ❌ Library only |

**Note:** These are libraries used by the CLI tools below. Don't run them directly.

---

### ⭐ Impact Score Tools (3) - Most Commonly Used

#### 1️⃣ `intelligent_estimator.py` - **PRIMARY TOOL**

**When to use:**
- You have a single Zendesk PDF or Jira PDF
- You want automatic analysis with keyword detection
- You need impact score quickly

**What it does:**
- Automatically analyzes ticket content
- Detects severity, workarounds, RCA indicators, frequency
- Uses keyword matching and heuristics
- Can override ARR if needed

**Example:**
```bash
python3 src/intelligent_estimator.py zendesk_ticket.pdf
python3 src/intelligent_estimator.py jira_export.pdf --arr 5M-10M
python3 src/intelligent_estimator.py ticket.pdf --output scores.json
```

**Output:** Console display + optional JSON file

**Best for:** Quick analysis of individual tickets

---

#### 2️⃣ `calculate_jira_scores.py` - Batch Processing

**When to use:**
- You have a Jira Excel export with multiple tickets
- You need to score many tickets at once
- Excel already has some impact score columns

**What it does:**
- Reads Excel file with Jira tickets
- Calculates impact scores for all rows
- Validates existing scores
- Outputs processed Excel file

**Example:**
```bash
python3 src/calculate_jira_scores.py jira_export.xlsx
python3 src/calculate_jira_scores.py jira_export.xlsx --output results.xlsx
python3 src/calculate_jira_scores.py jira_export.xlsx --top 20
```

**Output:** Excel file with calculated scores

**Best for:** Bulk processing, reporting, analysis

---

#### 3️⃣ `estimate_impact_score.py` - Interactive Manual Entry

**When to use:**
- You don't have a file export
- You want to manually enter each component
- You need to estimate a hypothetical scenario

**What it does:**
- Prompts you for each scoring component
- Shows options with point values
- Calculates total score
- Provides priority level

**Example:**
```bash
python3 src/estimate_impact_score.py
# Follow interactive prompts
```

**Output:** Console display with score breakdown

**Best for:** Quick estimates, training, "what if" scenarios

---

### 📋 Jira Creation Tools (2)

#### 4️⃣ `create_jira_from_zendesk.py` - Zendesk → Jira

**When to use:**
- You have a Zendesk PDF
- You want to create a Jira bug ticket
- You need automatic field mapping

**What it does:**
- Parses Zendesk PDF
- Extracts ticket info (title, description, customer)
- Calculates impact score automatically
- Generates Jira-ready markdown

**Example:**
```bash
python3 src/create_jira_from_zendesk.py zendesk_ticket.pdf
python3 src/create_jira_from_zendesk.py ticket.pdf --project RED
python3 src/create_jira_from_zendesk.py ticket.pdf --output jira_data.json
```

**Output:** Markdown file for Jira + optional JSON

**Best for:** Converting support tickets to bug trackers

---

#### 5️⃣ `create_rca.py` - Create RCA Tickets

**When to use:**
- You need to create an RCA ticket
- You have basic incident info (customer, date)
- You may have multiple related tickets/bugs

**What it does:**
- Creates RCA ticket structure
- Links related Zendesk tickets
- Links related bug Jiras
- Supports multi-cluster incidents

**Example:**
```bash
python3 src/create_rca.py --customer "Azure" --date "11/21/25" \
  --zendesk-tickets 149320 149321 \
  --related-bugs RED-172012 \
  --clusters "cluster1" "cluster2"
```

**Output:** Markdown file with RCA structure

**Best for:** Formal incident documentation

---

### 🔧 RCA Content Generation (3)

#### 6️⃣ `generate_rca_form.py` - Auto-Generate RCA Content

**When to use:**
- You have PDFs for Zendesk tickets and bug Jiras
- You want auto-generated RCA summary and timeline
- You need to fill out the full RCA form

**What it does:**
- Analyzes multiple PDFs
- Extracts timeline events
- Generates root cause summary
- Creates action items
- Outputs in exact Jira RCA form format

**Example:**
```bash
python3 src/generate_rca_form.py --customer "Azure" --date "11/21/25" \
  --zendesk-pdfs ticket1.pdf ticket2.pdf \
  --jira-pdfs bug1.pdf bug2.pdf \
  --clusters "cluster1" "cluster2"
```

**Output:** Complete RCA form in markdown

**Best for:** Comprehensive RCA creation from multiple sources

---

#### 7️⃣ `generate_complete_rca.py` - Complete RCA Package

**When to use:**
- Similar to `generate_rca_form.py`
- You want additional cluster/region analysis
- You need a comprehensive RCA document

**What it does:**
- Combines summary generation with cluster info
- Auto-generates timeline and action items
- Includes support package links
- Provides complete RCA structure

**Example:**
```bash
python3 src/generate_complete_rca.py --customer "FedEx" --date "11/21/25" \
  --zendesk-pdfs ticket1.pdf \
  --clusters "prd65" "prd69" \
  --regions "us-west" "us-east"
```

**Output:** Complete RCA markdown document

**Best for:** Multi-cluster incidents with geographic distribution

---

#### 8️⃣ `generate_rca_summary.py` - RCA Summary Only

**When to use:**
- You only need the summary section
- You'll fill out other RCA sections manually
- You want to analyze PDFs for insights

**What it does:**
- Analyzes Zendesk and Jira PDFs
- Generates incident summary
- Extracts timeline
- Identifies root cause from bug descriptions

**Example:**
```bash
python3 src/generate_rca_summary.py \
  --zendesk-pdfs ticket1.pdf ticket2.pdf \
  --jira-pdfs bug1.pdf \
  --customer "Customer Name" \
  --date "11/21/25"
```

**Output:** RCA summary in markdown

**Best for:** Quick RCA summaries, preliminary analysis

---

## Workflow Examples

### Workflow 1: Support Ticket → Bug Jira

```bash
# Step 1: Analyze Zendesk PDF for impact score
python3 src/intelligent_estimator.py zendesk_ticket.pdf --arr 5M-10M

# Step 2: Create Jira ticket from Zendesk
python3 src/create_jira_from_zendesk.py zendesk_ticket.pdf --project RED

# Step 3: Copy generated markdown to Jira
# (Output is in output/ folder)
```

---

### Workflow 2: Multiple Tickets → RCA

```bash
# Step 1: Collect all PDFs
# - ticket1.pdf, ticket2.pdf (Zendesk)
# - bug1.pdf, bug2.pdf (Jira bugs)

# Step 2: Generate complete RCA
python3 src/generate_complete_rca.py \
  --customer "Azure" \
  --date "11/21/25" \
  --zendesk-pdfs ticket1.pdf ticket2.pdf \
  --jira-pdfs bug1.pdf bug2.pdf \
  --clusters "cluster1" "cluster2" "cluster3"

# Step 3: Create RCA ticket
python3 src/create_rca.py \
  --customer "Azure" \
  --date "11/21/25" \
  --zendesk-tickets 149320 149321 \
  --related-bugs RED-172012 RED-172013

# Step 4: Copy both generated files to Jira
```

---

### Workflow 3: Batch Processing Many Tickets

```bash
# Step 1: Export Jira tickets to Excel

# Step 2: Process all tickets
python3 src/calculate_jira_scores.py jira_export.xlsx --output scored.xlsx

# Step 3: Analyze results
python3 src/calculate_jira_scores.py scored.xlsx --top 20 --priority HIGH
```

---

## Tool Comparison Matrix

| Feature | intelligent_estimator | calculate_jira_scores | estimate_impact_score |
|---------|----------------------|----------------------|----------------------|
| **Input** | PDF (Zendesk/Jira) | Excel | Manual entry |
| **Auto-analysis** | ✅ Yes | ⚠️ Partial | ❌ No |
| **Batch processing** | ❌ No | ✅ Yes | ❌ No |
| **Speed** | Fast | Fast | Slow (interactive) |
| **Accuracy** | Good | Very Good | Perfect (manual) |
| **Best for** | Single tickets | Many tickets | Quick estimates |

---

## Common Questions

### Q: Which tool is most accurate for impact scores?

**A:** `estimate_impact_score.py` (manual entry) is most accurate since you control all inputs. However, `intelligent_estimator.py` is very good for most cases and much faster.

---

### Q: Can I use multiple tools together?

**A:** Yes! Common pattern:
1. Use `intelligent_estimator.py` for quick analysis
2. Use `create_jira_from_zendesk.py` to create ticket
3. Manually adjust if needed

---

### Q: What's the difference between `generate_rca_form.py` and `generate_complete_rca.py`?

**A:**
- `generate_rca_form.py` - Outputs exact Jira RCA form structure
- `generate_complete_rca.py` - More comprehensive, includes cluster analysis
- Both analyze PDFs and auto-generate content
- Choose based on your RCA template preference

---

### Q: How do I know my customer's ARR?

**A:**
1. Check Zendesk organization notes (if available)
2. Ask your TAM or Account Manager
3. Use `--arr unknown` flag and estimate manually
4. Check customer database/Salesforce

---

### Q: Can these tools create Jira tickets automatically?

**A:** No, they generate markdown files that you copy/paste into Jira. Automatic creation would require:
- Jira API credentials
- Permission setup
- Custom field mapping
- Currently out of scope for these tools

---

## Output Files

All tools output to the `output/` folder (gitignored):

| File Pattern | Created By | Purpose |
|--------------|-----------|---------|
| `JIRA-*.md` | create_jira_from_zendesk.py | Bug ticket markdown |
| `RCA-*.md` | create_rca.py | RCA ticket markdown |
| `*.json` | Any (with --output) | Structured data |
| `*_processed.xlsx` | calculate_jira_scores.py | Scored Excel file |

---

## Getting Help

### For Each Tool

Run with `--help` or `-h`:

```bash
python3 src/intelligent_estimator.py --help
python3 src/calculate_jira_scores.py --help
python3 src/create_jira_from_zendesk.py --help
```

### Documentation

See `docs/` folder:
- `INTELLIGENT_ESTIMATOR_GUIDE.md` - Detailed guide for main tool
- `IMPACT_SCORE_MODEL.md` - Scoring algorithm explanation
- `IMPACT_SCORE_VISUAL_GUIDE.md` - Quick reference tables
- `JIRA_PROCESSOR_USER_GUIDE.md` - Batch processing guide

---

## Troubleshooting

### "File not found" errors

- Use absolute paths or run from project root
- Check file extensions (.pdf, .xlsx)

### "No module named..." errors

```bash
pip3 install -r requirements.txt
```

### "Invalid PDF" errors

- Ensure PDF is not encrypted
- Try re-exporting from Zendesk/Jira

### Impact scores seem wrong

- Check ARR value (use `--arr` flag if needed)
- Review keyword detection in verbose mode
- Consider using manual estimator for verification

---

## Version History

**v2.0 (Nov 2025)** - Post-refactoring
- Removed 4 obsolete scripts
- Renamed tools for clarity
- Updated this guide

**v1.0 (Oct 2025)** - Initial version
- 16 scripts total
- Multiple overlapping tools

---

*Last Updated: November 21, 2025*
