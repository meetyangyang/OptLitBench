# Security Policy

## Supported versions

Security fixes are applied to the `main` branch of [OptLitBench](https://github.com/meetyangyang/OptLitBench).

## Reporting a vulnerability

If you discover a security issue (e.g., accidental secret exposure, unsafe dependency, or data handling concern), please report it privately:

- Email: **yangyang@cipuc.edu.cn**
- Subject: `[OptLitBench Security]`

Please include:

1. A description of the issue
2. Steps to reproduce (if applicable)
3. Potential impact

We aim to acknowledge reports within **7 business days**.

## Secrets and credentials

- **Never commit** GitHub tokens, passwords, or private keys.
- Use environment variables such as `GITHUB_TOKEN` for local upload scripts.
- If a token is accidentally pushed, revoke it immediately in GitHub settings and force-rotate credentials.

## Dependencies

Pinned dependencies are listed in `requirements-lock.txt`. We recommend running dependency audits before releases:

```powershell
pip install pip-audit
pip-audit -r requirements-lock.txt
```
