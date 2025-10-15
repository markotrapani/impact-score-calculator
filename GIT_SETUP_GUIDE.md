# Setting Up Git Repository for Claude Code (VS Code)

## 🚀 Super Easy Setup - 5 Minutes!

### Step 1: Prepare Your Files

1. **Copy all files** from `/mnt/user-data/outputs/` to a local directory
2. **Replace** the current `README.md` with `README_GIT.md`:
   ```bash
   mv README_GIT.md README.md
   ```

### Step 2: Initialize Git Repository

```bash
# Navigate to your directory
cd /path/to/jira-impact-score-toolkit

# Initialize git
git init

# Add all files
git add .

# First commit
git commit -m "Initial commit: Jira Impact Score Calculator Toolkit"
```

### Step 3: Create GitHub Repository

**Option A: Using GitHub CLI (easiest)**
```bash
# Install GitHub CLI if needed: https://cli.github.com/

# Create repo and push
gh repo create jira-impact-score-toolkit --public --source=. --remote=origin --push
```

**Option B: Using GitHub Web UI**
1. Go to https://github.com/new
2. Name: `jira-impact-score-toolkit`
3. Description: "Python toolkit for calculating Jira ticket impact scores"
4. Make it Public or Private
5. **Don't** initialize with README (you already have one)
6. Click "Create repository"

Then connect and push:
```bash
git remote add origin https://github.com/YOUR_USERNAME/jira-impact-score-toolkit.git
git branch -M main
git push -u origin main
```

### Step 4: Use with Claude Code in VS Code

**Install Claude Code Extension:**
1. Open VS Code
2. Install "Claude Code" extension from marketplace
3. Configure with your API key

**Clone and work on repo:**
```bash
# Clone your repo
git clone https://github.com/YOUR_USERNAME/jira-impact-score-toolkit.git
cd jira-impact-score-toolkit

# Open in VS Code
code .
```

**Use Claude Code:**
- Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
- Type "Claude Code"
- Start working with Claude in your repo!

### Step 5: Test It Works

```bash
# Install dependencies
pip install -r requirements.txt

# Test the intelligent estimator
python intelligent_estimator.py --help
```

---

## 📁 Repository Structure

```
jira-impact-score-toolkit/
├── README.md                           # Main documentation
├── requirements.txt                    # Python dependencies
├── .gitignore                         # Git ignore rules
│
├── Scripts/
│   ├── intelligent_estimator.py       # Auto-estimation tool
│   ├── calculate_jira_scores.py       # Batch processor
│   ├── estimate_impact_score.py       # Interactive estimator
│   ├── impact_score_calculator.py     # Core library
│   └── jira_impact_score_processor.py # Processing engine
│
├── docs/
│   ├── INTELLIGENT_ESTIMATOR_GUIDE.md
│   ├── Impact_Score_Model.md
│   ├── Impact_Score_Visual_Guide.md
│   ├── TOOL_SELECTION_GUIDE.md
│   ├── QUICK_REFERENCE.md
│   ├── ESTIMATOR_GUIDE.md
│   ├── JIRA_PROCESSOR_USER_GUIDE.md
│   ├── SCRIPT_UPDATE_LOG.md
│   └── FINAL_SCRIPT_UPDATES_SUMMARY.md
│
└── examples/
    └── (sample files if you want to add them)
```

**Optional: Reorganize into folders**

```bash
# Create folders
mkdir -p scripts docs examples

# Move files
mv *.py scripts/
mv *.md docs/
mv README.md .  # Keep README at root

# Update paths in README if needed
```

---

## 🎯 Claude Code Usage Examples

### Example 1: Ask Claude to Add a Feature

In VS Code with Claude Code:
```
Hey Claude, can you add a feature to export results as PDF?
```

Claude will:
1. Read your code
2. Understand the structure
3. Implement the feature
4. Create the necessary files

### Example 2: Debug an Issue

```
Claude, the intelligent_estimator.py is giving wrong ARR estimates.
Can you help me improve the customer detection logic?
```

Claude will:
1. Analyze the code
2. Identify the issue
3. Suggest improvements
4. Implement the fix

### Example 3: Add Tests

```
Claude, can you create unit tests for the impact_score_calculator.py?
```

---

## ✅ Pre-Commit Checklist

Before committing changes:

- [ ] Code runs without errors
- [ ] Updated documentation if needed
- [ ] Added new dependencies to `requirements.txt`
- [ ] Tested on sample data
- [ ] Updated CHANGELOG.md (if you create one)

---

## 🔄 Workflow with Claude Code

### Typical Development Flow:

1. **Open repo in VS Code**
2. **Start Claude Code** (Cmd+Shift+P → "Claude Code")
3. **Ask Claude to help** with your task
4. **Review changes** Claude makes
5. **Test the changes**
6. **Commit** with git:
   ```bash
   git add .
   git commit -m "Add feature: XYZ"
   git push
   ```

### Example Development Session:

```bash
# You: "Claude, add support for Excel output with formatting"
# Claude: *creates code*

# Test it
python intelligent_estimator.py ticket.xlsx --output report.xlsx

# Looks good!
git add .
git commit -m "Add Excel output with formatting support"
git push
```

---

## 📝 Suggested First Commits

After initial setup, good next commits:

1. **Add CHANGELOG.md**
   ```bash
   git commit -m "Add CHANGELOG for tracking updates"
   ```

2. **Add LICENSE**
   ```bash
   git commit -m "Add MIT license"
   ```

3. **Add example data** (without real customer info)
   ```bash
   git commit -m "Add example Jira exports for testing"
   ```

4. **Add tests**
   ```bash
   git commit -m "Add unit tests for core calculator"
   ```

---

## 🎓 Tips for Using with Claude Code

### Best Practices:

1. **Be specific**: "Add error handling to intelligent_estimator.py line 145"
2. **Provide context**: "This script processes Jira exports..."
3. **Ask for tests**: "Can you also add tests for this feature?"
4. **Review changes**: Always review what Claude generates
5. **Commit often**: Small, focused commits are better

### Great Questions to Ask Claude:

- "Can you refactor this function to be more efficient?"
- "Add docstrings to all functions in this file"
- "Create a config file for customizable settings"
- "Write comprehensive tests for the workaround detection"
- "Add logging to help with debugging"

---

## 🚀 You're Ready!

Your toolkit is now:
- ✅ Git-ready with proper `.gitignore`
- ✅ Python package with `requirements.txt`
- ✅ Documented with comprehensive README
- ✅ Structured for easy navigation
- ✅ Ready for Claude Code in VS Code

**Next step:** Push to GitHub and start coding with Claude! 🎉

---

## 📧 Need Help?

Common issues:

**Git not installed?**
```bash
# Mac
brew install git

# Ubuntu/Debian
sudo apt-get install git

# Windows
# Download from https://git-scm.com/
```

**Python not found?**
```bash
# Check Python version
python --version  # or python3 --version

# Install if needed: https://python.org
```

**Permission denied on git push?**
```bash
# Set up SSH keys or use personal access token
# Guide: https://docs.github.com/en/authentication
```

---

**Total setup time: ~5 minutes** ⚡
