#!/usr/bin/env python3
"""
Download Git Repository

This script clones a git repository from a URL specified via environment variable.
The repository URL is read from the GIT_REPO_URL environment variable.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


def get_repo_name_from_url(url: str) -> str:
    """
    Extract repository name from git URL.

    Args:
        url: Git repository URL

    Returns:
        Repository name (without .git extension)
    """
    parsed = urlparse(url)
    path = parsed.path

    # Remove leading/trailing slashes
    path = path.strip('/')

    # Get the last part of the path (repo name)
    repo_name = path.split('/')[-1]

    # Remove .git extension if present
    if repo_name.endswith('.git'):
        repo_name = repo_name[:-4]

    return repo_name


def clone_repository(
    repo_url: str,
    target_dir: str = None,
    branch: str = None,
    depth: int = None,
    quiet: bool = False
) -> bool:
    """
    Clone a git repository.

    Args:
        repo_url: Git repository URL
        target_dir: Target directory for cloning (default: repo name in current dir)
        branch: Specific branch to clone (default: default branch)
        depth: Clone depth for shallow clone (default: full clone)
        quiet: Suppress git output

    Returns:
        True if successful, False otherwise
    """
    # Determine target directory
    if target_dir is None:
        repo_name = get_repo_name_from_url(repo_url)
        target_dir = os.path.join(os.getcwd(), repo_name)

    target_path = Path(target_dir)

    # Check if directory already exists
    if target_path.exists():
        if target_path.is_dir() and any(target_path.iterdir()):
            print(f"⚠️  Warning: Directory '{target_dir}' already exists and is not empty")
            response = input("Do you want to remove it and re-clone? (y/N): ")
            if response.lower() != 'y':
                print("❌ Aborted")
                return False

            # Remove existing directory
            import shutil
            shutil.rmtree(target_path)
            print(f"🗑️  Removed existing directory")

    # Build git clone command
    cmd = ['git', 'clone']

    if branch:
        cmd.extend(['--branch', branch])

    if depth:
        cmd.extend(['--depth', str(depth)])

    if quiet:
        cmd.append('--quiet')

    cmd.extend([repo_url, str(target_path)])

    # Execute git clone
    print(f"📥 Cloning repository from: {repo_url}")
    if branch:
        print(f"   Branch: {branch}")
    if depth:
        print(f"   Depth: {depth} (shallow clone)")
    print(f"   Target: {target_path}")

    try:
        subprocess.run(
            cmd,
            capture_output=not quiet,
            text=True,
            check=True
        )

        print(f"✅ Successfully cloned repository to: {target_path}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Error cloning repository:")
        if e.stderr:
            print(f"   {e.stderr}")
        return False

    except FileNotFoundError:
        print("❌ Error: 'git' command not found. Please install git first.")
        return False


def pull_repository(repo_dir: str, quiet: bool = False) -> bool:
    """
    Pull latest changes in an existing repository.

    Args:
        repo_dir: Directory containing the git repository
        quiet: Suppress git output

    Returns:
        True if successful, False otherwise
    """
    repo_path = Path(repo_dir)

    if not repo_path.exists():
        print(f"❌ Error: Directory '{repo_dir}' does not exist")
        return False

    if not (repo_path / '.git').exists():
        print(f"❌ Error: '{repo_dir}' is not a git repository")
        return False

    print(f"🔄 Pulling latest changes in: {repo_dir}")

    cmd = ['git', '-C', str(repo_path), 'pull']
    if quiet:
        cmd.append('--quiet')

    try:
        subprocess.run(
            cmd,
            capture_output=not quiet,
            text=True,
            check=True
        )

        print(f"✅ Successfully pulled latest changes")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Error pulling changes:")
        if e.stderr:
            print(f"   {e.stderr}")
        return False


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Clone a git repository from a URL (via environment variable or argument)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  GIT_REPO_URL      Git repository URL to clone
  GIT_TARGET_DIR    Target directory for cloning (optional)

Examples:
  # Using environment variable
  export GIT_REPO_URL="https://github.com/user/repo.git"
  python 0_download_git_repo.py

  # Using environment variables for URL and target
  export GIT_REPO_URL="https://github.com/user/repo.git"
  export GIT_TARGET_DIR="./my-repos/my-repo"
  python 0_download_git_repo.py

  # Using command line argument
  python 0_download_git_repo.py --url https://github.com/user/repo.git

  # Clone to specific directory
  python 0_download_git_repo.py --url https://github.com/user/repo.git --target ./my-repo

  # Clone specific branch
  python 0_download_git_repo.py --url https://github.com/user/repo.git --branch main

  # Shallow clone (faster, less disk space)
  python 0_download_git_repo.py --url https://github.com/user/repo.git --depth 1

  # Pull latest changes in existing repo
  python 0_download_git_repo.py --pull ./my-repo
        """
    )

    parser.add_argument(
        '--url',
        type=str,
        help='Git repository URL (overrides GIT_REPO_URL env var)'
    )

    parser.add_argument(
        '--target',
        type=str,
        help='Target directory for cloning (overrides GIT_TARGET_DIR env var, default: repo name in current directory)'
    )

    parser.add_argument(
        '--branch',
        type=str,
        help='Specific branch to clone (default: default branch)'
    )

    parser.add_argument(
        '--depth',
        type=int,
        help='Clone depth for shallow clone (e.g., --depth 1 for latest commit only)'
    )

    parser.add_argument(
        '--pull',
        type=str,
        metavar='DIR',
        help='Pull latest changes in existing repository instead of cloning'
    )

    parser.add_argument(
        '--quiet',
        '-q',
        action='store_true',
        help='Suppress git output'
    )

    parser.add_argument(
        '--env-var',
        type=str,
        default='GIT_REPO_URL',
        help='Name of environment variable containing repo URL (default: GIT_REPO_URL)'
    )

    args = parser.parse_args()

    # Handle pull mode
    if args.pull:
        success = pull_repository(args.pull, quiet=args.quiet)
        sys.exit(0 if success else 1)

    # Get repository URL
    repo_url = args.url

    if not repo_url:
        # Try to get from environment variable
        repo_url = os.environ.get(args.env_var)

    if not repo_url:
        print(f"❌ Error: No repository URL provided")
        print(f"   Set {args.env_var} environment variable or use --url argument")
        print(f"\n   Example:")
        print(f"     export {args.env_var}='https://github.com/user/repo.git'")
        print(f"     python {sys.argv[0]}")
        print(f"\n   Or:")
        print(f"     python {sys.argv[0]} --url https://github.com/user/repo.git")
        sys.exit(1)

    # Validate URL
    if not repo_url.startswith(('http://', 'https://', 'git@', 'ssh://')):
        print(f"❌ Error: Invalid git URL: {repo_url}")
        print(f"   URL should start with http://, https://, git@, or ssh://")
        sys.exit(1)

    # Get target directory
    target_dir = args.target

    if not target_dir:
        # Try to get from environment variable
        target_dir = os.environ.get('GIT_TARGET_DIR')

    # Clone repository
    success = clone_repository(
        repo_url=repo_url,
        target_dir=target_dir,
        branch=args.branch,
        depth=args.depth,
        quiet=args.quiet
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
