#!/usr/bin/python

import argparse
import sys

from argparse import ArgumentTypeError as err
import os

class PathType(object):
    def __init__(self, exists=True, type='file', dash_ok=True):
        '''exists:
                True: a path that does exist
                False: a path that does not exist, in a valid parent directory
                None: don't care
           type: file, dir, symlink, None, or a function returning True for valid paths
                None: don't care
           dash_ok: whether to allow "-" as stdin/stdout'''

        assert exists in (True, False, None)
        assert type in ('file','dir','symlink',None) or hasattr(type,'__call__')

        self._exists = exists
        self._type = type
        self._dash_ok = dash_ok

    def __call__(self, string):
        if string=='-':
            # the special argument "-" means sys.std{in,out}
            if self._type == 'dir':
                raise err('standard input/output (-) not allowed as directory path')
            elif self._type == 'symlink':
                raise err('standard input/output (-) not allowed as symlink path')
            elif not self._dash_ok:
                raise err('standard input/output (-) not allowed')
        else:
            e = os.path.exists(string)
            if self._exists==True:
                if not e:
                    raise err("path does not exist: '%s'" % string)

                if self._type is None:
                    pass
                elif self._type=='file':
                    if not os.path.isfile(string):
                        raise err("path is not a file: '%s'" % string)
                elif self._type=='symlink':
                    if not os.path.symlink(string):
                        raise err("path is not a symlink: '%s'" % string)
                elif self._type=='dir':
                    if not os.path.isdir(string):
                        raise err("path is not a directory: '%s'" % string)
                elif not self._type(string):
                    raise err("path not valid: '%s'" % string)
            else:
                if self._exists==False and e:
                    raise err("path exists: '%s'" % string)

                p = os.path.dirname(os.path.normpath(string)) or '.'
                if not os.path.isdir(p):
                    raise err("parent path is not a directory: '%s'" % p)
                elif not os.path.exists(p):
                    raise err("parent directory does not exist: '%s'" % p)

        return string

import textwrap as _textwrap
class MultilineFormatter(argparse.HelpFormatter):
    def _fill_text(self, text, width, indent):
        text = self._whitespace_matcher.sub(' ', text).strip()
        paragraphs = text.split('|')
        multiline_text = ''
        for paragraph in paragraphs:
            formatted_paragraph = _textwrap.fill(paragraph.strip().replace('>','\t'), width, initial_indent=indent, subsequent_indent=indent) + '\n\n'
            multiline_text = multiline_text + formatted_paragraph
        return multiline_text

def main():
    parser = argparse.ArgumentParser(
        description='merge OpenWRT feeds',
        epilog='''Except for the `feeds.conf` in the specified QSDK_DIR, every `src-link`
                  is modified when merging the feeds. A typical line in a qsdk external `feeds.conf`
                  file located in the repo root directory `./platform` might be:
                  |>src-link platform_apps package|
                  If the qsdk is located in the repo root directory `./qsdk`, the line is modified to
                  |>src-link platform.platform_apps ../../platform/package|
                  The package-name is prepended with the directory name to prevent naming conflicts.
                  The destination directory as adjusted to a path relative from `./qsdk/feeds`''',
        formatter_class=MultilineFormatter)
    parser.add_argument('-q', '--qsdk-dir',
                        dest='qsdk_dir',
                        type=PathType(exists=True, type='dir'),
                        required=True)
    parser.add_argument('-o', '--output',
                        dest='output_file',
                        type=argparse.FileType('w'), default=sys.stdout,
                        help='file to output to (stdout if omitted)')
    parser.add_argument('feeds_to_merge',
                        type=argparse.FileType('r'), nargs='+',
                        help='list of feed.conf files to merge')

    args = parser.parse_args()

    qsdkPath = os.path.abspath(args.qsdk_dir)
    feedsPath = os.path.join(qsdkPath, 'feeds')
    
    for f in args.feeds_to_merge:
        projectPath = os.path.dirname(os.path.abspath(f.name))
        projectName = os.path.basename(projectPath)
        for line in f:
            (srcType, packageName, dest) = line.split()
            packageName = projectName + "_" + packageName
            if projectPath == qsdkPath:
                pass
            else:
                destPath = os.path.join(projectPath, dest)
                print 'os.path.relpath("%s", "%s"): %s' % (destPath, feedsPath, os.path.relpath(destPath, feedsPath)) 
                dest = os.path.relpath(destPath, feedsPath)
            args.output_file.write(" ".join([srcType, packageName, dest]) + "\n")
        
    sys.exit(0)

if __name__ == "__main__":
    main()
