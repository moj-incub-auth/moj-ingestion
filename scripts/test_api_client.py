#!/usr/bin/env python3
"""
Test client for MOJ Component Search API

Simple Python client to test the search API.
"""

import requests
import json
import sys


class SearchAPIClient:
    """Client for the MOJ Component Search API."""

    def __init__(self, base_url="http://localhost:5000"):
        """
        Initialize the API client.

        Args:
            base_url: Base URL of the API server
        """
        self.base_url = base_url.rstrip('/')

    def health(self):
        """Check API health."""
        response = requests.get(f"{self.base_url}/health")
        return response.json()

    def search(self, message, limit=5):
        """
        Search for components.

        Args:
            message: Natural language query
            limit: Number of results to return

        Returns:
            Dictionary with 'components' key containing results
        """
        response = requests.post(
            f"{self.base_url}/search",
            json={"message": message, "limit": limit},
            headers={"Content-Type": "application/json"}
        )

        if response.status_code != 200:
            raise Exception(f"Search failed: {response.text}")

        return response.json()


def main():
    """Run interactive test client."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Test client for MOJ Component Search API"
    )

    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:5000",
        help="API base URL (default: http://localhost:5000)"
    )

    parser.add_argument(
        "--query",
        "-q",
        type=str,
        help="Search query (if not provided, enters interactive mode)"
    )

    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=5,
        help="Number of results (default: 5)"
    )

    args = parser.parse_args()

    # Initialize client
    client = SearchAPIClient(args.url)

    # Check health
    print("🏥 Checking API health...")
    try:
        health = client.health()
        print(f"✅ Status: {health['status']}")
        if 'entities' in health:
            print(f"📊 Entities in collection: {health['entities']}")
        print()
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        print("   Make sure the API server is running")
        sys.exit(1)

    # Search mode
    if args.query:
        # Single query mode
        print(f"🔍 Searching for: '{args.query}'")
        print()

        try:
            results = client.search(args.query, limit=args.limit)

            print(f"📊 Found {len(results['components'])} component(s):")
            print()

            for idx, component in enumerate(results['components'], 1):
                print(f"Result #{idx}")
                print(f"  Title: {component['title']}")
                print(f"  Description: {component['description'][:100]}...")
                print(f"  URL: {component['url']}")
                print(f"  Parent: {component['parent']}")
                print(f"  Accessibility: {component['accessibility']}")
                print(f"  Has Research: {component['has_research']}")
                print(f"  Views: {component['views']}")
                print()

        except Exception as e:
            print(f"❌ Search failed: {e}")
            sys.exit(1)

    else:
        # Interactive mode
        print("💬 Interactive Mode (Ctrl+C to exit)")
        print("=" * 60)
        print()

        try:
            while True:
                query = input("Enter your query: ").strip()
                if not query:
                    continue

                try:
                    results = client.search(query, limit=args.limit)

                    print()
                    print(f"📊 Found {len(results['components'])} component(s):")
                    print()

                    for idx, component in enumerate(results['components'], 1):
                        print(f"Result #{idx}")
                        print(f"  Title: {component['title']}")
                        print(f"  Description: {component['description'][:100]}...")
                        print(f"  URL: {component['url']}")
                        print()

                    print("-" * 60)
                    print()

                except Exception as e:
                    print(f"❌ Search failed: {e}")
                    print()

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")


if __name__ == "__main__":
    main()
