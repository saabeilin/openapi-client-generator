"""
Command-line interface for OpenAPI Client Generator.

This module provides the entry point for the OpenAPI Client Generator tool.
"""

import argparse
import os
import sys
from pathlib import Path

from .parser import OpenAPIParser
from .generator import (
    RequestsClientGenerator,
    AiohttpClientGenerator,
    HttpxClientGenerator,
)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate Python client libraries from OpenAPI v3 specifications."
    )

    # Required arguments
    parser.add_argument(
        "spec_path",
        help="Path to the OpenAPI specification file (JSON or YAML)",
    )

    # Optional arguments
    parser.add_argument(
        "--requests",
        action="store_true",
        help="Generate a client using the requests library (synchronous)",
    )
    parser.add_argument(
        "--aiohttp",
        action="store_true",
        help="Generate a client using the aiohttp library (asynchronous)",
    )
    parser.add_argument(
        "--httpx",
        action="store_true",
        help="Generate a client using the httpx library (both synchronous and asynchronous)",
    )
    parser.add_argument(
        "--output-dir",
        default=os.getcwd(),
        help="Directory where the generated client will be placed (default: current directory)",
    )
    parser.add_argument(
        "--package-name",
        help="Name of the generated Python package (default: derived from the API title in the spec)",
    )
    parser.add_argument(
        "--no-models",
        action="store_true",
        help="Skip generation of model classes",
    )

    args = parser.parse_args()

    # Validate arguments
    if not any([args.requests, args.aiohttp, args.httpx]):
        parser.error("At least one of --requests, --aiohttp, or --httpx must be specified")

    return args


def main():
    """Main entry point for the OpenAPI Client Generator."""
    args = parse_args()

    try:
        # Parse the OpenAPI specification
        parser = OpenAPIParser()
        spec = parser.parse(args.spec_path)

        # Generate client code
        if args.requests:
            generator = RequestsClientGenerator(
                output_dir=args.output_dir,
                package_name=args.package_name,
                generate_models=not args.no_models,
            )
            generator.generate(spec)
            print(f"Generated requests client in {args.output_dir}")

        if args.aiohttp:
            generator = AiohttpClientGenerator(
                output_dir=args.output_dir,
                package_name=args.package_name,
                generate_models=not args.no_models,
            )
            generator.generate(spec)
            print(f"Generated aiohttp client in {args.output_dir}")

        if args.httpx:
            generator = HttpxClientGenerator(
                output_dir=args.output_dir,
                package_name=args.package_name,
                generate_models=not args.no_models,
            )
            generator.generate(spec)
            print(f"Generated httpx client in {args.output_dir}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
