# CLAUDE.md - Impact Score Calculator

## Project Overview

**Impact Score Calculator** is a Python toolkit for calculating Jira ticket impact scores used in Redis Cloud support operations. It automates the scoring of support tickets based on severity, customer ARR, frequency, workarounds, SLA breaches, and RCA action items.

**GitHub Repository**: [https://github.com/markotrapani/impact-score-calculator](https://github.com/markotrapani/impact-score-calculator)

**Parent Repository**: Part of [marko-projects](https://github.com/markotrapani/marko-projects) as a git submodule

---

## 🎯 Project Purpose

This toolkit helps prioritize Redis Cloud support tickets by:
- Automatically analyzing Jira ticket exports
- Calculating impact scores (0-100+ points) based on 6 key components
- Providing batch processing for multiple tickets
- Offering interactive estimation for single tickets

**Primary Use Case**: Redis Cloud Customer Success team ticket prioritization

---

## 📁 Project Structure

```
impact-score-calculator/
├── README.md                           # Main project documentation
├── CLAUDE.md                          # This file - Claude Code instructions
├── ROADMAP.md                         # Project roadmap and future plans
├── requirements.txt                    # Python dependencies
├── .gitignore                         # Git ignore rules
│
├── Python Scripts (Core Tools)
├── intelligent_estimator.py           # AI-powered auto-estimation (primary tool)
├── calculate_jira_scores.py           # Batch processor
├── estimate_impact_score.py           # Interactive single-ticket estimator
├── impact_score_calculator.py         # Core calculation library
├── jira_impact_score_processor.py     # Batch processing engine
│
└── Documentation
    ├── INTELLIGENT_ESTIMATOR_GUIDE.md
    ├── Impact_Score_Model.md
    ├── Impact_Score_Visual_Guide.md
    ├── JIRA_PROCESSOR_USER_GUIDE.md
    ├── ESTIMATOR_GUIDE.md
    ├── TOOL_SELECTION_GUIDE.md
    ├── QUICK_REFERENCE.md
    └── SCRIPT_UPDATE_LOG.md
```

---

## 🛠️ Technology Stack

- **Language**: Python 3.8+
- **Key Libraries**:
  - `pandas` (>= 2.0.0) - Data processing
  - `openpyxl` (>= 3.1.0) - Excel file handling
  - `pymupdf` (>= 1.23.0) - PDF extraction
  - `python-docx` (>= 1.1.0) - Word document support
  - `lxml` (>= 5.0.0) - XML parsing
- **Supported Input Formats**:
  - **Jira**: PDF, Excel (.xlsx), XML, Word (.docx)
  - **Zendesk**: PDF
- **Output Formats**: Console, JSON, Excel

---

## 🎓 How It Works

### Impact Score Components (6 Total)

1. **Impact & Severity** (0-38 points): Based on Jira priority/severity
2. **Customer ARR** (0-15 points): Annual recurring revenue of affected customer
3. **SLA Breach** (0 or 8 points): Whether SLA was breached
4. **Frequency** (0-16 points): How often the issue occurs
5. **Workaround** (5-15 points): Availability and complexity of workarounds
6. **RCA Action Item** (0 or 8 points): Whether ticket is part of RCA follow-up

**Optional Multipliers**:
- Support blocking: 1.0-1.5x
- Account risk: 1.0-2.0x

**Total Score Range**: 0-100+ points

See [Impact_Score_Model.md](Impact_Score_Model.md) for complete details.

---

## 🚀 Common Development Tasks

### Adding New Features

When adding features, consider:
1. **Which script needs modification**: Most new features go in `intelligent_estimator.py`
2. **Update documentation**: Modify relevant .md files
3. **Update ROADMAP.md**: Mark features as completed
4. **Test with sample data**: Use real Jira exports (anonymized)

### Modifying Scoring Logic

Core scoring logic is in:
- `impact_score_calculator.py` - Core calculation functions
- `intelligent_estimator.py` - Automatic estimation logic (keywords, detection)

**Important**: Keep scoring logic consistent across all three tools!

**⚠️ CRITICAL: Scoring Model Documentation Sync**

When modifying scoring rules or clarifications:
1. **Update BOTH documentation files:**
   - `docs/IMPACT_SCORE_MODEL.md` - Complete scoring specification
   - `docs/IMPACT_SCORE_VISUAL_GUIDE.md` - Quick reference tables and examples
2. **Keep them in sync:** Any change to scoring logic, thresholds, or clarifications MUST be reflected in both files
3. **Recent example:** SLA Breach and RCA Action Item clarifications (Oct 2025)
   - Added ACRE exception to SLA Breach (always 0 for ACRE)
   - Clarified RCA Action Item definition (past RCA follow-up vs current incident)

### Adding New Keywords

Keywords are defined in `intelligent_estimator.py`:
```python
WORKAROUND_KEYWORDS = {
    'with_impact': [...],
    'no_workaround': [...],
    # etc.
}
```

Update these dictionaries when improving detection accuracy.

### Testing

Currently **no automated tests** (see ROADMAP.md). When testing:
1. Use real Jira exports (anonymized)
2. Test all three tools for consistency
3. Verify score breakdowns match expected values
4. Check edge cases (missing fields, unusual values)

---

## 📝 Documentation Guidelines

### When to Update Documentation

Update docs when:
- Adding/removing features
- Changing scoring logic
- Modifying keyword detection
- Adding new output formats
- Changing script behavior

### Key Documentation Files

- **README.md**: High-level overview, quick start, examples
- **INTELLIGENT_ESTIMATOR_GUIDE.md**: Detailed guide for main tool
- **Impact_Score_Model.md**: Scoring algorithm specification
- **ROADMAP.md**: Feature status, future plans
- **SCRIPT_UPDATE_LOG.md**: Recent changes and improvements

### Documentation Style

- Use clear, concise language
- Include code examples
- Add tables for comparisons
- Use emoji for visual hierarchy (✅ ⚠️ 🎯 etc.)
- Keep examples realistic and practical

---

## 🐛 Known Issues & Limitations

See [ROADMAP.md](ROADMAP.md) "Known Issues & Technical Debt" section.

**Key limitations**:
1. ARR detection is keyword-based (not always accurate)
2. RCA templates may be falsely detected as actual RCA content
3. Frequency relies on keywords (may miss contextual indicators)
4. Intelligent estimator processes one ticket at a time (no batch mode yet)

---

## 🎯 Current Development Priorities

See [ROADMAP.md](ROADMAP.md) for full roadmap.

**High Priority**:
1. Add unit tests and integration tests
2. Implement batch mode for intelligent estimator
3. Create configuration file support (YAML/JSON)
4. Improve ARR detection accuracy

**Medium Priority**:
1. Direct Jira API integration
2. Web-based UI
3. ML-based scoring improvements

---

## 🤝 Code Review Guidelines

When reviewing changes:
1. **Consistency**: Ensure scoring logic matches across all tools
2. **Documentation**: All new features should update relevant docs
3. **Testing**: Manually test with sample Jira exports
4. **Keywords**: Verify new keywords don't create false positives
5. **Edge cases**: Check behavior with missing/unusual data

---

## 📦 Dependencies

Current dependencies in `requirements.txt`:
```
pandas>=2.0.0
openpyxl>=3.1.0
```

**When adding dependencies**:
- Justify the need (avoid bloat)
- Update requirements.txt
- Update README.md if user-facing
- Test installation on fresh environment

---

## 🔄 Git Workflow

This project follows the parent repository's git workflow (see parent [CLAUDE.md](../CLAUDE.md)):
- Never commit/push without explicit user permission
- Use conventional commit format (feat:, fix:, docs:, etc.)
- Include Claude Code attribution footer
- Ask before creating PRs

---

## 🧪 Sample Data

**⚠️ IMPORTANT**: Never commit real customer data!

Sample Jira exports should:
- Use anonymized customer names
- Use realistic but fake ARR values
- Preserve field structure for testing
- Be added to `.gitignore` if they contain any real data

---

## 📚 Additional Resources

- [Jira Cloud API Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [pandas Documentation](https://pandas.pydata.org/docs/)
- [openpyxl Documentation](https://openpyxl.readthedocs.io/)

---

## 🎓 Claude Code Usage Tips

### Useful Prompts

**"Add a new keyword to workaround detection"**
→ Claude will update WORKAROUND_KEYWORDS dict in intelligent_estimator.py

**"Test the intelligent estimator with sample data"**
→ Claude will run the script and show results

**"Improve ARR detection accuracy"**
→ Claude will analyze keyword logic and suggest improvements

**"Add unit tests for core calculator"**
→ Claude will create test files and test cases

### What Claude Should Know

- This is a **production tool** used by Redis Cloud CS team
- Scoring accuracy is critical (affects ticket prioritization)
- Changes should be **backward compatible** with existing Jira exports
- Documentation is important (multiple users reference guides)

---

## 📧 Questions?

For questions about:
- **Scoring logic**: See [Impact_Score_Model.md](Impact_Score_Model.md)
- **Tool usage**: See individual guide files
- **Development**: See [ROADMAP.md](ROADMAP.md)
- **Project setup**: See [README.md](README.md)

---

**Last Updated**: October 15, 2025
