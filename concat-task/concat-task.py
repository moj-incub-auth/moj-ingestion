#!/usr/bin/env python3
"""
Markdown File Concatenator

This script reads all markdown (.md) files from a directory and concatenates
them into a single output file.
"""

import argparse
import os
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


def process_single_directory(
    source_dir: Path,
    output_file: Path,
    recursive: bool = False,
    exclude: List[str] = None,
    add_separators: bool = True,
    add_filenames: bool = True
) -> bool:
    """
    Process a single directory and concatenate its markdown files.

    Args:
        source_dir: Source directory containing markdown files
        output_file: Output file path
        recursive: Whether to search recursively
        exclude: List of filenames to exclude
        add_separators: Whether to add separators between files
        add_filenames: Whether to add filename headers

    Returns:
        True if successful, False otherwise
    """
    # Find markdown files
    md_files = find_markdown_files(source_dir, recursive)

    # Apply exclusions
    if exclude:
        excluded_names = set(exclude)
        md_files = [f for f in md_files if f.name not in excluded_names]

    if not md_files:
        print(f"⚠️  No markdown files found in: {source_dir}")
        return False

    print(f"   Found {len(md_files)} file(s)")

    # Warn if output file is in the same directory
    if output_file in md_files:
        md_files = [f for f in md_files if f != output_file]

    # Concatenate files
    concatenate_files(
        md_files,
        output_file,
        add_separators=add_separators,
        add_filenames=add_filenames
    )

    return True


def process_batch(
    parent_dir: Path,
    output_dir: Path,
    recursive: bool = False,
    exclude: List[str] = None,
    add_separators: bool = True,
    add_filenames: bool = True
) -> int:
    """
    Process multiple subdirectories in batch mode.

    Args:
        parent_dir: Parent directory containing component subdirectories
        output_dir: Output directory for concatenated files
        recursive: Whether to search recursively within each component
        exclude: List of filenames to exclude
        add_separators: Whether to add separators between files
        add_filenames: Whether to add filename headers

    Returns:
        Number of successfully processed directories
    """
    print(f"🔄 Batch mode: Processing subdirectories in {parent_dir}")
    print(f"📂 Output directory: {output_dir}")
    print()

    # Find all subdirectories
    subdirs = [d for d in parent_dir.iterdir() if d.is_dir()]

    if not subdirs:
        print(f"❌ No subdirectories found in: {parent_dir}")
        return 0

    print(f"📊 Found {len(subdirs)} subdirectory(ies) to process")
    print()

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process each subdirectory
    successful = 0
    failed = 0

    for subdir in sorted(subdirs):
        component_name = subdir.name
        print(f"{'='*60}")
        print(f"Processing: {component_name}")
        print(f"{'='*60}")

        # Create output subdirectory
        #component_output_dir = output_dir / component_name
        #component_output_dir.mkdir(parents=True, exist_ok=True)

        # Create output file
        #output_file = component_output_dir / f"{component_name}-combined.md"
        output_file = output_dir / f"{component_name}-combined.md"

        print(f"   Source: {subdir}")
        print(f"   Output: {output_file}")

        # Process the directory
        success = process_single_directory(
            source_dir=subdir,
            output_file=output_file,
            recursive=recursive,
            exclude=exclude,
            add_separators=add_separators,
            add_filenames=add_filenames
        )

        if success:
            successful += 1
            print(f"✅ Success!")
        else:
            failed += 1
            print(f"❌ Failed!")

        print()

    # Summary
    print(f"{'='*60}")
    print(f"Batch Processing Summary")
    print(f"{'='*60}")
    print(f"Total directories: {len(subdirs)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print()

    return successful


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Concatenate all markdown files from a directory into a single file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  MD_SOURCE_DIR     Directory containing markdown files
  MD_OUTPUT_FILE    Output file path (single mode)
  MD_OUTPUT_DIR     Output directory (batch mode)

Examples:
  # Single directory mode
  python 1_concat_markdown.py ./docs/components/alert -o alert-combined.md

  # Batch mode: process all subdirectories
  python 1_concat_markdown.py ./docs/components --batch --output-dir ./output

  # Batch mode with recursive search in each component
  python 1_concat_markdown.py ./docs/components --batch --output-dir ./output --recursive

  # Using environment variables (batch mode)
  export MD_SOURCE_DIR="./docs/components"
  export MD_OUTPUT_DIR="./output"
  python 1_concat_markdown.py --batch --recursive

  # Concatenate all .md files in current directory
  python 1_concat_markdown.py . -o combined.md

  # Recursively search subdirectories
  python 1_concat_markdown.py ./docs -o all_docs.md --recursive

  # No separators or filenames
  python 1_concat_markdown.py ./notes -o notes.md --no-separators --no-filenames
        """
    )

    parser.add_argument(
        "directory",
        type=str,
        nargs="?",
        help="Directory containing markdown files (overrides MD_SOURCE_DIR env var)"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file path (overrides MD_OUTPUT_FILE env var, default: concatenated.md)"
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

    parser.add_argument(
        "--batch",
        action="store_true",
        help="Batch mode: process all subdirectories as separate components"
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        help="Output directory for batch mode (overrides MD_OUTPUT_DIR env var, default: ./output)"
    )

    args = parser.parse_args()

    # Get directory from args or environment variable
    directory_path = args.directory

    if not directory_path:
        # Try to get from environment variable
        directory_path = os.environ.get('MD_SOURCE_DIR')

    if not directory_path:
        print("❌ Error: No source directory provided")
        print("   Set MD_SOURCE_DIR environment variable or provide directory argument")
        print("\n   Example:")
        print("     export MD_SOURCE_DIR='./docs/components'")
        print("     python 1_concat_markdown.py")
        print("\n   Or:")
        print("     python 1_concat_markdown.py ./docs/components")
        sys.exit(1)

    # Get output path from args or environment variable
    output_path = args.output

    if not output_path:
        # Try to get from environment variable
        output_path = os.environ.get('MD_OUTPUT_FILE')

    if not output_path:
        # Use default
        output_path = "concatenated.md"

    # Validate directory
    directory = Path(directory_path)
    if not directory.exists():
        print(f"❌ Error: Directory does not exist: {directory}")
        sys.exit(1)

    if not directory.is_dir():
        print(f"❌ Error: Not a directory: {directory}")
        sys.exit(1)

    # Handle batch mode
    if args.batch:
        # Get output directory
        output_dir_path = args.output_dir

        if not output_dir_path:
            # Try environment variable
            output_dir_path = os.environ.get('MD_OUTPUT_DIR')

        if not output_dir_path:
            # Use default
            output_dir_path = "./output"

        output_dir = Path(output_dir_path)

        # Process in batch mode
        successful = process_batch(
            parent_dir=directory,
            output_dir=output_dir,
            recursive=args.recursive,
            exclude=args.exclude,
            add_separators=not args.no_separators,
            add_filenames=not args.no_filenames
        )

        if successful > 0:
            print(f"🎉 Done! Successfully processed {successful} component(s)")
        else:
            print(f"❌ No components were successfully processed")
            sys.exit(1)

    else:
        # Single directory mode
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

        # Set up output file (convert string to Path)
        output_file = Path(output_path)

        # Warn if output file is in the same directory and will be included
        if output_file in md_files:
            print(f"⚠️  Warning: Output file {output_file.name} is in the source directory")
            print(f"   It will be excluded from concatenation")
            md_files = [f for f in md_files if f != output_file]

        # Concatenate files
        concatenate_files(
            md_files,
            output_file,
            add_separators=not args.no_separators,
            add_filenames=not args.no_filenames
        )

        print("\n🎉 Done!")


if __name__ == "__main__":
    main()
