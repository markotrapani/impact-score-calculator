# Jira Impact Score Processor - User Guide

## Overview

The Jira Impact Score Processor is a Python tool that automatically calculates and validates impact scores for Jira tickets exported to Excel. It processes your Jira exports, calculates priority scores, and generates reports to help with ticket prioritization.

## Features

✅ **Automatic Score Calculation** - Processes Excel exports and calculates impact scores using the standard formula  
✅ **Flexible Column Mapping** - Handles various Excel export formats and column names  
✅ **Score Validation** - Validates calculated scores against existing scores  
✅ **Priority Classification** - Automatically categorizes tickets (CRITICAL, HIGH, MEDIUM, LOW, MINIMAL)  
✅ **Summary Statistics** - Provides insights into your ticket backlog  
✅ **Export Capabilities** - Generates processed Excel files with scores and priorities  

## Quick Start

### 1. Basic Usage

```python
from jira_impact_score_processor import JiraImpactScoreProcessor

# Initialize with your Jira Excel export
processor = JiraImpactScoreProcessor('your_jira_export.xlsx')

# Load and process
processor.load_data()
processor.calculate_scores()

# Get top priorities
top_tickets = processor.get_top_priorities(n=10)
print(top_tickets)

# Export results
processor.export_results('processed_output.xlsx')
```

### 2. Command-Line Usage

```bash
python jira_impact_score_processor.py
```

## Expected Excel Format

The processor expects an Excel file with the following columns (in any order):

### Required Columns:
- **Jira** / Jira ID / Issue Key - Ticket identifier
- **Impact & Severity** - Score 0-38
- **Customer ARR** - Score 0-15
- **SLA Breach** - Score 0 or 8
- **Frequency** - Score 0-16
- **Workaround** - Score 5-15
- **RCA Action Item** - Score 0 or 8

### Optional Columns:
- **Support Multiplier** - 0 to 0.15 (0-15%)
- **Account Multiplier** - 0 to 0.15 (0-15%)
- **Last Update** - Timestamp
- **Person** / Assignee - Person assigned

### Example Excel Structure:

| Jira | Impact & Severity | Customer ARR | SLA Breach | Frequency | Workaround | RCA Action Item | Support Multiplier | Account Multiplier | Person |
|------|------------------|--------------|------------|-----------|------------|-----------------|-------------------|-------------------|--------|
| RED-12345 | 38 | 15 | 8 | 16 | 15 | 8 | 0.15 | 0.15 | John Doe |
| MOD-67890 | 30 | 10 | 0 | 0 | 10 | 8 | 0 | 0 | Jane Smith |

## API Reference

### JiraImpactScoreProcessor Class

#### `__init__(excel_path: str)`
Initialize the processor with a Jira Excel export.

```python
processor = JiraImpactScoreProcessor('jira_export.xlsx')
```

#### `load_data(sheet_name: str = 'Calculation') -> pd.DataFrame`
Load data from the Excel file.

```python
df = processor.load_data(sheet_name='Calculation')
```

#### `calculate_scores() -> pd.DataFrame`
Calculate impact scores for all tickets.

```python
results = processor.calculate_scores()
```

#### `get_summary_stats() -> Dict`
Get summary statistics of processed tickets.

```python
stats = processor.get_summary_stats()
# Returns: {
#     'total_tickets': 332,
#     'average_score': 59.3,
#     'median_score': 60.0,
#     'max_score': 106.1,
#     'min_score': 13.0,
#     'priority_distribution': {...},
#     'tickets_by_priority': {...}
# }
```

#### `get_top_priorities(n: int = 10) -> pd.DataFrame`
Get top N highest priority tickets.

```python
top_10 = processor.get_top_priorities(n=10)
```

#### `export_results(output_path: str, include_all_columns: bool = True)`
Export processed results to Excel.

```python
processor.export_results('output.xlsx', include_all_columns=True)
```

#### `validate_scores(tolerance: float = 0.1) -> Tuple[bool, List[str]]`
Validate calculated scores against existing scores.

```python
is_valid, discrepancies = processor.validate_scores(tolerance=0.1)
if not is_valid:
    for disc in discrepancies:
        print(disc)
```

## Priority Classification

The processor automatically classifies tickets based on their impact score:

| Score Range | Priority | Action Required |
|-------------|----------|-----------------|
| 90-130+ | **CRITICAL** | Immediate attention required |
| 70-89 | **HIGH** | Prioritize in current sprint |
| 50-69 | **MEDIUM** | Schedule in upcoming sprints |
| 30-49 | **LOW** | Backlog, address as capacity allows |
| 0-29 | **MINIMAL** | Defer or close |

## Advanced Usage Examples

### Example 1: Batch Processing Multiple Files

```python
import glob
from jira_impact_score_processor import JiraImpactScoreProcessor

# Process all Excel files in a directory
for file_path in glob.glob('jira_exports/*.xlsx'):
    print(f"Processing {file_path}...")
    processor = JiraImpactScoreProcessor(file_path)
    processor.load_data()
    processor.calculate_scores()
    
    output_name = file_path.replace('.xlsx', '_processed.xlsx')
    processor.export_results(output_name)
```

### Example 2: Filter and Report Critical Tickets

```python
processor = JiraImpactScoreProcessor('jira_export.xlsx')
processor.load_data()
results = processor.calculate_scores()

# Get only critical tickets
critical = results[results['priority_level'] == 'CRITICAL']

print(f"Found {len(critical)} critical tickets:")
for idx, row in critical.iterrows():
    print(f"  {row['jira']}: Score={row['calculated_impact_score']:.1f}")
```

### Example 3: Custom Analysis

```python
processor = JiraImpactScoreProcessor('jira_export.xlsx')
processor.load_data()
results = processor.calculate_scores()

# Analyze by assignee
assignee_stats = results.groupby('person').agg({
    'calculated_impact_score': ['count', 'mean', 'max'],
    'priority_level': lambda x: x.value_counts().to_dict()
})

print(assignee_stats)
```

### Example 4: Export Only High Priority Tickets

```python
processor = JiraImpactScoreProcessor('jira_export.xlsx')
processor.load_data()
results = processor.calculate_scores()

# Filter high and critical
high_priority = results[results['calculated_impact_score'] >= 70]

# Export filtered results
high_priority.to_excel('high_priority_tickets.xlsx', index=False)
```

## Troubleshooting

### Issue: Column names not recognized

**Solution:** The processor includes flexible column mapping. If your export has different column names, they should still be recognized. Supported variations include:

- Jira: `Jira`, `jira`, `Jira ID`, `Issue Key`, `Key`
- Impact & Severity: `Impact & Severity\nMax 38`, `Impact & Severity`, `Severity`, `Impact`
- etc.

### Issue: Missing data / NaN values

**Solution:** The processor automatically fills missing numeric values with 0. Ensure required columns are present.

### Issue: Score discrepancies

**Solution:** Use the `validate_scores()` method to identify discrepancies:

```python
is_valid, discrepancies = processor.validate_scores(tolerance=0.1)
for disc in discrepancies:
    print(disc)
```

### Issue: Import errors

**Solution:** Ensure required packages are installed:

```bash
pip install pandas openpyxl numpy --break-system-packages
```

## Output Format

The processed Excel file includes all original columns plus:

- **calculated_impact_score** - The computed impact score
- **priority_level** - Classification (CRITICAL, HIGH, MEDIUM, LOW, MINIMAL)

Tickets are automatically sorted by impact score (highest to lowest).

## Real-World Example Output

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
   MOD-9262: Score=106.1 (CRITICAL) - M Thompson
   RED-164431: Score=100.8 (CRITICAL) - Prakash
   RED-168233: Score=100.1 (CRITICAL) - Prakash Selvaraj
   MOD-10006: Score=100.0 (CRITICAL) - Jeff G
   RED-166789: Score=99.5 (CRITICAL) - Sarah Chen

6. Exporting results...
✓ Results exported to jira_impact_scores_processed.xlsx
```

## Integration Tips

### With Jira Automation
Export your Jira tickets to Excel on a regular schedule, then run this processor to maintain up-to-date priority scores.

### With BI Tools
Import the processed Excel into Tableau, Power BI, or similar tools for advanced visualization and reporting.

### With CI/CD
Integrate into your pipeline to automatically validate impact scores when tickets are updated.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the API reference
3. Examine the example code
4. Validate your Excel format matches expected structure
