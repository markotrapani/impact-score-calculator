# Script Architecture & Relationships

**Last Updated:** November 21, 2025

---

## Purpose of This Document

This document explains **why we have 12 scripts** and **how they relate to each other**. If you're wondering "Why do we have both X and Y?", this is for you.

---

## The Big Picture: Libraries vs CLI Tools

### 📚 **Libraries** (4 scripts)
**Purpose:** Reusable code that other scripts import
**Users:** Other Python scripts, not humans
**How to identify:** Other scripts import them with `from X import Y`

### 🔧 **CLI Tools** (8 scripts)
**Purpose:** User-facing command-line tools
**Users:** Humans running them from terminal
**How to identify:** You run them with `python3 src/script_name.py`

---

## Question 1: Why Both `create_jira_from_zendesk.py` AND `jira_creator.py`?

### Answer: One is a CLI Tool, One is a Library

| Script | Type | Purpose |
|--------|------|---------|
| `jira_creator.py` | **LIBRARY** | Core Jira creation logic (classes, functions) |
| `create_jira_from_zendesk.py` | **CLI TOOL** | User-facing script that USES jira_creator |

**Think of it like:**
- `jira_creator.py` = The engine
- `create_jira_from_zendesk.py` = The car that uses the engine

**Code relationship:**
```python
# In create_jira_from_zendesk.py:
from jira_creator import JiraCreator  # ← Imports the library

creator = JiraCreator()
ticket = creator.create_from_zendesk(pdf_file)
```

**Why separate them?**
- **Reusability:** Multiple CLI tools can use `jira_creator.py`
- **Maintainability:** Core logic in one place
- **Testability:** Can test library independently

**Other scripts that use `jira_creator.py`:**
- `create_rca.py`
- `generate_rca_summary.py`
- `generate_complete_rca.py`

---

## Question 2: Impact Score Scripts - What's the Difference?

You have **5 scripts related to impact scores**. Here's how they relate:

### The Pyramid Structure

```
                  CLI Tools (User-Facing)
                 ╱                        ╲
    intelligent_estimator.py    estimate_impact_score.py    calculate_jira_scores.py
           (Auto PDF)              (Manual Interactive)         (Batch Excel)
                 ╲                        ╱                          │
                  ╲                      ╱                           │
                   ╲____________________╱____________________________│
                               │
                               │  Uses
                               ▼
                   impact_score_calculator.py
                      (Core Calculation Logic)
                               ▲
                               │  Also uses
                               │
                   jira_impact_score_processor.py
                      (Excel Processing Logic)
```

### Detailed Breakdown

#### 1️⃣ **`impact_score_calculator.py`** - LIBRARY (Core Logic)

**Type:** Library
**Purpose:** Pure calculation logic
**Contains:**
- Scoring constants (SEVERITY_P1 = 38, etc.)
- Calculation functions
- ImpactScoreComponents dataclass

**Used by:** ALL other impact score tools

**Example:**
```python
from impact_score_calculator import ImpactScoreCalculator

calc = ImpactScoreCalculator()
score = calc.calculate_total_score(
    severity=30,
    arr=15,
    sla_breach=0,
    frequency=16,
    workaround=15,
    rca=0
)
# Returns: 76
```

---

#### 2️⃣ **`jira_impact_score_processor.py`** - LIBRARY (Excel Logic)

**Type:** Library
**Purpose:** Excel-specific processing
**Contains:**
- Excel file reading
- Column mapping
- Batch processing logic
- Data validation

**Used by:** `calculate_jira_scores.py`

**Example:**
```python
from jira_impact_score_processor import JiraImpactScoreProcessor

processor = JiraImpactScoreProcessor('jira_export.xlsx')
results = processor.calculate_scores()
processor.save_to_excel('output.xlsx')
```

---

#### 3️⃣ **`intelligent_estimator.py`** - CLI TOOL (Auto PDF Analysis)

**Type:** User-facing CLI tool
**Purpose:** Automatically analyze PDFs and estimate scores
**What it does:**
1. Parses PDF (Zendesk or Jira)
2. Looks for keywords (CRITICAL, RCA, workaround, etc.)
3. Uses heuristics to estimate each component
4. Calculates final score

**Uses:**
- `universal_ticket_parser` (to read PDFs)
- `impact_score_calculator` (for calculation)

**When to use:** You have a PDF and want quick automatic analysis

**Example:**
```bash
python3 src/intelligent_estimator.py ticket.pdf --arr 5M-10M
```

---

#### 4️⃣ **`estimate_impact_score.py`** - CLI TOOL (Manual Interactive)

**Type:** User-facing CLI tool
**Purpose:** Interactive Q&A to manually enter score components
**What it does:**
1. Asks you questions (What's the severity? What's the ARR?)
2. Shows you options with point values
3. You enter your choices
4. Calculates final score

**Uses:**
- `impact_score_calculator` (for calculation only)

**When to use:** You don't have a file, or you want to manually specify each value

**Example:**
```bash
python3 src/estimate_impact_score.py
# Prompts:
# Select priority level (P1-P5): P2
# Select ARR (1-6): 1
# ... etc
```

---

#### 5️⃣ **`calculate_jira_scores.py`** - CLI TOOL (Batch Excel)

**Type:** User-facing CLI tool
**Purpose:** Process Excel file with many Jira tickets
**What it does:**
1. Reads Excel file exported from Jira
2. Processes ALL rows/tickets
3. Calculates scores for each
4. Saves results to new Excel file

**Uses:**
- `jira_impact_score_processor` (for Excel handling)
- `impact_score_calculator` (for calculation)

**When to use:** You have a Jira Excel export with 10, 50, or 100+ tickets

**Example:**
```bash
python3 src/calculate_jira_scores.py jira_export.xlsx --output scored.xlsx
```

---

### Summary Table: Impact Score Tools

| Script | Type | Input | Output | Use Case |
|--------|------|-------|--------|----------|
| `impact_score_calculator.py` | Library | Python values | Score | Used by all tools |
| `jira_impact_score_processor.py` | Library | Excel file | Processed data | Used by batch tool |
| `intelligent_estimator.py` | CLI Tool | PDF file | Score + breakdown | Single ticket, auto-analysis |
| `estimate_impact_score.py` | CLI Tool | Manual input | Score + breakdown | Single ticket, manual entry |
| `calculate_jira_scores.py` | CLI Tool | Excel file | Excel + scores | Many tickets at once |

---

## Question 3: RCA Scripts - What's the Difference?

You have **3 RCA-related scripts**. Here's how they differ:

### 1️⃣ **`create_rca.py`** - Create RCA Ticket Structure

**Purpose:** Creates the basic RCA Jira ticket
**Input:** Command-line arguments (customer, date, ticket IDs, bug IDs)
**Output:** Basic RCA ticket markdown with template structure

**What it does:**
- Creates RCA ticket skeleton
- Links related Zendesk tickets
- Links related bug Jiras
- Provides empty template fields to fill

**When to use:** You want to quickly create an RCA ticket and fill details manually

**Example:**
```bash
python3 src/create_rca.py \
  --customer "FedEx" \
  --date "11/21/25" \
  --zendesk-tickets 149320 \
  --related-bugs RED-172012
```

**Output:**
```markdown
# RCA: FedEx - 11/21/25

Related Zendesk: #149320
Related Bugs: RED-172012

## Summary
[To be filled]

## Timeline
[To be filled]

## Root Cause
[To be filled]
```

---

### 2️⃣ **`generate_rca_summary.py`** - Generate Summary from PDFs

**Purpose:** Analyzes PDFs and generates RCA summary section
**Input:** Zendesk PDFs + Jira PDFs
**Output:** RCA summary with timeline, root cause, action items

**What it does:**
- Reads multiple PDFs
- Extracts timestamps, errors, resolutions
- Generates summary narrative
- Creates timeline
- Suggests root cause based on bug descriptions

**When to use:** You have PDFs and want auto-generated summary content

**Example:**
```bash
python3 src/generate_rca_summary.py \
  --zendesk-pdfs ticket1.pdf ticket2.pdf \
  --jira-pdfs bug1.pdf bug2.pdf \
  --customer "FedEx" \
  --date "11/21/25"
```

**Output:**
```markdown
## Summary
Multi-cluster CRDB issue affecting FedEx production...

## Timeline
- Nov 12, 2025 09:17 - Initial report
- Nov 12, 2025 16:22 - Investigation started
- Nov 13, 2025 11:43 - OVC discrepancy identified
...

## Root Cause
Analysis shows slave shard OVC higher than master...
```

---

### 3️⃣ **`generate_rca_form.py`** - Generate Complete RCA in Jira Form Format

**Purpose:** Generate complete RCA content in exact Jira form structure
**Input:** Zendesk PDFs + Jira PDFs + cluster info
**Output:** Complete RCA markdown matching Jira RCA form exactly

**What it does:**
- Everything `generate_rca_summary.py` does
- PLUS: Formats output to match Jira RCA form fields exactly
- PLUS: Includes support package links
- PLUS: Includes cluster-specific information
- PLUS: Includes action items section

**When to use:** You want a complete, ready-to-paste RCA document

**Example:**
```bash
python3 src/generate_rca_form.py \
  --customer "FedEx" \
  --date "11/21/25" \
  --zendesk-pdfs ticket1.pdf \
  --jira-pdfs bug1.pdf \
  --clusters "prd65" "prd69"
```

**Output:**
```markdown
## Incident Summary
[Generated summary]

## Affected Systems
Clusters: prd65, prd69
Regions: us-west, us-east

## Timeline
[Generated timeline with cluster-specific events]

## Root Cause Analysis
[Generated analysis]

## Resolution
[Generated resolution steps]

## Action Items
- [ ] Action 1
- [ ] Action 2

## Support Packages
- prd65: debuginfo.XXX.tar.gz
- prd69: debuginfo.YYY.tar.gz
```

---

### RCA Scripts Comparison

| Script | Automation Level | Output Completeness | Best For |
|--------|------------------|---------------------|----------|
| `create_rca.py` | Low | Basic template | Quick RCA ticket creation |
| `generate_rca_summary.py` | Medium | Summary + timeline | Auto-generate narrative |
| `generate_rca_form.py` | High | Complete RCA form | Ready-to-paste RCA document |

**Progressive workflow:**
1. Start with `create_rca.py` for basic ticket
2. Use `generate_rca_summary.py` for auto-generated content
3. Use `generate_rca_form.py` for complete, polished RCA

---

## Question 4: What is `universal_ticket_parser.py`?

**Type:** Library
**Purpose:** Universal file format parser

### What Problem Does It Solve?

You need to read ticket data from:
- Zendesk PDFs
- Jira PDFs
- Jira Excel exports
- Jira XML exports
- Jira Word documents

Each format is different. This library handles all of them.

### What It Does

**Input:** File path (any supported format)
**Output:** Standardized Python dictionary with ticket data

```python
{
    'source': 'zendesk',
    'ticket_id': '149320',
    'title': 'FedEx - Clusters PRD 65...',
    'description': 'Full ticket description...',
    'customer': 'FedEx',
    'severity': 'Normal',
    'priority': 'Normal',
    # ... etc
}
```

### Who Uses It?

- `intelligent_estimator.py` - To read PDFs
- `create_jira_from_zendesk.py` - To parse Zendesk PDFs
- `generate_rca_summary.py` - To analyze multiple PDFs
- `generate_rca_form.py` - To extract info from PDFs

### Example

```python
from universal_ticket_parser import UniversalTicketParser

parser = UniversalTicketParser('zendesk_ticket.pdf')
data = parser.parse()

print(data['ticket_id'])   # → "149320"
print(data['customer'])    # → "FedEx"
```

**Think of it as:** A universal translator for ticket files

---

## Complete Dependency Map

```
CLI Tools Layer (User-Facing)
├── intelligent_estimator.py
│   ├── uses → universal_ticket_parser
│   └── uses → impact_score_calculator
│
├── estimate_impact_score.py
│   └── uses → impact_score_calculator
│
├── calculate_jira_scores.py
│   ├── uses → jira_impact_score_processor
│   └── uses → impact_score_calculator
│
├── create_jira_from_zendesk.py
│   ├── uses → jira_creator
│   ├── uses → universal_ticket_parser
│   └── uses → intelligent_estimator
│
├── create_rca.py
│   └── uses → jira_creator
│
├── generate_rca_summary.py
│   ├── uses → jira_creator
│   ├── uses → universal_ticket_parser
│   └── uses → intelligent_estimator
│
├── generate_rca_form.py
│   └── uses → generate_rca_summary
│
└── generate_complete_rca.py
    ├── uses → generate_rca_summary
    └── uses → create_rca

Library Layer (Imported by Tools)
├── impact_score_calculator.py       # Core scoring logic
├── jira_impact_score_processor.py   # Excel batch processing
├── universal_ticket_parser.py       # Multi-format parsing
└── jira_creator.py                  # Jira ticket creation
```

---

## Design Principles

### 1. **Separation of Concerns**
- **Libraries** = Logic
- **CLI Tools** = User interface to that logic

### 2. **Don't Repeat Yourself (DRY)**
- Core logic in libraries
- CLI tools are thin wrappers
- Multiple tools can share same libraries

### 3. **Progressive Enhancement**
- Basic tools: `create_rca.py`
- Enhanced tools: `generate_rca_summary.py`
- Complete tools: `generate_rca_form.py`

### 4. **Composability**
- Tools can import other tools
- `generate_rca_form.py` uses `generate_rca_summary.py`
- Avoids code duplication

---

## When to Create a New Script vs Enhance Existing

### Create NEW script when:
- ✅ Completely different input format
- ✅ Completely different use case
- ✅ Different user workflow

### Enhance EXISTING script when:
- ✅ Same input, just more features
- ✅ Same use case, better algorithm
- ✅ Same workflow, added options

---

## FAQ

### Q: Why not just have one mega-script that does everything?

**A:** Violates single responsibility principle. Each tool should do ONE thing well:
- `intelligent_estimator` = Analyze PDFs for impact scores
- `create_jira_from_zendesk` = Convert Zendesk to Jira
- `calculate_jira_scores` = Batch process Excel

### Q: Why have libraries if they're not user-facing?

**A:** Code reuse and maintainability:
- If scoring logic changes, update `impact_score_calculator.py` once
- All 3 CLI tools automatically benefit
- Without libraries, you'd update 3+ files

### Q: Can I run library files directly?

**A:** No. Libraries don't have CLI interfaces. They're meant to be imported:
```bash
# ❌ WRONG
python3 src/impact_score_calculator.py

# ✅ RIGHT
python3 src/intelligent_estimator.py  # This imports the library
```

### Q: How do I know if I need a library or CLI tool?

Ask yourself:
- **Will users run this from command line?** → CLI Tool
- **Will other scripts import this?** → Library
- **Both?** → Split into library + CLI tool

---

## Refactoring History

### Before Refactoring (16 scripts)
- 4 obsolete/superseded scripts
- 2 hardcoded examples
- Confusing naming ("_fixed" suffix)

### After Refactoring (12 scripts)
- 4 core libraries
- 8 well-defined CLI tools
- Clear naming
- Better organization

**Reduction:** 25% fewer scripts, 100% clearer purpose

---

*Last Updated: November 21, 2025*
