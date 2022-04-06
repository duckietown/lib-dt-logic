from dt_logic import logger
from dt_logic.validation import safe_chained_dict_get
from dt_logic.fsm_state import FSMState
from dt_logic.fsm_event import FSMEvent

import networkx as nx
from networkx import DiGraph
from typing import Tuple, List, Dict, Optional
from collections import defaultdict
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def factory_empty_dict():
    return {}


class FSM(DiGraph):
    """Finite state machine implemented using a Directed Graph"""
    def __init__(self,
                 states: List[FSMState],
                 transitions: Dict[FSMEvent, List[Tuple[FSMState, FSMState]]],
                 initial_state: FSMState,
                 **attr
                 ):
        """
        Constructor for a graph-based FSM
        :param states: the list of states
        :param transitions: on each event, a list of possible transitions
        :param initial_state: the initial fsm state
        :param attr: any other attributes
        """
        super().__init__(**attr)

        self.add_nodes_from(states)
        # convenient data structure for transition lookup
        self.event_map = defaultdict(factory_empty_dict)
        for ev, lst_edges in transitions.items():
            self.bind_event(ev, lst_edges)
        assert initial_state in set(self.nodes())
        self._state: FSMState = initial_state
        self._state.enter()

    def bind_event(self,
                   event: FSMEvent,
                   l_edges: List[Tuple[FSMState, FSMState]],
                   ) -> None:
        """
        Bind an event with all its edges
        :param event: the event type
        :param l_edges: the list of edges that acts on this event
        """
        for e0, e1 in l_edges:
            if safe_chained_dict_get(self.event_map, event, e0) is not None:
                logger.warn(
                    f"Redefinition for event [{event}] from state [{e0}].")
            self.event_map[event][e0] = e1
            nodes = set(self.nodes())
            assert e0 in nodes and e1 in nodes
            self.add_edge(e0, e1, event=event)

    def fire_event(self,
                   event: FSMEvent,
                   viz: bool = False,
                   ) -> Tuple[FSMState, Optional[np.ndarray]]:
        """
        Propagate an event to the FSM
        :param event: the event that happened
        :param viz: whether to visualize or not
        :return: a tuple of the current FSMState, and optionally, the visualized FSM as np.ndarray
        """
        curr_state = self._state
        next_state = safe_chained_dict_get(self.event_map, event, self._state)
        if next_state is None:
            logger.debug(
                f"From state [{self._state}], no transition on event [{event}]")
        elif next_state == self._state:
            logger.info(
                f"Self-loop in state [{self._state}] on event [{event}]")
            self._transit_to(next_state)
        else:
            logger.info(
                f"State [{self._state}] -> [{next_state}] on event [{event}]")
            self._transit_to(next_state)

        data = None
        if viz:
            if next_state is not None:
                data = self.visualize(last_event_edge=(curr_state, next_state))
            else:
                data = self.visualize()

        return next_state, data

    def visualize(self,
                  last_event_edge: Optional[Tuple[FSMState, FSMState]] = None,
                  ) -> np.ndarray:
        """
        Visualize the underlying DiGraph for the FSM
        :param last_event_edge: the transition that occurred, if any
        :return: the graph visualization as a np.ndarray
        """
        # settings in matplotlib for obtaining the renderer buffer
        fig = plt.figure()
        fig.add_subplot(111)

        # calculate a graph layout
        pos = nx.circular_layout(self)

        # draw nodes, active - green, inactive - gray
        def draw_nodes(
            nodes: List[FSMState],
            active: bool = False,
        ):
            nx.draw_networkx_nodes(
                self,
                pos=pos,
                nodelist=nodes,
                node_color="gray" if not active else "green",
            )

        inactive = set(self.nodes())
        inactive.remove(self._state)
        draw_nodes(list(inactive), active=False)
        draw_nodes([self._state], active=True)

        # draw node labels
        nx.draw_networkx_labels(
            self,
            pos=pos,
            labels=dict(zip(self.nodes, self.nodes)),
        )

        # draw edges
        nx.draw_networkx_edges(self, pos)

        # draw edge labels, last fired - blue, others - black
        def draw_edge_labels(
            labels: Dict[Tuple[FSMState, FSMState], str],
            is_last_transition: bool = False,
        ):
            nx.draw_networkx_edge_labels(
                self,
                pos=pos,
                edge_labels=labels,
                horizontalalignment="right",
                verticalalignment="top",
                # case wise settings
                font_size=30 if is_last_transition else 20,
                font_color="blue" if is_last_transition else "black",
            )

        edge_labels = dict(zip(
            self.edges, [self[e0][e1]["event"] for e0, e1 in self.edges]
        ))
        if last_event_edge is not None:
            edge_labels.pop(last_event_edge, None)
            e0, e1 = last_event_edge
            last_event_edge_label = {last_event_edge: self[e0][e1]["event"]}
            draw_edge_labels(last_event_edge_label, is_last_transition=True)

        draw_edge_labels(edge_labels, is_last_transition=False)

        # obtain the image from matplotlib renderer
        fig.canvas.draw()
        data = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        return data

    def _transit_to(self, next_state: FSMState) -> None:
        """
        perform exit actions on current, and entry actions for next
        :param next_state: the state to transit into
        """
        # fixme 1: better options than this, to enforce entry and exit actions
        # fixme 2: atomic operations
        self._state.exit()
        self._state = next_state
        self._state.enter()
        # todo: what happens for the ending states?
        # for our scenario, if the fsm never exits, no need to worry;

    @property
    def current_state(self) -> FSMState:
        """get current state"""
        return self._state
