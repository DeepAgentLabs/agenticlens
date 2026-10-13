"""Handoff sequence helpers shared by diagnosis rules and evaluators."""

from collections.abc import Sequence


def count_round_trips(transitions: Sequence[tuple[str, str]]) -> int:
    """Non-overlapping A->B immediately followed by B->A, in chronological order.

    `A->B, B->A, A->B, B->A` is two round trips; grouped handoffs such as
    `A->B, A->B, B->A, B->A` are one, because only one reversal alternates.
    """
    trips = 0
    index = 0
    while index < len(transitions) - 1:
        source, target = transitions[index]
        if transitions[index + 1] == (target, source):
            trips += 1
            index += 2
        else:
            index += 1
    return trips
