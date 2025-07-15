"""CLI runner"""

import asyncio
import sys
from cli_mode import CLIChattyDee

async def main():
    cli = CLIChattyDee()
    await cli.run()

if __name__ == "__main__":
    asyncio.run(main())
