def __getattr__(name):
    if name in ("root_agent", "coordinator_agent"):
        from .coordinator.agent import coordinator_agent
        return coordinator_agent
    raise AttributeError(f"module 'agents' has no attribute {name!r}")
