# Jira Helper

A comprehensive Python toolkit for Jira ticket management, impact score calculation, and RCA automation. Features intelligent PDF analysis, automatic ticket creation, and multi-cluster RCA generation.

## 🎯 Features

### **Core Impact Score Calculation**
- **Multi-Format Support**: Process Jira (PDF/Excel/XML/Word) and Zendesk (PDF) exports
- **Intelligent Auto-Estimation**: AI-powered analysis to automatically estimate impact scores
- **Batch Processing**: Calculate scores for multiple tickets at once
- **Interactive Estimation**: Step-by-step wizard for single ticket scoring
- **ACRE & RCA Detection**: Automatic handling of Azure Cache for Redis and RCA action items

### **Jira Ticket Creation & Management**
- **Bug Jira Creation**: Create Jira tickets from Zendesk PDFs with automatic field mapping
- **RCA Ticket Creation**: Generate RCA tickets following your Confluence template
- **Multi-Cluster RCA Support**: Handle complex incidents across multiple clusters and regions
- **Auto-Population**: Automatically fill RCA fields from related bug Jira PDFs
- **PDF Analysis**: Extract timestamps, components, and resolution methods from PDFs

### **Advanced RCA Automation**
- **PDF Summary Generation**: Analyze multiple Zendesk and Jira PDFs to generate comprehensive summaries
- **Cluster-Specific Timestamps**: Extract and organize timestamps for each affected cluster
- **Resolution Method Detection**: Distinguish between manual restarts and automatic VM freeze events
- **Timeline Generation**: Create detailed incident timelines from PDF content
- **Action Item Extraction**: Automatically identify and categorize action items

### **Documentation & Examples**
- **Comprehensive Documentation**: Detailed guides and scoring model reference
- **Example PDFs**: Real-world examples of Zendesk tickets, Jira exports, and RCA templates
- **Generated Examples**: Sample outputs showing the full RCA creation workflow

## 📦 What's Included

### Repository Structure

```
jira-helper/
├── README.md                           # This file
├── CLAUDE.md                           # Claude Code instructions
├── requirements.txt                    # Python dependencies
├── src/                                # Python Scripts (Core Tools)
│   ├── intelligent_estimator.py        # AI-powered auto-estimation (multi-format)
│   ├── universal_ticket_parser.py      # Multi-format parser (PDF/XML/Word)
│   ├── jira_creator.py                 # Jira ticket creation engine
│   ├── create_jira_from_zendesk.py     # Create bug Jiras from Zendesk PDFs
│   ├── create_rca_ticket.py            # Create RCA tickets from template
│   ├── create_multi_cluster_rca.py     # Multi-cluster RCA creation
│   ├── generate_rca_summary.py         # PDF analysis and summary generation
│   ├── generate_complete_rca.py        # Complete RCA with auto-generated content
│   ├── calculate_jira_scores.py        # Batch processor
│   ├── estimate_impact_score.py        # Interactive single-ticket estimator
│   ├── impact_score_calculator.py      # Core calculation library
│   └── jira_impact_score_processor.py  # Batch processing engine
├── docs/                               # Documentation
│   ├── IMPACT_SCORE_MODEL.md           # Scoring model specification
│   ├── IMPACT_SCORE_VISUAL_GUIDE.md    # Visual diagrams and examples
│   ├── INTELLIGENT_ESTIMATOR_GUIDE.md  # AI estimator guide
│   ├── JIRA_PROCESSOR_USER_GUIDE.md    # Batch processor API reference
│   ├── JIRA_CREATION_GUIDE.md          # Jira creation guide
│   ├── ROADMAP.md                      # Project roadmap
│   └── pdfs/                           # Example PDFs and templates
└── examples/                           # Generated examples and outputs
    ├── corrected_rca_description.txt   # Ready-to-use RCA description
    ├── azure_*_rca.json                # Example RCA data files
    └── example_*_ticket.json           # Example ticket data files
```

## 🔄 RCA Automation Workflow

### **Complete RCA Creation Process**

1. **📄 PDF Analysis**: Analyze multiple Zendesk and Jira PDFs to extract key information
2. **🕐 Timestamp Extraction**: Identify start/end times and resolution methods for each cluster
3. **📝 Summary Generation**: Create comprehensive incident summary and timeline
4. **🎯 Root Cause Analysis**: Generate initial root cause analysis based on PDF content
5. **📋 Action Items**: Extract and categorize action items from all sources
6. **🔗 RCA Ticket Creation**: Generate complete RCA ticket with all auto-populated fields

### **Multi-Cluster RCA Example**
```bash
# Generate complete RCA for multi-cluster incident
python src/generate_complete_rca.py \
  --customer "Azure Customer" \
  --date "10/24/2025" \
  --zendesk-pdfs "docs/pdfs/Support Tickets/*.pdf" \
  --jira-pdfs "docs/pdfs/Jiras/*.pdf" \
  --clusters "prod110-europe-hdc-europe-cp102-titan2.northeurope,rediscluster-ktcsproda11.eastus2" \
  --regions "northeurope,eastus2" \
  --components "DMC"
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd jira-helper

# Install dependencies
pip install -r requirements.txt
```

### Usage

#### **RCA Automation (New!)**

```bash
# Create RCA ticket from Zendesk PDFs
python src/create_rca_ticket.py \
  --customer "Azure Customer" \
  --date "10/24/2025" \
  --zendesk-tickets "146983,146173,146404" \
  --related-bugs "RED-172734,RED-172012" \
  --bug-jira-file "docs/pdfs/Jiras/[#RED-172012] Azure_ DMCproxy stuck at High CPU utilisation.pdf"

# Generate complete multi-cluster RCA
python src/generate_complete_rca.py \
  --customer "Azure Customer" \
  --date "10/24/2025" \
  --zendesk-pdfs "docs/pdfs/Support Tickets/*.pdf" \
  --jira-pdfs "docs/pdfs/Jiras/*.pdf" \
  --clusters "prod110-europe-hdc-europe-cp102-titan2.northeurope,rediscluster-ktcsproda11.eastus2" \
  --regions "northeurope,eastus2" \
  --components "DMC"
```

#### **Impact Score Calculation**

##### Option 1: Intelligent Auto-Estimation (Recommended)

```bash
# Analyze Jira PDF export
python src/intelligent_estimator.py RED-12345.pdf

# Analyze Zendesk PDF export
python src/intelligent_estimator.py zendesk_ticket_789.pdf

# Analyze Jira Excel export
python src/intelligent_estimator.py jira_export.xlsx --verbose

# Analyze Jira Word/XML export
python src/intelligent_estimator.py ticket.docx --output scores.json
```

**Supported formats:**
- **Jira**: PDF, Excel (.xlsx), XML, Word (.docx)
- **Zendesk**: PDF

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

#### Option 4: Create Jira Tickets (NEW!)

```bash
# Create bug Jira from Zendesk PDF
python src/create_jira_from_zendesk.py zendesk_ticket.pdf --project RED

# Analyze Zendesk ticket and suggest Jira fields
python src/create_jira_from_zendesk.py zendesk_ticket.pdf --suggest-only

# Create RCA ticket
python src/create_rca_ticket.py --customer "Azure" --date "10/25/25" --zendesk-tickets 131142
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

See [docs/IMPACT_SCORE_MODEL.md](docs/IMPACT_SCORE_MODEL.md) for complete details.

### Quick Reference

| Component | Min | Max | Description |
|-----------|-----|-----|-------------|
| **Impact & Severity** | 8 | 38 | P1=38, P2=30, P3=22, P4=16, P5=8 |
| **Customer ARR** | 0 | 15 | >$1M=15, $500K-$1M=13, $100K-$500K=10 |
| **SLA Breach** | 0 | 8 | Breached=8, OK=0 |
| **Frequency** | 0 | 16 | >4 times=16, 2-4 times=8, 1 time=0 |
| **Workaround** | 5 | 15 | None=15, Complex=10-12, Simple=5 |
| **RCA Action Item** | 0 | 8 | Yes=8, No=0 |
| **BASE SCORE** | **8** | **100** | Sum of above |
| **Multipliers** | 0% | 30% | Support + Account (optional) |
| **FINAL SCORE** | **8** | **130** | Base × (1 + multipliers) |

### Priority Levels

| Score Range | Priority | Action |
|-------------|----------|--------|
| **90-130+** | 🔴 CRITICAL | Immediate attention - escalate |
| **70-89** | 🟠 HIGH | Current sprint priority |
| **50-69** | 🟡 MEDIUM | Upcoming sprint |
| **30-49** | 🟢 LOW | Backlog |
| **0-29** | ⚪ MINIMAL | Defer/close |

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

## 🛠️ Which Tool Should I Use?

### Decision Tree

```
Do you have a Jira export file?
│
├─ YES → Is it a batch export with multiple tickets?
│   │
│   ├─ YES → Use: calculate_jira_scores.py (Batch Processor)
│   │         python src/calculate_jira_scores.py export.xlsx
│   │
│   └─ NO → Single ticket export
│           Use: intelligent_estimator.py (AI Auto-Estimation)
│           python src/intelligent_estimator.py RED-12345.xlsx
│
└─ NO → Manual estimation needed?
          Use: estimate_impact_score.py (Interactive Estimator)
          python src/estimate_impact_score.py --interactive
```

### Tools Comparison

| Tool | Use Case | Input | Output | Best For |
|------|----------|-------|--------|----------|
| **intelligent_estimator.py** | Auto-estimate any ticket | Single Jira XLSX | Console + JSON | Quick analysis of any export |
| **calculate_jira_scores.py** | Batch process many tickets | Batch Jira XLSX | Excel with scores | Regular bulk processing |
| **estimate_impact_score.py** | Manual single ticket | Interactive prompts | Console + JSON | New tickets, validation |

## 📋 Requirements

**Core dependencies:**
- Python 3.8+
- pandas >= 2.0.0
- openpyxl >= 3.1.0

**Multi-format support:**
- pymupdf >= 1.23.0 (PDF extraction)
- python-docx >= 1.1.0 (Word documents)
- lxml >= 5.0.0 (XML parsing)

Install all dependencies:
```bash
pip install -r requirements.txt
```

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

**Essential guides:**
- [docs/IMPACT_SCORE_MODEL.md](docs/IMPACT_SCORE_MODEL.md) - Complete scoring model
- [docs/IMPACT_SCORE_VISUAL_GUIDE.md](docs/IMPACT_SCORE_VISUAL_GUIDE.md) - Visual diagrams and examples
- [docs/ROADMAP.md](docs/ROADMAP.md) - Project roadmap and future plans

**Tool-specific guides:**
- [docs/INTELLIGENT_ESTIMATOR_GUIDE.md](docs/INTELLIGENT_ESTIMATOR_GUIDE.md) - AI estimator detailed guide
- [docs/JIRA_PROCESSOR_USER_GUIDE.md](docs/JIRA_PROCESSOR_USER_GUIDE.md) - Batch processor API reference

**For contributors:**
- [CLAUDE.md](CLAUDE.md) - Project-specific Claude Code instructions

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
# Testing GitHub account selection - 12:03:25
# Testing SSH authentication - 12:04:27
