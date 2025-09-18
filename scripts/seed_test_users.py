#!/usr/bin/env python
"""Seed load-test users directly in the database and capture their credentials."""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from uuid import uuid4

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy.exc import IntegrityError

from app import models, utils
from app.database import AsyncSessionLocal


async def _create_users(count: int, password: str, email_prefix: str, domain: str) -> list[dict]:
    created: list[dict] = []
    async with AsyncSessionLocal() as session:
        async with session.begin():
            for _ in range(count):
                email = f"{email_prefix}{uuid4().hex}@{domain}"
                hashed = utils.hash(password)
                user = models.User(email=email, password=hashed)
                session.add(user)
                try:
                    await session.flush()
                except IntegrityError as exc:
                    raise RuntimeError(
                        "User creation failed due to duplicate email. "
                        "Choose a different prefix or domain."
                    ) from exc
                created.append({"id": user.id, "email": email, "password": password})
    return created


def _write_output(path: Path | None, data: list[dict], password: str) -> None:
    payload = {"password": password, "users": data}
    if path is None or str(path) == "-":
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed bulk test users for load testing.")
    parser.add_argument("--count", type=int, default=200, help="Number of users to create (default: 200)")
    parser.add_argument(
        "--password",
        default="LoadTest!234",
        help="Plain-text password assigned to every seeded user (default: LoadTest!234)",
    )
    parser.add_argument(
        "--email-prefix",
        default="loadtest_user_",
        help="Prefix used before the generated email UUID (default: loadtest_user_)",
    )
    parser.add_argument(
        "--domain",
        default="example.com",
        help="Email domain for seeded users (default: example.com)",
    )
    parser.add_argument(
        "--output",
        default=str(ROOT_DIR / "loadtests" / "test_users.json"),
        help="Path to write the credential list (use '-' for stdout)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate sample emails without touching the database",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.dry_run:
        sample = [f"{args.email_prefix}{uuid4().hex}@{args.domain}" for _ in range(min(5, args.count))]
        print("Dry run: would create", args.count, "users with emails like:")
        for email in sample:
            print("  -", email)
        return

    created = asyncio.run(_create_users(args.count, args.password, args.email_prefix, args.domain))

    output_path = None if args.output in {None, "-"} else Path(args.output)
    _write_output(output_path, created, args.password)

    print(f"Seeded {len(created)} users. Credentials written to {args.output}.")


if __name__ == "__main__":
    main()
