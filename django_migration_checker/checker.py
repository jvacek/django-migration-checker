#!/usr/bin/env python
import os
import re


def extract_dependencies(file_path):
    """
    Parse the file contents and return the list of dependencies.
    """
    file_contents = open(file_path).read()
    match = re.search(r"""^\s+dependencies [^\[]+
                          \[
                          ([^\]]*)
                          \]""",
                      file_contents,
                      flags=re.VERBOSE | re.MULTILINE)
    if not match:
        return []

    deps = match.group(1).strip()
    if not deps:
        return []

    match_iter = re.finditer(r"""\(
                                 '([^']+)'
                                 ,\s*
                                 '([^_][^']+)'
                                 \)""",
                             deps,
                             flags=re.VERBOSE)
    return [(match.group(1), match.group(2)) for match in match_iter]


def get_app_conflicts(app, migration_files):
    # Detect leaves
    leaves = set(os.path.basename(file)[:-3] for file in migration_files)
    for migration in migration_files:
        for dep in extract_dependencies(migration):
            if dep[0] == app and dep[1] in leaves:
                leaves.remove(dep)
    # assert len(leaves) > 0
    if len(leaves) > 1:
        return sorted(leaves)
    else:
        return []


def get_conflicts(app_dir=None):
    """
    Return a list of tuples, where each tuple has three elements:
    - app
    - migration file (no path)
    - full path to migration file
    """
    if app_dir is None:
        app_dir = os.getcwd()

    res = []
    for app in os.listdir(app_dir):
        entry_path = os.path.join(app_dir, app)
        # Skip if not a directory or there's no 'migration' dir
        if (not os.path.isdir(entry_path) or
                'migrations' not in os.listdir(entry_path)):
            continue

        migrations_dir = os.path.join(entry_path, 'migrations')
        migration_file_list = []
        for migration_file in os.listdir(migrations_dir):
            # Skip __init__.py and non-Python files
            if (migration_file.startswith('__') or
                    not migration_file.endswith('.py')):
                continue
            full_path = os.path.join(migrations_dir, migration_file)
            migration_file_list.append(full_path)
        app_conflicts = get_app_conflicts(app, migration_file_list)
        if app_conflicts:
            res.append((app, app_conflicts))
    return res
