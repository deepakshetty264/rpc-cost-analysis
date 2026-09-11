# Pushing this to GitHub

## 1. Add the workbook template

Copy your blank workbook into `templates/`, then force-add it
(the .gitignore blocks .xlsx by default):

    git add -f templates/RPC_Centre_Manager_TEMPLATE.xlsx

Make sure it is the TEMPLATE (empty) version, not the populated one.

## 2. Check nothing sensitive is staged

    git status
    git diff --cached --stat

Look for: any .csv, the populated workbook, call transcripts,
the report with real figures. None of these should appear.

## 3. Initialise and push

    git init
    git add .
    git commit -m "Cost model, methodology and record-keeping template"
    git branch -M main
    git remote add origin https://github.com/YOUR-USERNAME/rpc-cost-analysis.git
    git push -u origin main

Create the repo on GitHub first, as PRIVATE. Make it public only after
you have confirmation from the client.

## 4. If you commit something sensitive by accident

Deleting the file in a later commit does NOT remove it from history.
The simplest fix is to delete the repository on GitHub and start again
with a fresh `git init`. Do that rather than attempting to rewrite history.

## Before making it public

- [ ] Client has confirmed they are content with what is published
- [ ] Supervisor is aware
- [ ] No client figures anywhere in README, docs or code
- [ ] Workbook in templates/ is blank
- [ ] data/ contains nothing but its README
