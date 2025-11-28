# Deploy to Azure Button - Automatic Configuration

The "Deploy to Azure" button in the README.md is automatically configured when you push to GitHub.

## How It Works

A GitHub Action (`.github/workflows/update-deploy-button.yml`) runs on the first push and:

1. Detects the placeholder `YOUR_USERNAME/YOUR_REPO` in README.md
2. Automatically replaces it with your actual repository owner and name
3. Commits the updated README.md back to the repository

## First-Time Setup

1. **Push to GitHub** with the placeholder intact:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/your-username/your-repo.git
   git push -u origin main
   ```

2. **Wait 30 seconds** - The GitHub Action runs automatically

3. **Pull the changes**:
   ```bash
   git pull
   ```

4. **Verify** - Check README.md, the button URL should now have your repo path

## Manual Configuration (Alternative)

If you prefer not to use GitHub Actions, or if the action doesn't have write permissions:

1. Delete the `.github/workflows/update-deploy-button.yml` file

2. Manually replace in README.md:
   ```
   YOUR_USERNAME%2FYOUR_REPO
   ```
   
   With your URL-encoded repo path:
   ```
   your-username%2Fyour-repo
   ```

## Troubleshooting

### Action Doesn't Run
- Check Actions tab in GitHub repository
- Ensure Actions are enabled (Settings → Actions → General → Allow all actions)
- Check if workflow file has correct syntax

### Action Fails with "Permission Denied"
The action needs write permissions. Fix:

1. Go to Settings → Actions → General
2. Scroll to "Workflow permissions"
3. Select "Read and write permissions"
4. Click "Save"
5. Re-run the failed action or push a new commit

### Button Still Shows Placeholder After Action Runs
- Pull the latest changes: `git pull`
- Check the Actions tab for errors
- Verify the workflow ran successfully
- If action shows "No changes needed", the README was already updated

## Disabling Auto-Update

To disable automatic updates:

```bash
# Delete the workflow file
rm .github/workflows/update-deploy-button.yml
git add .github/workflows/update-deploy-button.yml
git commit -m "Remove auto-update workflow"
git push
```

## Testing the Action Locally

To test what the action would do:

```bash
# Get your repo path
REPO_PATH=$(git remote get-url origin | sed 's/.*github.com[:/]\(.*\)\.git/\1/')
ENCODED_PATH=$(echo "$REPO_PATH" | sed 's/\//%2F/g')

# Check if placeholder exists
grep "YOUR_USERNAME%2FYOUR_REPO" README.md

# See what would be replaced
sed "s/YOUR_USERNAME%2FYOUR_REPO/${ENCODED_PATH}/g" README.md | grep "Deploy to Azure"
```

## Security Note

This workflow only modifies the README.md file and runs only when:
- Pushing to the `main` branch
- The README.md or workflow file itself changes

It uses the default `GITHUB_TOKEN` with minimal permissions and cannot access secrets or modify other parts of your repository.
