# 📋 Impact Score Quick Reference Card

## Formula
```
Impact Score = (Sum of Components) × (1 + Support Multiplier + Account Multiplier)
```

## Scoring Components

### 1️⃣ Impact & Severity (0-38)
| Value | Description |
|-------|-------------|
| **38** | P1 - Service stopped, multiple degraded, immediate financial impact |
| **30** | P2 - Service degraded, immediate financial impact |
| **22** | P3 - Non-critical stopped/degraded, possible financial impact |
| **16** | P4 - Non-critical service at risk |
| **8**  | P5 - No impact (informational) |

### 2️⃣ Customer ARR (0-15)
| Value | Description |
|-------|-------------|
| **15** | ARR > $1M |
| **13** | $1M > ARR > $500K |
| **10** | $500K > ARR > $100K |
| **8**  | >10 low ARR customers |
| **5**  | <10 low ARR customers |
| **0**  | Single low ARR customer |

### 3️⃣ SLA Breach (0 or 8)
| Value | Description |
|-------|-------------|
| **8** | Cloud SLA breached OR manual recovery |
| **0** | Cloud SLA OK OR automatic recovery |

### 4️⃣ Frequency (0-16)
| Value | Description |
|-------|-------------|
| **16** | > 4 occurrences |
| **8**  | 2-4 occurrences |
| **0**  | 1 occurrence |

### 5️⃣ Workaround (5-15)
| Value | Description |
|-------|-------------|
| **15** | No workaround; needs new version |
| **12** | Workaround with performance impact |
| **10** | Complex workaround, no performance impact |
| **5**  | Simple workaround (single command) |

### 6️⃣ RCA Action Item (0 or 8)
| Value | Description |
|-------|-------------|
| **8** | Part of RCA action items |
| **0** | Not part of RCA |

### 7️⃣ Support Multiplier (0-15%)
Optional boost based on CloudOps priority

### 8️⃣ Account Multiplier (0-15%)
Optional boost for business/customer impact

---

## Priority Levels

| Score Range | Priority | Action |
|-------------|----------|--------|
| **90-130+** | 🔴 CRITICAL | Immediate attention - escalate |
| **70-89** | 🟠 HIGH | Current sprint priority |
| **50-69** | 🟡 MEDIUM | Upcoming sprint |
| **30-49** | 🟢 LOW | Backlog |
| **0-29** | ⚪ MINIMAL | Defer/close |

---

## Quick Examples

### Example 1: Maximum Score
```
P1 (38) + ARR>$1M (15) + SLA Breach (8) + 
Frequent (16) + No Workaround (15) + RCA (8) = 100
With multipliers (15% + 15%): 100 × 1.30 = 130 ⭐ CRITICAL
```

### Example 2: Medium Priority
```
P2 (30) + ARR=$200K (10) + No Breach (0) + 
Once (0) + Complex Workaround (10) + RCA (8) = 58
No multipliers: 58 × 1.00 = 58 → MEDIUM
```

### Example 3: Low Priority
```
P5 (8) + Single Customer (0) + No Breach (0) + 
Once (0) + Simple Workaround (5) + No RCA (0) = 13
No multipliers: 13 × 1.00 = 13 → MINIMAL
```

---

## Command Line Cheat Sheet

```bash
# Basic calculation
python calculate_jira_scores.py export.xlsx

# Validate scores
python calculate_jira_scores.py export.xlsx --validate

# Show top 20 tickets
python calculate_jira_scores.py export.xlsx --top 20

# Filter critical only
python calculate_jira_scores.py export.xlsx --priority CRITICAL

# Stats only (no ticket list)
python calculate_jira_scores.py export.xlsx --stats-only

# Custom output location
python calculate_jira_scores.py export.xlsx -o results.xlsx
```

---

## Python API Quick Start

```python
from jira_impact_score_processor import JiraImpactScoreProcessor

# Process Jira export
processor = JiraImpactScoreProcessor('export.xlsx')
processor.load_data()
processor.calculate_scores()

# Get top tickets
top_10 = processor.get_top_priorities(n=10)

# Get statistics
stats = processor.get_summary_stats()

# Export results
processor.export_results('output.xlsx')
```

---

## Decision Tree

```
START → Is service stopped/degraded?
  ↓ YES → Severity 22-38
  ↓ NO  → Severity 8-16

→ VIP customer (ARR>$100K)?
  ↓ YES → ARR 10-15
  ↓ NO  → ARR 0-8

→ SLA breached or manual recovery?
  ↓ YES → +8 points
  ↓ NO  → +0 points

→ Multiple occurrences?
  ↓ YES → Frequency 8-16
  ↓ NO  → +0 points

→ Workaround available?
  ↓ NO  → +15 points
  ↓ YES → 5-12 points (based on complexity)

→ Part of RCA?
  ↓ YES → +8 points
  ↓ NO  → +0 points

→ Strategic/blocking?
  ↓ YES → Add multipliers (up to 30%)
  ↓ NO  → No multipliers

→ CALCULATE FINAL SCORE
```

---

## File Reference

| File | Purpose |
|------|---------|
| `README.md` | Main documentation |
| `Impact_Score_Model.md` | Detailed scoring model |
| `Impact_Score_Visual_Guide.md` | Visual diagrams |
| `JIRA_PROCESSOR_USER_GUIDE.md` | Complete user guide |
| `calculate_jira_scores.py` | CLI tool |
| `jira_impact_score_processor.py` | Excel processor |
| `impact_score_calculator.py` | Core calculator |

---

**📌 Remember:** The goal is objective, consistent prioritization based on customer impact, service reliability, and business value.
