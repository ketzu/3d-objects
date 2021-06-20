from editor3d.undopipeline import Operation


class Object3D:
    def __init__(self, name="Object", position=(0, 0, 0), rotation=(0, 0, 0), color="#dddddd"):
        self.name = name
        self.position = position
        self.rotation = rotation
        self.color = color
        self.parent = None

    def set_parent(self, parent):
        undo = Operation(self.set_parent, self.parent, parent)
        self.parent = parent
        return undo

    def set_color(self, color):
        undo = Operation(self.set_color, self.color, color)
        self.color = color
        return undo

    def set_name(self, name):
        undo = Operation(self.set_name, self.name, name)
        self.name = name
        return undo

    def set_rotation(self, angles):
        undo = Operation(self.set_rotation, self.rotation, angles)
        self.rotation = angles
        return undo

    def set_position(self, position):
        undo = Operation(self.set_position, self.position, position)
        self.position = position
        return undo


class Sphere3D(Object3D):
    def __init__(self, name="Box", position=(0, 0, 0), rotation=(0, 0, 0), color="#dddddd", radius=1):
        super().__init__(name, position, rotation, color)
        self.radius = radius

    def set_radius(self, radius):
        undo = Operation(self.set_position, self.radius, radius)
        self.radius = radius
        return undo


class Box3D(Object3D):
    def __init__(self, name="Box", position=(0, 0, 0), rotation=(0, 0, 0), color="#dddddd", length=1, width=1, height=1):
        super().__init__(name, position, rotation, color)
        self.length = length
        self.width = width
        self.height = height

    def set_width(self, width):
        undo = Operation(self.set_width, self.width, width)
        self.width = width
        return undo

    def set_height(self, height):
        undo = Operation(self.set_height, self.height, height)
        self.height = height
        return undo

    def set_length(self, length):
        undo = Operation(self.set_length, self.length, length)
        self.length = length
        return undo


class STL3D(Object3D):
    def __init__(self, path, name="Box", position=(0, 0, 0), rotation=(0, 0, 0), color="#dddddd", scale=1.0):
        super().__init__(name, position, rotation, scale, color)
        self.path = path

    def set_scale(self, scale):
        undo = Operation(self.set_scale, self.scale, scale)
        self.scale = scale
        return undo
