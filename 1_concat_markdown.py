#!/usr/bin/env python3
"""
Markdown File Concatenator

This script reads all markdown (.md) files from a directory and concatenates
them into a single output file.
"""

import argparse
from pathlib import Path
from typing import List
import sys


def find_markdown_files(directory: Path, recursive: bool = False) -> List[Path]:
    """
    Find all markdown files in the given directory.

    Args:
        directory: Path to the directory to search
        recursive: If True, search subdirectories recursively

    Returns:
        List of Path objects for markdown files
    """
    if recursive:
        # Recursively find all .md files
        md_files = sorted(directory.rglob("*.md"))
    else:
        # Find .md files only in the top-level directory
        md_files = sorted(directory.glob("*.md"))

    return md_files


def concatenate_files(
    files: List[Path],
    output_file: Path,
    add_separators: bool = True,
    add_filenames: bool = True
) -> None:
    """
    Concatenate markdown files into a single output file.

    Args:
        files: List of file paths to concatenate
        output_file: Path to the output file
        add_separators: If True, add visual separators between files
        add_filenames: If True, add filename headers before each file's content
    """
    print(f"📝 Concatenating {len(files)} markdown files...")

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for idx, file_path in enumerate(files):
            print(f"   [{idx+1}/{len(files)}] Reading: {file_path.name}")

            # Add filename header
            if add_filenames:
                outfile.write(f"# Source: {file_path.name}\n\n")
                if file_path.relative_to(file_path.parent.parent) != file_path.name:
                    outfile.write(f"*Path: {file_path}*\n\n")

            # Read and write file content
            try:
                content = file_path.read_text(encoding='utf-8')
                outfile.write(content)

                # Ensure content ends with newline
                if not content.endswith('\n'):
                    outfile.write('\n')

            except Exception as e:
                print(f"   ⚠️  Warning: Could not read {file_path.name}: {e}")
                outfile.write(f"\n*[Error reading file: {e}]*\n")

            # Add separator between files (except after the last file)
            if add_separators and idx < len(files) - 1:
                outfile.write("\n---\n\n")

    print(f"✅ Successfully created: {output_file}")
    print(f"📊 Total size: {output_file.stat().st_size:,} bytes")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Concatenate all markdown files from a directory into a single file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Concatenate all .md files in current directory
  python 1_concat_markdown.py . -o combined.md

  # Recursively search subdirectories
  python 1_concat_markdown.py ./docs -o all_docs.md --recursive

  # No separators or filenames
  python 1_concat_markdown.py ./notes -o notes.md --no-separators --no-filenames

  # Specify custom output location
  python 1_concat_markdown.py ./input -o /tmp/output.md
        """
    )

    parser.add_argument(
        "directory",
        type=str,
        help="Directory containing markdown files"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        default="concatenated.md",
        help="Output file path (default: concatenated.md)"
    )

    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Search subdirectories recursively"
    )

    parser.add_argument(
        "--no-separators",
        action="store_true",
        help="Don't add separators between files"
    )

    parser.add_argument(
        "--no-filenames",
        action="store_true",
        help="Don't add filename headers before each file's content"
    )

    parser.add_argument(
        "--exclude",
        type=str,
        nargs="+",
        help="Exclude files matching these patterns (e.g., README.md CHANGELOG.md)"
    )

    args = parser.parse_args()

    # Validate directory
    directory = Path(args.directory)
    if not directory.exists():
        print(f"❌ Error: Directory does not exist: {directory}")
        sys.exit(1)

    if not directory.is_dir():
        print(f"❌ Error: Not a directory: {directory}")
        sys.exit(1)

    # Find markdown files
    print(f"🔍 Searching for markdown files in: {directory}")
    if args.recursive:
        print("   (Searching recursively)")

    md_files = find_markdown_files(directory, args.recursive)

    # Apply exclusions
    if args.exclude:
        excluded_names = set(args.exclude)
        original_count = len(md_files)
        md_files = [f for f in md_files if f.name not in excluded_names]
        excluded_count = original_count - len(md_files)
        if excluded_count > 0:
            print(f"   Excluded {excluded_count} file(s)")

    if not md_files:
        print("❌ No markdown files found!")
        sys.exit(1)

    print(f"✅ Found {len(md_files)} markdown file(s):")
    for f in md_files:
        print(f"   - {f.relative_to(directory) if args.recursive else f.name}")

    # Set up output file
    output_path = Path(args.output)

    # Warn if output file is in the same directory and will be included
    if output_path in md_files:
        print(f"⚠️  Warning: Output file {output_path.name} is in the source directory")
        print(f"   It will be excluded from concatenation")
        md_files = [f for f in md_files if f != output_path]

    # Concatenate files
    concatenate_files(
        md_files,
        output_path,
        add_separators=not args.no_separators,
        add_filenames=not args.no_filenames
    )

    print("\n🎉 Done!")


if __name__ == "__main__":
    main()
