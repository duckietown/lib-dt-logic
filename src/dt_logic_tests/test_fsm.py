import random
from random import randint, shuffle
from typing import List
from types import SimpleNamespace
import unittest

from dt_logic import FSM, FSMState, FSMEvent


NUM_TESTS_RAND = 1000
MAX_STATES = 100


def test_sequential_state_transitions():
    """
    Test for (NUM_TESTS_RAND) times with maximum (MAX_STATES) states,
    that transitions are correct in a sequential fsm
    """
    random.seed(41)

    for _ in range(NUM_TESTS_RAND):
        lst = list(map(str, range(randint(1, MAX_STATES))))
        shuffle(lst)

        states = [FSMState(s) for s in lst]
        ev_self = FSMEvent("a")
        ev_inter = FSMEvent("b")
        transitions = {
            ev_self: [(s, s) for s in states],
            ev_inter: [(s0, s1) for s0, s1 in zip(states[:-1], states[1:])],
        }
        fsm = FSM(states, transitions, states[0])
        yield(
            check_sequential_transition,
            states, fsm,
            ev_self, randint(0, len(states)),
            ev_inter, randint(0, len(states) - 1),
        )


def check_sequential_transition(states: List[FSMState],
                                fsm: FSM,
                                ev_self: FSMEvent,
                                num_self_trans: int,
                                ev_inter: FSMEvent,
                                num_inter_trans: int,
                                ):

    true_res = states[num_inter_trans]
    # perform transitions
    events = [ev_self] * num_self_trans + [ev_inter] * num_inter_trans
    shuffle(events)
    st = fsm.current_state
    for ev in events:
        st, _ = fsm.fire_event(ev)
    print(list(fsm.nodes()), num_self_trans, num_inter_trans)
    print(st, true_res)
    assert st == true_res


class TestFSMEdgeCase(unittest.TestCase):
    def test_invalid_initial_state(self):
        self.assertRaises(
            AssertionError,
            FSM,
            states=[],
            transitions={},
            initial_state=None,
        )

    def test_one_state(self):
        a = FSMState("a")
        FSM(states=[a], transitions={}, initial_state=a)

    def test_wrong_transition_node(self):
        a = FSMState("a")
        self.assertRaises(
            AssertionError,
            FSM,
            states=[a],
            transitions={FSMEvent("e0"): [(a, FSMState("non exist"))]},
            initial_state=a,
        )


class TestFSMTransitions(unittest.TestCase):
    def test_self_transition(self):
        sa = FSMState("a")
        e0 = FSMEvent("e0")
        fsm = FSM(states=[sa], transitions={e0: [(sa, sa)]}, initial_state=sa)
        fsm.fire_event(e0)
        self.assertEqual(sa, fsm.current_state)

    def test_single_transition(self):
        sa, sb = FSMState("a"), FSMState("b")
        e0 = FSMEvent("e0")
        fsm = FSM(states=[sa, sb],
                  transitions={e0: [(sa, sb)]},
                  initial_state=sa)
        self.assertEqual(sa, fsm.current_state)
        fsm.fire_event(e0)
        self.assertEqual(sb, fsm.current_state)

    def test_event_no_transition(self):
        sa, sb = FSMState("a"), FSMState("b")
        e0, e1 = FSMEvent("e0"), FSMEvent("e1")
        fsm = FSM(states=[sa, sb],
                  transitions={e0: [(sa, sb)], e1: [(sb, sa)]},
                  initial_state=sa)
        self.assertEqual(sa, fsm.current_state)
        fsm.fire_event(e1)
        self.assertEqual(sa, fsm.current_state)

    def test_circular_transitions(self):
        sa, sb = FSMState("sa"), FSMState("sb")
        e0, e1 = FSMEvent("e0"), FSMEvent("e1")
        fsm = FSM(states=[sa, sb],
                  transitions={e0: [(sa, sb)], e1: [(sb, sa)]},
                  initial_state=sa)
        for i in range(42):
            fsm.fire_event(e0 if i % 2 == 0 else e1)
        self.assertEqual(sa, fsm.current_state)
        for i in range(199):
            fsm.fire_event(e0 if i % 2 == 0 else e1)
        self.assertEqual(sb, fsm.current_state)


def simple_action(instance: SimpleNamespace, amount: int = 1):
    instance.x += amount


class TestFSMStateActions(unittest.TestCase):
    ns = SimpleNamespace()

    def test_entry_action(self):
        """test entry actions and args"""
        self.ns.x = 0
        sa = FSMState("sa", entry_actions=simple_action, entry_args=[self.ns])
        _ = FSM([sa], {}, sa)
        self.assertEqual(self.ns.x, 1)

    def test_exit_action(self):
        """test exit actions and kwargs"""
        self.ns.x = 0
        inc_amount = 5
        sa = FSMState(
            "sa",
            exit_actions=simple_action,
            exit_kwargs={"instance": self.ns, "amount": inc_amount},
        )
        sb = FSMState("sb")
        ev = FSMEvent("e0")
        fsm = FSM([sa, sb], {ev: [(sa, sb)]}, sa)
        self.assertEqual(self.ns.x, 0)
        fsm.fire_event(ev)
        self.assertEqual(self.ns.x, inc_amount)
