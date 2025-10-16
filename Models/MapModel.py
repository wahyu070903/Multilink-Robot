from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem
from PyQt5.QtCore import Qt, QPointF, pyqtSignal
from PyQt5.QtGui import QBrush, QPen, QColor, QPainter
import sys
import json
from mapGenerator import Ui_MapGenerator
from mapGeneratorOption import Ui_MapGeneratorOption

CELL_SIZE = 20
GRID_WIDTH = 40
GRID_HEIGHT = 40
isDrawEnabled = False
used_unit = None
map_data = None

class MapGeneratorPup(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MapGenerator()
        self.ui.setupUi(self)

class OptionDisplay(QtWidgets.QDialog):
    applySettings = pyqtSignal(float, float, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MapGeneratorOption()
        self.ui.setupUi(self)

        global CELL_SIZE
        global GRID_HEIGHT
        global GRID_WIDTH
        self.usedUnit = None
        self.ui.mapWidth_Input.setValue(CELL_SIZE * GRID_WIDTH)
        self.ui.mapHeight_Input.setValue(CELL_SIZE * GRID_HEIGHT)
        self.ui.cellSpace_Input.setValue(CELL_SIZE)

        self.unit_input = self.ui.unit_ComboBox
        index = self.unit_input.findText(used_unit)
        if index != -1:
            self.unit_input.setCurrentIndex(index)
        self.unit_label = [
            self.ui.unit_label_1,
            self.ui.unit_label_2,
            self.ui.unit_label_3
        ]
        self.changeUnitLabel()
        self.unit_input.currentIndexChanged.connect(self.changeUnitLabel)
        self.ui.clicked.connect(self.acceptCallback)
        self.ui.cancelBtn.clicked.connect(self.reject)

    def changeUnitLabel(self):
        label_text = None
        if self.unit_input.currentText() == "Meter":
            label_text = "M"
        elif self.unit_input.currentText() == "Centimeter":
            label_text = "Cm"

        for label in self.unit_label:
            label.setText(label_text)

        self.usedUnit = self.unit_input.currentText()

    def acceptCallback(self):
        map_width = self.ui.mapWidth_Input.value()
        map_height = self.ui.mapHeight_Input.value()
        map_spacing = self.ui.cellSpace_Input.value()

        grid_w = map_width / map_spacing
        grid_h = map_height / map_spacing

        self.applySettings.emit(grid_w, grid_h, map_spacing)

        self.accept()

class MapView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setMouseTracking(True)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        self.mouse_pressed = False
        self.cells = []
        self.zoom_level = 1.0
        self.min_zoom = 1.0   # Zoom out limit
        self.max_zoom = 5.0   # Zoom in limit

    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        new_zoom = self.zoom_level * zoom_factor

        if self.min_zoom <= new_zoom <= self.max_zoom:
            self.zoom_level = new_zoom
            self.scale(zoom_factor, zoom_factor)
        else:
            return

    def mousePressEvent(self, event):
        self.mouse_pressed = True
        if isDrawEnabled:
            self.set_cell_as_wall(event)
        else:
            self.set_cell_as_none(event)

    def mouseMoveEvent(self, event):
        if self.mouse_pressed:
            if isDrawEnabled:
                self.set_cell_as_wall(event)
            else:
                self.set_cell_as_none(event)

    def mouseReleaseEvent(self, event):
        self.mouse_pressed = False

    def set_cell_as_wall(self, event):
        pos = self.mapToScene(event.pos())
        x = int(pos.x() // CELL_SIZE)
        y = int(pos.y() // CELL_SIZE)

        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            cell = self.cells[y][x]
            cell.setBrush(Qt.black)

    def set_cell_as_none(self, event):
        pos = self.mapToScene(event.pos())
        x = int(pos.x() // CELL_SIZE)
        y = int(pos.y() // CELL_SIZE)

        if 0 <= x < GRID_WIDTH  and 0 <= y < GRID_HEIGHT:
            cell = self.cells[y][x]
            cell.setBrush(Qt.white)

    def reset_zoom(self):
        self.resetTransform()
        self.zoom_level = 1.0

class MapModel:
    def __init__(self):
        self.dbname = "map.json"
        self.readMapFiles()
        self.widget = MapGeneratorPup()
        layout = QtWidgets.QVBoxLayout(self.widget.ui.drawArea)
        self.widget.ui.drawBtn.clicked.connect(self.draw_environment)
        self.widget.ui.EraseBtn.clicked.connect(self.erase_environment)
        self.widget.ui.ClearBtn.clicked.connect(self.clear_environment)
        self.widget.ui.OptionBtn.clicked.connect(self.show_option)

        self.scene = QGraphicsScene()
        self.view = MapView(self.scene)
        layout.addWidget(self.view)
        layout.setContentsMargins(0, 0, 0, 0)

        self.scene.setSceneRect(0, 0, GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE)
        self.view.setMinimumSize(420, 420)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.init_grid()
        self.load_map_to_scene()
        self.widget.ui.cancelBtn.clicked.connect(self.widget.reject)
        self.widget.ui.saveBtn.clicked.connect(self.saveMap)
        self.used_unit = None
        desired_display_size = 20
        scale_factor = desired_display_size / CELL_SIZE
        self.view.scale(scale_factor, scale_factor)

    def init_grid(self):
        pen = QPen(Qt.gray)
        pen.setWidth(0)
        self.view.cells = []

        for row in range(GRID_HEIGHT):
            row_cells = []
            for col in range(GRID_WIDTH):
                rect = QGraphicsRectItem(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                rect.setPen(pen)
                rect.setBrush(Qt.white)
                self.scene.addItem(rect)
                row_cells.append(rect)
            self.view.cells.append(row_cells)

    def draw_environment(self):
        global isDrawEnabled
        isDrawEnabled = True

    def erase_environment(self):
        global isDrawEnabled
        isDrawEnabled = False

    def clear_environment(self):
        for row in self.view.cells:
            for cell in row:
                cell.setBrush(Qt.white)

    def ShowMakerWindow(self):
        return self.widget.exec_()

    def show_option(self):
        display = OptionDisplay()
        display.applySettings.connect(self.apply_new_settings)
        display.exec()

    def apply_new_settings(self, grid_w, grid_h, spacing):
        global GRID_WIDTH, GRID_HEIGHT, CELL_SIZE
        GRID_WIDTH = int(grid_w)
        GRID_HEIGHT = int(grid_h)
        CELL_SIZE = int(spacing)
        self.scene.clear()
        self.scene.setSceneRect(0, 0, GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.init_grid()

        desired_display_size = 20
        scale_factor = desired_display_size / CELL_SIZE
        self.view.resetTransform()
        self.view.scale(scale_factor, scale_factor)
    
    def readMapFiles(self):
        global CELL_SIZE
        global GRID_WIDTH
        global GRID_HEIGHT
        global used_unit
        global map_data
        
        with open(self.dbname, "r") as db:
            maps = json.load(db)

        unit = maps['unit']
        row = maps['row']
        column = maps['col']
        cell_spacing = maps['cell_spacing']
        walls = maps['walls']

        GRID_WIDTH = column 
        GRID_HEIGHT = row
        CELL_SIZE = cell_spacing
        used_unit = unit
        map_data = walls
    
    def get_numeric_grid(self):
        grid = []
        for row in self.view.cells:
            row_values = []
            for cell in row:
                color = cell.brush().color()
                if color == Qt.black:
                    row_values.append(1)
                else:
                    row_values.append(0)
            grid.append(row_values)
        return grid

    def saveMap(self):
        global CELL_SIZE
        global GRID_HEIGHT
        global GRID_WIDTH
        global used_unit

        numeric_map = self.get_numeric_grid()

        with open(self.dbname, "r") as db:
            maps = json.load(db)

        maps['unit'] = used_unit
        maps['row'] = GRID_HEIGHT
        maps['col'] = GRID_WIDTH
        maps['cell_spacing'] = CELL_SIZE
        maps['walls'] = numeric_map

        with open(self.dbname, 'w') as db:
             json.dump(maps, db, indent=4)

        self.widget.reject()

    def load_map_to_scene(self):
        global map_data
        if map_data is None:
            return
        rows = min(GRID_HEIGHT, len(map_data))
        cols = min(GRID_WIDTH, len(map_data[0]))

        for y in range(rows):
            for x in range(cols):
                cell = self.view.cells[y][x]
                if map_data[y][x] == 1:
                    cell.setBrush(Qt.black)
                else:
                    cell.setBrush(Qt.white)


