import sys

from PySide2.Qt3DCore import Qt3DCore
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.QtGui import QVector3D, QColor, QTransform, QQuaternion

from editor3d.objects import Box3D, Sphere3D, STL3D
from editor3d.undopipeline import Pipeline
from editor3d.window import QtFrontend


class ObjectRoot:
    def __init__(self):
        self.children = set()


class Manager:
    def __init__(self):
        self.entities = {}
        self.objects = {}

        self.undopipeline = Pipeline()

        self.object_root = ObjectRoot()

        # Scene root object to start the rendering tree and Qt Frontend
        self.entity_root = Qt3DCore.QEntity()
        self.qt_frontend = QtFrontend(sys.argv, self.entity_root, self)

        self.qt_frontend.set_known_objects(self.object_root)

    def start(self):
        self.qt_frontend.show()
        return self.qt_frontend.exec()

    def update_color(self, obj, color):
        self.undopipeline.add_operation(obj.set_color(color))
        material = self.objects[obj][3]
        material.setDiffuse(QColor(obj.color))

    def update_position(self, obj, position):
        self.undopipeline.add_operation(obj.set_position(position))
        transform = self.objects[obj][2]
        transform.setTranslation(QVector3D(obj.position[0], obj.position[1], obj.position[2]))

    def update_rotation(self, obj, rotation):
        self.undopipeline.add_operation(obj.set_rotation(rotation))
        transform = self.objects[obj][2]
        transform.setRotation(QQuaternion.fromEulerAngles(obj.rotation[0], obj.rotation[1], obj.rotation[2]))

    def update_box_dimension(self, obj, box_dimension):
        self.undopipeline.add_operation(obj.set_dimension(box_dimension))
        mesh = self.objects[obj][1]
        mesh.setXExtent(obj.width)
        mesh.setYExtent(obj.length)
        mesh.setZExtent(obj.height)

    def update_radius(self, obj, radius):
        self.undopipeline.add_operation(obj.set_radius(radius))
        mesh = self.objects[obj][1]
        mesh.setRadius(radius)

    def update_scale(self, obj, scale):
        self.undopipeline.add_operation(obj.set_scale(scale))

    def update_name(self, obj, name):
        self.undopipeline.add_operation(obj.set_name(name))
        self.qt_frontend.set_known_objects(self.object_root)

    def update_object(self, obj):
        mesh = self.objects[obj][1]
        transform = self.objects[obj][2]
        material = self.objects[obj][3]

        material.setDiffuse(QColor(obj.color))
        transform.setTranslation(QVector3D(obj.position[0], obj.position[1], obj.position[2]))
        transform.setRotation(QQuaternion.fromEulerAngles(obj.rotation[0], obj.rotation[1], obj.rotation[2]))

        if isinstance(obj, Sphere3D):
            mesh.setRadius(obj.radius)
        elif isinstance(obj, Box3D):
            mesh.setXExtent(obj.width)
            mesh.setYExtent(obj.length)
            mesh.setZExtent(obj.height)

        self.qt_frontend.set_known_objects(self.object_root)
        self.qt_frontend.update_object_editor(obj)

    def add_box(self):
        pass

    def add_sphere(self):
        pass

    def add_stl_object(self, path):
        pass

    def undo(self):
        target = self.undopipeline.undo()
        if target is not None:
            self.update_object(target)

    def redo(self):
        target = self.undopipeline.redo()
        if target is not None:
            self.update_object(target)

    def create_entity(self, mesh, material, transform):
        entity = Qt3DCore.QEntity(self.entity_root)
        entity.addComponent(mesh)
        entity.addComponent(material)
        entity.addComponent(transform)
        return entity

    def create_box(self):
        box = Box3D()

        mesh = Qt3DExtras.QCuboidMesh()
        mesh.setXExtent(box.width)
        mesh.setYExtent(box.length)
        mesh.setZExtent(box.height)

        x, y, z = box.position
        transform = Qt3DCore.QTransform(scale=1.0, translation=QVector3D(x, y, z))
        material = Qt3DExtras.QDiffuseSpecularMaterial(diffuse=QColor(box.color))
        entity = self.create_entity(mesh, material, transform)

        self.objects[box] = [entity, mesh, transform, material]
        self.entities[entity] = box

        box.set_parent(self.object_root)

        self.qt_frontend.set_known_objects(self.object_root)

    def create_sphere(self):
        sphere = Sphere3D()

        mesh = Qt3DExtras.QSphereMesh(rings=20, slices=20, radius=sphere.radius)

        x, y, z = sphere.position
        transform = Qt3DCore.QTransform(scale=1.0, translation=QVector3D(x, y, z))
        material = Qt3DExtras.QDiffuseSpecularMaterial(diffuse=QColor(sphere.color))
        entity = self.create_entity(mesh, material, transform)

        self.objects[sphere] = [entity, mesh, transform, material]
        self.entities[entity] = sphere

        sphere.set_parent(self.object_root)

        self.qt_frontend.set_known_objects(self.object_root)
