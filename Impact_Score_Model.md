# Jira Ticket Impact Score Calculation Model

## Overview
The Impact Score is a comprehensive metric used to prioritize Jira tickets (bugs and features) based on their severity, business impact, and customer effect. The score ranges from **0 to 130+** points.

## Formula

```
Impact Score = Base Score × (1 + Support Multiplier + Account Multiplier)

Where:
Base Score = Impact & Severity + Customer ARR + SLA Breach + Frequency + Workaround + RCA Action Item
```

---

## Scoring Components

### 1. Impact & Severity (Max: 38 points)
**Purpose:** Reflects the severity and impact of the bug, measured by magnitude and duration of impact (actual or potential).

| Score | Criteria |
|-------|----------|
| **38** | P1 - Single service stopped with no backup/redundancy (or data loss)<br>• Multiple services in degraded state<br>• Immediate financial or security impact to customers/partners/business |
| **30** | P2 - Single service in degraded state<br>• Immediate financial or security impact to customers/partners business |
| **22** | P3 - Non-critical business service stopped or severely degraded<br>• Critical business service at risk of degradation/stoppage<br>• Possible financial or security impact |
| **16** | P4 - Non-critical business service at risk of degradation/stoppage |
| **8** | P5 - No current or potential impact (informational) |

---

### 2. Customer ARR (Max: 15 points)
**Purpose:** Weights tickets based on customer value and VIP status.

| Score | Criteria |
|-------|----------|
| **15** | ARR > $1M |
| **13** | $1M > ARR > $500K |
| **10** | $500K > ARR > $100K |
| **8** | >10 low ARR customers affected |
| **5** | <10 low ARR customers affected |
| **0** | Single low ARR customer |

*Note: Check Zendesk tags to find customer ARR*

---

### 3. SLA Breach (Max: 8 points)
**Purpose:** Indicates if the bug caused a breach in Redis Cloud SLA or exceeded on-prem downtime thresholds.

| Score | Criteria |
|-------|----------|
| **8** | Cloud SLA breached OR on-prem manual recovery required |
| **0** | Cloud SLA not breached OR on-prem automatic recovery |

**Redis Cloud SLA Targets:**
- **Active-Active:** 99.999% (26s monthly / 5m13s yearly downtime allowed)
- **Multi AZ:** 99.99% (4m21s monthly / 52m9.8s yearly downtime allowed)
- **Single AZ (HA):** 99.9% (43m28s monthly / 8h41m38s yearly downtime allowed)

**Redis Software Downtime Thresholds:**
- **Active-Active:** > 5 minutes
- **Multi AZ:** > 1 hour
- **Single AZ:** > 9 hours

**Support Add-on Consideration:**
- Manual recovery = 8 points
- Automatic recovery = 0 points

---

### 4. Frequency (Max: 16 points)
**Purpose:** Higher scores for recurring issues vs. one-time events.

| Score | Criteria |
|-------|----------|
| **16** | > 4 occurrences |
| **8** | 2-4 occurrences |
| **0** | 1 occurrence |

---

### 5. Workaround (Max: 15 points)
**Purpose:** Availability and complexity of workarounds affect priority.

| Score | Criteria |
|-------|----------|
| **15** | No workaround provided; fix requires new version |
| **12** | Workaround available with performance impact |
| **10** | Complex workaround (multiple steps), no performance impact |
| **5** | Simple workaround (single command), no performance impact |

*Note: This score may change over time if a workaround is discovered*

---

### 6. RCA Action Item (Max: 8 points)
**Purpose:** Prioritizes tickets that are part of Root Cause Analysis action items.

| Score | Criteria |
|-------|----------|
| **8** | Ticket is part of RCA action items |
| **0** | Ticket is not part of RCA action items |

---

### 7. Support Multiplier (Optional: 0-15%)
**Purpose:** Applied when bugs have relatively lower base scores but are blockers for upcoming versions or pose high service risk.

- **Range:** 0% to 15%
- **Applied by:** CloudOps team ranking

---

### 8. Account Multiplier (Optional: 0-15%)
**Purpose:** Accounts for impact on deal closures, customer confidence, and customer-facing team efforts.

- **Range:** 0% to 15%
- **Applied when:** Bug impacts business development, customer relationships, or strategic initiatives

---

## Calculation Examples

### Example 1: High Priority Customer Issue
```
Impact & Severity: 30 (P2 - degraded service)
Customer ARR: 15 (ARR > $1M)
SLA Breach: 0
Frequency: 0 (first occurrence)
Workaround: 10 (complex workaround, no perf impact)
RCA Action Item: 8 (part of RCA)
Support Multiplier: 0%
Account Multiplier: 0%

Base Score = 30 + 15 + 0 + 0 + 10 + 8 = 63
Impact Score = 63 × (1 + 0 + 0) = 63.0
```

### Example 2: Critical Issue with Multiplier
```
Impact & Severity: 38 (P1 - service stopped)
Customer ARR: 15 (ARR > $1M)
SLA Breach: 8 (SLA breached)
Frequency: 16 (>4 occurrences)
Workaround: 15 (no workaround)
RCA Action Item: 8 (part of RCA)
Support Multiplier: 15%
Account Multiplier: 15%

Base Score = 38 + 15 + 8 + 16 + 15 + 8 = 100
Impact Score = 100 × (1 + 0.15 + 0.15) = 130.0
```

### Example 3: Lower Priority Issue
```
Impact & Severity: 8 (P5 - informational)
Customer ARR: 5 (<10 low ARR customers)
SLA Breach: 0
Frequency: 8 (2-4 occurrences)
Workaround: 5 (simple workaround)
RCA Action Item: 0
Support Multiplier: 0%
Account Multiplier: 0%

Base Score = 8 + 5 + 0 + 8 + 5 + 0 = 26
Impact Score = 26 × (1 + 0 + 0) = 26.0
```

---

## Score Interpretation

### Priority Ranges (Suggested)
- **90-130+:** Critical - Immediate attention required
- **70-89:** High - Prioritize in current sprint
- **50-69:** Medium - Schedule in upcoming sprints
- **30-49:** Low - Backlog, address as capacity allows
- **0-29:** Minimal - Defer or close

---

## Key Principles

1. **Dynamic Scoring:** Fields like Frequency, Workaround, and Customer ARR can be updated as situations evolve
2. **Customer Empathy:** VIP customers and RCA action items receive priority to ensure world-class service
3. **Risk-Based:** Multipliers account for strategic risks beyond immediate technical impact
4. **Transparency:** All scores are calculated using objective criteria from Confluence documentation

---

## Implementation Notes

- Maximum theoretical base score: 38 + 15 + 8 + 16 + 15 + 8 = **100 points**
- With maximum multipliers (15% + 15%): 100 × 1.30 = **130 points**
- The "DO NOT EDIT" Impact Score column is auto-calculated using this formula
- Ensure all team members understand the scoring criteria for consistent application
