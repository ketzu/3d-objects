from PySide2.Qt3DInput import Qt3DInput
from PySide2.Qt3DRender import Qt3DRender
from PySide2.Qt3DCore import Qt3DCore
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.QtCore import QSize, Qt
from PySide2.QtGui import QColor, QVector3D
from PySide2.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QTreeWidget

from editor3d.objects import Sphere3D, Box3D, STL3D


class MainWindow:
    def __setup_lit_camera(self, camera):
        camera.lens().setPerspectiveProjection(45.0, 16.0 / 9.0, 0.1, 1000.0)
        camera.setPosition(QVector3D(0, 0, 20))
        camera.setUpVector(QVector3D(0, 1, 0))
        camera.setViewCenter(QVector3D(0, 0, 0))

        light_entity = Qt3DCore.QEntity(camera)
        light = Qt3DRender.QPointLight(light_entity)
        light.setColor("white")
        light.setIntensity(1)
        light_entity.addComponent(light)
        light_transform = Qt3DCore.QTransform(light_entity)
        light_transform.setTranslation(camera.position())
        light_entity.addComponent(light_transform)

    def __setup_basic_layout(self):
        self.window3d = Qt3DExtras.Qt3DWindow()
        self.window3d.defaultFrameGraph().setClearColor(QColor("#4d4d4f"))

        self.container = QWidget.createWindowContainer(self.window3d)
        self.container.setMinimumSize(QSize(200, 100))
        self.container.setMaximumSize(self.window3d.screen().size())

        self.widget = QWidget()
        hlayout = QHBoxLayout(self.widget)
        vlayout = QVBoxLayout()
        vlayout.setAlignment(Qt.AlignTop)
        hlayout.addWidget(self.container, 1)
        hlayout.addLayout(vlayout)

        box_button = QPushButton("Add Box")
        sphere_button = QPushButton("Add Sphere")
        stl_button = QPushButton("Load from stl")

        vlayout.addWidget(box_button)
        vlayout.addWidget(sphere_button)
        vlayout.addWidget(stl_button)

        self.tree_list = QTreeWidget()
        self.tree_list.setHeaderLabel("Known Objects")
        vlayout.addWidget(self.tree_list)

        self.widget.setWindowTitle("3D Editor")

    def __init__(self, objects, argv):
        self.objects = objects
        self.connections = {}

        self.app = QApplication(argv)
        self.__setup_basic_layout()

        self.input_aspect = Qt3DInput.QInputAspect()
        self.window3d.registerAspect(self.input_aspect)

        # Scene root object to start the rendering tree
        self.object_root = Qt3DCore.QEntity()

        # Setup basic camera with light bound to the camera
        self.__setup_lit_camera(self.window3d.camera(), self.object_root)

        # Setup camera controller to allow panning, moving, etc.
        self.camera_controller = Qt3DExtras.QOrbitCameraController(self.object_root)
        self.camera_controller.setCamera(self.window3d.camera())

        for obj in objects:
            self.resolve_object(obj)

        self.window3d.setRootEntity(self.object_root)

        self.widget.resize(1000, 700)

    def show(self):
        self.widget.show()

    def exec(self):
        return self.app.exec_()

    def resolve_object(self, obj):
        if obj.parent is not None:
            self.resolve_object(obj.parent)
        if self.connections[obj] is None:
            self.add_object(obj)

    def add_sphere(self, sphere):
        mesh = Qt3DExtras.QSphereMesh(rings=20, slices=20, radius=sphere.radius)

        transform = Qt3DCore.QTransform(scale=1.0, translation=QVector3D(sphere.position))

        material = Qt3DExtras.QPhongMaterial(diffuse=QColor(sphere.color))

        entity = Qt3DCore.QEntity(self.object_root if sphere.parent is None else self.connections[sphere.parent][0])
        entity.addComponent(mesh)
        entity.addComponent(material)
        entity.addComponent(transform)

        self.connections[sphere] = [entity, mesh, transform, material]
        self.connections[entity] = sphere

    def add_box(self, box):
        mesh = Qt3DExtras.QCuboidMesh()
        mesh.setXExtent(box.length)
        mesh.setZExtent(box.height)
        mesh.setYExtent(box.width)

        transform = Qt3DCore.QTransform(scale=1.0, translation=QVector3D(box.position))

        material = Qt3DExtras.QPhongMaterial(diffuse=QColor(box.color))

        entity = Qt3DCore.QEntity(self.object_root if box.parent is None else self.connections[box.parent][0])
        entity.addComponent(mesh)
        entity.addComponent(material)
        entity.addComponent(transform)

        self.connections[box] = [entity, mesh, transform, material]
        self.connections[entity] = box

    def add_stl_object(self, stlobj):
        pass

    def add_object(self, obj):
        if isinstance(obj, Sphere3D):
            self.add_sphere(obj)
        elif isinstance(obj, Box3D):
            self.add_box(obj)
        elif isinstance(obj, STL3D):
            self.add_stl_object(obj)

