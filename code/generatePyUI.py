from PyQt5 import uic

with open('PyUI.py', 'w') as file:
    uic.compileUi('app.ui', file)