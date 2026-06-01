import py_compile
import warnings
from pathlib import Path


def test_gui_modules_compile_without_syntax_warnings(tmp_path):
    sources = sorted(Path("faster_whisper_GUI").glob("*.py"))
    syntax_warnings = []

    for source in sources:
        compiled = tmp_path / f"{source.stem}.pyc"
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", SyntaxWarning)
            py_compile.compile(str(source), cfile=str(compiled), doraise=True)

        syntax_warnings.extend(
            f"{source}: {warning.message}"
            for warning in caught
            if issubclass(warning.category, SyntaxWarning)
        )

    assert syntax_warnings == []
