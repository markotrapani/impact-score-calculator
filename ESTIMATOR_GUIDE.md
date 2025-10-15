# Individual Jira Ticket Impact Score Estimator

## Overview

This tool estimates impact scores for **individual Jira tickets** through an interactive prompt system. It's designed for cases where:
- You have a single Jira ticket export (not a batch file)
- The impact score components are stored as images/screenshots
- You want to manually calculate an impact score

## The Problem

Individual Jira ticket exports have a different format than batch exports:
- ❌ Single ticket exports have 317+ columns with different naming conventions
- ❌ Impact score breakdowns are often stored as **screenshots/images**, not data fields
- ❌ The batch processor can't extract the component scores

## The Solution

This interactive estimator prompts you for each component and calculates the score automatically.

## Usage

### Method 1: Interactive Mode (Recommended)

```bash
python estimate_impact_score.py --interactive
```

You'll be prompted for each component:

```
JIRA TICKET IMPACT SCORE ESTIMATOR
================================================================================

Entering INTERACTIVE MODE - Please answer the following questions:

================================================================================
1. IMPACT & SEVERITY (Max 38 points)
================================================================================
  P1 (38 pts): Service stopped with no backup/redundancy, multiple services degraded, immediate financial/security impact
  P2 (30 pts): Single service degraded, immediate financial/security impact
  P3 (22 pts): Non-critical service stopped/degraded, critical service at risk, possible financial impact
  P4 (16 pts): Non-critical service at risk
  P5 ( 8 pts): No current or potential impact (informational)

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

### Method 2: With Excel File

```bash
python estimate_impact_score.py RED-153478_Export.xlsx
```

The tool will:
1. Try to extract data from the Excel file
2. If it can't find the component scores, fall back to interactive mode

### Method 3: Python API

```python
from estimate_impact_score import ImpactScoreEstimator

# Define components manually
components = {
    'impact_severity': 22,      # P3
    'customer_arr': 15,         # ARR > $1M
    'sla_breach': 0,            # No breach
    'frequency': 0,             # Single occurrence
    'workaround': 10,           # Complex workaround
    'rca_action_item': 0,       # Not part of RCA
    'support_multiplier': 0.0,  # No multiplier
    'account_multiplier': 0.0   # No multiplier
}

# Calculate
base_score, final_score, priority = ImpactScoreEstimator.calculate_score(components)

print(f"Impact Score: {final_score} ({priority})")
```

## Scoring Guide

### 1. Impact & Severity (0-38 points)

| Option | Points | Description |
|--------|--------|-------------|
| **P1** | 38 | Service stopped with no backup/redundancy, multiple services degraded, immediate financial/security impact |
| **P2** | 30 | Single service degraded, immediate financial/security impact |
| **P3** | 22 | Non-critical service stopped/degraded, critical service at risk, possible financial impact |
| **P4** | 16 | Non-critical service at risk |
| **P5** | 8 | No current or potential impact (informational) |

### 2. Customer ARR (0-15 points)

| Option | Points | Description |
|--------|--------|-------------|
| **1** | 15 | ARR > $1M |
| **2** | 13 | $1M > ARR > $500K |
| **3** | 10 | $500K > ARR > $100K |
| **4** | 8 | >10 low ARR customers |
| **5** | 5 | <10 low ARR customers |
| **6** | 0 | Single low ARR customer |

### 3. SLA Breach (0 or 8 points)

| Option | Points | Description |
|--------|--------|-------------|
| **Y** | 8 | SLA breached or manual recovery required |
| **N** | 0 | SLA not breached or automatic recovery |

### 4. Frequency (0-16 points)

| Option | Points | Description |
|--------|--------|-------------|
| **1** | 0 | 1 occurrence |
| **2** | 8 | 2-4 occurrences |
| **3** | 16 | >4 occurrences |

### 5. Workaround (5-15 points)

| Option | Points | Description |
|--------|--------|-------------|
| **1** | 5 | Simple workaround (single command), no performance impact |
| **2** | 10 | Complex workaround (multiple steps), no performance impact |
| **3** | 12 | Workaround available with performance impact |
| **4** | 15 | No workaround; fix requires new version |

### 6. RCA Action Item (0 or 8 points)

| Option | Points | Description |
|--------|--------|-------------|
| **Y** | 8 | Ticket is part of RCA action items |
| **N** | 0 | Ticket is not part of RCA action items |

### 7. Support Multiplier (0-15%)

Optional percentage boost for bugs that:
- Block upcoming releases
- Pose high risk to service reliability
- Are prioritized by CloudOps team

### 8. Account Multiplier (0-15%)

Optional percentage boost for bugs that:
- Impact deal closures
- Affect customer confidence
- Impact strategic initiatives

## Example: RED-153478

Based on the ticket screenshot provided:

```
Component Values:
  Impact & Severity:    22 (P3 - Non-critical service issue)
  Customer ARR:         15 (ARR > $1M)
  SLA Breach:            0 (No SLA breach)
  Frequency:             0 (Single occurrence)
  Workaround:           10 (Complex workaround, no perf impact)
  RCA Action Item:       0 (Not part of RCA)
  Support Multiplier:    0% (None)
  Account Multiplier:    0% (None)

Calculation:
  Base Score = 22 + 15 + 0 + 0 + 10 + 0 = 47
  Final Score = 47 × (1 + 0 + 0) = 47.0
  
  Priority: LOW (30-49 range)
```

✓ **Matches the expected score of 47!**

## Command-Line Options

```
usage: estimate_impact_score.py [-h] [-i] [file]

positional arguments:
  file                Optional: Path to Jira Excel export

optional arguments:
  -h, --help          Show help message
  -i, --interactive   Force interactive mode (ignore Excel data)
```

## When to Use This Tool

| Scenario | Use This Tool? |
|----------|----------------|
| Single Jira ticket export with image-based scores | ✅ Yes |
| Need to estimate score for a new ticket | ✅ Yes |
| Want to validate a manual calculation | ✅ Yes |
| Batch processing multiple tickets | ❌ No (use `calculate_jira_scores.py`) |
| Excel has proper column structure | ❌ No (use `calculate_jira_scores.py`) |

## Integration with Main Calculator

For batch processing, use the main calculator:

```bash
# For batch/multiple tickets
python calculate_jira_scores.py batch_export.xlsx

# For single ticket estimation
python estimate_impact_score.py --interactive
```

## Tips

1. **Have ticket details ready** - Review the Jira ticket before running the tool
2. **Check Zendesk for ARR** - Customer ARR values are often in Zendesk tags
3. **Document your choices** - The tool shows your selections for verification
4. **Save the output** - Copy/paste the results into the Jira ticket

## Limitations

⚠️ **Cannot extract from image-based data** - If your Jira export stores impact scores as screenshots/images, you must enter values manually

⚠️ **Single ticket only** - For batch processing, use the main `calculate_jira_scores.py` tool

## Validation

The tool was validated against ticket RED-153478:
- Expected score: 47
- Calculated score: 47.0
- ✓ **Match confirmed**
