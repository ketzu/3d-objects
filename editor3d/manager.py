import sys

from PySide2.Qt3DCore import Qt3DCore
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.QtGui import QVector3D, QColor, QTransform, QQuaternion

from editor3d.objects import Box3D, Sphere3D, STL3D
from editor3d.storage import Storage
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
        self.store = Storage("Shapes.db", ObjectRoot())

        # Scene root object and backend root object setup
        self.object_root = self.store.get_root()
        self.entity_root = Qt3DCore.QEntity()
        self.objects[self.object_root] = [self.entity_root, None, None, None]
        self.entities[self.entity_root] = self.object_root

        self.qt_frontend = QtFrontend(sys.argv, self.entity_root, self)

        # generate objects in case any were loaded
        self.generate_from_root()

        self.qt_frontend.set_known_objects(self.object_root)

    def create_entity(self, mesh, material, transform, root=None):
        entity = Qt3DCore.QEntity(self.entity_root if root is None else root)
        entity.addComponent(mesh)
        entity.addComponent(material)
        entity.addComponent(transform)
        return entity

    def create_shape_from_object(self, obj):
        if isinstance(obj, Sphere3D):
            mesh = Qt3DExtras.QSphereMesh(rings=20, slices=20, radius=obj.radius)
        elif isinstance(obj, Box3D):
            mesh = Qt3DExtras.QCuboidMesh()
            mesh.setXExtent(obj.width)
            mesh.setYExtent(obj.length)
            mesh.setZExtent(obj.height)
        else:
            mesh = Qt3DExtras.QCylinderMesh()

        x, y, z = obj.position
        a, b, c = obj.rotation
        transform = Qt3DCore.QTransform(scale=1.0, translation=QVector3D(x, y, z))
        transform.setRotation(QQuaternion.fromEulerAngles(a, b, c))
        material = Qt3DExtras.QDiffuseSpecularMaterial(diffuse=QColor(obj.color))
        entity = self.create_entity(mesh, material, transform, self.objects[obj.parent][0])

        self.objects[obj] = [entity, mesh, transform, material]
        self.entities[entity] = obj

        return entity

    def _recursive_generation(self, obj):
        entity = self.create_shape_from_object(obj)
        for child in obj.children:
            child_entity = self._recursive_generation(child)
        return entity

    def generate_from_root(self):
        for node in self.object_root.children:
            self._recursive_generation(node)

    def start(self):
        self.qt_frontend.show()
        return self.qt_frontend.exec()

    def update_color(self, obj, color):
        self.undopipeline.add_operation(obj.set_color(color))
        material = self.objects[obj][3]
        material.setDiffuse(QColor(obj.color))
        self.store.schedule_store()

    def update_position(self, obj, position):
        self.undopipeline.add_operation(obj.set_position(position))
        transform = self.objects[obj][2]
        transform.setTranslation(QVector3D(obj.position[0], obj.position[1], obj.position[2]))
        self.store.schedule_store()

    def update_rotation(self, obj, rotation):
        self.undopipeline.add_operation(obj.set_rotation(rotation))
        transform = self.objects[obj][2]
        transform.setRotation(QQuaternion.fromEulerAngles(obj.rotation[0], obj.rotation[1], obj.rotation[2]))
        self.store.schedule_store()

    def update_box_dimension(self, obj, box_dimension):
        self.undopipeline.add_operation(obj.set_dimension(box_dimension))
        mesh = self.objects[obj][1]
        mesh.setXExtent(obj.width)
        mesh.setYExtent(obj.length)
        mesh.setZExtent(obj.height)
        self.store.schedule_store()

    def update_radius(self, obj, radius):
        self.undopipeline.add_operation(obj.set_radius(radius))
        mesh = self.objects[obj][1]
        mesh.setRadius(radius)
        self.store.schedule_store()

    def update_scale(self, obj, scale):
        self.undopipeline.add_operation(obj.set_scale(scale))
        self.store.schedule_store()

    def update_name(self, obj, name):
        self.undopipeline.add_operation(obj.set_name(name))
        self.qt_frontend.set_known_objects(self.object_root)
        self.store.schedule_store()

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
        self.store.schedule_store()

    def delete_object(self, obj):
        obj.set_parent(None)
        entity, mesh, transform, material = self.objects[obj]
        del self.objects[obj]
        del self.entities[entity]
        entity.deleteLater()
        self.undopipeline.clean(obj)
        self.qt_frontend.update_object_editor(None)
        self.qt_frontend.set_known_objects(self.object_root)
        self.store.schedule_store()

    def undo(self):
        target = self.undopipeline.undo()
        if target is not None:
            self.update_object(target)
        self.store.schedule_store()

    def redo(self):
        target = self.undopipeline.redo()
        if target is not None:
            self.update_object(target)
        self.store.schedule_store()

    def create_box(self):
        box = Box3D()
        box.set_parent(self.object_root)

        self.create_shape_from_object(box)

        self.qt_frontend.set_known_objects(self.object_root)
        self.store.schedule_store()

    def create_sphere(self):
        sphere = Sphere3D()
        sphere.set_parent(self.object_root)

        self.create_shape_from_object(sphere)

        self.qt_frontend.set_known_objects(self.object_root)
        self.store.schedule_store()
