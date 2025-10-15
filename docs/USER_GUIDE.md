# Impact Score Calculator - Complete User Guide

**A comprehensive guide to all tools in the Impact Score Calculator toolkit.**

---

## Table of Contents

1. [Quick Start - Which Tool Should I Use?](#quick-start---which-tool-should-i-use)
2. [Tool 1: Intelligent Estimator](#tool-1-intelligent-estimator-intelligent_estimatorpy)
3. [Tool 2: Interactive Estimator](#tool-2-interactive-estimator-estimate_impact_scorepy)
4. [Tool 3: Batch Processor](#tool-3-batch-processor-calculate_jira_scorespy)
5. [Tool 4: Python Library (Advanced)](#tool-4-python-library-advanced)
6. [Scoring Model Reference](#scoring-model-reference)
7. [Common Workflows](#common-workflows)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start - Which Tool Should I Use?

### Decision Tree

```
What do you want to do?
│
├─ Automatically analyze a Jira export
│  └─→ Use: intelligent_estimator.py (AI-powered)
│     python intelligent_estimator.py ticket.xlsx
│
├─ Manually estimate a single ticket score
│  └─→ Use: estimate_impact_score.py (Interactive)
│     python estimate_impact_score.py --interactive
│
├─ Process multiple tickets in batch
│  └─→ Use: calculate_jira_scores.py (Batch)
│     python calculate_jira_scores.py batch_export.xlsx
│
└─ Build custom integration
   └─→ Use: Python library (API)
      from jira_impact_score_processor import JiraImpactScoreProcessor
```

### Tool Comparison Table

| Tool | Input | Processing | Output | Best For |
|------|-------|------------|--------|----------|
| **intelligent_estimator.py** | Single Jira XLSX | AI keyword analysis | Console + JSON | Auto-estimation from any export |
| **estimate_impact_score.py** | Interactive prompts | Manual input | Console | Single ticket manual scoring |
| **calculate_jira_scores.py** | Batch Jira XLSX | Batch calculation | Excel + stats | Multiple tickets with proper columns |
| **Python library** | API calls | Programmatic | Custom | Integration with other systems |

---

## Tool 1: Intelligent Estimator (`intelligent_estimator.py`)

### Overview

**AI-powered automatic estimation** that analyzes Jira exports and estimates all 6 components using keyword detection and pattern recognition.

✅ No manual input required
✅ Analyzes ticket description, labels, priority
✅ Shows reasoning for each estimate
✅ Works with any Jira XLSX export

### Quick Start

```bash
# Basic usage
python intelligent_estimator.py RED-153478_Export.xlsx

# With detailed output
python intelligent_estimator.py ticket.xlsx --verbose

# Save results to JSON
python intelligent_estimator.py ticket.xlsx --output results.json
```

### How It Works

The intelligent estimator uses keyword analysis to estimate each component:

#### 1. Impact & Severity (0-38)
- Checks: Priority field, Severity field
- Keywords: "critical", "outage", "degraded", "error"
- Logic: Priority Blocker=38, High=30, Medium=22, Low=16

#### 2. Customer ARR (0-15)
- Checks: VIP customer list, customer mentions
- Keywords: Customer names, "enterprise", "premium"
- Logic: VIP customers = 15 points

#### 3. SLA Breach (0 or 8)
- Checks: SLA keywords, downtime mentions
- Keywords: "sla breach", "exceeded sla", critical priority
- Logic: Evidence of breach = 8 points

#### 4. Frequency (0-16)
- Checks: Occurrence counts, recurrence keywords
- Keywords: "multiple", "recurring", "again", "repeated", "5 times"
- Logic: Explicit counts or multiple indicators = 16 points

#### 5. Workaround (5-15)
- Checks: Workaround field, complexity indicators
- Keywords: "no workaround", "requires fix", "patch"
- Logic: None=15, With impact=12, Complex=10, Simple=5

#### 6. RCA Action Item (0 or 8)
- Checks: RCA field content (>50 characters)
- Keywords: "rca", "root cause", "action item"
- Logic: Substantial RCA content = 8 points

### Real Example

**Input:** RED-153478_Export.xlsx
```
Priority: Medium
Description: "Similar to as observed by Monday.com..."
Labels: cluster, devops, support
RCA: "1. Bug Description: Issue caused by..."
```

**Output:**
```
COMPONENT BREAKDOWN
─────────────────────────────────────────────

1. Impact & Severity: 22 points
   → Priority 'medium' indicates 22 points

2. Customer ARR: 15 points
   → VIP customer 'monday.com' identified

3. SLA Breach: 0 points
   → No SLA breach indicators found

4. Frequency: 16 points
   → Multiple occurrence keyword 'again' found

5. Workaround: 10 points
   → No clear workaround information

6. RCA Action Item: 8 points
   → RCA field contains substantial content

─────────────────────────────────────────────
FINAL IMPACT SCORE: 71.0 points
PRIORITY LEVEL: HIGH
```

### Customization

#### Add VIP Customers

Edit `intelligent_estimator.py`:
```python
VIP_CUSTOMERS = [
    'monday.com', 'salesforce', 'twilio',
    'your-customer-name',  # Add your customers
]
```

#### Adjust Keywords

```python
WORKAROUND_KEYWORDS = {
    'none': ['no workaround', 'requires fix'],
    'with_impact': ['inconvenient', 'manual steps'],
    # Add your domain-specific keywords
}
```

### Command Options

```bash
python intelligent_estimator.py <file.xlsx>           # Basic
python intelligent_estimator.py <file.xlsx> --verbose # Show all data
python intelligent_estimator.py <file.xlsx> -v        # Verbose (short)
python intelligent_estimator.py <file.xlsx> -o out.json  # Save JSON
```

### Output Formats

**Console Output:**
- Ticket summary
- Component breakdown with reasoning
- Final score and priority

**JSON Output (`--output`):**
```json
{
  "ticket": "RED-153478",
  "components": {
    "impact_severity": 22,
    "customer_arr": 15,
    "sla_breach": 0,
    "frequency": 16,
    "workaround": 10,
    "rca_action_item": 8
  },
  "reasoning": {
    "impact_severity": "Priority 'medium' indicates 22 points",
    "customer_arr": "VIP customer 'monday.com' identified",
    ...
  },
  "scores": {
    "final_score": 71.0,
    "priority": "HIGH"
  }
}
```

### Best Practices

1. ✅ **Review the reasoning** - Understand why each score was assigned
2. ✅ **Customize keywords** - Add domain-specific terms
3. ✅ **Update VIP list** - Keep customer list current
4. ✅ **Validate estimates** - Compare with manual scores
5. ✅ **Use as starting point** - Refine manually if needed

### Limitations

- **Keyword-based**: Relies on text patterns (may miss context)
- **Single ticket**: Processes one at a time (no batch mode)
- **No images**: Can't read score screenshots
- **Conservative**: May overestimate for safety
- **English only**: Works best with English text

---

## Tool 2: Interactive Estimator (`estimate_impact_score.py`)

### Overview

**Interactive manual estimation** for single tickets through guided prompts. Best for tickets where automated analysis isn't sufficient or when you need precise control.

✅ Step-by-step prompts
✅ Immediate score calculation
✅ Works without Jira export
✅ Perfect for new tickets

### Quick Start

```bash
# Interactive mode (recommended)
python estimate_impact_score.py --interactive

# With Excel file (falls back to interactive if needed)
python estimate_impact_score.py RED-153478_Export.xlsx
```

### Interactive Walkthrough

```
JIRA TICKET IMPACT SCORE ESTIMATOR
================================================================================

Entering INTERACTIVE MODE - Please answer the following questions:

================================================================================
1. IMPACT & SEVERITY (Max 38 points)
================================================================================
  P1 (38 pts): Service stopped with no backup/redundancy
  P2 (30 pts): Single service degraded, immediate financial impact
  P3 (22 pts): Non-critical service stopped/degraded
  P4 (16 pts): Non-critical service at risk
  P5 ( 8 pts): No current or potential impact

Select priority level (P1-P5): P3
✓ Selected: P3 = 22 points

================================================================================
2. CUSTOMER ARR (Max 15 points)
================================================================================
  1 (15 pts): ARR > $1M
  2 (13 pts): $1M > ARR > $500K
  3 (10 pts): $500K > ARR > $100K
  4 ( 8 pts): >10 low ARR customers
  5 ( 5 pts): <10 low ARR customers
  6 ( 0 pts): Single low ARR customer

Select ARR level (1-6): 1
✓ Selected: 15 points

[... continues for all components ...]

================================================================================
IMPACT SCORE CALCULATION RESULTS
================================================================================

Component Breakdown:
  Impact & Severity:    22 points
  Customer ARR:         15 points
  SLA Breach:            0 points
  Frequency:             0 points
  Workaround:           10 points
  RCA Action Item:       0 points
  ────────────────────────────────────────
  BASE SCORE:           47 points

================================================================================
  FINAL IMPACT SCORE:   47.0 points
  PRIORITY LEVEL:       LOW
================================================================================
```

### Scoring Guide (Quick Reference)

#### Impact & Severity
- **P1 (38)**: Service stopped, no backup
- **P2 (30)**: Service degraded, financial impact
- **P3 (22)**: Non-critical stopped/degraded
- **P4 (16)**: Non-critical at risk
- **P5 (8)**: Informational only

#### Customer ARR
- **15**: ARR > $1M
- **13**: $1M > ARR > $500K
- **10**: $500K > ARR > $100K
- **8**: >10 low ARR customers
- **5**: <10 low ARR customers
- **0**: Single low ARR customer

#### SLA Breach
- **8**: SLA breached or manual recovery
- **0**: No breach or automatic recovery

#### Frequency
- **0**: 1 occurrence
- **8**: 2-4 occurrences
- **16**: >4 occurrences

#### Workaround
- **5**: Simple workaround, no impact
- **10**: Complex workaround, no impact
- **12**: Workaround with performance impact
- **15**: No workaround available

#### RCA Action Item
- **8**: Part of RCA action items
- **0**: Not part of RCA

### Python API Usage

```python
from estimate_impact_score import ImpactScoreEstimator

components = {
    'impact_severity': 22,
    'customer_arr': 15,
    'sla_breach': 0,
    'frequency': 0,
    'workaround': 10,
    'rca_action_item': 0,
    'support_multiplier': 0.0,
    'account_multiplier': 0.0
}

base_score, final_score, priority = ImpactScoreEstimator.calculate_score(components)
print(f"Impact Score: {final_score} ({priority})")
```

### When to Use

| Scenario | Use This Tool? |
|----------|----------------|
| Single ticket with image-based scores | ✅ Yes |
| Need to estimate score for new ticket | ✅ Yes |
| Want to validate manual calculation | ✅ Yes |
| Batch processing multiple tickets | ❌ No |
| Automated scoring needed | ❌ No |

### Tips

1. **Have ticket details ready** - Review Jira before running
2. **Check Zendesk for ARR** - Customer ARR often in Zendesk tags
3. **Document choices** - Tool shows selections for verification
4. **Save output** - Copy/paste results into Jira

---

## Tool 3: Batch Processor (`calculate_jira_scores.py`)

### Overview

**Batch processing** for multiple tickets with proper column structure. Calculates scores for all tickets at once and provides summary statistics.

✅ Process hundreds of tickets
✅ Summary statistics
✅ Score validation
✅ Priority classification

### Quick Start

```bash
# Process batch file
python calculate_jira_scores.py batch_export.xlsx

# Show top 20 tickets
python calculate_jira_scores.py batch_export.xlsx --top 20

# Validate scores
python calculate_jira_scores.py batch_export.xlsx --validate

# Filter by priority
python calculate_jira_scores.py batch_export.xlsx --priority CRITICAL
```

### Expected Excel Format

The processor expects these columns (names may vary):

**Required:**
- `Jira` / `Issue Key` - Ticket ID
- `Impact & Severity` - Score 0-38
- `Customer ARR` - Score 0-15
- `SLA Breach` - Score 0 or 8
- `Frequency` - Score 0-16
- `Workaround` - Score 5-15
- `RCA Action Item` - Score 0 or 8

**Optional:**
- `Support Multiplier` - 0 to 0.15
- `Account Multiplier` - 0 to 0.15
- `Person` / `Assignee`
- `Last Update`

### Example Excel Structure

| Jira | Impact & Severity | Customer ARR | SLA Breach | Frequency | Workaround | RCA Action Item |
|------|------------------|--------------|------------|-----------|------------|-----------------|
| RED-12345 | 38 | 15 | 8 | 16 | 15 | 8 |
| RED-67890 | 30 | 10 | 0 | 0 | 10 | 8 |

### Output

```
================================================================================
JIRA IMPACT SCORE PROCESSOR
================================================================================

1. Loading Jira export data...
✓ Loaded 332 tickets from jira_export.xlsx

2. Calculating impact scores...

3. Validating calculations...
   ✓ All calculated scores match existing scores!

4. Summary Statistics:
   Total Tickets: 332
   Average Score: 59.3
   Median Score: 60.0
   Score Range: 13.0 - 106.1

   Priority Distribution:
     CRITICAL: 21 tickets
     HIGH: 82 tickets
     MEDIUM: 124 tickets
     LOW: 74 tickets
     MINIMAL: 31 tickets

5. Top 5 Priority Tickets:
   MOD-9262: Score=106.1 (CRITICAL)
   RED-164431: Score=100.8 (CRITICAL)
   RED-168233: Score=100.1 (CRITICAL)
   MOD-10006: Score=100.0 (CRITICAL)
   RED-166789: Score=99.5 (CRITICAL)

6. Exporting results...
✓ Results exported to jira_impact_scores_processed.xlsx
```

### Priority Classification

| Score Range | Priority | Action |
|-------------|----------|--------|
| 90-130+ | **CRITICAL** | Immediate attention |
| 70-89 | **HIGH** | Current sprint |
| 50-69 | **MEDIUM** | Upcoming sprints |
| 30-49 | **LOW** | Backlog |
| 0-29 | **MINIMAL** | Defer/close |

---

## Tool 4: Python Library (Advanced)

### Overview

**Programmatic access** for custom integrations and automation.

### Core Calculator (`impact_score_calculator.py`)

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

### Batch Processor Library (`jira_impact_score_processor.py`)

```python
from jira_impact_score_processor import JiraImpactScoreProcessor

# Initialize
processor = JiraImpactScoreProcessor('export.xlsx')

# Load and process
processor.load_data()
results = processor.calculate_scores()

# Get statistics
stats = processor.get_summary_stats()
print(f"Average score: {stats['average_score']}")

# Get top priorities
top_10 = processor.get_top_priorities(n=10)

# Export
processor.export_results('processed_output.xlsx')

# Validate
is_valid, discrepancies = processor.validate_scores(tolerance=0.1)
```

### Advanced Examples

#### Filter Critical Tickets

```python
processor = JiraImpactScoreProcessor('export.xlsx')
processor.load_data()
results = processor.calculate_scores()

critical = results[results['priority_level'] == 'CRITICAL']
print(f"Found {len(critical)} critical tickets")
```

#### Custom Analysis by Assignee

```python
assignee_stats = results.groupby('person').agg({
    'calculated_impact_score': ['count', 'mean', 'max']
})
print(assignee_stats)
```

#### Batch Process Multiple Files

```python
import glob

for file_path in glob.glob('exports/*.xlsx'):
    processor = JiraImpactScoreProcessor(file_path)
    processor.load_data()
    processor.calculate_scores()
    processor.export_results(file_path.replace('.xlsx', '_processed.xlsx'))
```

---

## Scoring Model Reference

### Formula

```
Base Score = Impact & Severity + Customer ARR + SLA Breach +
             Frequency + Workaround + RCA Action Item

Final Score = Base Score × (1 + Support Multiplier + Account Multiplier)
```

### Component Ranges

| Component | Min | Max | Purpose |
|-----------|-----|-----|---------|
| Impact & Severity | 8 | 38 | Service impact level |
| Customer ARR | 0 | 15 | Customer value |
| SLA Breach | 0 | 8 | SLA violation |
| Frequency | 0 | 16 | Occurrence rate |
| Workaround | 5 | 15 | Solution availability |
| RCA Action Item | 0 | 8 | Part of RCA |
| **Base Score** | **13** | **100** | Sum of components |
| Support Multiplier | 0% | 15% | Release blocker |
| Account Multiplier | 0% | 15% | Deal impact |
| **Final Score** | **13** | **130+** | With multipliers |

For complete details, see [Impact_Score_Model.md](Impact_Score_Model.md).

---

## Common Workflows

### Workflow 1: Weekly Backlog Review

```bash
# Export tickets from Jira to Excel
# Then process:
python calculate_jira_scores.py weekly_export.xlsx --top 20

# Review top 20 tickets and prioritize sprint
```

### Workflow 2: New Bug Reported

```bash
# Estimate score interactively
python estimate_impact_score.py --interactive

# Document score in Jira ticket
```

### Workflow 3: Analyze Single Ticket Export

```bash
# Try automated analysis first
python intelligent_estimator.py RED-12345_Export.xlsx --verbose

# If estimation needs refinement, use interactive
python estimate_impact_score.py --interactive
```

### Workflow 4: Validate Existing Scores

```bash
# Check calculations match
python calculate_jira_scores.py export.xlsx --validate

# Fix any discrepancies found
```

### Workflow 5: Custom Priority Report

```python
from jira_impact_score_processor import JiraImpactScoreProcessor

processor = JiraImpactScoreProcessor('export.xlsx')
processor.load_data()
processor.calculate_scores()

# Generate custom report
high_priority = processor.df[processor.df['calculated_impact_score'] >= 70]
high_priority.to_excel('sprint_priorities.xlsx', index=False)
```

---

## Troubleshooting

### "Column not found" Error

**Problem**: Batch processor can't find expected columns
**Solution**: Use interactive estimator instead:
```bash
python estimate_impact_score.py --interactive
```

### Intelligent Estimator Shows Wrong Score

**Problem**: AI estimation doesn't match expected score
**Solution**:
1. Review the reasoning with `--verbose`
2. Check if keywords need adjustment
3. Use interactive mode for precise control

### "No data to process"

**Problem**: Excel file has wrong format
**Solution**: Check if you have:
- Multiple rows (for batch processor)
- Proper column names
- Try intelligent estimator for single exports

### Score Validation Fails

**Problem**: Calculated scores don't match existing scores
**Solution**:
```python
processor = JiraImpactScoreProcessor('export.xlsx')
processor.load_data()
processor.calculate_scores()
is_valid, discrepancies = processor.validate_scores(tolerance=0.1)
for disc in discrepancies:
    print(disc)  # Review each discrepancy
```

### Missing Dependencies

**Problem**: Import errors
**Solution**:
```bash
pip install pandas openpyxl
```

### Can't Read Image-Based Scores

**Problem**: Single ticket export has scores as screenshots
**Solution**: This is expected. Use interactive mode:
```bash
python estimate_impact_score.py --interactive
```

---

## Additional Documentation

- **[Impact_Score_Model.md](Impact_Score_Model.md)** - Complete scoring specification
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - One-page cheat sheet
- **[Impact_Score_Visual_Guide.md](Impact_Score_Visual_Guide.md)** - Visual diagrams
- **[SCRIPT_UPDATE_LOG.md](SCRIPT_UPDATE_LOG.md)** - Recent improvements
- **[ROADMAP.md](ROADMAP.md)** - Future plans and features

---

**Need more help?** Check the specific documentation files above or open an issue in the repository.

**Last Updated**: October 15, 2025
