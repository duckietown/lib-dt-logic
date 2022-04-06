from typing import List, Callable, Dict, Optional
from dt_logic import logger


class FSMState:
    def __init__(self,
                 uid: str,
                 entry_actions: Optional[Callable] = None,
                 entry_args: Optional[List] = None,
                 entry_kwargs: Optional[Dict] = None,
                 exit_actions: Optional[Callable] = None,
                 exit_args: Optional[List] = None,
                 exit_kwargs: Optional[Dict] = None,
                 ):
        """
        State type for the FSM
        :param uid: unique identifier
        :param entry_actions: a callback when entering the state
        :param entry_args: enter-callback args
        :param entry_kwargs:  enter-callback keyword args
        :param exit_actions: a callback when exiting the state
        :param exit_args: exit-callback args
        :param exit_kwargs: exit-callback keyword args
        """
        self.uid = uid

        self.entry_actions = entry_actions
        self.entry_args = [] if entry_args is None else entry_args
        self.entry_kwargs = {} if entry_kwargs is None else entry_kwargs

        self.exit_actions = exit_actions
        self.exit_args = [] if exit_args is None else exit_args
        self.exit_kwargs = {} if exit_kwargs is None else exit_kwargs
        # FIXME: is it necessary to allow callback time param passing?

    def enter(self):
        if self.entry_actions is not None:
            logger.debug(f"Entry actions: state [{self.uid}]")
            self.entry_actions(*self.entry_args, **self.entry_kwargs)

    def exit(self):
        if self.exit_actions is not None:
            logger.debug(f"Exit actions: state [{self.uid}]")
            self.exit_actions(*self.exit_args, **self.exit_kwargs)

    def __repr__(self):
        return self.uid
