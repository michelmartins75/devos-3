#!/usr/bin/env python3
"""Idempotent development seed for DevOS 3.0 tenants and users."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]

TENANTS = [
    ("portalliz", "own", "unrestricted"),
    ("zev-lur", "own", "unrestricted"),
    ("nau", "own", "unrestricted"),
]

USERS = [
    ("michel@forgeworks.digital", "Michel Martins", "owner"),
    ("daniel@forgeworks.digital", "Daniel Castro", "owner"),
    ("andre@forgeworks.digital", "André", "operator"),
]


def _migrator_dsn() -> str:
    return os.getenv(
        "DATABASE_MIGRATOR_URL",
        "postgresql://devos_migrator:devos_migrator@localhost:5432/devos_app",
    )


def main() -> int:
    conn = psycopg.connect(_migrator_dsn(), autocommit=True)
    try:
        with conn.cursor() as cur:
            tenant_ids: dict[str, str] = {}
            for name, tenant_class, policy in TENANTS:
                cur.execute(
                    """
                    INSERT INTO tenants (
                        name, class, motor_version, inference_policy, data_residency, status
                    )
                    VALUES (%s, %s, '0.1.0', %s, 'eu', 'active')
                    ON CONFLICT (name) DO UPDATE SET status = EXCLUDED.status
                    RETURNING id
                    """,
                    (name, tenant_class, policy),
                )
                row = cur.fetchone()
                assert row is not None
                tenant_ids[name] = str(row[0])

            for email, display_name, role in USERS:
                cur.execute(
                    """
                    INSERT INTO users (email, display_name, status)
                    VALUES (%s, %s, 'active')
                    ON CONFLICT (email) DO UPDATE SET display_name = EXCLUDED.display_name
                    RETURNING id
                    """,
                    (email, display_name),
                )
                inserted = cur.fetchone()
                assert inserted is not None
                user_id = inserted[0]

                for tenant_name in tenant_ids:
                    cur.execute(
                        """
                        INSERT INTO memberships (user_id, tenant_id, role)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (user_id, tenant_id) DO UPDATE SET role = EXCLUDED.role
                        """,
                        (user_id, tenant_ids[tenant_name], role),
                    )

        print("Seed completed successfully.")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
