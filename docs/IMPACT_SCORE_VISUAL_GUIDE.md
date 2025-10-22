# Impact Score Calculation - Visual Model

## Formula Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     IMPACT SCORE CALCULATOR                     │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │   Calculate Base Score  │
                    └─────────────────────────┘
                                  │
                 ┌────────────────┴────────────────┐
                 │                                  │
                 ▼                                  ▼
    ┌──────────────────────┐          ┌──────────────────────┐
    │  Core Components     │          │  Binary Components   │
    │  (Variable Scores)   │          │  (Yes/No)           │
    └──────────────────────┘          └──────────────────────┘
                 │                                  │
        ┌────────┴────────┐              ┌─────────┴─────────┐
        ▼                 ▼              ▼                   ▼
┌─────────────┐   ┌─────────────┐   ┌──────────┐   ┌──────────────┐
│Impact &     │   │Customer     │   │SLA       │   │RCA Action    │
│Severity     │   │ARR          │   │Breach?   │   │Item?         │
│(8-38 pts)   │   │(0-15 pts)   │   │(0/8 pts) │   │(0/8 pts)     │
└─────────────┘   └─────────────┘   └──────────┘   └──────────────┘
        │                 │              │                   │
        └────────┬────────┴──────────────┴───────────┬───────┘
                 │                                    │
                 ▼                                    ▼
        ┌─────────────┐                      ┌──────────────┐
        │Frequency    │                      │Workaround    │
        │(0-16 pts)   │                      │(5-15 pts)    │
        └─────────────┘                      └──────────────┘
                 │                                    │
                 └────────────────┬───────────────────┘
                                  │
                                  ▼
                        ┌──────────────────┐
                        │   BASE SCORE     │
                        │   (Sum: 0-100)   │
                        └──────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │  Apply Multipliers      │
                    │  (Optional)             │
                    └─────────────────────────┘
                                  │
                 ┌────────────────┴────────────────┐
                 │                                  │
                 ▼                                  ▼
        ┌──────────────────┐            ┌──────────────────┐
        │Support           │            │Account           │
        │Multiplier        │            │Multiplier        │
        │(0-15%)           │            │(0-15%)           │
        └──────────────────┘            └──────────────────┘
                 │                                  │
                 └────────────────┬─────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────────┐
                    │  Final Impact Score             │
                    │  = Base × (1 + SM + AM)         │
                    │  Range: 0 to 130+               │
                    └─────────────────────────────────┘
```

---

## Scoring Matrix - Quick Reference

### Component Breakdown

| Component | Min | Max | Key Factors |
|-----------|-----|-----|-------------|
| **Impact & Severity** | 8 | 38 | Priority level (P1-P5) |
| **Customer ARR** | 0 | 15 | Customer value/count |
| **SLA Breach** | 0 | 8 | SLA status (Redis Cloud only; ACRE = 0) |
| **Frequency** | 0 | 16 | # of occurrences |
| **Workaround** | 5 | 15 | Availability & complexity |
| **RCA Action Item** | 0 | 8 | Follow-up from past RCA (not current incident) |
| **BASE SCORE** | **8** | **100** | **Sum of above** |
| **Support Multiplier** | 0% | 15% | CloudOps priority |
| **Account Multiplier** | 0% | 15% | Business impact |
| **FINAL SCORE** | **8** | **130** | **Base × (1 + multipliers)** |

---

## Decision Tree: Impact & Severity Selection

```
START: What is the service state and impact?

┌─────────────────────────────────────────────────────────┐
│ Is a critical service STOPPED with no backup?          │
│ OR Multiple services degraded?                          │
│ OR Immediate financial/security impact?                 │
└─────────────────────────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │ YES                            │ NO
        ▼                                ▼
    ┌───────┐              ┌─────────────────────────────────┐
    │ P1=38 │              │ Is single service DEGRADED?     │
    └───────┘              │ OR Immediate financial impact?  │
                           └─────────────────────────────────┘
                                        │
                        ┌───────────────┴───────────────┐
                        │ YES                            │ NO
                        ▼                                ▼
                    ┌───────┐          ┌─────────────────────────────────┐
                    │ P2=30 │          │ Non-critical service stopped?   │
                    └───────┘          │ OR Critical service at risk?    │
                                       │ OR Possible financial impact?   │
                                       └─────────────────────────────────┘
                                                    │
                                    ┌───────────────┴───────────────┐
                                    │ YES                            │ NO
                                    ▼                                ▼
                                ┌───────┐          ┌────────────────────────┐
                                │ P3=22 │          │ Non-critical at risk?  │
                                └───────┘          └────────────────────────┘
                                                                │
                                                ┌───────────────┴──────────┐
                                                │ YES                       │ NO
                                                ▼                           ▼
                                            ┌───────┐                   ┌──────┐
                                            │ P4=16 │                   │ P5=8 │
                                            └───────┘                   └──────┘
```

---

## Priority Score Ranges & Actions

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRIORITY INTERPRETATION                       │
└─────────────────────────────────────────────────────────────────┘

    130 ▲
        │  ┌──────────────────────────────────────┐
        │  │  CRITICAL (90-130+)                  │
    100 │  │  • Immediate action required         │
        │  │  • Escalate to leadership            │
        │  │  • Daily updates to stakeholders     │
        │  └──────────────────────────────────────┘
     90 ┤
        │  ┌──────────────────────────────────────┐
        │  │  HIGH (70-89)                        │
     70 │  │  • Prioritize in current sprint      │
        │  │  • Assign senior engineers           │
        │  │  • Regular progress updates          │
        │  └──────────────────────────────────────┘
        │
        │  ┌──────────────────────────────────────┐
     50 │  │  MEDIUM (50-69)                      │
        │  │  • Schedule in upcoming sprints      │
        │  │  • Standard engineering resources    │
        │  │  • Weekly review                     │
        │  └──────────────────────────────────────┘
     30 ┤
        │  ┌──────────────────────────────────────┐
        │  │  LOW (30-49)                         │
        │  │  • Add to backlog                    │
        │  │  • Address as capacity allows        │
        │  │  • Monthly review                    │
        │  └──────────────────────────────────────┘
        │
        │  ┌──────────────────────────────────────┐
      0 │  │  MINIMAL (0-29)                      │
        │  │  • Consider deferring/closing        │
        │  │  • Quarterly review                  │
        │  └──────────────────────────────────────┘
        ▼
   IMPACT SCORE
```

---

## Real-World Example Scenarios

### Scenario A: Production Outage
```
┌─────────────────────────────────────────────┐
│ VIP Customer Database Completely Down       │
├─────────────────────────────────────────────┤
│ Impact & Severity:    38 (P1 - stopped)     │
│ Customer ARR:         15 (>$1M)             │
│ SLA Breach:            8 (breached)         │
│ Frequency:             0 (first time)       │
│ Workaround:           15 (none available)   │
│ RCA Action Item:       8 (yes)              │
│ Support Multiplier:   15% (blocking release)│
│ Account Multiplier:   15% (renewal at risk) │
├─────────────────────────────────────────────┤
│ BASE SCORE:           84                    │
│ FINAL SCORE:          109.2 → CRITICAL      │
└─────────────────────────────────────────────┘
```

### Scenario B: Performance Degradation
```
┌─────────────────────────────────────────────┐
│ Multiple Small Customers Slow Queries       │
├─────────────────────────────────────────────┤
│ Impact & Severity:    30 (P2 - degraded)    │
│ Customer ARR:          8 (>10 low ARR)      │
│ SLA Breach:            0 (within SLA)       │
│ Frequency:             8 (3 occurrences)    │
│ Workaround:           10 (complex steps)    │
│ RCA Action Item:       0 (no)               │
│ Support Multiplier:    0% (none)            │
│ Account Multiplier:    0% (none)            │
├─────────────────────────────────────────────┤
│ BASE SCORE:           56                    │
│ FINAL SCORE:          56.0 → MEDIUM         │
└─────────────────────────────────────────────┘
```

### Scenario C: Minor Bug
```
┌─────────────────────────────────────────────┐
│ UI Display Issue - Single Customer          │
├─────────────────────────────────────────────┤
│ Impact & Severity:     8 (P5 - info)        │
│ Customer ARR:          0 (single low ARR)   │
│ SLA Breach:            0 (no impact)        │
│ Frequency:             0 (once)             │
│ Workaround:            5 (simple command)   │
│ RCA Action Item:       0 (no)               │
│ Support Multiplier:    0% (none)            │
│ Account Multiplier:    0% (none)            │
├─────────────────────────────────────────────┤
│ BASE SCORE:           13                    │
│ FINAL SCORE:          13.0 → MINIMAL        │
└─────────────────────────────────────────────┘
```

---

## ⚠️ Important Scoring Clarifications

### SLA Breach Component (0 or 8 points)

**Redis Cloud vs ACRE Distinction:**
- This component **ONLY applies to Redis Cloud** (our managed service)
- For **ACRE** (Azure Cache for Redis Enterprise), **always score 0 points**
  - ACRE is Azure's managed service
  - Azure owns the SLA relationship with end customers
  - We don't have direct SLA agreements with ACRE end users

### RCA Action Item Component (0 or 8 points)

**Definition:**
- Score **8 points**: Ticket is a **follow-up action item** from a **previously completed RCA**
  - Example: "Implement monitoring improvements" identified in past incident's RCA
  - Example: "Add validation logic" recommended by previous root cause investigation
- Score **0 points**: Ticket **IS the incident currently under investigation**
  - Even if ticket requests RCA or mentions "need RCA"
  - This is the incident being analyzed, NOT an action item from a prior RCA

**Rule of thumb:** If this ticket is **generating** the RCA (future), score 0. If this ticket was **generated BY** an RCA (past), score 8.

---

