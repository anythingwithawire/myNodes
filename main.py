import math
import sys
from random import random

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import json
import uuid
# from SizeGripItem import SizeGripItem

# import QtGui
from PyQt5 import QtCore
from PyQt5 import QtGui
from PySide2.QtGui import QMatrix

data = [
    {"label": "constant", "nodes": [{"type": "void", "output": [], "input": []}]},
    {"label": "operation",
     "nodes": [{"type": "add", "output": [{"type": "void"}], "input": [{"type": "int"}, {"type": "int"}]}]},
    {"label": "Group", "nodes": [{"type": "group", "output": [], "input": []}]}
]


class WindowClass(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.view = ViewClass()
        self.setCentralWidget(self.view)

        self.nodesEditor = QNodesEditor(self)
        self.nodesEditor.install(self.view.s)

        self.toolBar = QToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, self.toolBar)

        self.statusbar = QStatusBar(self)
        # self.statusbar.setObjectName(_fromUtf8("statusbar"))
        self.setStatusBar(self.statusbar)

        self.menubar = QMenuBar(self)
        self.setMenuBar(self.menubar)
        self.menu_file = QMenu(self.menubar)
        self.menu_file.setTitle('File')
        self.menubar.addAction(self.menu_file.menuAction())

        # exit action
        self.menu_action_exit = QAction(self)
        self.menu_action_exit.setText("Exit")
        self.menu_action_exit.triggered.connect(self.close)
        self.menubar.addAction(self.menu_action_exit)

        self.menu_file.addAction('New', self.actionNew)
        self.menu_file.addAction('Load', self.actionLoad)
        self.menu_file.addAction('Save', self.actionSave)
        self.menu_file.addAction('Save As', self.actionSaveAs)

    def actionNew(self):
        pass

    def actionLoad(self):
        self.nodesEditor.load()

    def actionSave(self):
        self.nodesEditor.save()

    def actionSaveAs(self):
        pass


class MenuAction(QAction):
    def __init__(self, label, parent=None):
        super(MenuAction, self).__init__(label, parent)
        self.typenode = None

    def setTypeNode(self, typenode):
        self.typenode = typenode

    def typeNode(self):
        return self.typenode


class ViewClass(QGraphicsView):
    xConnector = []
    xCable = []

    def __init__(self, parent=None):
        QGraphicsView.__init__(self, parent)
        super(ViewClass, self).__init__(parent)
        self.mousePos = None
        # self.setCacheMode(QGraphicsView.CacheBackground)
        ViewClass.viewport(self).installEventFilter(self)

        self.j = None
        self.menu = None
        self.menuaction = []
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.s = SceneClass()
        myScene = self.s
        self.setScene(self.s)
        self.setRenderHint(QPainter.Antialiasing)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.viewContextMenu)
        self.initAction()

    def eventFilter(self, source, event):
        if (source == self.viewport() and
                event.type() == QtCore.QEvent.Wheel):
            if event.angleDelta().y() > 0:
                scale = 1.25
            else:
                scale = .8
            self.scale(scale, scale)
            # do not propagate the event to the scroll area scrollbars
            return True
        elif event.type() == QEvent.GraphicsSceneMouseMove:
            self.mousePos = event.scenePos()
            # ...
        return super().eventFilter(source, event)

    def initAction(self):
        for typestr in data:
            # print(typestr)
            # self.action_addNode = QAction(u"Add Node %s " % ( data["data"][typestr]["type"] ), self)
            for nodesa in typestr["nodes"]:
                action = MenuAction(u"Add Node %s " % (typestr["label"]), self)
                action.setTypeNode(nodesa)
                # self.action_addNode = QAction(u"Add Node", self)
                action.triggered.connect(self.addNode)
                self.menuaction.append(action)

        action = MenuAction(u"cable node", self)
        action.setTypeNode(None)
        # self.action_addNode = QAction(u"Add Node", self)
        action.triggered.connect(self.special)
        self.menuaction.append(action)

        action = MenuAction(u"cable", self)
        # action.self =self
        # action_makeCable = QAction(u"Group", self)
        action.triggered.connect(self.special2)
        self.menuaction.append(action)

    def addNode(self):
        print(self.sender())
        return self.s.addNode(self.mapToScene(self.mapFromGlobal(self.menu.pos())), self.sender().typeNode())

    def special(self):
        print("special")
        self.j = ViewClass.addConnector(self, 0, 0)

    def special2(self):
        print("group nodes")
        self.g = QGraphicsItemGroup()
        for item in self.scene().items():
            if item.isSelected:
                item.setGroup(self.g)

    def viewContextMenu(self, p):
        self.menu = QMenu(self)
        for a in self.menuaction:
            self.menu.addAction(a)
        self.menu.exec_(self.mapToGlobal(p))

    def addConnector(self, x, y):
        ic = QGraphicsEllipseItem(-5, -5, 10, 10, None)
        ic.uuid = str(random() * 98787878)
        ic.setBrush(Qt.magenta)
        ic.setPen(Qt.blue)
        ic.setBrush(QBrush(Qt.darkYellow))
        ic.setPos(x, y)

        ic.setSelected(True)
        ic.setFlags(QGraphicsItem.ItemIsMovable |
                    QGraphicsItem.ItemIsSelectable |
                    QGraphicsItem.ItemSendsGeometryChanges | QGraphicsItem.ItemIsFocusable | QGraphicsItem.ItemIgnoresParentOpacity | QGraphicsItem.ItemAcceptsInputMethod)
        # self.setCacheMode(QGraphicsItem.ItemCoordinateCache)

        ic.setZValue(101)

        ViewClass.xConnector.append(ic)
        self.s.addItem(ic)

        # self.inputcj.append(ic)
        # label = QGraphicsTextItem(("bbb"), self)
        # label.setPos(10, 10)
        return ic


class JustConnector(QGraphicsItem):
    Type = QGraphicsItem.UserType + 9
    inputcj = []

    def __init__(self, parent):
        super(JustConnector, self).__init__(parent)

    '''def install(self, scene):
        self.scene = scene
        self.scene.installEventFilter(self)'''

    def itemAt(self, position):
        items = self.scene.items(QRectF(position - QPointF(1, 1), QSizeF(3, 3)))
        for item in items:
            if isinstance(item, JustConnector):
                print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                return item
        return None

    '''def eventFilter(self, object, event):
        if event.type() == QEvent.GraphicsSceneMousePress:
            if event.button() == Qt.LeftButton:
                item = self.itemAt(event.scenePos())
                if item is not None:
                    self.connection = item
                    self.edgeCreated = item.createEdge(event)
                    return super(JustConnector, self).eventFilter(object, event)
            elif event.button() == Qt.RightButton:
                item = self.itemAt(event.scenePos())
                if item is not None:
                    print("Mouse Right %s " % (item.type()))
                return super(JustConnector, self).eventFilter(object, event)
        elif event.type() == QEvent.GraphicsSceneMouseMove:
            print(self.itemAt(event.childItems()scenePos()))
            pass
        elif event.type() == QEvent.GraphicsSceneMouseRelease:  # EDGE ACTUALLY CREATED HERE
            # if self.connection and event.button() == Qt.LeftButton:
            item = self.itemAt(event.scenePos())
            if self.edgeCreated is not None:
                if self.edgeCreated.isCompatible(item):
                    self.edgeCreated.target = item
                    self.edgeCreated = None
                else:
                    self.edgeCreated.source.removeEdge(self.edgeCreated)
                    self.scene.removeItem(self.edgeCreated)
                    self.edgeCreated = None
        return super(JustConnector, self).eventFilter(object, event)'''

    def makeCable(self):
        return
        position = self.pos()
        print("Arrived")
        items = self.scene().items()
        i1 = i2 = None
        for item in items:
            print("item", item)
            if isinstance(item, QGraphicsEllipseItem):
                print("Bang1")
                if not i2 and i1:
                    i2 = item
                if not i1:
                    i1 = item
                if i2:
                    print("Cable")
                    cable = [i1, i2]
                    ViewClass.xCable.append(cable)
                    # c = Cable()
                    # c.addCable(i1, i2)
                    break

    def mousePressEvent(self, event):
        print("=======>>>>", self.isUnderMouse())
        JustConnector.mousePressEvent(self, event)

    def boundingRect(self):
        return QRectF(-5, -5, 10, 10)

    def paint(self, painter, option, widget):
        painter.setBrush(Qt.magenta)
        painter.setPen(Qt.red)
        painter.setBrush(QBrush(Qt.magenta))
        painter.drawEllipse(self.boundingRect())


class QNodesEditor(QObject):
    def __init__(self, parent):
        super(QNodesEditor, self).__init__(parent)
        self.mousePos = None
        self.connection = None
        self.edgeCreated = None
        self.scene = None

    def getItems(self):
        return self.items(QRectF(QPointF(0, 0) - QPointF(-300, -300), QSizeF(600, 600)))

    def install(self, scene):
        self.scene = scene
        self.scene.installEventFilter(self)

    def itemAt(self, position):
        items = self.scene.items(QRectF(position - QPointF(1, 1), QSizeF(3, 3)))
        for item in items:
            if isinstance(item, Connector) or isinstance(item, QGraphicsEllipseItem):
                return item
        return None

    def itemAtConnector(self, position):
        items = self.scene.items(QRectF(position - QPointF(1, 1), QSizeF(3, 3)))
        for item in items:
            if isinstance(item, Connector):
                return item
        return None

    def save(self):
        result = []
        for item in self.scene.items():
            if isinstance(item, Node):
                result.append(item.serialize())
            if isinstance(item, Node):
                result.append(item.serialize())
        print(result)
        with open('data.json', 'w') as outfile:
            json.dump(result, outfile, indent=4, sort_keys=True)

    def load(self):
        with open('data.json', 'r') as outfile:
            result = json.load(outfile)
            allnodeInput = {}
            allnodeOutput = {}
            for r in result:
                n = self.scene.addNode(QPointF(r["pos"]["x"], r["pos"]["y"]), r)
                n.setValue(r["value"])
                for iconc in n.inputConnector:
                    allnodeInput[iconc.uuid] = iconc
                for oconc in n.outputConnector:
                    allnodeOutput[oconc.uuid] = oconc
                # print(n.outputConnector)
            print(allnodeInput)
            print(allnodeOutput)
            for r in result:
                # TODO inverse input and output Connector
                for iconn, oconn in r["connection"]:
                    allnodeOutput[iconn].loadEdge(allnodeInput[oconn])

    def eventFilter(self, object, event):
        if event.type() == QEvent.GraphicsSceneMousePress:
            if event.button() == Qt.LeftButton:
                item = self.itemAtConnector(event.scenePos())
                if item is not None:
                    self.connection = item
                    self.edgeCreated = item.createEdge(event)
                    return super(QNodesEditor, self).eventFilter(object, event)
            elif event.button() == Qt.RightButton:
                item = self.itemAt(event.scenePos())
                if item is not None:
                    print("Mouse Right %s " % (item.type()))
                return super(QNodesEditor, self).eventFilter(object, event)
        elif event.type() == QEvent.GraphicsSceneMouseMove:
            print(self.itemAt(event.scenePos()), event.scenePos())
            self.mousePos = event.scenePos()
            pass
        elif event.type() == QEvent.GraphicsSceneMouseRelease:  # EDGE ACTUALLY CREATED HERE
            # if self.connection and event.button() == Qt.LeftButton:
            item = self.itemAt(event.scenePos())
            if self.edgeCreated is not None:
                if self.edgeCreated.isCompatible(item):
                    self.edgeCreated.target = item
                    self.edgeCreated = None
                else:
                    self.edgeCreated.source.removeEdge(self.edgeCreated)
                    self.scene.removeItem(self.edgeCreated)
                    self.edgeCreated = None
        return super(QNodesEditor, self).eventFilter(object, event)


class SceneClass(QGraphicsScene):
    grid = 30

    # myScene = None

    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, QRectF(-1000, -1000, 2000, 2000), parent)
        x = 1
        # self.setSortCacheEnabled(True)
        self.setItemIndexMethod(QGraphicsScene.NoIndex)

    def getScene(self):
        return self

    def drawBackground(self, painter, rect):
        painter.fillRect(rect, QColor(190, 190, 190))
        left = int(rect.left()) - int((rect.left()) % self.grid)
        top = int(rect.top()) - int((rect.top()) % self.grid)
        right = int(rect.right())
        bottom = int(rect.bottom())
        lines = []
        for x in range(left, right, self.grid):
            lines.append(QLineF(x, top, x, bottom))
        for y in range(top, bottom, self.grid):
            lines.append(QLineF(left, y, right, y))
        painter.setPen(QPen(QColor(150, 150, 150)))
        painter.drawLines(lines)

    def mouseDoubleClickEvent(self, event):
        self.addNode(event.scenePos(),
                     {'type': 'void', 'output': [{'type': ''}, {'type': ''}, {'type': ''}, {'type': ''}],
                      'input': [{'type': ''}, {'type': ''}, {'type': ''}, {'type': ''}]})
        QGraphicsScene.mouseMoveEvent(self, event)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            if len(self.selectedItems()) == 2:
                e = Edge()
                e.addEdge(self.selectedItems()[0], self.selectedItems()[1])
                self.addItem(e)

            if len(self.selectedItems()) == 3:
                e = Edge()
                e.addEdge3(self.selectedItems()[0], self.selectedItems()[1], self.selectedItems()[2])
                self.addItem(e)
        QGraphicsScene.mousePressEvent(self, event)

    def addNode(self, pos, typenode):
        print(typenode)
        if typenode["type"] == "int":
            node = NodeInt(typenode["type"], typenode["input"], typenode["output"])
        elif typenode["type"] == "add":
            node = NodeAdd(typenode["type"], typenode["input"], typenode["output"])
        elif typenode["type"] == "group":
            node = NodeAdd(typenode["type"], typenode["input"], typenode["output"])
            node.setScale(10.0)
            node.setZValue(-100)
        else:
            node = Node(typenode["type"], typenode["input"], typenode["output"])

        if node:
            self.addItem(node)
            node.setPos(pos)
            return node
        return None


'''
class Cable(QGraphicsPathItem):
    """A connection between two Knobs."""

    def __init__(self, parent=None):
        QGraphicsPathItem.__init__(self, parent)

        self.lineColor = QColor(200, 200, 10)
        self.removalColor = Qt.red
        self.thickness = 5

        self.source = None
        self.target = None

        self.sourcePos = QPointF(0, 0)
        self.targetPos = QPointF(0, 0)

        self.curv1 = 0.6
        self.curv3 = 0.4

        self.curv2 = 0.2
        self.curv4 = 0.8

        self.edgeType =''

        self.setAcceptHoverEvents(True)

    def updatePath(self):
        """Adjust current shape based on Knobs and curvature settings."""
        if self.source:
            self.sourcePos = self.source.mapToScene(
                self.source.boundingRect().center())

        if self.target:
            self.targetPos = self.target.mapToScene(
                self.target.boundingRect().center())

        # path = QPainterPath()

        # path.moveTo(self.sourcePos)

        self.dx = self.targetPos.x() - self.sourcePos.x()
        self.dy = self.targetPos.y() - self.sourcePos.y()

        ctrl1 = QPointF(self.sourcePos.x() + self.dx * self.curv1,
                        self.sourcePos.y() + self.dy * self.curv2)
        ctrl2 = QPointF(self.sourcePos.x() + self.dx * self.curv3,
                        self.sourcePos.y() + self.dy * self.curv4)
        # path.lineTo(ctrl1)
        # path.lineTo(ctrl2)
        # path.lineTo(self.targetPos)
        myFont = QFont()
        myFont.setFamily("Helvetica")
        # path.addText((ctrl1.x() + ctrl2.x()) / 2, -5 + (ctrl1.y() + ctrl2.y()) / 2, myFont, "text")
        # item = QtGui.QPainterPath(path)
        # self.sourcePos.scene.linkToItem = item
        # self.targetPos.scene.linkToItem = item

        # self.scene().addItem(path)
        # self.setPath(path)

    def boundingRect(self):
        return QRectF(-5000, -5000, 10000, 10000)

    def paint(self, painter, option, widget):
        """Paint Edge color depending on modifier key pressed or not."""
        self.setPen(QPen(self.lineColor, self.thickness))
        self.setZValue(11)
        painter = QPainter(self)
        painter.drawPath(self.path)
        super(Cable, self).paint(painter, option, widget)

    def isCompatible(self, connector):
        if connector is None:
            return False
        if connector is self.source:
            return False
        return True
        # if self.source.isCompatible(connector):
        #    return True
        # return False

    def addCable(self, p1, p2):
        self.source = p1
        self.source = p2
        self.sourcePos = p1.pos()
        self.targetPos = p2.pos()
        print("Source, Target", self.sourcePos, self.targetPos)
        self.updatePath()
'''


class Edge(QGraphicsPathItem):
    """A connection between two Knobs."""
    Type = QGraphicsItem.UserType + 1

    def __init__(self, parent=None):
        QGraphicsPathItem.__init__(self, parent)
        super().__init__(parent)

        self.cable = None
        self.lineColor = QColor(100, 50, 100)
        self.removalColor = Qt.red
        self.thickness = 0.4

        self.source = None
        self.target = None

        self.sourcePos = QPointF(0, 0)
        self.wayPointsPos = None
        self.targetPos = QPointF(0, 0)

        self.wayPoints = []

        self.curv1 = 0.6
        self.curv3 = 0.4

        self.curv2 = 0.2
        self.curv4 = 0.8

        self.edgeType = 'core'

        self.setAcceptHoverEvents(True)


    def addEdge(self, source, dest, parent=None):

        # self.line = QGraphicsLineItem()
        self.source = source

        self.target = dest
        # self.prepareGeometryChange()
        self.curv1 = 0.6
        self.curv3 = 0.4

        self.curv2 = 0.2
        self.curv4 = 0.8

        g = ViewClass()
        g.addConnector(source.scenePos().x() + 100, source.scenePos().y())

        h = ViewClass()
        h.addConnector(dest.scenePos().x() - 100, dest.scenePos().y())

        self.cable = [source, g, h, dest]
        ViewClass.xCable.append(self.cable)

        self.sourcePos = self.source.scenePos()
        self.targetPos = self.target.scenePos()
        self.lineColor = QColor(200, 0, 0)
        self.edgeType = 'cable'

        return

    def addEdge3(self, source, waypoint, dest, parent=None):
        # self.line = QGraphicsLineItem()
        self.source = source
        self.wayPoints.append(waypoint)
        print("appending waypoint")
        self.target = dest
        # self.prepareGeometryChange()
        self.curv1 = 0.6
        self.curv3 = 0.4

        self.curv2 = 0.2
        self.curv4 = 0.8

        self.updatePath()

        cable = [source, self.wayPoints, dest]
        cd = None
        for cb in ViewClass.xCable:
            if cb[0] == source and cb[-1] == dest:
                cd = cb
                cable = [cb[0], cb[1], waypoint, cb[-1]]
                self.wayPoints.append(cb[1])
                # self.wayPoints.append(waypoint)
                break
        if cd:
            ViewClass.xCable.remove(cd)
        ViewClass.xCable.append(cable)

        '''justDidDelete = False
        for n in range(0, pathNum):
            p = self.path.elementAt(n)
            if math.fabs(p.x - source.scenePos().x()) < 1.0 and math.fabs(p.y - source.scenePos().y()) < 1.0:
                print("XXXXXXXXXXXXXXXXXXXXZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ")
                #self.path.setElementPositionAt(n, 0.0, 0.0)
                justDidDelete = True
            else:
                if not justDidDelete:
                    newP.lineTo(100.0,100.0)
                    newP.moveTo(0.0, 0.0)
                    newP.setElementPositionAt(n, p.x, p.y)
                justDidDelete = False

            #if math.fabs(p.x - dest.scenePos().x()) < 1.0 and math.fabs(p.y - dest.scenePos().y()) < 1.0:
            #    print("XXXXXXXXXXXXXXXXXXXXZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ")
            #    self.path.setElementPositionAt(n, 0.0, 0.0)'''
        self.path.clear()
        '''for c in ViewClass.xCable:
            self.path.moveTo(c[0].scenePos().x(), c[0].scenePos().y())
            for z in range(1, len(c)):
                self.path.lineTo(c[z].scenePos().x(), c[z].scenePos().y())'''
        self.updatePath()

        self.sourcePos = self.source.scenePos()
        self.wayPointsPos = self.wayPoints[0].scenePos()
        self.targetPos = self.target.scenePos()
        self.lineColor = QColor(80, 100, 200)
        self.edgeType = 'waypoints'

        return

    def updatePath(self):
        """Adjust current shape based on Knobs and curvature settings."""
        if self.source:
            self.sourcePos = self.source.mapToScene(
                self.source.boundingRect().center())

        if self.target:
            self.targetPos = self.target.mapToScene(
                self.target.boundingRect().center())

        self.path = QPainterPath()

        myFont = QFont('Arial')
        myFont.setFixedPitch(True)
        myFont.setStyleStrategy(QFont.PreferAntialias)
        myFont.setStyleHint(QFont.Serif)

        # path.addPath(Cable.path)

        # Pen.rotationAngle = degrees
        if self.cable:
            if len(self.cable) > 2:
                self.path.moveTo(self.cable[0].scenePos())
                for w in self.cable:
                    self.path.lineTo(w.scenePos())
                    # self.path.addText(self.mid(self.sourcePos, wPos), myFont, self.edgeType)
                    # self.path.addText(self.mid(wPos, self.targetPos), myFont, self.edgeType)
                    # self.path.moveTo(wPos)
            elif len(self.cable == 2):
                self.path.moveTo(self.sourcePos)
                self.path.lineTo(self.targetPos)
                self.path.addText(self.mid(self.sourcePos, self.targetPos), myFont, self.edgeType)
            '''t = QGraphicsTextItem()
        t.setText('AAAAAAA')
        t.setPos(self.mid(self.sourcePos, self.targetPos))
        t.setRotation(-angle)
        if t not in self.scene().items():
            self.scene().addItem(t)'''
        # dx = self.targetPos.x() - self.sourcePos.x()
        # dy = self.targetPos.y() - self.sourcePos.y()
        '''ctrl1 = QPointF(self.sourcePos.x() + dx * self.curv1,
                        self.sourcePos.y() + dy * self.curv2)
        ctrl2 = QPointF(self.sourcePos.x() + dx * self.curv3,
                        self.sourcePos.y() + dy * self.curv4)'''
        # path.lineTo(ctrl1)
        # path.lineTo(ctrl2)
        # path.lineTo(self.targetPos)
        '''if ViewClass.xCable and ViewClass.xCable[0] and ViewClass.xCable[0][1]:
            path.moveTo(ViewClass.xCable[0][0].pos())
            path.moveTo(ViewClass.xCable[0][1].pos())
            path.addText((ctrl1.x() + ctrl2.x()) / 2, -5 + (ctrl1.y() + ctrl2.y()) / 2, myFont, "cable")'''
        self.setPath(self.path)

    def mid(self, a, b):
        x = (a.x() + b.x()) / 2
        y = ((a.y() + b.y()) / 2) - 2
        return QPointF(x, y)

    def angle(self, a, b):
        math.arcsin()

    def boundingRect(self):
        a = self.sourcePos
        b = self.targetPos
        return QRectF(min(a.x(), b.x()), min(a.y(), b.y()), max(a.x(), b.x()), max(a.y(), b.y()))

    def paint(self, painter, option, widget):
        """Paint Edge color depending on modifier key pressed or not."""
        self.setPen(QPen(self.lineColor, self.thickness))
        self.setZValue(11)
        self.updatePath()
        self.scene().update()
        super(Edge, self).paint(painter, option, widget)

    def isCompatible(self, connector):
        if connector is None:
            return False
        if connector is self.source:
            return False
        return True
        # if self.source.isCompatible(connector):
        #    return True
        # return False


class GraphLineEdit(QLineEdit):
    def __init__(self, connector, text, parent=None):
        super(GraphLineEdit, self).__init__(text, parent)
        self.connector = connector


"""
  Class Connector
"""


class Connector(QGraphicsEllipseItem):
    Type = QGraphicsItem.UserType + 1

    def __init__(self, rect, parent=None):
        self.uuid = str(uuid.uuid4())
        print("connector %s" % self.uuid)
        self.mousehover = False
        self.parent = parent
        QGraphicsEllipseItem.__init__(self, rect, parent)
        # self.setFlags(QGraphicsItem.ItemIsSelectable)

        self.createSpecificGui()
        self.edges = []

        self.setAcceptHoverEvents(True)
        self.setZValue(2)
        self.value = None

    # def boundingRect(self):
    # return QRectF(-30, 0, 150, 20 * 30 + 50)

    def paint(self, painter, option, widget):
        # painter = QPainter()
        # painter.begin(self)
        bbox = self.boundingRect()
        if self.mousehover:
            painter.setBrush(QBrush(QColor(255, 255, 0)))
        else:
            painter.setBrush(QBrush(QColor(0, 0, 130)))
        painter.drawEllipse(QRectF(bbox))
        painter.drawText(10, 10, "01")

        # painter.drawEllipse(bbox)
        if len(self.edges) > 0:
            painter.setBrush(QBrush(QColor(0, 255, 0)))
            bbox2 = QRectF(bbox)
            painter.drawEllipse(bbox2)
        # painter.end()

    def hoverEnterEvent(self, event):
        """Change the Knob's rectangle color."""
        self.mousehover = True
        self.update()

    def hoverLeaveEvent(self, event):
        """Change the Knob's rectangle color."""
        self.mousehover = False
        # print("hoverLeaveEvent")
        self.update()

    def loadEdge(self, target):
        self.newEdge = Edge()
        self.newEdge.source = self
        self.newEdge.target = target
        self.edges.append(self.newEdge)
        scene = self.scene()
        if self.newEdge not in scene.items():
            scene.addItem(self.newEdge)

    def createEdge(self, event):
        self.newEdge = Edge()
        self.newEdge.source = self
        self.newEdge.targetPos = event.scenePos()
        self.newEdge.updatePath()
        self.edges.append(self.newEdge)
        scene = self.scene()
        if self.newEdge not in scene.items():
            scene.addItem(self.newEdge)
        return self.newEdge

    def removeEdge(self, event):
        self.update()
        self.newEdge.source = None
        self.edges.pop()

    def setValue(self, value):
        for e in self.edges:
            if e.target is not None:
                e.target.setInputValue(value)

    def setInputValue(self, value):
        print(self.parent)
        self.value = value
        self.parent.execute()

    def mousePressEvent(self, event):
        pass
        # print("mousePressEvent")
        # Connector.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.newEdge:
            # print("mouseMoveEvent dragging ")
            self.newEdge.targetPos = event.scenePos()
            self.newEdge.updatePath()
        # Connector.mouseMoveEvent(self, event)

    def createSpecificGui(self):
        pass

    def mouseReleaseEvent(self, event):
        print("mouseReleaseEvent")

    def isCompatible(self, connector):
        return False


class ConnectorOutput(Connector):
    def isCompatible(self, connector):
        if isinstance(connector, ConnectorInput):
            return True
        return False


class ConnectorInput(Connector):
    def isCompatible(self, connector):
        if isinstance(connector, ConnectorOutput):
            return True
        return False


class Box(QGraphicsRectItem):
    r = QRectF(0, 0, 50, 50)

    def __init__(self, a, b, c, d, parent=None):
        super().__init__(a, b, c, d, parent)
        self.a = a
        self.b = b
        self.c = c
        self.d = d

        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        self.setPos(100, 100)

    def boundingRect(self):
        return QRectF(self.a, self.b, self.c, self.d)

    def paint(self, painter, option, widget=None):
        pen = QPen()
        pen.setColor(Qt.black)
        painter.setPen(pen)
        painter.setBrush(Qt.transparent)
        painter.drawRect(self.a, self.b, self.c, self.d)

    @pyqtSlot()
    def resize(self, change):
        self.setRect(self.rect().adjusted(0, 0, change.x(), change.y()))
        self.prepareGeometryChange()
        self.update()


# class Node(QGraphicsRectItem):
class Node(QGraphicsObject):
    def __init__(self, label, inputc, outputc, parent=None):
        #       QGraphicsRectItem.__init__(self, rect, parent)
        QGraphicsObject.__init__(self, parent)
        self.isSelected = False
        self.label = label
        self.inputc = []
        for i in inputc:
            print(i)
            self.inputc.append(i.copy())
        self.outputc = []
        for o in outputc:
            print(o)
            self.outputc.append(o.copy())
        self.edges = []
        self.inputConnector = []
        self.outputConnector = []
        self.setZValue(1)
        self.setFlags(QGraphicsItem.ItemIsMovable |
                      QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemSendsGeometryChanges)
        # self.label = QGraphicsTextItem(self.getLabel(), self)
        self.attributes = {}
        # self.createSpecificGui()
        self.createInputConnector()
        self.createOutputConnector()

    def getNbInput(self):
        return len(self.inputc)

    def getNbOutput(self):
        return len(self.outputc)

    def getLabel(self):
        return self.label

    def getType(self):
        return "int"

    def getAttributes(self):
        return self.attributes

    def createSpecificGui(self):
        pass

    def createInputConnector(self):
        for n in range(self.getNbInput()):
            ic = ConnectorInput(QRectF(-10, 25 * n + 50, 20, 20))
            if "uid" in self.inputc[n]:
                ic.uuid = self.inputc[n]["uid"]
            else:
                self.inputc[n]["uid"] = ic.uuid

            self.inputConnector.append(ic)
            # label = QGraphicsTextItem(("%d" % (n)), self)
            # label.setPos(10, 25 * n + 50)

    def createOutputConnector(self):
        for n in range(self.getNbOutput()):
            connector = ConnectorOutput(QRectF(90, 25 * n + 50, 20, 20), self)
            self.outputConnector.append(connector)
            if "uid" in self.outputc[n]:
                connector.uuid = self.outputc[n]["uid"]
            else:
                self.outputc[n]["uid"] = connector.uuid

            if self.outputc[n]["type"] == "int":
                proxy = QGraphicsProxyWidget(self)
                widget = GraphLineEdit(connector, "")
                widget.textChanged.connect(self.valueChanged)
                widget.setMaximumWidth(80)
                proxy.setWidget(widget)
                br = proxy.boundingRect()
                proxy.setPos(90 - br.width(), 25 * n + 50)
            # else:
            # label = QGraphicsTextItem(("%d" % (n)), self)
            # br = label.boundingRect()
            # label.setPos(90 - br.width(), 25 * n + 50)

            """
            label = QGraphicsTextItem(("%d" % (n)),self)
            br = label.boundingRect()
            label.setPos(90 - br.width() ,25*n+50)
            """

            '''connector = ConnectorOutput(parent=self)
            connector.setPos(130,n*20)
            connector.setVisible(True)
            if "uid" in self.outputc[n]:
                connector.uuid = self.outputc[n]["uid"]
                self.outputConnector.append(connector)
            else:
                self.outputc[n]["uid"] = connector.uuid

            connector = ConnectorOutput(parent=self)
            connector.setPos(90,n*20)
            if "uid" in self.outputc[n]:
                connector.uuid = self.outputc[n]["uid"]
                self.outputConnector.append(connector)
            else:
                self.outputc[n]["uid"] = connector.uuid

            if self.outputc[n]["type"] == "int":
                proxy = QGraphicsProxyWidget(self)
                widget = GraphLineEdit(connector, "")
                widget.textChanged.connect(self.valueChanged)
                widget.setMaximumWidth(80)
                proxy.setWidget(widget)
                br = proxy.boundingRect()
                proxy.setPos(90 - br.width(), 25 * n + 50)
            else:
                label = QGraphicsTextItem(("%d" % n), self)
                br = label.boundingRect()
                label.setPos(90 - br.width(), 25 * n + 50)'''

    def boundingRect(self):
        nb = max(self.getNbInput(), self.getNbOutput())
        return QRectF(-10, -10, 120, nb * 25 + 90)

    def paint(self, painter, option, widget):
        if self.isSelected:
            painter.setBrush(Qt.darkGreen)
            painter.setPen(Qt.blue)
        else:
            painter.setBrush(Qt.darkGray)
            painter.setPen(Qt.blue)

        painter.drawRect(self.boundingRect())

    def addEdge(self, edge):
        self.edges.append(edge)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for edge in self.edges:
                edge.adjust()

        return QGraphicsItem.itemChange(self, change, value)

    def mousePressEvent(self, event):
        if self.isSelected:
            self.isSelected = False
        else:
            self.isSelected = True
        self.update()
        QGraphicsItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        # self.isSelected = False
        # self.update()
        QGraphicsItem.mouseReleaseEvent(self, event)

    def setValue(self, value):
        print(value)
        self.execute()

    def getValue(self):
        return None

    def execute(self):
        pass

    def valueChanged(self, text):
        self.sender().connector.setValue(text)

    def serialize(self):
        print("SERIALIZE ")

        result = {}
        result["type"] = self.getType()
        result["input"] = self.inputc  # self.getinput()
        result["output"] = self.outputc  # self.getoutput()
        result["pos"] = {}
        result["pos"]["x"] = self.scenePos().x()
        result["pos"]["y"] = self.scenePos().y()
        result["value"] = self.getValue()
        result["connection"] = []
        result["'attributes"] = {}
        for output in self.outputConnector:
            for edge in output.edges:
                result["connection"].append((edge.source.uuid, edge.target.uuid))
        return result


class NodeAdd(Node):

    def createSpecificGui(self):
        # proxy = QGraphicsProxyWidget(self)
        # self.widget = QLabel("    ")
        # proxy.setWidget(self.widget)
        # proxy.setPos(10, 30)
        pass

    def execute(self):
        if self.inputConnector[0].value is not None and self.inputConnector[1].value is not None:
            computeValue = (int(self.inputConnector[0].value) + int(self.inputConnector[1].value))
            self.widget.setText("%d" % computeValue)
            for outc in self.outputConnector:
                outc.setValue(computeValue)

    def getType(self):
        return "add"

    def getValue(self):
        return str(self.widget.text())

    def getAttribute(self, att):
        if self.attributes[att]:
            return self.attributes[att]
        return None


class NodeInt(Node):
    def __init__(self, label, inputc, outputc, parent=None):
        super().__init__(label, inputc, outputc, parent)
        self.widget = None

    def createSpecificGui(self):
        # proxy = QGraphicsProxyWidget(self, flags=self.flags())
        # self.widget = QLineEdit("")
        # self.widget.textChanged.connect(self.valueChanged)
        # self.widget.setMaximumWidth(1000)
        # proxy.setWidget(self.widget)
        # proxy.setPos(10, 30)
        pass

    def getType(self):
        return "NodeInt"

    def valueChanged(self, text):
        for con in self.outputConnector:
            con.setValue(text)

    def getValue(self):
        return str(self.widget.text())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wd = WindowClass(None)
    wd.show()
    sys.exit(app.exec_())
