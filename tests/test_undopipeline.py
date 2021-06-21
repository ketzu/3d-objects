import unittest
from editor3d.undopipeline import *


class MockTarget:
    def __init__(self, value):
        self.value = value

    def set(self, value):
        self.value = value


class TestOperation(unittest.TestCase):
    def test_simple(self):
        target = MockTarget(20)
        self.assertEqual(target.value, 20)
        op = Operation(target, target.set, 15, 20)

        op.undo()
        self.assertEqual(target.value, 15)

        op.redo()
        self.assertEqual(target.value, 20)


class TestPipeline(unittest.TestCase):
    def test_empty(self):
        pipeline = Pipeline()
        self.assertEqual(len(pipeline.queue), 0)
        self.assertEqual(pipeline.position, -1)

        pipeline.undo()
        self.assertEqual(len(pipeline.queue), 0)
        self.assertEqual(pipeline.position, -1)

        pipeline.redo()
        self.assertEqual(len(pipeline.queue), 0)
        self.assertEqual(pipeline.position, -1)

    def test_simple(self):
        target = MockTarget(20)
        pipeline = Pipeline()

        self.assertEqual(target.value, 20)
        self.assertEqual(len(pipeline.queue), 0)
        self.assertEqual(pipeline.position, -1)

        pipeline.add_operation(Operation(target, target.set, 15, 20))
        self.assertEqual(len(pipeline.queue), 1)
        self.assertEqual(pipeline.position, 0)

        pipeline.redo()
        self.assertEqual(target.value, 20)
        self.assertEqual(len(pipeline.queue), 1)
        self.assertEqual(pipeline.position, 0)

        pipeline.undo()
        self.assertEqual(target.value, 15)
        self.assertEqual(len(pipeline.queue), 1)
        self.assertEqual(pipeline.position, -1)

        pipeline.redo()
        self.assertEqual(target.value, 20)
        self.assertEqual(len(pipeline.queue), 1)
        self.assertEqual(pipeline.position, 0)

    def test_multiple(self):
        target1 = MockTarget(20)
        target2 = MockTarget(0)
        pipeline = Pipeline()

        self.assertEqual(target1.value, 20)
        self.assertEqual(target2.value, 0)
        self.assertEqual(len(pipeline.queue), 0)
        self.assertEqual(pipeline.position, -1)

        pipeline.add_operation(Operation(target2, target2.set, 50, 10))
        pipeline.add_operation(Operation(target1, target1.set, 40, 4))
        pipeline.add_operation(Operation(target1, target1.set, 4, 15))
        pipeline.add_operation(Operation(target1, target1.set, 15, 20))
        pipeline.add_operation(Operation(target2, target2.set, 10, 0))

        self.assertEqual(len(pipeline.queue), 5)
        self.assertEqual(pipeline.position, 4)

        pipeline.undo()
        self.assertEqual(target2.value, 10)
        self.assertEqual(len(pipeline.queue), 5)
        self.assertEqual(pipeline.position, 3)

        pipeline.undo()
        self.assertEqual(target1.value, 15)
        self.assertEqual(len(pipeline.queue), 5)
        self.assertEqual(pipeline.position, 2)

        pipeline.undo()
        self.assertEqual(target1.value, 4)
        self.assertEqual(len(pipeline.queue), 5)
        self.assertEqual(pipeline.position, 1)

        target2.set(0)
        pipeline.add_operation(Operation(target2, target2.set, 10, 0))
        self.assertEqual(target2.value, 0)
        self.assertEqual(len(pipeline.queue), 3)
        self.assertEqual(pipeline.position, 2)
