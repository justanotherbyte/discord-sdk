from .state import State

class AbstractContext:
    """
    A class that houses some common methods that all context's will have.
    """
    _state: State # set after context object is created

    async def send(self):
        raise NotImplementedError
    