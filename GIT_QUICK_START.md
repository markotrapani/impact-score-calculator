# Git Setup - One Page Quick Start

## ⚡ 3-Minute Setup

### 1️⃣ Initialize Git (1 min)
```bash
cd /path/to/jira-impact-score-toolkit
git init
git add .
git commit -m "Initial commit: Jira Impact Score Toolkit"
```

### 2️⃣ Create GitHub Repo (1 min)
**Using GitHub CLI (easiest):**
```bash
gh repo create jira-impact-score-toolkit --public --source=. --push
```

**OR using Web UI:**
- Go to https://github.com/new
- Name: `jira-impact-score-toolkit`  
- Click "Create"
- Then:
```bash
git remote add origin https://github.com/YOUR_USERNAME/jira-impact-score-toolkit.git
git push -u origin main
```

### 3️⃣ Use with Claude Code in VS Code (1 min)
```bash
# Clone your repo
git clone https://github.com/YOUR_USERNAME/jira-impact-score-toolkit.git

# Open in VS Code
code jira-impact-score-toolkit

# Install Claude Code extension in VS Code
# Press Cmd+Shift+P → "Claude Code"
```

---

## 📦 Files Already Included

- ✅ `.gitignore` - Ignores temp files, user data
- ✅ `requirements.txt` - Python dependencies
- ✅ `README_GIT.md` - Repository README (rename to README.md)
- ✅ All Python scripts
- ✅ All documentation

---

## 🎯 First Steps After Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Test it works
python intelligent_estimator.py --help

# Start using Claude Code!
# Ask: "Claude, help me add a new feature..."
```

---

## 📁 Suggested Folder Structure

```bash
# Optional: Organize into folders
mkdir -p scripts docs examples
mv *.py scripts/
mv *_GUIDE.md *_Model.md docs/
```

---

## ✅ That's It!

You now have a Git repo ready for Claude Code in VS Code! 🎉

**Full guide:** See `GIT_SETUP_GUIDE.md` for detailed instructions
