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
        vlayout.addWidget(self.edit_group)

        vboxlayout = QVBoxLayout()
        name_label = QLabel("Name:")
        name_edit = QLineEdit(name_label)
        vboxlayout.addWidget(name_label)
        vboxlayout.addWidget(name_edit)

        self.pos_group = QGroupBox("Position", self.edit_group)
        hboxlayout = QHBoxLayout()
        pos_x_edit = QDoubleSpinBox()
        pos_y_edit = QDoubleSpinBox()
        pos_z_edit = QDoubleSpinBox()
        hboxlayout.addWidget(pos_x_edit)
        hboxlayout.addWidget(pos_y_edit)
        hboxlayout.addWidget(pos_z_edit)
        vboxlayout.addWidget(self.pos_group)
        self.pos_group.setLayout(hboxlayout)

        self.angles_group = QGroupBox("Angles", self.edit_group)
        hboxlayout = QHBoxLayout()
        angles_x_edit = QDoubleSpinBox()
        angles_y_edit = QDoubleSpinBox()
        angles_z_edit = QDoubleSpinBox()
        hboxlayout.addWidget(angles_x_edit)
        hboxlayout.addWidget(angles_y_edit)
        hboxlayout.addWidget(angles_z_edit)
        vboxlayout.addWidget(self.angles_group)
        self.angles_group.setLayout(hboxlayout)

        color_label_text = QLabel("Color:")
        color_label = QLabel()
        color_palette = color_label.palette()
        color_palette.setColor(color_label.backgroundRole(), QColor("#00aa00"))
        color_label.setAutoFillBackground(True)
        color_label.setPalette(color_palette)
        vboxlayout.addWidget(color_label_text)
        vboxlayout.addWidget(color_label)

        self.specials_group = QGroupBox("Special Properties", self.edit_group)
        vboxlayout.addWidget(self.specials_group)

        vboxlayout.addStretch(.5)
        self.edit_group.setLayout(vboxlayout)

        self.tree_list = QTreeWidget()
        self.tree_list.setHeaderLabel("Known Objects")
        vlayout.addWidget(self.tree_list)

        self.widget.setWindowTitle("3D Editor")

    def __init__(self, argv, object_root):
        self.app = QApplication(argv)
        self.__setup_basic_layout()

        self.input_aspect = Qt3DInput.QInputAspect()
        self.window3d.registerAspect(self.input_aspect)

        # Setup basic camera with light bound to the camera
        self.__setup_lit_camera(self.window3d.camera())

        # Setup camera controller to allow panning, moving, etc.
        self.camera_controller = Qt3DExtras.QOrbitCameraController(object_root)
        self.camera_controller.setCamera(self.window3d.camera())

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

    def set_slected_object(self, object):
        pass
