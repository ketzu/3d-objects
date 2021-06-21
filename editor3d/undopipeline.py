class Operation:
    def __init__(self, target, setter, from_value, to_value):
        self.target = target
        self.setter = setter
        self.from_value = from_value
        self.to_value = to_value

    def undo(self):
        self.setter(self.from_value)

    def redo(self):
        self.setter(self.to_value)


class Pipeline:
    def __init__(self):
        self.queue = []
        # points to the last exectued operation
        self.position = -1

    def clean(self, target):
        queue = [_ for _ in self.queue if _.target is not target]
        self.position -= len(self.queue) - len(queue)
        self.queue = queue

    def undo(self):
        if 0 <= self.position < len(self.queue):
            op = self.queue[self.position]
            op.undo()
            self.position -= 1
            return op.target
        return None

    def redo(self):
        if self.position+1 < len(self.queue):
            op = self.queue[self.position+1]
            op.redo()
            self.position += 1
            return op.target
        return None

    def add_operation(self, op):
        self.queue = self.queue[:self.position+1]
        self.queue.append(op)
        self.position += 1
