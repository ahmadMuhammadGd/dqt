from importlib.metadata import entry_points


class MissingExecutorError(Exception): ...


def get_executor(executor: str):
    eps = entry_points(group="dqt.executors")
    match = next((ep for ep in eps if ep.name == executor), None)
    if not match:
        raise MissingExecutorError(
            f"Install dqt-executor-{executor} to use this engine"
        )
    return match.load()


def get_artifact_store(artifact_store: str):
    eps = entry_points(group="dqt.artifacts")
    match = next((ep for ep in eps if ep.name == artifact_store), None)
    if not match:
        raise MissingExecutorError(
            f"Install dqt-artifact-{artifact_store} to use this store"
        )
    return match.load()
