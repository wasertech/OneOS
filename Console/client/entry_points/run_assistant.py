import sys
import asyncio

from client.main import main

def run():
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        sys.exit(1)

if __name__ == '__main__':
    run()