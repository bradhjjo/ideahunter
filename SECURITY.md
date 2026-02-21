# Security Guide

## ⚠️ Files That Must Never Be Committed

The following files must **never** be committed to Git:

- `.env` — contains real API keys and credentials
- `*.key` — private key files
- `secrets.json` — configuration files with sensitive data
- `credentials.txt` — authentication credentials

## ✅ Safe Credential Management

### Local Development

- Store real keys in your `.env` file
- `.env` is already listed in `.gitignore` — it will never be accidentally staged
- `.env.example` contains only placeholder values — safe to commit

### GitHub Actions

- Store API keys in **GitHub Secrets** (Settings → Secrets and variables → Actions)
- Reference them in workflows as `${{ secrets.KEY_NAME }}` — never hardcode values

### Documentation

- Use placeholders like `your_api_key_here` instead of real values
- Only describe how to obtain a key, never share its value

## 🔍 Pre-Commit Checklist

Before every commit, verify no secrets are staged:

```powershell
# Check which files are staged
git status

# Review the diff
git diff

# Scan for common API key patterns
git diff | Select-String -Pattern "AIza|[0-9]{10}:[A-Za-z0-9_-]{35}|sk-[A-Za-z0-9]{48}"
```

## 🚨 If You Accidentally Commit a Secret

1. **Immediately revoke / rotate the exposed key** at the provider's dashboard
2. **Remove it from Git history** using [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)
3. **Issue a new key** and update GitHub Secrets
4. **Force-push** to overwrite the remote history

## 📚 References

- [GitHub Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)
- [Removing Sensitive Data from a Repository](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
