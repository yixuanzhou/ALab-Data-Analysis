import sys
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QApplication, QPushButton, QRadioButton, QLabel, QComboBox, QLineEdit, QFileDialog, QMessageBox
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout
from matplotlib.figure import Figure
from calculateQ import baseQ
from draggable import PlotCanvas
from graph import Graph
from process import readlvm
import csv
import os


class MainWindow(QFrame):
    canvas = None

    def __init__(self, parent=None):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Q")        
        self.setObjectName('Main')
        self.setStyleSheet(open("QSS/mainwindow.qss", "r").read())
        self.resize(900, 600)
        
        self.parent = parent

        self.setButtons()
        self.setLabels()
        self.setLayouts()

    def setButtons(self):
        ''' Set all buttons here. '''
        self.Load = QPushButton(self) # PushButton 'Load'
        #self.Load.setText(u"Open")
        #self.Load.setFixedWidth(90)
        self.Load.setIcon(QIcon('./resource/icons8-open-100.png'))  
        self.Load.setIconSize(QtCore.QSize(30,30))     
        self.Load.setToolTip('Open the base file')
        self.Load.clicked.connect(self.openQ)

        self.Run = QPushButton(self) # PushButton 'Run'
        # self.Run.setText(u"Load")
        # self.Run.setFixedWidth(90)
        self.Run.setIcon(QIcon('./resource/icons8-start-100.png'))
        self.Run.setIconSize(QtCore.QSize(30,30))  
        self.Run.setToolTip('Start calculating')
        self.Run.clicked.connect(self.process)

        self.Fit = QPushButton(self) # PushButton 'Run'
        # self.Fit.setText(u"Fit")
        # self.Fit.setFixedWidth(90)
        self.Fit.setIcon(QIcon('./resource/icons8-line-chart-100.png'))
        self.Fit.setIconSize(QtCore.QSize(30,30))  
        self.Fit.setToolTip('Fitting selected points')
        self.Fit.clicked.connect(self.fit)

        self.Export = QPushButton(self)
        # self.Export.setText(u"Export")
        # self.Export.setFixedWidth(90)
        self.Export.setIcon(QIcon('./resource/icons8-export-csv-100.png'))
        self.Export.setIconSize(QtCore.QSize(30,30))  
        self.Export.setToolTip('Export data as csv file')
        self.Export.clicked.connect(self.export)

        self.Reset = QPushButton(self)
        # self.Reset.setText(u"Reset")
        # self.Reset.setFixedWidth(90)
        self.Reset.setIcon(QIcon('./resource/icons8-synchronize-100.png'))
        self.Reset.setIconSize(QtCore.QSize(30,30))  
        self.Reset.setToolTip('Reset all')
        self.Reset.clicked.connect(self.reset)

        self.Unfit = QPushButton(self) # PushButton 'Run'
        # self.Unfit.setText(u"Unfit")
        # self.Unfit.setFixedWidth(90)
        self.Unfit.setIcon(QIcon('./resource/icons8-undo-100.png'))
        self.Unfit.setIconSize(QtCore.QSize(30,30))  
        self.Unfit.setToolTip('Cancel Fitting')
        self.Unfit.clicked.connect(self.unfit)

        self.b1 = QRadioButton("1 Peak")
        self.b1.setChecked(True)
        self.b2 = QRadioButton("2 Peaks")
     
    def setLabels(self):
        ''' Set all labels here. '''
        self.modulation = QLabel(self)
        self.modulation.setText("Modulation Coefficient:")
        self.comboBox = QComboBox(self)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("0.025 (633)")
        self.comboBox.addItem("0.036 (633)")
        self.comboBox.addItem("0.0083 (633)")
        self.comboBox.addItem("0.038 (765)")
        self.comboBox.addItem("0.033 (765)")
        self.comboBox.addItem("0.049 (980)")
        self.comboBox.addItem("0.036 (980)")
        self.comboBox.addItem("0.043 (1064)")
        self.comboBox.addItem("0.089 (1330)")
        self.comboBox.addItem("0.052 (1550)")

        self.lambda_tag = QLabel(self)
        self.lambda_tag.setText("Starting lambda:")
        self.slambda = QLineEdit()
        # self.slope.setValidator(QIntValidator())
        self.slambda.setText("1572.42")
        self.slambda.setAlignment(Qt.AlignRight)

        self.slope_tag = QLabel(self)
        self.slope_tag.setText("Slope:")
        self.slope = QLineEdit()
        # self.slope.setValidator(QIntValidator())
        self.slope.setText("396.5")
        self.slope.setAlignment(Qt.AlignRight)
      
        self.result = QLabel(self) # Label 'Output_image'
        self.result.setObjectName("OutputImg")
        # self.result.setFixedHeight(25)   
        # self.result.setFixedWidth(300)        

    def setLayouts(self):
        ''' Set layout here. '''
        self.mainLayout = QVBoxLayout()
        self.resultLayout = QHBoxLayout()
        self.drawLayout = QHBoxLayout()
        self.graphLayout = QGridLayout()
        self.functionLayout = QHBoxLayout()

        self.functionLayout.addWidget(self.modulation, 0, Qt.AlignCenter)
        self.functionLayout.addWidget(self.comboBox, 0, Qt.AlignCenter)
        self.functionLayout.addWidget(self.lambda_tag, 0, Qt.AlignCenter)
        self.functionLayout.addWidget(self.slambda, 0, Qt.AlignCenter)
        self.functionLayout.addWidget(self.slope_tag, 0, Qt.AlignCenter)
        self.functionLayout.addWidget(self.slope, 0, Qt.AlignCenter)
        self.functionLayout.addWidget(self.b1)
        self.functionLayout.addWidget(self.b2)


        self.resultLayout.addWidget(self.result, 0, Qt.AlignCenter)

        self.graph = Graph()
        self.canvas = PlotCanvas(self)
        self.graphLayout.addWidget(self.graph, 0, Qt.AlignCenter)
        self.drawLayout.addWidget(self.canvas)
        
        # Button layout
        self.functionLayout.addWidget(self.Load, 0, Qt.AlignCenter)
        self.functionLayout.addWidget(self.Run, 0, Qt.AlignCenter)
        self.functionLayout.addWidget(self.Fit, 0, Qt.AlignCenter)
        self.functionLayout.addWidget(self.Unfit, 0, Qt.AlignCenter)
        


        # Result layout
        self.functionLayout.addWidget(self.Export, 0, Qt.AlignCenter)
        self.functionLayout.addWidget(self.Reset, 0, Qt.AlignCenter)
        

        self.mainLayout.addLayout(self.graphLayout)
        self.mainLayout.addLayout(self.resultLayout)
        self.mainLayout.addLayout(self.drawLayout)
        self.mainLayout.addSpacing(20)
        self.mainLayout.addLayout(self.functionLayout)
     
        self.setLayout(self.mainLayout)

    def reset(self):
        print("reset")
        #self.canvas.axes.clear()
        # plt.draw()
        # self.canvas.__init__()
        self.canvas.reset()
        self.graph.reset()
        self.result.setText("")
        #self.canvas.updateFigure()
        #self.canvas.__init__()

    def export(self):
        filename = QFileDialog.getSaveFileName(self, 'Save File', "", ".csv")
        #print(filename)
        if (self.b1.isChecked() == True):
            try:
                with open(filename[0]+".csv", "w") as output:
                    writer = csv.writer(output, lineterminator='\n')
                    writer.writerows(map(lambda x, y, z: [x, y, z], self.canvas.lambdas, self.canvas.Qs, self.canvas.couplings))
            except (FileNotFoundError):
                pass
        else:
            try:
                with open(filename[0]+".csv", "w") as output:
                    writer = csv.writer(output, lineterminator='\n')
                    left_lambdas, right_lambdas = self.canvas.lambdas[::2], self.canvas.lambdas[1::2]
                    left_Qs, right_Qs = self.canvas.Qs[::2], self.canvas.Qs[1::2]
                    left_couplings, right_couplings = self.canvas.couplings[::2], self.canvas.couplings[1::2]
                    writer.writerows("B")
                    writer.writerows(map(lambda x, y, z: [x, y, z], left_lambdas, left_Qs, left_couplings))
                    writer.writerows("R")
                    writer.writerows(map(lambda x, y, z: [x, y, z], right_lambdas, right_Qs, right_couplings))
            except (FileNotFoundError):
                pass


    def openQ(self):
        global Qname
        Qname, _ = QFileDialog.getOpenFileName(self, "Open lvm File", "", " *.lvm;;All Files (*)")
        Qname = os.path.normpath(Qname)
        try:
            exp = Qname[:-5] + "1.lvm"
            self.graph.show()
            self.graph.plot(readlvm(exp))
        except (FileNotFoundError):
            pass

    def process(self):
        if (self.b1.isChecked() == True):
            Qs, couplings, lambdas = baseQ(Qname, self.slambda.text(), self.slope.text(), self.comboBox.currentText(), 1)
            self.canvas.setParameter(Qs, couplings, lambdas)
            self.canvas.plot(1)
            self.canvas.updateFigure()
        else:
            fit_range = self.graph.calcRange()
            rg = 0
            if fit_range < 250:
                rg = 1500
            elif fit_range < 500:
                rg = 3000
            elif fit_range < 1000:
                rg = 5000
            else:
                rg = 6000
            Qs, couplings, lambdas = baseQ(Qname, self.slambda.text(), self.slope.text(), self.comboBox.currentText(), 2, rg)
            self.canvas.setParameter(Qs, couplings, lambdas)
            self.canvas.plot(2)
            self.canvas.updateFigure()
        # import numpy as np
        # x = np.asarray(couplings[:-1], dtype='float')
        # Y = np.asarray(Qs[:-1], dtype='float')
        # A = np.vstack([x, np.ones(len(x))]).T
        # m, c = np.linalg.lstsq(A, Y, rcond=None)[0]
        # self.canvas.create_draggable_points(x.min(), m*x.min()+c, x.max(), m*x.max()+c, 0.1, 1000000)

    def fit(self):
        self.canvas.Rsquared()

    def unfit(self):
        self.canvas.unfit()

    # def export(self):
    #     self.canvas.export()

    def updateQ(self, intercept, std_err):
        self.result.setText(str('{:.3e}'.format(intercept))+"±"+str('{:.3e}'.format(std_err)))


    def alert(self, num):
        if (num == 1): QMessageBox.about(self, "Error", "No point selected")
        if (num == 2): QMessageBox.about(self, "Error", "You should fit first")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())