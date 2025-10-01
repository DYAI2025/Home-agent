#!/usr/bin/env python3
"""Main entry point for the Voice AI Agent stack."""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, urlunparse

from dotenv import load_dotenv

from livekit.agents import WorkerOptions, cli

# Ensure the repository root is on the Python path for package imports
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from voice_ai_agent.integrated_agent import LiveKitVoiceAgent


# Load environment variables as early as possible so local development works
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def _probe_livekit_endpoint(url: str, api_key: str, api_secret: str) -> None:
    """Check whether the configured LiveKit deployment is reachable."""

    from livekit import api  # Imported lazily to avoid unnecessary dependency loading

    timeout = aiohttp_timeout(total=5)
    async with api.LiveKitAPI(url=url, api_key=api_key, api_secret=api_secret, timeout=timeout) as client:
        await client.room.list_rooms()


def aiohttp_timeout(total: float) -> "aiohttp.ClientTimeout":
    from aiohttp import ClientTimeout

    return ClientTimeout(total=total)


def _http_url_from_ws_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"ws", "wss"}:
        return url

    scheme = "https" if parsed.scheme == "wss" else "http"
    return urlunparse(parsed._replace(scheme=scheme))


def _verify_livekit_connectivity(ws_url: str, api_key: str, api_secret: str) -> bool:
    rest_url = _http_url_from_ws_url(ws_url)
    logger.info("Checking LiveKit connectivity at %s", rest_url)

    try:
        asyncio.run(_probe_livekit_endpoint(rest_url, api_key, api_secret))
    except Exception as exc:  # pragma: no cover - best effort logging
        logger.warning("LiveKit connectivity probe failed: %s", exc)
        return False
    else:
        logger.info("LiveKit connectivity verified successfully")
        return True


def _create_worker_options() -> WorkerOptions:
    agent = LiveKitVoiceAgent()
    worker_options = WorkerOptions(entrypoint_fnc=agent.entrypoint)
    return worker_options


def _ensure_default_command(argv: Optional[list[str]] = None) -> None:
    args = argv if argv is not None else sys.argv
    if len(args) == 1:
        args.append("start")


def _gather_livekit_config(worker_options: WorkerOptions) -> tuple[str, Optional[str], Optional[str]]:
    ws_url = os.getenv("LIVEKIT_URL") or worker_options.ws_url
    api_key = os.getenv("LIVEKIT_API_KEY") or worker_options.api_key
    api_secret = os.getenv("LIVEKIT_API_SECRET") or worker_options.api_secret

    return ws_url, api_key, api_secret


def main() -> None:
    """Start the LiveKit worker and the integrated voice agent."""

    logger.info("Starting Voice AI Agent with all features...")

    worker_options = _create_worker_options()
    ws_url, api_key, api_secret = _gather_livekit_config(worker_options)

    default_invocation = len(sys.argv) == 1

    if default_invocation:
        missing = [name for name, value in (
            ("LIVEKIT_API_KEY", api_key),
            ("LIVEKIT_API_SECRET", api_secret),
        ) if not value]

        if missing:
            logger.error(
                "Cannot start LiveKit worker automatically because the following secrets are missing: %s",
                ", ".join(missing),
            )
            raise SystemExit(1)

    if api_key and api_secret:
        _verify_livekit_connectivity(ws_url, api_key, api_secret)

    logger.info("Voice AI Agent is starting...")
    _ensure_default_command()
    cli.run_app(worker_options)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Voice AI Agent stopped by user")
    except Exception as exc:  # pragma: no cover - surface startup failures
        logger.error("Error running Voice AI Agent: %s", exc)
        raise
