class Operation:
    def __init__(self, setter, from_value, to_value):
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

    def undo(self):
        if 0 <= self.position < len(self.queue):
            self.queue[self.position].undo()
            self.position -= 1

    def redo(self):
        if self.position+1 < len(self.queue):
            self.queue[self.position+1].redo()
            self.position += 1

    def add_operation(self, op):
        self.queue = self.queue[:self.position+1]
        self.queue.append(op)
        self.position += 1
