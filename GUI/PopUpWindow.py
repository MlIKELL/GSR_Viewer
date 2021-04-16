from functools import partial

from PyQt5.QtWidgets import QMessageBox

selection_pop_up_key = {
    'Cancel': -1,
    'OK': 1,
    '&No': 0
}

selection_pop_up_key2 = {
    'Save': 1,
    '&No': 0
}

button_name_map = {
    'Cancel': 'Cancelar',
    'OK': 'Sim',
    '&No': 'Não'
}

button_name_map2 = {
    'Save': 'Salvar',
    '&No': 'Não'
}

def warning(text):
    pop_up = QMessageBox()
    pop_up.setWindowTitle("ATENÇÃO")
    pop_up.setText(text)
    pop_up.setIcon(QMessageBox.Warning)
    pop_up.exec_()



def selection_pop_up(title, text, function):
    pop_up = QMessageBox()
    pop_up.setWindowTitle(title)
    pop_up.setText(text)
    pop_up.setIcon(QMessageBox.Question)
    pop_up.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok | QMessageBox.No)

    for button in pop_up.buttons():
        button.clicked.connect(partial(function, selection_pop_up_key[button.text()]))
        button.setText(button_name_map[button.text()])

    pop_up.exec_()

def saving_pop_up(title, text, function):
    pop_up = QMessageBox()
    pop_up.setWindowTitle(title)
    pop_up.setText(text)
    pop_up.setIcon(QMessageBox.Question)
    pop_up.setStandardButtons(QMessageBox.Save | QMessageBox.No)

    for button in pop_up.buttons():
        button.clicked.connect(partial(function, selection_pop_up_key2[button.text()]))
        button.setText(button_name_map2[button.text()])

    pop_up.exec_()


