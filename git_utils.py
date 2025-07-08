from git import Repo
import os

def get_git_commits(repo_path, date):
    try:
        repo = Repo(repo_path)
        since = date.strftime('%Y-%m-%d 00:00:00')
        until = date.strftime('%Y-%m-%d 23:59:59')
        logs = repo.git.log('--since', since, '--until', until, '--pretty=format:%H%n%an%n%ae%n%aD%n%s%n%b%n---END---')
        entries = logs.strip().split('\n---END---')
        commits = []
        for i, entry in enumerate(entries):
            lines = entry.strip().split('\n')
            if len(lines) >= 5:
                author = lines[1].strip()
                commits.append(f"【提交 {i+1}】\n作者: {author}\n标题: {lines[4]}\n描述:\n" + "\n".join(lines[5:]))
        return "\n\n".join(commits) if commits else "无提交记录"
    except Exception as e:
        return f"获取提交失败: {str(e)}"