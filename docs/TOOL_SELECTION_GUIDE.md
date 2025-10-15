# Tool Selection Guide - Which Script Should I Use?

## Quick Decision Tree

```
Do you have a Jira export file?
│
├─ YES → What format is it?
│   │
│   ├─ Multiple tickets with columns:
│   │   "Impact & Severity\nMax 38", "Customer ARR\nMax 15", etc.
│   │   │
│   │   └─→ Use: calculate_jira_scores.py (Batch Processor)
│   │       Command: python calculate_jira_scores.py export.xlsx
│   │
│   └─ Single ticket with 317+ columns and image-based scores
│       │
│       └─→ Use: estimate_impact_score.py (Interactive Estimator)
│           Command: python estimate_impact_score.py export.xlsx --interactive
│
└─ NO → Want to calculate score manually?
    │
    └─→ Use: estimate_impact_score.py (Interactive Estimator)
        Command: python estimate_impact_score.py --interactive
```

## Tool Comparison

| Tool | Purpose | Input Format | Output | Best For |
|------|---------|--------------|--------|----------|
| **calculate_jira_scores.py** | Batch processing | Multi-ticket Excel with proper columns | Processed Excel + statistics | Regular score calculation, bulk processing |
| **estimate_impact_score.py** | Single ticket estimation | Interactive prompts OR single-ticket export | Console output with score | Individual tickets, manual estimation |
| **impact_score_calculator.py** | Core calculation engine | Python API calls | Score value | Integration into other systems |
| **jira_impact_score_processor.py** | Excel processor library | Excel DataFrame | Processed DataFrame | Custom Python scripts |

## Detailed Tool Descriptions

### 1. calculate_jira_scores.py - Batch Processor ⚡

**Use when:**
- ✅ You have a batch export with multiple tickets
- ✅ Excel has columns: "Impact & Severity\nMax 38", "Customer ARR\nMax 15", etc.
- ✅ You want to process many tickets at once
- ✅ You need statistics and reports

**Input format:**
```
| Jira | Impact & Severity | Customer ARR | SLA Breach | ... |
|------|------------------|--------------|------------|-----|
| RED-1| 38               | 15           | 8          | ... |
| RED-2| 30               | 10           | 0          | ... |
```

**Example usage:**
```bash
# Process batch file
python calculate_jira_scores.py batch_export.xlsx

# Validate and show top 20
python calculate_jira_scores.py batch_export.xlsx --validate --top 20

# Filter critical tickets only
python calculate_jira_scores.py batch_export.xlsx --priority CRITICAL
```

**Output:**
- Processed Excel file with scores
- Summary statistics
- Priority distribution
- Top priority tickets list

---

### 2. estimate_impact_score.py - Interactive Estimator 🎯

**Use when:**
- ✅ You have a single ticket export (RED-12345_Export.xlsx format)
- ✅ Impact scores are stored as images/screenshots
- ✅ You need to manually estimate a score
- ✅ You want to validate a manual calculation

**Input format:**
Single ticket export with 317+ columns:
```
| Issue key | Custom field (Impact Score) | Custom field (Impact Score details) | ... |
|-----------|----------------------------|-------------------------------------|-----|
| RED-12345 | 47.0                       | [image/screenshot]                  | ... |
```

**Example usage:**
```bash
# Interactive mode (recommended)
python estimate_impact_score.py --interactive

# With Excel file (falls back to interactive if needed)
python estimate_impact_score.py RED-153478_Export.xlsx
```

**Interactive prompts:**
```
1. IMPACT & SEVERITY (Max 38 points)
   P1 (38 pts): Service stopped...
   P2 (30 pts): Service degraded...
   Select priority level (P1-P5): P3

2. CUSTOMER ARR (Max 15 points)
   1 (15 pts): ARR > $1M
   2 (13 pts): $1M > ARR > $500K
   Select ARR level (1-6): 1

[... continues for all components ...]
```

**Output:**
- Component breakdown
- Base score
- Final impact score
- Priority classification

---

### 3. impact_score_calculator.py - Core Engine 🔧

**Use when:**
- ✅ Building custom integrations
- ✅ Need programmatic access
- ✅ Want helper methods for score calculation

**Example usage:**
```python
from impact_score_calculator import ImpactScoreComponents, ImpactScoreCalculator

# Define components
ticket = ImpactScoreComponents(
    impact_severity=38,
    customer_arr=15,
    sla_breach=8,
    frequency=16,
    workaround=15,
    rca_action_item=8,
    support_multiplier=0.15,
    account_multiplier=0.15
)

# Calculate
score = ImpactScoreCalculator.calculate_impact_score(ticket)
print(f"Impact Score: {score}")  # Output: 130.0
```

---

### 4. jira_impact_score_processor.py - Excel Processor 📊

**Use when:**
- ✅ Building custom batch processing scripts
- ✅ Need advanced DataFrame manipulation
- ✅ Want to customize processing logic

**Example usage:**
```python
from jira_impact_score_processor import JiraImpactScoreProcessor

processor = JiraImpactScoreProcessor('export.xlsx')
processor.load_data()
results = processor.calculate_scores()

# Custom analysis
critical = results[results['priority_level'] == 'CRITICAL']
print(f"Critical tickets: {len(critical)}")
```

## Common Scenarios

### Scenario 1: Weekly Backlog Review
**Goal:** Process all open tickets and identify top priorities

```bash
python calculate_jira_scores.py weekly_export.xlsx --top 20
```

### Scenario 2: New Bug Reported
**Goal:** Estimate impact score for a newly reported bug

```bash
python estimate_impact_score.py --interactive
```

### Scenario 3: Single Ticket Export
**Goal:** Calculate score from a single ticket's Excel export

```bash
python estimate_impact_score.py RED-12345_Export.xlsx --interactive
```

### Scenario 4: Validate Existing Scores
**Goal:** Check if calculated scores match existing scores

```bash
python calculate_jira_scores.py export.xlsx --validate
```

### Scenario 5: Custom Report Generation
**Goal:** Build a custom report with specific metrics

```python
from jira_impact_score_processor import JiraImpactScoreProcessor

processor = JiraImpactScoreProcessor('export.xlsx')
processor.load_data()
processor.calculate_scores()

stats = processor.get_summary_stats()
# Generate custom visualizations, etc.
```

## Format Detection

### Batch Export Format (Use calculate_jira_scores.py)
**Indicators:**
- Multiple rows (tickets)
- Columns with names like: "Impact & Severity\nMax 38"
- Each row is a different ticket
- Exported from Jira with specific column configuration

### Single Ticket Export (Use estimate_impact_score.py)
**Indicators:**
- Single row only
- 317+ columns
- Column names like: "Custom field (Impact Score)"
- Impact score details stored as image reference
- Exported using Jira's single-ticket export feature

## Troubleshooting

### "Column not found" error
→ **Use:** `estimate_impact_score.py --interactive` instead

### "No data to process"
→ **Check:** Does your Excel have multiple rows? If yes, use `calculate_jira_scores.py`

### "Cannot extract scores from image"
→ **Solution:** Use `estimate_impact_score.py --interactive` to manually enter values

### Need both tools?
```bash
# Process batch file
python calculate_jira_scores.py batch.xlsx

# Estimate score for a new ticket
python estimate_impact_score.py --interactive
```

## Quick Reference

| Task | Command |
|------|---------|
| Process batch export | `python calculate_jira_scores.py export.xlsx` |
| Validate batch scores | `python calculate_jira_scores.py export.xlsx --validate` |
| Show top 10 tickets | `python calculate_jira_scores.py export.xlsx --top 10` |
| Filter by priority | `python calculate_jira_scores.py export.xlsx --priority CRITICAL` |
| Estimate single ticket | `python estimate_impact_score.py --interactive` |
| Process single export | `python estimate_impact_score.py RED-12345.xlsx --interactive` |

## Documentation Files

- **README.md** - Main documentation and getting started guide
- **ESTIMATOR_GUIDE.md** - Detailed guide for single ticket estimation
- **JIRA_PROCESSOR_USER_GUIDE.md** - Complete API reference for batch processing
- **Impact_Score_Model.md** - Scoring methodology and criteria
- **Impact_Score_Visual_Guide.md** - Visual diagrams and examples
- **QUICK_REFERENCE.md** - One-page cheat sheet

---

**Need Help?** Check the appropriate guide based on your use case!
