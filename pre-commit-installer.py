import os
import sys
import stat
import subprocess

from flake8 import exceptions


def piped_process(command):
    return subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def get_executable():
    if sys.executable is not None:
        return sys.executable
    return '/usr/bin/env python'


def find_git_directory():
    rev_parse = piped_process(['git', 'rev-parse', '--git-dir'])

    (stdout, _) = rev_parse.communicate()
    stdout = to_text(stdout)

    if rev_parse.returncode == 0:
        return stdout.strip()
    return None


def to_text(string):
    if callable(getattr(string, 'decode', None)):
        return string.decode('utf-8')
    return string


def set_strict():
    piped_process(['git', 'config', '--bool', 'flake8.strict', 'true'])
    return None


_HOOK_TEMPLATE = """#!{executable}
import sys
import os

from flake8.main import git


def hook(lazy=False, strict=False):
    from flake8.main import application
    app = application.Application()
    with git.make_temporary_directory() as tempdir:
        filepaths = list(copy_indexed_files_to(tempdir, lazy))
        app.initialize(['.'])
        app.options.exclude = update_excludes(app.options.exclude, tempdir)
        app.run_checks(filepaths)

    app.report_errors()
    if strict:
        return app.result_count
    return 0


def copy_indexed_files_to(temporary_directory, lazy):
    modified_files = find_modified_files(lazy)
    for filename in modified_files:
        contents = git.get_staged_contents_from(filename)
        yield git.copy_file_to(temporary_directory, filename, contents)


def find_modified_files(lazy):
    diff_index_cmd = [
        'git', 'diff-index', '--cached', '--name-only',
        '--diff-filter=ACMRTUXB', 'HEAD', '|', 'grep', '-e', '\.py$'
    ]
    if lazy:
        diff_index_cmd.remove('--cached')

    diff_index = git.piped_process(diff_index_cmd)
    (stdout, _) = diff_index.communicate()
    stdout = git.to_text(stdout)
    return stdout.splitlines()


def update_excludes(exclude_list, temporary_directory_path):
    return exclude_list + [
        (temporary_directory_path + pattern)
        for pattern in exclude_list
        if os.path.isabs(pattern)
    ]


if __name__ == '__main__':
    sys.exit(
        hook(
            strict=git.config_for('strict'),
            lazy=git.config_for('lazy'),
        )
    )
"""


def install():
    git_directory = find_git_directory()
    if git_directory is None or not os.path.exists(git_directory):
        return False

    hooks_directory = os.path.join(git_directory, 'hooks')
    if not os.path.exists(hooks_directory):
        os.mkdir(hooks_directory)

    pre_commit_file = os.path.abspath(
        os.path.join(hooks_directory, 'pre-commit')
    )
    if os.path.exists(pre_commit_file):
        raise exceptions.GitHookAlreadyExists(
            'File already exists',
            path=pre_commit_file,
        )

    executable = get_executable()

    with open(pre_commit_file, 'w') as fd:
        fd.write(_HOOK_TEMPLATE.format(executable=executable))

    # NOTE(sigmavirus24): The following sets:
    # - read, write, and execute permissions for the owner
    # - read permissions for people in the group
    # - read permissions for other people
    # The owner needs the file to be readable, writable, and executable
    # so that git can actually execute it as a hook.
    pre_commit_permissions = stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH
    os.chmod(pre_commit_file, pre_commit_permissions)

    set_strict()
    return True


if __name__ == '__main__':
    install()
