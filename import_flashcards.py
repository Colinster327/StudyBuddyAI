#!/usr/bin/env python3
"""
CLI tool to import flashcards from JSON into the database.

Usage:
    python import_flashcards.py <json_file> [--clear]
    
Examples:
    python import_flashcards.py os-flashcards.json
    python import_flashcards.py os-flashcards.json --clear
"""

import sys
import argparse
import os
from database import init_database, import_flashcards_from_json, count_flashcards


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def main():
    parser = argparse.ArgumentParser(
        description='Import flashcards from JSON into StudyBuddyAI database'
    )
    parser.add_argument(
        'json_file',
        type=str,
        help='Path to JSON file containing flashcards'
    )
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear existing flashcards before importing'
    )
    
    args = parser.parse_args()
    
    # Validate file exists
    if not os.path.exists(args.json_file):
        print(f"{Colors.RED}Error: File '{args.json_file}' not found{Colors.END}")
        sys.exit(1)
    
    print()
    print(f"{Colors.BOLD}{Colors.BLUE}StudyBuddyAI Flashcard Import Tool{Colors.END}")
    print(f"{Colors.BLUE}{'=' * 50}{Colors.END}")
    print()
    
    # Initialize database (creates tables if they don't exist)
    print(f"{Colors.CYAN}Initializing database...{Colors.END}")
    init_database()
    
    # Check current flashcard count
    current_count = count_flashcards()
    print(f"{Colors.CYAN}Current flashcards in database: {current_count}{Colors.END}")
    
    if args.clear and current_count > 0:
        print(f"{Colors.YELLOW}Warning: --clear flag will delete all existing flashcards{Colors.END}")
        response = input("Are you sure? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print(f"{Colors.YELLOW}Import cancelled{Colors.END}")
            sys.exit(0)
    
    print()
    print(f"{Colors.CYAN}Importing from: {args.json_file}{Colors.END}")
    
    # Import flashcards
    imported_count = import_flashcards_from_json(args.json_file, clear_existing=args.clear)
    
    if imported_count > 0:
        new_count = count_flashcards()
        print()
        print(f"{Colors.GREEN}{Colors.BOLD}✓ Success!{Colors.END}")
        print(f"{Colors.GREEN}Imported {imported_count} flashcards{Colors.END}")
        print(f"{Colors.GREEN}Total flashcards in database: {new_count}{Colors.END}")
        print()
    else:
        print()
        print(f"{Colors.RED}Failed to import flashcards. Check the JSON file format.{Colors.END}")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()
