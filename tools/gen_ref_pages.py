"""Generate the code reference pages and navigation."""

from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

root = Path(__file__).parent.parent
src = root / "extraction_methods"

for path in sorted(src.rglob("*.py")):
    print("PATH", path)
    module_path = path.relative_to(src).with_suffix("")
    print("MODULE PATH", module_path)
    doc_path = path.relative_to(src).with_suffix(".md")
    print("DOC PATH", doc_path)
    full_doc_path = Path("reference", doc_path)
    print("FULL DOC PATH", full_doc_path)

    parts = tuple(module_path.parts)
    print("PARTS", parts)

    if parts[-1] == "__init__":
        continue
        parts = parts[:-1]
        doc_path = doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")
    elif parts[-1] == "__main__":
        continue

    if not parts:
        continue

    nav[parts] = doc_path.as_posix()

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        ident = ".".join(parts)
        fd.write(f"::: {ident}")

    mkdocs_gen_files.set_edit_path(full_doc_path, path.relative_to(root))

with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
