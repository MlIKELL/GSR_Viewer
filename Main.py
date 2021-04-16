
import sys
from copy import deepcopy

import pandas as pd
from Processamento.Moving_Average import moving_average
import csv
import serial
import numpy as np
from pathlib import Path
import pyqtgraph as pg
from GUI.PopUpWindow import warning, selection_pop_up, saving_pop_up
from GetArduino.get_arduino import get_arduino_port
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QApplication, QWidget, QHBoxLayout, QSplitter,\
    QVBoxLayout, QLabel, QComboBox, QPushButton, QProgressBar, QFileDialog, QListWidget, QSpinBox


class Janelaprincipal(QMainWindow):
    counter = 0
    counter_3 = 0
    progresso = 0
    number_files = 0
    leitura = []
    AuxTempo = []
    AuxAverage = []
    unsaved_files = []



    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        self.file_data = {}

        self.divisoes = Split(self)
        self.setCentralWidget(self.divisoes)

        self.divisoes.bottomleft.add_file.clicked.connect(self.open_file)
        self.divisoes.bottomleft.clr.clicked.connect(self.limpar_janela)
        self.divisoes.bottomleft.init_bttn.clicked.connect(self.iniciar_leitura)
        self.divisoes.bottomleft.stop_bttn.clicked.connect(self.parar_leitura)
        self.divisoes.bottomleft.timer.timeout.connect(self.step_leitura)
        self.divisoes.bottomleft.show_graph.clicked.connect(self.plotar)


        self.resize(1280, 720)
        self.center()
        self.setWindowIcon(QIcon("GUI/Icons/chart.svg"))
        self.setWindowTitle('GSR Viewer')
        self.show()

    def center(self):

        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2),
                  int((screen.height() - size.height()) / 2))

    def open_file(self):
        i = 0
        Aux_checagem_list = []
        flag = False
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file', filter='*.csv')

        if fname:
            for i in range(self.divisoes.bottomleft.file_list.count()):
                Aux_checagem = self.divisoes.bottomleft.file_list.item(i).text()
                Aux_checagem_list.append(Aux_checagem)

            if Path(fname).stem in Aux_checagem_list:
                print(Aux_checagem_list)
                warning('Variável já existe')

            else:
                df = pd.read_csv(fname)
                time = df.Tempo.values.tolist()
                Valor = df.Valor.values.tolist()

                self.file_data[Path(fname).stem] = {'Tempo': time,'Valor': Valor}
                self.divisoes.bottomleft.file_list.insertItem(self.number_files, Path(fname).stem)
                self.number_files = self.number_files + 1



    def limpar_janela(self):
        if len(self.unsaved_files) !=0:
            selection_pop_up('AVISO', 'Existem variáveis nao salvas. \n Deseja Salvá-las?', self.limpar_janela_handler)
        else:
            self.divisoes.bottomleft.file_list.clear()
            self.number_files = 0
            self.file_data.clear()
            self.unsaved_files.clear()

    def limpar_janela_handler(self, action):
        Auxtamanho = len(self.leitura)
        i = 0
        if action != -1:
            if action == 1:
                for file in self.unsaved_files:
                    fname, _ = QFileDialog.getSaveFileName(self, 'Save', filter='*.csv')
                    if fname:
                        with open(fname, 'w') as csv_file:
                            writer = csv.writer(csv_file)
                            writer.writerow(['Tempo', 'Valor'])
                            while i < Auxtamanho:
                                writer.writerow([self.file_data[file]['Tempo'][i], self.file_data[file]['Valor'][i]])
                                i = i + 1



            self.divisoes.bottomleft.file_list.clear()
            self.number_files = 0
            self.file_data.clear()
            self.unsaved_files.clear()


    def iniciar_leitura(self):
         self.divisoes.bottomleft.init_bttn.setDisabled(True)
         self.divisoes.bottomleft.stop_bttn.setEnabled(True)
         self.progresso = 0
         self.divisoes.right.plot.clear()
         self.leitura.clear()
         self.AuxTempo.clear()
         self.AuxAverage.clear()
         self.divisoes.bottomleft.clr.setDisabled(True)
         self.valor_atual = self.divisoes.bottomleft.time_selection.value() * 10
         try:
             porta = self.divisoes.topleft.port_selection.currentText()
             self.ser = serial.Serial(port=porta, baudrate=9600)
             self.divisoes.bottomleft.show_graph.setDisabled(True)
             self.divisoes.bottomleft.timer.start(100)
         except:
             warning('Arduíno não Conectado')
             self.divisoes.bottomleft.init_bttn.setEnabled(True)
             self.divisoes.bottomleft.stop_bttn.setDisabled(True)
             self.divisoes.bottomleft.clr.setEnabled(True)


    def parar_leitura(self):
        self.divisoes.bottomleft.timer.stop()
        self.counter = 0
        self.counter_3 = 0
        self.divisoes.bottomleft.init_bttn.setEnabled(True)
        self.divisoes.bottomleft.stop_bttn.setDisabled(True)
        self.divisoes.bottomleft.show_graph.setEnabled(True)
        self.divisoes.bottomleft.clr.setEnabled(True)
        self.ser.close()
        saving_pop_up('AVISO', 'Você deseja salvar o arquivo gerado pela leitura?', self.parar_leitura_handler)

    def parar_leitura_handler(self, action):
        Auxtamanho = len(self.leitura)
        i=0
        if action == 1:
            fname, _ = QFileDialog.getSaveFileName(self, 'Save', filter='*.csv')
            if fname:
                with open(fname,'w') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(['Tempo','Valor'])

                    while i < Auxtamanho:
                        writer.writerow([self.AuxTempo[i],self.leitura[i]])
                        i=i+1

                    csv_file.close()

                self.divisoes.bottomleft.file_list.insertItem(self.number_files, Path(fname).stem)
                self.number_files = self.number_files + 1
                self.file_data[Path(fname).stem] = deepcopy({'Tempo': self.AuxTempo, 'Valor': self.leitura})

        elif action != 1:
            Auxnome = 'leitura' + str(self.number_files + 1)
            self.divisoes.bottomleft.file_list.insertItem(self.number_files, Auxnome)
            self.unsaved_files.append(Auxnome)

            self.file_data[Auxnome] = deepcopy({'Tempo': self.AuxTempo,'Valor': self.leitura})
            self.number_files = self.number_files + 1



    def step_leitura(self):

        self.counter = self.counter +1
        self.counter_3 = self.counter_3 + 1
        self.leitura.append(int(self.ser.readline()))
        self.AuxTempo.append(self.counter/10)
        self.progresso = (self.counter / self.valor_atual) * 100

        if self.counter_3 == 30:
            self.AuxAverage = moving_average(self.leitura, 0.95, 30)
            self.divisoes.right.plot.clear()
            self.divisoes.right.plot.addLegend()
            self.divisoes.right.plot.plot(self.AuxTempo, self.leitura, pen=pg.mkPen('r', width=3), name='Sinal GSR')
            self.divisoes.right.plot.plot(self.AuxTempo[0:-15], self.AuxAverage[15:], pen=pg.mkPen('b', width=3), name='Nível Tônico')
            self.counter_3= 0

        self.divisoes.bottomleft.progress.setValue(self.progresso)


        if self.counter == self.valor_atual:

            self.divisoes.bottomleft.timer.stop()
            self.counter = 0
            self.counter_3 = 0
            self.divisoes.bottomleft.init_bttn.setEnabled(True)
            self.divisoes.bottomleft.stop_bttn.setDisabled(True)
            self.divisoes.bottomleft.show_graph.setEnabled(True)
            self.divisoes.bottomleft.clr.setEnabled(True)
            self.ser.close()
            saving_pop_up('AVISO', 'Você deseja salvar o arquivo gerado pela leitura?', self.parar_leitura_handler)





    def plotar(self):

        try:
            item = self.divisoes.bottomleft.file_list.currentItem().text()
            self.divisoes.right.plot.clear()
            self.divisoes.right.plot.addLegend()
            self.divisoes.right.plot.plot(self.file_data[item]['Tempo'],self.file_data[item]['Valor'],pen=pg.mkPen('k', width=3), name='Sinal GSR')

            AuxAverages = moving_average(self.file_data[item]['Valor'], 0.95, 250)

            self.divisoes.right.plot.plot(self.file_data[item]['Tempo'][0:-180], AuxAverages[180:],pen=pg.mkPen('m', width=3), name='Nível Tônico')

        except:
            itens = self.divisoes.bottomleft.file_list.count()


class TopLeft(QWidget):

    def __init__(self,parent):
        super().__init__(parent)

        self.initTopLeft()

    def initTopLeft(self):

        self.texto1 = QLabel(self)
        self.texto1.setText('Selecione a Porta de Comunicação do Arduíno')
        self.port_selection = QComboBox(self)
        self.port_selection.addItems(get_arduino_port())
        self.refresh_bttn = QPushButton('Atualizar', self)



        self.refresh_bttn.clicked.connect(self.buttonClicked)



        vbox = QVBoxLayout()
        vbox.addWidget(self.texto1)
        vbox.addWidget(self.port_selection)
        vbox.addWidget(self.refresh_bttn)
        vbox.addStretch(1)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox)
        hbox.addStretch(1)

        self.setLayout(hbox)

    def buttonClicked(self):
         sender = self.sender()
         self.port_selection.clear()
         self.port_selection.addItems(get_arduino_port())



class BottomLeft(QWidget):

    def __init__(self,parent):
        super().__init__(parent)

        self.initBottomLeft()


    def initBottomLeft(self):

        self.texto3 = QLabel(self)
        self.texto3.setText('Selecione o Tempo de Duração da Leitura \n em Segundos (s)')
        self.texto3.adjustSize()


        self.time_selection = QSpinBox(self)
        # self.time_selection.setMinimum(10)
        # self.time_selection.setMaximum(900)
        self.time_selection.setRange(10,900)
        self.time_selection.setSingleStep(10)

        self.init_bttn = QPushButton('Iniciar Leitura', self)
        self.stop_bttn = QPushButton('Parar Leitura', self)
        self.stop_bttn.setDisabled(True)

        self.file_list = QListWidget()
        self.file_list.setMaximumWidth(219)
        self.file_list.horizontalScrollBar().setValue(10)

        self.add_file = QPushButton('Adicionar Arquivo', self)
        self.clr = QPushButton('Limpar Janela', self)
        self.show_graph = QPushButton('Mostrar Gráfico do Arquivo Selecionado', self)
        self.progress = QProgressBar()
        self.progress.setMinimumWidth(219)

        self.timer = QTimer(self)


        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.init_bttn)
        hbox2.addWidget(self.stop_bttn)
        hbox5 = QHBoxLayout()
        hbox5.addWidget(self.add_file)
        hbox5.addWidget(self.clr)

        vbox2 = QVBoxLayout()
        vbox2.addWidget(self.texto3)
        vbox2.addWidget(self.time_selection)
        vbox2.addLayout(hbox2)
        vbox2.addWidget(self.file_list)
        vbox2.addLayout(hbox5)
        vbox2.addWidget(self.show_graph)
        vbox2.addWidget(self.progress)


        hbox4 = QHBoxLayout()
        hbox4.addLayout(vbox2)
        hbox4.addStretch(1)



        self.setLayout(hbox4)


class Right(QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        self.initRight()

    def initRight(self):

        hbox6 = QHBoxLayout()
        vbox3 = QVBoxLayout()

        font = QFont()
        font.setPixelSize(20)

        self.plot = pg.PlotWidget()
        self.plot.setBackground('w')
        self.plot.setTitle('Medição GSR',**{'color':'k', 'size':'18pt'})
        self.plot.setLabel('left',text= '<font size = "6">Valor</font>')
        self.plot.setLabel('bottom', text='<font size = "6">Tempo (s)</font>')
        self.plot.getAxis('left').setTextPen('k')
        self.plot.getAxis('left').setStyle(tickFont=font)
        self.plot.getAxis('bottom').setTextPen('k')
        self.plot.getAxis('bottom').setStyle(tickFont= font)
        self.plot.getAxis('top').setTextPen('k')
        self.plot.showGrid(x = True, y = True)


        vbox3.addWidget(self.plot)
        hbox6.addLayout(vbox3)

        self.setLayout(hbox6)


class Split(QWidget):

    def __init__(self, parent):
        super().__init__(parent)

        self.initSplit()

    def initSplit(self):

        hbox3 = QHBoxLayout(self)

        self.topleft = TopLeft(self)

        self.bottomleft = BottomLeft(self)

        self.right = Right(self)

        splitter1 = QSplitter(Qt.Vertical)
        splitter1.addWidget(self.topleft)
        splitter1.addWidget(self.bottomleft)
        splitter1.setStretchFactor(1, 2)
        index = splitter1.indexOf(self.topleft)
        splitter1.setCollapsible(index, False)
        index3 = splitter1.indexOf(self.bottomleft)
        splitter1.setCollapsible(index3, False)


        splitter2 = QSplitter(Qt.Horizontal)
        splitter2.addWidget(splitter1)
        splitter2.addWidget(self.right)
        splitter2.setStretchFactor(1,10)
        index2 = splitter2.indexOf(splitter1)
        splitter2.setCollapsible(index2, False)
        hbox3.addWidget(splitter2)

        self.setLayout(hbox3)


def main():
    app = QApplication(sys.argv)
    ex = Janelaprincipal()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
