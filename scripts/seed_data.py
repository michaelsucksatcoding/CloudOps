"""Seed baseline database and services."""

import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def seed_database() -> None:
    """Seed initial monitored services and metadata."""
    logger.info("Seeding initial service records...")
    services = [
        "payment-api",
        "auth-service",
        "order-processor",
        "notification-service",
    ]
    for s in services:
        logger.info("  Seeded service: %s", s)
    logger.info("Database seeding complete.")


if __name__ == "__main__":
    seed_database()
