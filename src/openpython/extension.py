"""IPython magic commands for notebook-first use."""

from __future__ import annotations

import os
import shlex
from getpass import getpass
from typing import Optional

from .assistant import DEFAULT_BASE_URL, OpenPythonError, generate_code


def _prompt_for_openai_key() -> None:
    """Ask once, only when the default hosted provider needs a key."""
    base_url = os.getenv("OPENPYTHON_BASE_URL", DEFAULT_BASE_URL)
    if "api.openai.com" not in base_url or os.getenv("OPENPYTHON_API_KEY") or os.getenv("OPENAI_API_KEY"):
        return
    key = getpass("OpenAI API key (input is hidden): ").strip()
    if not key:
        raise OpenPythonError("No API key entered. Set OPENPYTHON_API_KEY and try again.")
    os.environ["OPENPYTHON_API_KEY"] = key


def load_ipython_extension(ipython) -> None:
    """Register ``%openpython`` and ``%%openpython`` on an IPython shell."""
    from IPython.core.magic import Magics, line_cell_magic, magics_class
    from IPython.display import Code, display

    @magics_class
    class OpenPythonMagics(Magics):
        @line_cell_magic
        def openpython(self, line: str, cell: Optional[str] = None):
            """Generate notebook-ready code. Add --run to a cell to execute it."""
            try:
                args = shlex.split(line)
            except ValueError as exc:
                raise OpenPythonError(f"Could not parse options: {exc}") from None

            run_generated = False
            if args and args[0] in ("--help", "-h"):
                print(
                    "%openpython <short task>       Generate Python code\n"
                    "%%openpython [--run]           Generate code from the cell body\n"
                    "%%openpython --run             Generate and execute in this kernel\n"
                    "\nGenerated code is displayed but not executed unless --run is explicit."
                )
                return None
            if args and args[0] == "--run":
                if cell is None:
                    raise OpenPythonError("Use --run with %%openpython in a cell, not %openpython.")
                run_generated = True
                args = args[1:]

            prompt = " ".join(args) if cell is None else " ".join(args + [cell.strip()]).strip()
            _prompt_for_openai_key()
            code = generate_code(prompt)
            display(Code(code, language="python"))
            if run_generated:
                return self.shell.run_cell(code)
            return None

    ipython.register_magics(OpenPythonMagics)


def start() -> None:
    """Activate the magics in the current notebook's kernel."""
    try:
        from IPython import get_ipython
    except ImportError:
        raise RuntimeError("Openpython needs IPython. Run this from a Jupyter notebook kernel.") from None

    shell = get_ipython()
    if shell is None:
        raise RuntimeError("No active IPython kernel found. Run this inside a Jupyter notebook.")
    load_ipython_extension(shell)
    print("Openpython is ready. Try: %openpython create a list of squares from 1 to 10")
    print("Use %%openpython --run in a cell to generate and execute code. See %openpython --help.")
