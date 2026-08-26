"""Main entry point for running the ClaimIQ Backend API with Uvicorn."""

import sys
import uvicorn
from backend.config import BackendConfig


def main():
    config = BackendConfig()
    if config.is_dev_secret:
        print("[WARNING] Running with development JWT secret. Set CLAIMIQ_JWT_SECRET for production.", file=sys.stderr)

    print(f"Starting ClaimIQ Backend API on {config.api_host}:{config.api_port}...")
    uvicorn.run(
        "backend.app:create_app",
        factory=True,
        host=config.api_host,
        port=config.api_port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
