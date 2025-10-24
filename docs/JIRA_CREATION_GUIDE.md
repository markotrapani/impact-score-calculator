# Jira Creation Guide

## 🎯 Overview

The Impact Score Calculator now supports **creating Jira tickets** from Zendesk tickets and RCA templates, with automatic impact score calculation and proper field mapping.

## 🚀 New Capabilities

### **1. Bug Jira Creation from Zendesk**
- ✅ **Parse Zendesk PDFs** and extract ticket information
- ✅ **Calculate impact scores** using AI-powered analysis
- ✅ **Map fields** to Jira format (project, priority, severity, labels)
- ✅ **Extract cache info** (name, region) from descriptions
- ✅ **Suggest components** and environment details
- ✅ **Generate descriptions** with Zendesk links and impact scores

### **2. RCA Ticket Creation**
- ✅ **Template-based creation** following your Confluence process
- ✅ **Link related tickets** (Zendesk IDs, bug Jiras)
- ✅ **Auto-generate fields** (customer name, dates, Slack channels)
- ✅ **Structured descriptions** with action item tables
- ✅ **Proper labeling** and project assignment

---

## 🛠️ New Tools

### **1. `create_jira_from_zendesk.py`** - Bug Ticket Creator
```bash
# Analyze Zendesk ticket and suggest Jira fields
python src/create_jira_from_zendesk.py zendesk_ticket.pdf --suggest-only

# Create bug Jira ticket data
python src/create_jira_from_zendesk.py zendesk_ticket.pdf --project RED

# Save to JSON for automation
python src/create_jira_from_zendesk.py ticket.pdf --output ticket_data.json
```

### **2. `create_rca_ticket.py`** - RCA Ticket Creator
```bash
# Create RCA ticket
python src/create_rca_ticket.py --customer "Azure" --date "10/25/25"

# Link related tickets
python src/create_rca_ticket.py --customer "Customer Name" --date "10/25/25" \
  --zendesk-tickets 131142 131143 --related-bugs RED-172012 MOD-12345

# Save to JSON
python src/create_rca_ticket.py --customer "Azure" --date "10/25/25" --output rca_data.json
```

### **3. `jira_creator.py`** - Core Creation Engine
```python
from jira_creator import JiraCreator

# Create bug from Zendesk
creator = JiraCreator()
bug_data = creator.create_bug_from_zendesk("ticket.pdf", project="RED")

# Create RCA ticket
rca_data = creator.create_rca_ticket(
    customer_name="Azure",
    date="10/25/25",
    zendesk_tickets=["131142"],
    related_bugs=["RED-172012"]
)
```

---

## 📊 Field Mapping

### **Bug Ticket Fields**

| Zendesk Field | Jira Field | Mapping Logic |
|---------------|------------|---------------|
| **Subject** | Summary | Direct mapping |
| **Description** | Description | Enhanced with impact score |
| **Priority** | Priority | Mapped via impact score |
| **Customer** | Labels | Added as label |
| **Ticket ID** | Custom Field | Zendesk ID field |
| **Cache Info** | Custom Fields | Extracted from description |
| **Impact Score** | Custom Field | Calculated automatically |

### **RCA Ticket Fields**

| Template Field | Jira Field | Auto-Generated |
|----------------|------------|----------------|
| **Customer Name** | Summary | From parameter |
| **Date** | Summary | From parameter |
| **Zendesk Tickets** | Custom Field | From parameters |
| **Slack Channel** | Custom Field | Auto-generated |
| **Related Bugs** | Linked Issues | From parameters |
| **Action Items** | Description | Template table |

---

## 🎯 Usage Examples

### **Example 1: Analyze Zendesk Ticket**
```bash
python src/create_jira_from_zendesk.py customer_issue.pdf --suggest-only --verbose
```

**Output:**
```
ZENDESK TICKET ANALYSIS
Zendesk ID: 131142
Summary: DMC stuck at High CPU utilisation
Impact Score: 61.0
Priority Level: MEDIUM

Component Breakdown:
  Impact Severity: 30 points (Priority 'high' indicates 30 points)
  Customer ARR: 0 points (No customer information found)
  SLA Breach: 0 points (ACRE detected - Azure owns SLA)
  Frequency: 16 points (Multiple occurrences mentioned)
  Workaround: 15 points (Fix/patch required, no workaround)
  RCA Action Item: 0 points (No RCA action item indicators)

SUGGESTED JIRA FIELDS
Project: RED
Issue Type: Bug
Priority: Medium
Severity: Medium
Labels: Support, Customer-Reported, ACRE, Azure-Integration
Component: DMC
Environment: Production
```

### **Example 2: Create Bug Jira**
```bash
python src/create_jira_from_zendesk.py ticket.pdf --project RED --output bug_data.json
```

**Generated Jira Fields:**
```json
{
  "project": "RED",
  "issue_type": "Bug",
  "summary": "DMC stuck at High CPU utilisation",
  "priority": "Medium",
  "severity": "Medium",
  "labels": ["Support", "Customer-Reported", "ACRE", "Azure-Integration"],
  "custom_fields": {
    "impact_score": 61.0,
    "zendesk_id": "131142",
    "cache_name": "rediscluster-ktcsproda11",
    "region": "eastus2",
    "component": "DMC",
    "environment": "Production"
  }
}
```

### **Example 3: Create RCA Ticket**
```bash
python src/create_rca_ticket.py --customer "Azure" --date "10/25/25" \
  --zendesk-tickets 131142 131143 --related-bugs RED-172012
```

**Generated RCA Fields:**
```json
{
  "project": "Root Cause Analysis",
  "issue_type": "RCA",
  "summary": "Azure - RCA 10/25/25",
  "priority": "Medium",
  "labels": ["Azure"],
  "custom_fields": {
    "zendesk_tickets": ["131142", "131143"],
    "slack_channel": "#prod-102525-azure",
    "initial_root_cause": "<Add your initial RCA here>",
    "final_root_cause": "<Add your final RCA and Conclusions here>"
  },
  "linked_issues": ["RED-172012"]
}
```

---

## 🔧 Configuration

### **Project Mappings**
```python
PROJECT_MAPPINGS = {
    'redis': 'RED',
    'modules': 'MOD', 
    'documentation': 'DOC',
    'rdi': 'RDSC',
    'rca': 'Root Cause Analysis'
}
```

### **Priority Mappings**
```python
PRIORITY_MAPPINGS = {
    'critical': 'Highest',
    'high': 'High',
    'medium': 'Medium', 
    'low': 'Low',
    'minimal': 'Lowest'
}
```

### **Severity Mappings**
```python
SEVERITY_MAPPINGS = {
    0: 'Very High',
    1: 'High', 
    2: 'Medium',
    3: 'Low'
}
```

---

## 🎯 Workflow Integration

### **Current Workflow (Read-Only)**
```
Zendesk PDF → Impact Analysis → Excel/JSON → Manual Jira Creation
```

### **New Workflow (End-to-End)**
```
Zendesk PDF → Impact Analysis → Jira Field Suggestions → Automated Creation
```

### **RCA Workflow**
```
Incident → RCA Template → Auto-Generated Fields → Jira Creation → Action Items
```

---

## 📋 Field Requirements

### **Bug Ticket Required Fields**
- ✅ **Project**: RED, MOD, DOC, RDSC
- ✅ **Issue Type**: Bug
- ✅ **Summary**: From Zendesk subject
- ✅ **Description**: Enhanced with impact score
- ✅ **Priority**: Based on impact score
- ✅ **Severity**: Based on impact score
- ✅ **Labels**: Auto-generated (Support, Customer-Reported, etc.)
- ✅ **Custom Fields**: Impact score, Zendesk ID, cache info

### **RCA Ticket Required Fields**
- ✅ **Project**: Root Cause Analysis
- ✅ **Issue Type**: RCA
- ✅ **Summary**: Customer Name - RCA Date
- ✅ **Description**: Template with action items
- ✅ **Labels**: Customer name (underscore format)
- ✅ **Custom Fields**: Zendesk tickets, Slack channel, root cause
- ✅ **Linked Issues**: Related bug Jiras

---

## 🚀 Next Steps

### **Phase 1: Manual Creation (Current)**
1. Run the tools to get suggested fields
2. Copy the JSON output
3. Create Jira tickets manually with suggested fields
4. Update custom fields with calculated impact scores

### **Phase 2: API Integration (Future)**
1. Add Jira API credentials
2. Implement direct Jira creation
3. Auto-assign based on impact scores
4. Send notifications for high-priority tickets

### **Phase 3: Workflow Automation (Future)**
1. Webhook integration with Zendesk
2. Automatic ticket creation on Zendesk updates
3. RCA ticket auto-creation from incident patterns
4. Dashboard for created tickets

---

## 🎯 Benefits

### **For Bug Tickets**
- ✅ **Consistent Scoring**: All tickets get proper impact scores
- ✅ **Field Mapping**: Automatic mapping from Zendesk to Jira
- ✅ **Cache Detection**: Extracts cache name and region
- ✅ **Component Detection**: Identifies DMC, Redis, Cluster components
- ✅ **Environment Detection**: Identifies Azure, AWS, GCP

### **For RCA Tickets**
- ✅ **Template Compliance**: Follows your Confluence process exactly
- ✅ **Auto-Linking**: Links related Zendesk and bug tickets
- ✅ **Field Generation**: Auto-generates customer labels, Slack channels
- ✅ **Action Items**: Structured table for action items
- ✅ **Timeline**: Template for incident timeline

---

## 🐛 Troubleshooting

### **Common Issues**

1. **PDF Parsing Errors**
   - Ensure PDF is not password-protected
   - Check if PDF contains text (not just images)
   - Try different PDF format if available

2. **Field Mapping Issues**
   - Review the suggested fields
   - Adjust project selection if needed
   - Verify customer name format for labels

3. **Impact Score Discrepancies**
   - Review component reasoning
   - Adjust keywords in intelligent_estimator.py
   - Update VIP customer list

### **Debug Mode**
```bash
python src/create_jira_from_zendesk.py ticket.pdf --suggest-only --verbose
```

---

## 📚 Related Documentation

- [Impact Score Model](IMPACT_SCORE_MODEL.md) - Scoring algorithm
- [Intelligent Estimator Guide](INTELLIGENT_ESTIMATOR_GUIDE.md) - AI analysis
- [Jira Processor Guide](JIRA_PROCESSOR_USER_GUIDE.md) - Batch processing

---

**Last Updated**: October 25, 2025  
**Made with ❤️ for better Jira ticket creation**
