# Jira Impact Score Calculator Toolkit

A comprehensive Python toolkit for calculating and estimating Jira ticket impact scores based on multiple factors including severity, customer ARR, frequency, workarounds, and more.

## 🎯 Features

- **Intelligent Auto-Estimation**: AI-powered analysis of Jira exports to automatically estimate impact scores
- **Batch Processing**: Calculate scores for multiple tickets at once
- **Interactive Estimation**: Step-by-step wizard for single ticket scoring
- **Zendesk Integration**: Convert Zendesk tickets to Jira-importable formats
- **Comprehensive Documentation**: Detailed guides and scoring model reference

## 📦 What's Included

### Repository Structure

```
impact-score-calculator/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── src/                        # Python scripts
│   ├── intelligent_estimator.py
│   ├── calculate_jira_scores.py
│   ├── estimate_impact_score.py
│   ├── impact_score_calculator.py
│   └── jira_impact_score_processor.py
└── docs/                       # Documentation
    ├── USER_GUIDE.md           # Complete user guide (ALL tools)
    ├── CLAUDE.md               # Claude Code instructions
    ├── ROADMAP.md              # Project roadmap
    ├── Impact_Score_Model.md   # Scoring model specification
    ├── QUICK_REFERENCE.md      # Quick reference card
    └── ... (additional guides)
```

### Python Scripts (`src/`)
- `intelligent_estimator.py` - AI-powered automatic estimation from any Jira XLSX
- `calculate_jira_scores.py` - Batch processor for multiple tickets
- `estimate_impact_score.py` - Interactive estimator for single tickets
- `impact_score_calculator.py` - Core calculation library
- `jira_impact_score_processor.py` - Batch processing engine

### Documentation (`docs/`)
- **[USER_GUIDE.md](docs/USER_GUIDE.md)** - **START HERE!** Complete guide for all tools
- [CLAUDE.md](docs/CLAUDE.md) - Project-specific Claude Code instructions
- [ROADMAP.md](docs/ROADMAP.md) - Project roadmap and future plans
- [Impact_Score_Model.md](docs/Impact_Score_Model.md) - Complete scoring model
- [QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) - Quick reference card

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd jira-impact-score-toolkit

# Install dependencies
pip install -r requirements.txt
```

### Usage

#### Option 1: Intelligent Auto-Estimation (Recommended)

```bash
# Analyze any Jira ticket export - AI estimates all components!
python src/intelligent_estimator.py RED-12345_Export.xlsx

# With detailed output
python src/intelligent_estimator.py ticket.xlsx --verbose

# Save to JSON
python src/intelligent_estimator.py ticket.xlsx --output results.json
```

#### Option 2: Batch Processing

```bash
# Process multiple tickets
python src/calculate_jira_scores.py your_jira_export.xlsx

# Show top tickets and validate
python src/calculate_jira_scores.py tickets.xlsx --top 20 --validate
```

#### Option 3: Interactive Single Ticket

```bash
# Interactive mode - prompts for each component
python src/estimate_impact_score.py --interactive
```

## 📊 Impact Score Model

The impact score is calculated from **6 components**:

1. **Impact & Severity (0-38 points)**: Based on priority/severity level
2. **Customer ARR (0-15 points)**: Annual recurring revenue of affected customer(s)
3. **SLA Breach (0 or 8 points)**: Whether SLA was breached
4. **Frequency (0-16 points)**: How often the issue occurs
5. **Workaround (5-15 points)**: Availability and complexity of workarounds
6. **RCA Action Item (0 or 8 points)**: Whether this is part of an RCA

**Plus optional multipliers** for support blocking and account risk.

See `Impact_Score_Model.md` for complete details.

## 🎓 Examples

### Example 1: Auto-Estimate from Jira Export

```bash
python src/intelligent_estimator.py RED-172041_Export.xlsx
```

**Output:**
```
FINAL IMPACT SCORE: 62.0 points
PRIORITY LEVEL: MEDIUM

Component Breakdown:
1. Impact & Severity: 16 points
   → Monitoring/metrics issue with service functioning normally (P4)
2. Customer ARR: 10 points
   → Customer mentioned but ARR unknown
3. SLA Breach: 0 points
   → No SLA breach (service confirmed stable/functional)
4. Frequency: 16 points
   → Multiple occurrence keyword 'multiple' found
5. Workaround: 12 points
   → Workaround with performance/operational impact detected
6. RCA Action Item: 8 points
   → RCA field contains substantial content
```

### Example 2: Batch Processing

```bash
python src/calculate_jira_scores.py tickets_export.xlsx --top 10
```

Creates `jira_impact_scores_processed.xlsx` with calculated scores.

### Example 3: Interactive Single Ticket

```bash
python src/estimate_impact_score.py --interactive
```

Walks you through each component with prompts.

## 🛠️ Tools Comparison

| Tool | Use Case | Input | Output |
|------|----------|-------|--------|
| `src/intelligent_estimator.py` | Auto-estimate any ticket | Single Jira XLSX | Console + JSON |
| `src/calculate_jira_scores.py` | Batch process many tickets | Batch Jira XLSX | Excel with scores |
| `src/estimate_impact_score.py` | Manual single ticket | Interactive prompts | Console + JSON |

See [docs/USER_GUIDE.md](docs/USER_GUIDE.md) for complete guide.

## 📋 Requirements

- Python 3.8+
- pandas >= 2.0.0
- openpyxl >= 3.1.0

## 🔧 Configuration

### Customize VIP Customers

Edit `src/intelligent_estimator.py`:

```python
VIP_CUSTOMERS = [
    'monday.com', 'salesforce', 'your-customer-name'
]
```

### Adjust Keywords

Modify keyword dictionaries in `src/intelligent_estimator.py`:

```python
WORKAROUND_KEYWORDS = {
    'with_impact': ['inconvenient', 'hard-coded', 'your-keyword'],
    # ...
}
```

## 📚 Documentation

**Start here:**
- **[docs/USER_GUIDE.md](docs/USER_GUIDE.md)** - Complete guide for all tools (recommended!)

**Reference docs:**
- [docs/Impact_Score_Model.md](docs/Impact_Score_Model.md) - Complete scoring model
- [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) - Quick reference card
- [docs/ROADMAP.md](docs/ROADMAP.md) - Project roadmap and future plans

**For contributors:**
- [docs/CLAUDE.md](docs/CLAUDE.md) - Project-specific Claude Code instructions

## 🐛 Known Limitations

1. **Customer ARR**: Script estimates based on keywords, manual input recommended
2. **RCA Detection**: May flag RCA template as actual RCA content
3. **Frequency**: Relies on keyword detection, may need manual adjustment
4. **Single Ticket Focus**: Intelligent estimator processes one ticket at a time

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- Add support for more Jira field types
- Improve ARR estimation with external data sources
- Add ML-based component prediction
- Create GUI interface
- Add API endpoint wrapper

## 📝 License

[Add your license here]

## 🙏 Acknowledgments

Built with insights from real Jira impact scoring workflows. Special thanks to teams using Redis Cloud support ticketing systems.

## 📧 Support

For questions or issues:
- Open an issue in this repository
- Check the documentation in `/docs`
- Review examples in `/examples`

## 🔄 Recent Updates

**October 14, 2025:**
- ✅ Enhanced workaround detection for operational impact (12 pts)
- ✅ Improved P4 detection for monitoring/metrics issues (16 pts)
- ✅ Better SLA breach detection to avoid false positives
- ✅ See `SCRIPT_UPDATE_LOG.md` for details

## 🗺️ Roadmap

- [ ] Web-based UI
- [ ] API endpoint
- [ ] Integration with Jira API (direct import/export)
- [ ] Machine learning model for automated scoring
- [ ] Custom field mapping configuration
- [ ] Multi-language support

---

**Made with ❤️ for better Jira impact scoring**
