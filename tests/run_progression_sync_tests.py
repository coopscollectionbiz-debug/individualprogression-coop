"""Compile the production progression functions against instrumented player/group doubles.

Run with a C++17 compiler on PATH:
    python tests/run_progression_sync_tests.py [--compiler cl]
MSVC requires a Developer Command Prompt. No database or server is started.
"""
import argparse
from pathlib import Path
import subprocess
import tempfile


def extract(source, signature):
    start = source.index(signature)
    opening = source.index("{", start)
    depth = 1
    end = opening + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[start:end].replace(" override", "")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", default="c++")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    implementation = (root / "src/IndividualProgression.cpp").read_text()
    hooks = (root / "src/IndividualProgressionPlayer.cpp").read_text()
    functions = "\n\n".join(extract(implementation, signature) for signature in (
        "uint8 IndividualProgression::GetPlayerProgressionFromQuests",
        "void IndividualProgression::ForceUpdateProgressionState",
        "void IndividualProgression::SyncBotsProgressionToLeader",
    ))
    functions += "\nstruct Hooks\n{\n" + "\n".join(extract(hooks, signature) for signature in (
        "bool OnPlayerCanGroupAccept", "void OnAddMember",
    )) + "\n};\n"
    with tempfile.TemporaryDirectory(prefix="ip-progression-") as directory:
        output = Path(directory)
        (output / "production.inc").write_text(functions)
        executable = output / "progression-tests.exe"
        source = str(root / "tests/progression_sync.cpp")
        if Path(args.compiler).stem.lower() == "cl":
            command = [args.compiler, "/nologo", "/std:c++17", "/EHsc", "/W4", "/WX",
                       f"/I{output}", source, f"/Fe:{executable}", f"/Fo:{output / 'test.obj'}"]
        else:
            command = [args.compiler, "-std=c++17", "-Wall", "-Wextra", "-Werror",
                       "-I", str(output), source, "-o", str(executable)]
        subprocess.run(command, cwd=output, check=True)
        subprocess.run([str(executable)], check=True)


if __name__ == "__main__":
    main()
