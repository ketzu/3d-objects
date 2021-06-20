import sys

from PySide2.Qt3DCore import Qt3DCore
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.QtGui import QVector3D, QColor

from editor3d.objects import Box3D, Sphere3D, STL3D
from editor3d.window import QtFrontend


class ObjectRoot:
    def __init__(self):
        self.children = set()


class Manager:
    def __init__(self):
        self.entities = {}
        self.objects = {}

        self.object_root = ObjectRoot()

        # Scene root object to start the rendering tree and Qt Frontend
        self.entity_root = Qt3DCore.QEntity()
        self.qt_frontend = QtFrontend(sys.argv, self.entity_root)

        self.create_box().set_parent(self.object_root)
        self.create_sphere().set_parent(self.object_root)

        self.qt_frontend.set_known_objects(self.object_root)

    def start(self):
        self.qt_frontend.show()
        return self.qt_frontend.exec()

    def create_entity(self, mesh, material, transform):
        entity = Qt3DCore.QEntity(self.entity_root)
        entity.addComponent(mesh)
        entity.addComponent(material)
        entity.addComponent(transform)
        return entity

    def create_box(self):
        box = Box3D()

        mesh = Qt3DExtras.QCuboidMesh()
        mesh.setXExtent(box.length)
        mesh.setZExtent(box.height)
        mesh.setYExtent(box.width)

        x, y, z = box.position
        transform = Qt3DCore.QTransform(scale=1.0, translation=QVector3D(x, y, z))
        material = Qt3DExtras.QPhongMaterial(diffuse=QColor(box.color))
        entity = self.create_entity(mesh, material, transform)

        self.objects[box] = [entity, mesh, transform, material]
        self.entities[entity] = box
        return box

    def create_sphere(self):
        sphere = Sphere3D()

        mesh = Qt3DExtras.QSphereMesh(rings=20, slices=20, radius=sphere.radius)

        x, y, z = sphere.position
        transform = Qt3DCore.QTransform(scale=1.0, translation=QVector3D(x, y, z))
        material = Qt3DExtras.QPhongMaterial(diffuse=QColor(sphere.color))
        entity = self.create_entity(mesh, material, transform)

        self.objects[sphere] = [entity, mesh, transform, material]
        self.entities[entity] = sphere
        return sphere
