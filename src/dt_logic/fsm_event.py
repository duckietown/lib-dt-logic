class FSMEvent:
    """type def for an event in the finite state machine"""
    def __init__(self, uid: str):
        self.uid = uid

    def __repr__(self):
        return self.uid
