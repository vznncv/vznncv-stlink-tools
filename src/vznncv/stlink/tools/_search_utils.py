"""
Helper module to search files.
"""
import logging
import os

from os.path import isdir, join, isfile, exists, abspath

logger = logging.getLogger(__name__)


def find_files_at_same_level(start_dir, name_matcher, max_depth=None):
    """
    Find files in the ``start_dir`` that are matched to ``name_matcher``

    If files aren't found in the ``start_dir`` then function will try to find them in the subdirectories.
    If files aren't found in the subdirectories, then next level of subdirectories will be scanned.
    The process will be continues until the files are found, all we reach ``max_depth`` or all directories are scanned.

    :param start_dir:
    :param name_matcher:
    :param max_depth:
    :return:
    """
    current_level = 0
    current_dirs = [start_dir]
    result_files = []

    while current_dirs:
        if max_depth is not None and current_level > max_depth:
            break

        next_level_dirs = []
        for current_dir in current_dirs:
            for filename in os.listdir(current_dir):
                filepath = join(current_dir, filename)
                if isdir(filepath):
                    next_level_dirs.append(filepath)
                elif name_matcher(filename):
                    result_files.append(filepath)

        if result_files:
            break

        current_level += 1
        current_dirs = next_level_dirs

    return result_files


def create_extension_matcher(extension):
    if not extension.startswith('.'):
        extension = '.' + extension
    extension = extension.lower()

    def extension_matcher(filename):
        return filename.lower().endswith(extension)

    return extension_matcher


def resolve_filepath(explicit_filepath=None, alternative_dirs=None, extension=None, max_depth=None):
    """
    Resolve filepath.

    :param explicit_filepath: explicit filepath
    :param alternative_dir: directory to search file if ``explicit_filepath`` is ``None``
    :param extension: file extension
    :param max_depth: max depth of the subdirectories to check
    :return: resolved filepath
    """

    if extension is not None:
        name_matcher = create_extension_matcher(extension)
    else:
        name_matcher = lambda filename: True

    result_files = []

    if explicit_filepath is not None:
        explicit_filepath = abspath(explicit_filepath)
        if not exists(explicit_filepath):
            raise ValueError("Filepath: '{}' doesn't exists".format(explicit_filepath))
        elif isfile(explicit_filepath):
            return explicit_filepath
        else:
            result_files = find_files_at_same_level(
                start_dir=explicit_filepath,
                name_matcher=name_matcher,
                max_depth=0
            )
    elif alternative_dirs is not None:
        for alternative_dir in alternative_dirs:
            if not exists(alternative_dir):
                continue
            result_files = find_files_at_same_level(
                start_dir=alternative_dir,
                name_matcher=name_matcher,
                max_depth=max_depth
            )
            if result_files:
                break
    else:
        raise ValueError("explicit_filepath and alternative_dir aren't set")

    if len(result_files) == 1:
        logger.info("Found '{}'".format(result_files[0]))
    elif len(result_files) > 1:
        raise ValueError("Found multiple files:\n{}".format('\n'.join(result_files)))
    elif extension is None:
        raise ValueError("No files are found")
    else:
        raise ValueError("No file with extension *{} is found".format(extension))

    return result_files[0]