import enum

from PySide2.Qt3DInput import Qt3DInput
from PySide2.Qt3DRender import Qt3DRender
from PySide2.Qt3DCore import Qt3DCore
from PySide2.Qt3DExtras import Qt3DExtras
from PySide2.QtCore import QSize, Qt
from PySide2.QtGui import QColor, QVector3D
from PySide2.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QTreeWidget, \
    QTreeWidgetItem, QGroupBox, QLabel, QLineEdit, QDoubleSpinBox

from editor3d.objects import Sphere3D, Box3D, STL3D


def _recursive_tree_add(node):
    widget_item = QTreeWidgetItem([node.name])
    widget_item.original = node
    for child in node.children:
        widget_item.addChild(_recursive_tree_add(child))
    return widget_item


class PropertyType(enum.Enum):
    POSITION = 1
    ROTATION = 2
    BOX_DIMENSIONS = 3
    RADIUS = 4
    SCALE = 5
    NAME = 6
    COLOR = 7


class PropertyEditor:
    def update_color(self, color):
        self.manager.update_color(self.obj, color)

    def update_name(self, name):
        self.manager.update_name(self.obj, name)

    def update_scalar(self, scalar):
        if isinstance(self.obj, Sphere3D):
            self.manager.update_radius(self.obj, scalar)
        elif isinstance(self.obj, STL3D):
            self.manager.update_scale(self.obj, scalar)

    def update_trio(self, _):
        vector = (self.x_edit.value(), self.y_edit.value(), self.z_edit.value())
        if self.type == PropertyType.POSITION:
            self.manager.update_position(self.obj, vector)
        elif self.type == PropertyType.ROTATION:
            self.manager.update_rotation(self.obj, vector)
        elif self.type == PropertyType.BOX_DIMENSIONS:
            self.manager.update_box_dimension(self.obj, vector)

    def __init__(self, parent, type, title, manager, obj):
        self.manager = manager
        self.group = QGroupBox(title, parent)
        self.type = type
        self.obj = obj
        hboxlayout = QHBoxLayout()
        if type in [PropertyType.POSITION, PropertyType.ROTATION, PropertyType.BOX_DIMENSIONS]:
            if type is PropertyType.POSITION:
                x, y, z = obj.position
            elif type is PropertyType.ROTATION:
                x, y, z = obj.rotation
            elif type is PropertyType.BOX_DIMENSIONS:
                x, y, z = (obj.width, obj.length, obj.height)
            else:
                x, y, z = (0, 0, 0)
            self.x_edit = QDoubleSpinBox()
            self.x_edit.setValue(x)
            self.x_edit.setRange(-9999, 9999)
            self.x_edit.valueChanged.connect(self.update_trio)

            self.y_edit = QDoubleSpinBox()
            self.y_edit.setValue(y)
            self.y_edit.setRange(-9999, 9999)
            self.y_edit.valueChanged.connect(self.update_trio)

            self.z_edit = QDoubleSpinBox()
            self.z_edit.setValue(z)
            self.z_edit.setRange(-9999, 9999)
            self.z_edit.valueChanged.connect(self.update_trio)

            hboxlayout.addWidget(self.x_edit)
            hboxlayout.addWidget(self.y_edit)
            hboxlayout.addWidget(self.z_edit)
        elif type == PropertyType.NAME:
            str_edit = QLineEdit(self.group)
            str_edit.setText(obj.name)
            str_edit.textChanged.connect(self.update_name)
            hboxlayout.addWidget(str_edit)
        elif type in [PropertyType.RADIUS, PropertyType.SCALE]:
            single_edit = QDoubleSpinBox()
            single_edit.setRange(-9999, 9999)
            if type is PropertyType.RADIUS:
                single_edit.setValue(obj.radius)
            elif type is PropertyType.SCALE:
                single_edit.setValue(obj.scale)
            single_edit.valueChanged.connect(self.update_scalar)
            hboxlayout.addWidget(single_edit)
        elif type == PropertyType.COLOR:
            color_label = QLabel()
            color_palette = color_label.palette()
            color_palette.setColor(color_label.backgroundRole(), QColor(obj.color))
            color_label.setAutoFillBackground(True)
            color_label.setPalette(color_palette)
            hboxlayout.addWidget(color_label)
            # todo: make it changeable
        self.group.setLayout(hboxlayout)



class QtFrontend:
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

    def update_object_editor(self, obj):
        vboxlayout = self.edit_group.layout()

        while vboxlayout.takeAt(0) is not None:
            pass
        self.editors.clear()

        self.editors[PropertyType.NAME] = PropertyEditor(self.edit_group, PropertyType.NAME, "Name", self.manager, obj)
        vboxlayout.addWidget(self.editors[PropertyType.NAME].group)

        self.editors[PropertyType.POSITION] = PropertyEditor(self.edit_group, PropertyType.POSITION, "Position", self.manager, obj)
        vboxlayout.addWidget(self.editors[PropertyType.POSITION].group)

        self.editors[PropertyType.ROTATION] = PropertyEditor(self.edit_group, PropertyType.ROTATION, "Rotation", self.manager, obj)
        vboxlayout.addWidget(self.editors[PropertyType.ROTATION].group)

        self.editors[PropertyType.COLOR] = PropertyEditor(self.edit_group, PropertyType.COLOR, "Color", self.manager, obj)
        vboxlayout.addWidget(self.editors[PropertyType.COLOR].group)

        if isinstance(obj, Sphere3D):
            self.editors[PropertyType.RADIUS] = PropertyEditor(self.edit_group, PropertyType.RADIUS, "Radius", self.manager, obj)
            vboxlayout.addWidget(self.editors[PropertyType.RADIUS].group)
        elif isinstance(obj, Box3D):
            self.editors[PropertyType.BOX_DIMENSIONS] = PropertyEditor(self.edit_group, PropertyType.BOX_DIMENSIONS, "Dimensions", self.manager, obj)
            vboxlayout.addWidget(self.editors[PropertyType.BOX_DIMENSIONS].group)
        elif isinstance(obj, STL3D):
            self.editors[PropertyType.SCALE] = PropertyEditor(self.edit_group, PropertyType.SCALE, "Scale", self.manager, obj)
            vboxlayout.addWidget(self.editors[PropertyType.SCALE].group)

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

        self.edit_group = QGroupBox("Edit Object", self.widget)
        vboxlayout = QVBoxLayout()
        self.edit_group.setLayout(vboxlayout)
        vlayout.addWidget(self.edit_group)

        self.tree_list = QTreeWidget()
        self.tree_list.setHeaderLabel("Known Objects")
        vlayout.addWidget(self.tree_list)

        self.widget.setWindowTitle("3D Editor")

    def __init__(self, argv, object_root, manager):
        self.manager = manager
        self.editors = {}

        self.app = QApplication(argv)
        self.__setup_basic_layout()

        self.input_aspect = Qt3DInput.QInputAspect()
        self.window3d.registerAspect(self.input_aspect)

        # Setup basic camera with light bound to the camera
        self.__setup_lit_camera(self.window3d.camera())

        # Setup camera controller to allow panning, moving, etc.
        self.camera_controller = Qt3DExtras.QOrbitCameraController(object_root)
        self.camera_controller.setCamera(self.window3d.camera())

        # Base node for tree of elements
        self.window3d.setRootEntity(object_root)

        self.widget.resize(1000, 700)

    def show(self):
        self.widget.show()

    def exec(self):
        return self.app.exec_()

    def set_known_objects(self, root):
        self.tree_list.clear()
        self.tree_list.setHeaderLabel("Known Objects")
        for element in root.children:
            self.tree_list.addTopLevelItem(_recursive_tree_add(element))

    def set_slected_object(self, obj):
        self.update_object_editor(obj)
