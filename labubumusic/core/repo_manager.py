import asyncio
import shlex
from typing import Tuple
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError

import config
from ..logging import LOGGER

def install_dependencies(command: str) -> Tuple[str, str, int, int]:
    async def run_installation():
        cmd_args = shlex.split(command)
        sub_process = await asyncio.create_subprocess_exec(
            *cmd_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        out, err = await sub_process.communicate()
        return (
            out.decode("utf-8", "replace").strip(),
            err.decode("utf-8", "replace").strip(),
            sub_process.returncode,
            sub_process.pid,
        )

    return asyncio.get_event_loop().run_until_complete(run_installation())

def update_repo():
    repo_url = config.UPSTREAM_REPO
    
    if not config.GIT_TOKEN:
        upstream_link = repo_url
    else:
        git_user = repo_url.split("com/")[1].split("/")[0]
        temp_link = repo_url.split("https://")[1]
        upstream_link = f"https://{git_user}:{config.GIT_TOKEN}@{temp_link}"
        
    try:
        git_repo = Repo()
        LOGGER(__name__).info("Git Client Found [VPS DEPLOYER]")
    except GitCommandError:
        LOGGER(__name__).info("Invalid Git Command executed.")
    except InvalidGitRepositoryError:
        git_repo = Repo.init()
        
        origin = git_repo.remote("origin") if "origin" in git_repo.remotes else git_repo.create_remote("origin", upstream_link)
        origin.fetch()
        
        git_repo.create_head(config.UPSTREAM_BRANCH, origin.refs[config.UPSTREAM_BRANCH])
        git_repo.heads[config.UPSTREAM_BRANCH].set_tracking_branch(origin.refs[config.UPSTREAM_BRANCH])
        git_repo.heads[config.UPSTREAM_BRANCH].checkout(True)
        
        try:
            git_repo.create_remote("origin", config.UPSTREAM_REPO)
        except BaseException:
            pass
            
        new_remote = git_repo.remote("origin")
        new_remote.fetch(config.UPSTREAM_BRANCH)
        
        try:
            new_remote.pull(config.UPSTREAM_BRANCH)
        except GitCommandError:
            git_repo.git.reset("--hard", "FETCH_HEAD")
            
        install_dependencies("pip3 install --no-cache-dir -r requirements.txt")
        LOGGER(__name__).info("Fetching updates from upstream repository...")