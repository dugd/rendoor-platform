import asyncio


_loop: asyncio.AbstractEventLoop | None = None


def get_loop() -> asyncio.AbstractEventLoop:
    """Get or create an event loop for this worker process"""
    global _loop
    if _loop is None or _loop.is_closed():
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)
    return _loop


def clear_loop() -> None:
    """Clear the event loop for this worker process"""
    global _loop
    _loop.close()
    _loop = None
