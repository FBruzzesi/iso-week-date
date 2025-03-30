"""
Adjusted from narwhals https://github.com/narwhals-dev/narwhals/blob/25701453aaa0556adc491e428f6d5724a1eac177/utils/bump_version.py

License: MIT
Copyright (c) 2024 Marco Gorelli
"""
# python bump-version.py <patch|minor|major>

# mypy: ignore
# ruff: noqa
import re
import subprocess
import sys

out = subprocess.run(["git", "fetch", "upstream", "--tags"])
if out.returncode != 0:
    print(
        "Something went wrong with the release process, please check the Narwhals Wiki and try again."
    )
    print(out)
    sys.exit(1)
subprocess.run(["git", "reset", "--hard", "upstream/main"])

if (
    subprocess.run(
        ["git", "branch", "--show-current"], text=True, capture_output=True
    ).stdout.strip()
    != "bump-version"
):
    msg = "`bump-version.py` should be run from `bump-version` branch"
    raise RuntimeError(msg)

# Delete local tags, if present
try:
    # Get the list of all tags
    result = subprocess.run(
        ["git", "tag", "-l"], capture_output=True, text=True, check=True
    )
    tags = result.stdout.splitlines()  # Split the tags into a list by lines

    # Delete each tag using git tag -d
    for tag in tags:
        subprocess.run(["git", "tag", "-d", tag], check=True)
    print("All local tags have been deleted.")
except subprocess.CalledProcessError as e:
    print(f"An error occurred: {e}")

subprocess.run(["git", "fetch", "upstream", "--tags"])
subprocess.run(["git", "fetch", "upstream", "--prune", "--tags"])

how = sys.argv[1]

with open("pyproject.toml", encoding="utf-8") as f:
    content = f.read()

old_version = re.search(r'version = "(.*)"', content).group(1)
v_major, v_minor, v_patch = old_version.split(".")

if how == "patch":
    version = f"{v_major}.{v_minor}.{int(v_patch)+1}"
elif how == "minor":
    version = f"{v_major}.{int(v_minor)+1}.0"
elif how == "major":
    version = f"{int(v_major)+1}.0.0"

content = content.replace(f'version = "{old_version}"', f'version = "{version}"')

with open("pyproject.toml", "w", encoding="utf-8") as f:
    f.write(content)

subprocess.run(["git", "commit", "-a", "-m", f"release: Bump version to {version}"])
subprocess.run(["git", "tag", "-a", f"v{version}", "-m", f"v{version}"])
subprocess.run(["git", "push", "upstream", "HEAD", "--follow-tags"])
subprocess.run(["git", "push", "upstream", "HEAD:stable", "-f", "--follow-tags"])