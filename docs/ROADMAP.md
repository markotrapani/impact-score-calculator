# Impact Score Calculator - Roadmap

## Project Overview

A Python toolkit for calculating Jira ticket impact scores based on severity, customer ARR, frequency, workarounds, and other factors. Used for prioritizing Redis Cloud support tickets.

---

## ✅ Completed Features

### Core Functionality (v1.0)
- [x] Impact score calculation engine with 6 components
- [x] Batch processing of Jira exports (Excel)
- [x] Interactive single-ticket estimation
- [x] Comprehensive scoring model (0-100+ points)
- [x] Core Python library (`impact_score_calculator.py`)

### Intelligent Estimator (v1.1 - October 2025)
- [x] AI-powered automatic estimation from Jira exports
- [x] Keyword-based component detection
- [x] VIP customer recognition
- [x] Workaround complexity detection
- [x] RCA action item identification
- [x] SLA breach detection
- [x] Frequency analysis from ticket content
- [x] JSON output support
- [x] Verbose logging mode

### Documentation (v1.2 - October 2025)
- [x] Complete user guides for all tools
- [x] Impact score model specification
- [x] Visual guides and diagrams
- [x] Tool selection guide
- [x] Quick reference card
- [x] Script update log

### Repository Setup (Current)
- [x] Git repository initialization
- [x] GitHub repository creation
- [x] Basic .gitignore configuration
- [x] Requirements.txt for dependencies
- [x] Comprehensive README

---

## 🚧 In Progress

### Repository Migration
- [ ] Convert to git submodule of marko-projects
- [ ] Create CLAUDE.md with project-specific instructions
- [ ] Clean up obsolete git setup documentation
- [ ] Add to parent repository's CLAUDE.md

---

## 🎯 Short-Term Roadmap (Next 1-3 months)

### Code Quality & Testing
- [ ] Add unit tests for core calculator
- [ ] Add integration tests for intelligent estimator
- [ ] Set up pytest configuration
- [ ] Add code coverage reporting
- [ ] Implement error handling improvements
- [ ] Add input validation for all scripts

### Feature Enhancements
- [ ] Batch mode for intelligent estimator (process multiple tickets)
- [ ] CSV output format support
- [ ] Custom configuration file support (YAML/JSON)
- [ ] Configurable keyword dictionaries (external file)
- [ ] ARR estimation improvement with external data sources
- [ ] Support for custom Jira field mapping

### Documentation Improvements
- [ ] Add usage examples with sample data
- [ ] Create troubleshooting guide
- [ ] Add API reference documentation
- [ ] Create video walkthrough/tutorial
- [ ] Add contribution guidelines

---

## 🚀 Medium-Term Roadmap (3-6 months)

### Integration & Automation
- [ ] Direct Jira API integration (no Excel export needed)
- [ ] Automatic score updates in Jira custom fields
- [ ] Webhook support for real-time scoring
- [ ] Zendesk API direct integration
- [ ] Slack notifications for high-impact tickets

### Machine Learning
- [ ] ML model training on historical ticket data
- [ ] Improved ARR prediction using ML
- [ ] Automatic component weight optimization
- [ ] Pattern recognition for similar tickets
- [ ] Confidence scoring for automated estimates

### User Interface
- [ ] Command-line TUI (text user interface) with rich/textual
- [ ] Web-based dashboard (Flask/FastAPI backend)
- [ ] Interactive visualization of score breakdowns
- [ ] Bulk edit/review interface
- [ ] Configuration GUI

---

## 🌟 Long-Term Vision (6+ months)

### Enterprise Features
- [ ] Multi-tenant support
- [ ] Role-based access control
- [ ] Audit logging
- [ ] Custom scoring models per team/product
- [ ] Integration with ServiceNow, Monday.com, etc.
- [ ] RESTful API with authentication

### Advanced Analytics
- [ ] Historical trend analysis
- [ ] Impact score predictions
- [ ] Team performance metrics
- [ ] Customer impact heatmaps
- [ ] Automated reporting and dashboards

### Platform Expansion
- [ ] Docker containerization
- [ ] Cloud deployment (AWS Lambda, GCP Cloud Functions)
- [ ] SaaS offering
- [ ] Mobile app for on-the-go scoring
- [ ] Browser extension for inline Jira scoring

---

## 🐛 Known Issues & Technical Debt

### Current Limitations
1. **Customer ARR Detection**: Keyword-based, not always accurate
2. **RCA Template Detection**: May flag empty RCA templates as content
3. **Frequency Detection**: Relies on keywords, may miss context
4. **Single-Ticket Mode**: Intelligent estimator processes one at a time
5. **No Batch Undo**: Cannot easily revert batch score updates

### Technical Debt
- [ ] Refactor keyword dictionaries into configuration files
- [ ] Consolidate duplicate code between scripts
- [ ] Improve error messages and logging
- [ ] Add type hints throughout codebase
- [ ] Optimize pandas operations for large datasets
- [ ] Standardize output formats across all tools

---

## 📊 Success Metrics

### Current Usage (Baseline - October 2025)
- Tools created: 3 main scripts
- Components tracked: 6
- Documentation files: 10+
- Lines of code: ~2,000

### Target Metrics (6 months)
- Test coverage: >80%
- Processing speed: <1 second per ticket
- Estimation accuracy: >90% (compared to manual scoring)
- User adoption: 10+ active users
- Documentation completeness: 100% API coverage

---

## 🤝 Contributing

Want to contribute? Priority areas:
1. **Testing**: Unit tests, integration tests
2. **ML Model**: Training data collection, model development
3. **Jira Integration**: Direct API support
4. **Documentation**: Examples, tutorials, API docs
5. **UI Development**: Web dashboard, CLI improvements

---

## 📝 Version History

| Version | Date | Highlights |
|---------|------|------------|
| v1.2 | Oct 2025 | Repository setup, documentation cleanup |
| v1.1 | Oct 2025 | Intelligent estimator enhancements |
| v1.0 | Oct 2025 | Initial release with all core tools |

---

## 📧 Feedback

Have ideas for new features or improvements? Open an issue or submit a PR!

**Last Updated**: October 15, 2025
