from itertools import count


class Decider:
    def __init__(self, decisions):
        self._decisions = decisions
        self._index_iter = count(0)

    def get_item(self, collection):
        index = next(self._index_iter)
        count = len(collection)

        if index == len(self._decisions):
            self._decisions.append(count - 1)

        return collection[count - self._decisions[index] - 1]

    def get(self, *items):
        return self.get_item(items)

    def get_boolean(self):
        return self.get(False, True)


def iter_decisions(decision_fn):
    decider_sequence = []

    while True:
        yield decision_fn(Decider(decider_sequence))

        while decider_sequence:
            if decider_sequence[-1] > 0:
                break

            decider_sequence.pop()
        else:
            return

        decider_sequence[-1] -= 1
