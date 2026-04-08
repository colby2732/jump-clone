# Git & GitHub Guide for Windows

All commands below are run in **PowerShell** or **Command Prompt**.

---

## First-Time Setup

```powershell
# Install Git (if you haven't)
# Download from: https://git-scm.com/download/win

# Set your identity (one-time)
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

---

## Cloning the Repo

```powershell
# Clone the project to your machine
git clone https://github.com/colby2732/jump-clone.git

# Move into the project folder
cd jump-clone
```

---

## Branches

### See all branches
```powershell
# List local branches (* = current branch)
git branch

# List all branches (including remote)
git branch -a
```

### Create a new branch
```powershell
# Create and switch to a new branch
git checkout -b my-new-branch

# Or using the newer syntax
git switch -c my-new-branch
```

### Switch between branches
```powershell
# Switch to an existing branch
git checkout main
git checkout my-new-branch

# Or using newer syntax
git switch main
git switch my-new-branch
```

### Delete a branch
```powershell
# Delete a local branch (safe — won't delete unmerged work)
git branch -d my-new-branch

# Force delete a local branch
git branch -D my-new-branch
```

---

## Day-to-Day Workflow

### 1. Always pull before you start working
```powershell
git pull
```

### 2. Check what's changed
```powershell
# See which files you've modified
git status

# See the actual changes line-by-line
git diff
```

### 3. Stage your changes
```powershell
# Stage a specific file
git add filename.py

# Stage everything
git add .
```

### 4. Commit your changes
```powershell
git commit -m "describe what you changed"
```

### 5. Push your branch to GitHub
```powershell
# First time pushing a new branch
git push -u origin my-new-branch

# After the first push, just
git push
```

### 6. Pull updates from main into your branch
```powershell
git checkout my-new-branch
git pull origin main
```

---

## Merging

### Merge a branch into main (locally)
```powershell
# Switch to main
git checkout main

# Pull latest
git pull

# Merge your branch in
git merge my-new-branch

# Push the updated main
git push
```

### Or use a Pull Request (recommended)
1. Push your branch: `git push -u origin my-new-branch`
2. Go to https://github.com/colby2732/jump-clone
3. Click **"Compare & pull request"**
4. Add a description and click **"Create pull request"**
5. After review, click **"Merge pull request"**

---

## Fixing Common Problems

### Undo changes to a file (before staging)
```powershell
git checkout -- filename.py
```

### Unstage a file (after git add, before commit)
```powershell
git reset HEAD filename.py
```

### Undo your last commit (keep the changes)
```powershell
git reset --soft HEAD~1
```

### Merge conflicts
If git says there's a conflict:
1. Open the file — look for `<<<<<<<`, `=======`, `>>>>>>>` markers
2. Edit the file to keep what you want, delete the markers
3. `git add filename.py`
4. `git commit -m "resolved merge conflict"`

### Stash changes temporarily
```powershell
# Save your work-in-progress without committing
git stash

# Get it back later
git stash pop
```

---

## Useful Shortcuts

| Command | What it does |
|---|---|
| `git log --oneline` | Quick commit history |
| `git log --oneline --graph` | Visual branch history |
| `git remote -v` | Show the remote URL |
| `git fetch` | Download updates without merging |
| `git blame filename.py` | See who wrote each line |

---

## Recommended Branch Naming

- `feature/player-animation` — new features
- `fix/collision-bug` — bug fixes
- `test/new-level` — experiments

---

## Quick Reference: Full Feature Workflow

```powershell
git checkout main          # start from main
git pull                   # get latest
git checkout -b feature/my-thing   # new branch
# ... make your changes ...
git add .                  # stage everything
git commit -m "add my thing"       # commit
git push -u origin feature/my-thing  # push to GitHub
# then open a Pull Request on GitHub
```
