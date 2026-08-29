import os
from tools.miya_gateway.registry import register
try:
    from github import Github
except Exception:
    Github = None

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
gh = Github(GITHUB_TOKEN) if (GITHUB_TOKEN and Github) else None

@register(name="github.create_file", description="Create or update a file in a repo")
def create_file(owner: str, repo: str, path: str, content: str, branch: str = "main"):
    if gh is None:
        raise RuntimeError("GITHUB_TOKEN not set or PyGithub not installed")
    repository = gh.get_repo(f"{owner}/{repo}")
    try:
        existing = repository.get_contents(path, ref=branch)
        repository.update_file(path, f"chore: update {path}", content, existing.sha, branch=branch)
        return {"updated": True, "path": path}
    except Exception:
        repository.create_file(path, f"chore: add {path}", content, branch=branch)
        return {"created": True, "path": path}
