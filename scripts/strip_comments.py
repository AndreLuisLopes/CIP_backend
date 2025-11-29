

"""
Strip comments from source files across the repository.

- Python: removes # comments via tokenize (keeps docstrings)
- C-like (ts, tsx, js, jsx, mjs, cjs, css, scss): removes // and /* */ while preserving strings (', ") and template literals (`) with escapes.

Usage:
  python backend/scripts/strip_comments.py [ROOT]
If ROOT isn't provided, it uses the repository root (parent of this file's parent).

Note: This modifies files in place. A backup of the original file is NOT kept.
"""

from __future__ import annotations

import os

import sys

import io

import tokenize

from typing import Iterable





SKIP_DIRS = {

    '.git', '.hg', '.svn', 'node_modules', '.next', 'dist', 'build', '__pycache__', 'uploads'

}



PY_EXTS = {'.py'}

CLIKE_EXTS = {'.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs', '.css', '.scss'}





SKIP_FILES = {

    'pnpm-lock.yaml', 'package-lock.json', 'yarn.lock'

}





def strip_python_comments(src: str) -> str:

    buf = io.StringIO(src)

    out = io.StringIO()

    prev_end = (1, 0)

    try:

        for tok in tokenize.generate_tokens(buf.readline):

            tok_type = tok.type

            tok_str = tok.string

            srow, scol = tok.start

            erow, ecol = tok.end

            

            if prev_end[0] < srow:

                out.write("\n" * (srow - prev_end[0]))

                out.write(" " * scol)

            else:

                out.write(" " * (scol - prev_end[1]))



            if tok_type == tokenize.COMMENT:

                

                pass

            else:

                out.write(tok_str)

            prev_end = (erow, ecol)

    except tokenize.TokenError:

        

        return src

    return out.getvalue()





def strip_c_like_comments(src: str) -> str:

    """Remove // and /* */ comments while preserving strings and template literals."""

    i = 0

    n = len(src)

    out_chars = []

    state = 'code'  

    while i < n:

        ch = src[i]

        ch2 = src[i:i+2]



        if state == 'code':

            if ch2 == '//' :

                state = 'line_comment'

                i += 2

                continue

            if ch2 == '/*':

                state = 'block_comment'

                i += 2

                continue

            if ch == '"':

                state = 'd_quote'; out_chars.append(ch); i += 1; continue

            if ch == "'":

                state = 's_quote'; out_chars.append(ch); i += 1; continue

            if ch == '`':

                state = 'template'; out_chars.append(ch); i += 1; continue

            out_chars.append(ch); i += 1; continue



        if state == 'line_comment':

            if ch == '\n':

                out_chars.append('\n')

                state = 'code'

            i += 1

            continue



        if state == 'block_comment':

            if ch2 == '*/':

                i += 2

                state = 'code'

            else:

                i += 1

            continue



        if state == 'd_quote':

            if ch == '\\':

                

                out_chars.append(ch)

                if i + 1 < n:

                    out_chars.append(src[i+1])

                    i += 2

                else:

                    i += 1

                continue

            out_chars.append(ch)

            i += 1

            if ch == '"':

                state = 'code'

            continue



        if state == 's_quote':

            if ch == '\\':

                out_chars.append(ch)

                if i + 1 < n:

                    out_chars.append(src[i+1])

                    i += 2

                else:

                    i += 1

                continue

            out_chars.append(ch)

            i += 1

            if ch == "'":

                state = 'code'

            continue



        if state == 'template':

            if ch == '\\':

                out_chars.append(ch)

                if i + 1 < n:

                    out_chars.append(src[i+1])

                    i += 2

                else:

                    i += 1

                continue

            out_chars.append(ch)

            i += 1

            if ch == '`':

                state = 'code'

            continue



    return ''.join(out_chars)





def should_process_file(path: str) -> bool:

    base = os.path.basename(path)

    if base in SKIP_FILES:

        return False

    _, ext = os.path.splitext(base)

    return ext in PY_EXTS or ext in CLIKE_EXTS





def walk_files(root: str) -> Iterable[str]:

    for dirpath, dirnames, filenames in os.walk(root):

        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

        for fn in filenames:

            full = os.path.join(dirpath, fn)

            if should_process_file(full):

                yield full





def main():

    this_dir = os.path.dirname(os.path.abspath(__file__))

    repo_root = os.path.abspath(os.path.join(this_dir, os.pardir, os.pardir))

    root = sys.argv[1] if len(sys.argv) > 1 else repo_root

    processed = 0

    changed = 0

    for path in walk_files(root):

        try:

            with open(path, 'r', encoding='utf-8') as f:

                src = f.read()

        except Exception:

            continue

        new_src = src

        ext = os.path.splitext(path)[1]

        if ext in PY_EXTS:

            new_src = strip_python_comments(src)

        elif ext in CLIKE_EXTS:

            new_src = strip_c_like_comments(src)

        processed += 1

        if new_src != src:

            try:

                with open(path, 'w', encoding='utf-8', newline='') as f:

                    f.write(new_src)

                changed += 1

            except Exception:

                pass

    print(f"Processed {processed} files. Changed {changed} files.")



if __name__ == '__main__':

    main()

