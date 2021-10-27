import mkdocs_gen_files

with mkdocs_gen_files.open("automatically_generated.md", "w") as f:
    print("Hello, world!", file=f)
