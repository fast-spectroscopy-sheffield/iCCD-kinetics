import sys
import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import UnivariateSpline as Spline
from PyQt5 import QtCore, QtGui, QtWidgets
from PyUI import Ui_MainWindow
from kineticSplice import KineticSplice
from cosmicRayRemoval import CosmicRayRemoval
import ctypes
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('app')


class App(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('../icon.ico'))
        self.directory = os.path.join(os.path.expanduser('~'), 'Documents')
        self.placeMarker = '- - -'
        self.timeSlicePlot = self.timeSliceDisplay.canvas
        self.scaleIndividualTimeSlices = False
        self.kineticsPlot = self.kineticDisplay.canvas
        self.setConnections()
        self.initialiseDataStorage()
        self.setupDelimiters()
        self.displayStatus('application launched', 'blue', msecs=4000)

###############################################################################
######################    INITIALISATION METHODS    ###########################
###############################################################################

    def initialiseDataStorage(self):
        self.kineticsFilepathsDict = {}
        self.backgroundFilepathsDict = {}
        self.kineticsDict = {}
        self.sliderKeys = {}
        self.dataToPlot = pd.DataFrame()
        self.overlappingTimesList = []

    def setConnections(self):
        self.calibrationFileBrowseButton.clicked.connect(self.calibrationBrowse)
        self.firstKineticBrowseButton.clicked.connect(self.firstKineticBrowse)
        self.kineticFilesBrowseButton.clicked.connect(self.kineticBrowse)
        self.kineticsFilesListWidget.itemClicked.connect(self.fileListSelectionChanged)
        self.startTimesListWidget.itemClicked.connect(self.startTimeSelectionChanged)
        self.gateStepListWidget.itemClicked.connect(self.gateStepSelectionChanged)
        self.backgroundFilesListWidget.itemClicked.connect(self.backgroundListSelectionChanged)
        self.backgroundCheckBox.clicked.connect(self.backgroundCheckBoxSync)
        self.backgroundCheckBoxSync() # Sync up and apply correct formatting immediately
        self.moveUpButton.clicked.connect(self.moveRowUp)
        self.moveDownButton.clicked.connect(self.moveRowDown)
        self.deleteButton.clicked.connect(self.deleteRow)
        self.loadButton.clicked.connect(self.loadData)
        self.addTimeAxisButton.clicked.connect(self.addTimeAxes)
        self.removeCosmicRaysButton.clicked.connect(self.removeCosmicRays)
        self.backgroundSubtractButton.clicked.connect(self.subtractBackgrounds)
        self.joinButton.clicked.connect(self.performJoins)
        self.calibrateButton.clicked.connect(self.applyCalibration)
        self.saveDataButton.clicked.connect(self.saveCompleteKinetic)
        self.timeSlider.valueChanged.connect(self.plotTimeSlice)
        self.autoscaleCheckBox.clicked.connect(self.plotTimeSlice)
        self.scaleButton.clicked.connect(self.scaleButtonClicked)
        self.timeSliceWlMinSpinBox.valueChanged.connect(self.plotTimeSlice)
        self.timeSliceWlMaxSpinBox.valueChanged.connect(self.plotTimeSlice)
        self.kineticCentreWlSpinBox.valueChanged.connect(self.plotKinetic)
        self.kineticCentreWlSpinBox.valueChanged.connect(self.plotTimeSlice)
        self.kineticAveragingSpinBox.valueChanged.connect(self.plotKinetic)
        self.kineticAveragingSpinBox.valueChanged.connect(self.plotTimeSlice)
        self.kineticLogTCheckBox.clicked.connect(self.plotKinetic)
        self.kineticLogYCheckBox.clicked.connect(self.plotKinetic)
        self.kineticNormalisedCheckBox.clicked.connect(self.plotKinetic)
        self.kineticIntegratedCheckBox.clicked.connect(self.plotKinetic)
        self.saveKineticButton.clicked.connect(self.saveKineticSlice)
        self.resetButton.clicked.connect(self.resetApp)

    def setupDelimiters(self):
        self.delimiterComboBox.addItem('tab')
        self.delimiterComboBox.addItem(',')
        self.delimiterComboBox.addItem(':')
        self.delimiterComboBox.addItem(';')
        self.delimiterComboBox.setCurrentIndex(1) # set to comma to start with

###############################################################################
#########################    GENERAL METHODS    ###############################
###############################################################################

    def displayStatus(self, message, colour, msecs=0):
        self.statusBar.clearMessage()
        self.statusBar.setStyleSheet('QStatusBar{color:'+colour+';}')
        self.statusBar.showMessage(message, msecs=msecs)

    def resetApp(self):
        self.timeSlicePlot.ax.cla()
        self.timeSlicePlot.draw()
        self.kineticsPlot.ax.cla()
        self.kineticsPlot.draw()
        self.initialiseDataStorage()
        self.kineticsFilesListWidget.clear()
        self.startTimesListWidget.clear()
        self.gateStepListWidget.clear()
        self.backgroundFilesListWidget.clear()
        self.firstKineticFileListWidget.clear()
        self.firstKineticStartTimeListWidget.clear()
        self.firstKineticGateStepListWidget.clear()
        self.firstKineticBackgroundFileListWidget.clear()
        self.loadButton.setEnabled(True)
        self.addTimeAxisButton.setEnabled(False)
        self.removeCosmicRaysButton.setEnabled(False)
        self.backgroundSubtractButton.setEnabled(False)
        self.joinButton.setEnabled(False)
        self.saveDataButton.setEnabled(False)
        self.saveKineticButton.setEnabled(False)
        self.kineticCentreWlSpinBox.setEnabled(False)
        self.kineticAveragingSpinBox.setEnabled(False)
        self.kineticLogTCheckBox.setEnabled(False)
        self.kineticLogYCheckBox.setEnabled(False)
        self.kineticNormalisedCheckBox.setEnabled(False)
        self.timeSliceWlMaxSpinBox.setEnabled(False)
        self.timeSliceWlMinSpinBox.setEnabled(False)
        self.timeSlider.setEnabled(False)
        self.calibrateButton.setEnabled(False)
        self.autoscaleCheckBox.setEnabled(False)
        self.scaleButton.setEnabled(False)
        self.displayStatus('application reset', 'blue', msecs=4000)


###############################################################################
########################    FILE LOADING METHODS    ###########################
###############################################################################

    def fileListSelectionChanged(self):
        index = self.kineticsFilesListWidget.currentRow()
        self.trackListSelection(index)

    def startTimeSelectionChanged(self):
        index = self.startTimesListWidget.currentRow()
        self.trackListSelection(index)

    def gateStepSelectionChanged(self):
        index = self.gateStepListWidget.currentRow()
        self.trackListSelection(index)

    def backgroundListSelectionChanged(self):
        index = self.backgroundFilesListWidget.currentRow()
        self.trackListSelection(index)

    def trackListSelection(self, index):
        self.kineticsFilesListWidget.setCurrentRow(index)
        self.startTimesListWidget.setCurrentRow(index)
        self.gateStepListWidget.setCurrentRow(index)
        self.backgroundFilesListWidget.setCurrentRow(index)

    @staticmethod
    def addItemToList(listWidget, string, editable=False):
        item = QtWidgets.QListWidgetItem(string)
        if editable:
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        listWidget.addItem(item)
        listWidget.setCurrentItem(item)

    @staticmethod
    def removeCurrentItemFromList(listWidget):
        row = listWidget.currentRow()
        item = listWidget.takeItem(row)
        del(item)

    def fileLoadError(self):
        errorDialog = QtWidgets.QMessageBox()
        errorDialog.setIcon(QtWidgets.QMessageBox.Warning)
        errorDialog.setWindowIcon(QtGui.QIcon('../icon.ico'))
        errorDialog.setWindowTitle('File Load Warning')
        errorDialog.setText('Could not load file(s). App will reset.')
        errorDialog.setDetailedText('Files must be the original ASCII files from the iCCD. Make sure that all start times and gate steps have been entered.')
        errorDialog.exec_()
        self.resetApp()

    def timesError(self):
        errorDialog = QtWidgets.QMessageBox()
        errorDialog.setIcon(QtWidgets.QMessageBox.Warning)
        errorDialog.setWindowIcon(QtGui.QIcon('../icon.ico'))
        errorDialog.setWindowTitle('File Load Warning')
        errorDialog.setText('Not all start times or gate steps entered.')
        errorDialog.exec_()

    def calibrationBrowse(self):
        filetypes = 'CSV (*.csv)'
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'load calibration file', os.path.join(os.path.dirname(os.getcwd()), 'calibration_files'), filetypes)[0]
        if fname != '':
            self.calibrationFileLineEdit.setText(fname)
            try:
                self.calibration = pd.read_csv(fname, index_col=0, header=None, sep=',', squeeze=True)
            except Exception:
                self.fileLoadError()

    def firstKineticBrowse(self):
        filetypes = 'ASCII (*.asc)'
        kfname = QtWidgets.QFileDialog.getOpenFileName(self, 'load first kinetic', self.directory, filetypes)[0]
        if kfname != '':
            self.directory = os.path.dirname(kfname)
            if self.firstKineticFileListWidget.count() == 1:
                self.firstKineticFileListWidget.clear()
                self.firstKineticStartTimeListWidget.clear()
                self.firstKineticGateStepListWidget.clear()
            self.addItemToList(self.firstKineticFileListWidget, os.path.basename(kfname))
            self.addItemToList(self.firstKineticStartTimeListWidget, self.placeMarker, editable=True)
            self.addItemToList(self.firstKineticGateStepListWidget, self.placeMarker, editable=True)
            self.kineticsFilepathsDict[os.path.basename(kfname)] = kfname
            if not self.backgroundCheckBox.isChecked():
                bfname = QtWidgets.QFileDialog.getOpenFileName(self, 'load first background', self.directory, filetypes)[0]
                if bfname != '':
                    self.directory = os.path.dirname(bfname)
                    self.addItemToList(self.firstKineticBackgroundFileListWidget, os.path.basename(bfname))
                    self.backgroundFilepathsDict[os.path.basename(kfname)] = bfname

    def backgroundCheckBoxSync(self):
        '''
        Effectively monitors whether the 1st background checkbox is enabled
        or not, and accordingly greys out the relevant bits, to make it a bit
        clearer for the user.
        '''
        if self.backgroundCheckBox.isChecked() == True:
            self.firstKineticBackgroundFileListWidget.setEnabled(False)
            self.firstKineticBackgroundFileListWidget.setStyleSheet('color: rgb(204, 204, 204)')
            self.firstKineticBackgroundFileListWidgetLabel.setEnabled(False)
            self.firstKineticBackgroundFileListWidgetLabel.setText('1st Background File (not used, since above is checked)')
        else:
            self.firstKineticBackgroundFileListWidget.setEnabled(True)
            self.firstKineticBackgroundFileListWidget.setStyleSheet('color: rgb(0, 0, 0)')
            self.firstKineticBackgroundFileListWidgetLabel.setEnabled(True)
            self.firstKineticBackgroundFileListWidgetLabel.setText('1st Background File (used, since above is NOT checked)')

    def kineticBrowse(self):
        filetypes = 'ASCII (*.asc)'
        kfname = QtWidgets.QFileDialog.getOpenFileName(self, 'load kinetic', self.directory, filetypes)[0]
        if kfname != '':
            self.directory = os.path.dirname(kfname)
            self.addItemToList(self.kineticsFilesListWidget, os.path.basename(kfname))
            self.addItemToList(self.startTimesListWidget, self.placeMarker, editable=True)
            self.addItemToList(self.gateStepListWidget, self.placeMarker, editable=True)
            self.kineticsFilepathsDict[os.path.basename(kfname)] = kfname
            bfname = QtWidgets.QFileDialog.getOpenFileName(self, 'load background', self.directory, filetypes)[0]
            if bfname != '':
                self.directory = os.path.dirname(bfname)
                self.addItemToList(self.backgroundFilesListWidget, os.path.basename(bfname))
                self.backgroundFilepathsDict[os.path.basename(kfname)] = bfname
            else:
                del(self.kineticsFilepathsDict[os.path.basename(kfname)])
                self.removeCurrentItemFromList(self.kineticsFilesListWidget)
                self.removeCurrentItemFromList(self.startTimesListWidget)
                self.removeCurrentItemFromList(self.gateStepListWidget)

    def moveRowUp(self):
        row = self.kineticsFilesListWidget.currentRow()
        itemDataFile = self.kineticsFilesListWidget.takeItem(row)
        itemStartTime = self.startTimesListWidget.takeItem(row)
        itemGateStep = self.gateStepListWidget.takeItem(row)
        itemBackgroundFile = self.backgroundFilesListWidget.takeItem(row)
        self.kineticsFilesListWidget.insertItem(row - 1, itemDataFile)
        self.startTimesListWidget.insertItem(row - 1, itemStartTime)
        self.gateStepListWidget.insertItem(row - 1, itemGateStep)
        self.backgroundFilesListWidget.insertItem(row - 1, itemBackgroundFile)
        self.kineticsFilesListWidget.setCurrentItem(itemDataFile)
        self.startTimesListWidget.setCurrentItem(itemStartTime)
        self.gateStepListWidget.setCurrentItem(itemGateStep)
        self.backgroundFilesListWidget.setCurrentItem(itemBackgroundFile)

    def moveRowDown(self):
        row = self.kineticsFilesListWidget.currentRow()
        itemDataFile = self.kineticsFilesListWidget.takeItem(row)
        itemStartTime = self.startTimesListWidget.takeItem(row)
        itemGateStep = self.gateStepListWidget.takeItem(row)
        itemBackgroundFile = self.backgroundFilesListWidget.takeItem(row)
        self.kineticsFilesListWidget.insertItem(row + 1, itemDataFile)
        self.startTimesListWidget.insertItem(row + 1, itemStartTime)
        self.gateStepListWidget.insertItem(row + 1, itemGateStep)
        self.backgroundFilesListWidget.insertItem(row + 1, itemBackgroundFile)
        self.kineticsFilesListWidget.setCurrentItem(itemDataFile)
        self.startTimesListWidget.setCurrentItem(itemStartTime)
        self.gateStepListWidget.setCurrentItem(itemGateStep)
        self.backgroundFilesListWidget.setCurrentItem(itemBackgroundFile)

    def deleteRow(self):
        self.removeCurrentItemFromList(self.kineticsFilesListWidget)
        self.removeCurrentItemFromList(self.startTimesListWidget)
        self.removeCurrentItemFromList(self.gateStepListWidget)
        self.removeCurrentItemFromList(self.backgroundFilesListWidget)

    def loadData(self):
        blank = False
        try:
            timesEntered = self.checkTimesEntered()
        except AttributeError:
            blank = True
            self.fileLoadError()
        if not blank:
            if timesEntered:
                success = self.loadMethod()
                if not success:
                    self.fileLoadError()
            else:
                self.timesError()

    def checkTimesEntered(self):
        timesList = []
        for index in range(self.startTimesListWidget.count()):
            timesList.append(str(self.startTimesListWidget.item(index).text()))
            timesList.append(str(self.gateStepListWidget.item(index).text()))
        if self.placeMarker in [self.firstKineticStartTimeListWidget.currentItem().text(), self.firstKineticGateStepListWidget.currentItem().text(), *timesList]:
            return False
        else:
            return True

    def loadMethod(self):
        delimiter = self.delimiterComboBox.currentText()
        if delimiter == 'tab':
            delimiter = '\t'
        try:
            firstKineticFilePath = self.kineticsFilepathsDict[self.firstKineticFileListWidget.currentItem().text()]
        except AttributeError:
            return False
        firstKineticStartTime = int(self.firstKineticStartTimeListWidget.currentItem().text())
        firstKineticGateStep = int(self.firstKineticGateStepListWidget.currentItem().text())
        try:
            firstKinetic = pd.read_csv(firstKineticFilePath, index_col=0, header=None, nrows=1024, sep=delimiter)
        except Exception:
            return False
        firstKinetic.dropna(axis=1, inplace=True)
        self.kineticsDict[1] = [firstKinetic, firstKineticStartTime, firstKineticGateStep, 'no separate background']
        if not self.backgroundCheckBox.isChecked():
            try:
                firstKineticBackgroundFilePath = self.backgroundFilepathsDict[self.firstKineticFileListWidget.currentItem().text()]
            except AttributeError:
                return False
            try:
                firstKineticBackground = pd.read_csv(firstKineticBackgroundFilePath, index_col=0, header=None, nrows=1024, sep=delimiter)[1]
            except Exception:
                return False
            self.kineticsDict[1] = [firstKinetic, firstKineticStartTime, firstKineticGateStep, firstKineticBackground]
        for index in range(self.kineticsFilesListWidget.count()):
            kineticFilePath = self.kineticsFilepathsDict[self.kineticsFilesListWidget.item(index).text()]
            kineticStartTime = int(self.startTimesListWidget.item(index).text())
            kineticGateStep = int(self.gateStepListWidget.item(index).text())
            backgroundFilePath = self.backgroundFilepathsDict[self.kineticsFilesListWidget.item(index).text()]
            try:
                kinetic = pd.read_csv(kineticFilePath, index_col=0, header=None, nrows=1024, sep=delimiter)
            except Exception:
                return False
            kinetic.dropna(axis=1, inplace=True)
            try:
                background = pd.read_csv(backgroundFilePath, index_col=0, header=None, nrows=1024, sep=delimiter)[1]
            except Exception:
                return False
            self.kineticsDict[index+2] = [kinetic, kineticStartTime, kineticGateStep, background]
        self.loadButton.setEnabled(False)
        self.addTimeAxisButton.setEnabled(True)
        self.displayStatus('all files loaded successfully', 'green', msecs=4000)
        return True

###############################################################################
########################    DATA PROCESSING METHODS    ########################
###############################################################################

    @staticmethod
    def constructTimeAxis(timeZero, startTime, gateStep, numPoints):
        axis = np.arange(startTime-timeZero, startTime-timeZero+(numPoints*gateStep), gateStep)
        return axis

    def addTimeAxes(self):
        timeZero = int(self.timeZeroSpinBox.value())
        for index in self.kineticsDict.keys():
            kinetic = self.kineticsDict[index][0]
            startTime = self.kineticsDict[index][1]
            gateStep = self.kineticsDict[index][2]
            numPoints = len(kinetic.columns)
            axis = self.constructTimeAxis(timeZero, startTime, gateStep, numPoints)
            kinetic.columns = axis
            background = self.kineticsDict[index][3]
            self.kineticsDict[index] = [kinetic, background]
        self.dataToPlot = self.kineticsDict[1][0]
        self.addTimeAxisButton.setEnabled(False)
        self.removeCosmicRaysButton.setEnabled(True)
        self.backgroundSubtractButton.setEnabled(True)
        self.kineticCentreWlSpinBox.setEnabled(True)
        self.kineticAveragingSpinBox.setEnabled(True)
        self.kineticLogTCheckBox.setEnabled(True)
        self.kineticLogYCheckBox.setEnabled(True)
        self.kineticNormalisedCheckBox.setEnabled(True)
        self.timeSliceWlMinSpinBox.setEnabled(True)
        self.timeSliceWlMaxSpinBox.setEnabled(True)
        self.timeSlider.setEnabled(True)
        self.autoscaleCheckBox.setEnabled(True)
        self.scaleButton.setEnabled(True)
        self.setupTimeSlicePlot()
        self.plotTimeSlice()
        self.setupKineticsPlot()
        self.plotKinetic()
        self.displayStatus('time axis added successfully', 'green', msecs=4000)

    def removeCosmicRays(self):
        for index in self.kineticsDict.keys():
            kinetic = self.kineticsDict[index][0]
            crr = CosmicRayRemoval()
            corrected = crr.removeCosmicRaysPandasDataFrame(kinetic)
            self.kineticsDict[index][0] = corrected
        self.dataToPlot = self.kineticsDict[1][0]
        self.plotTimeSlice()
        self.plotKinetic()
        self.displayStatus('removed cosmic rays', 'green', msecs=4000)

    def subtractBackgrounds(self):
        backgroundEndTime = int(self.backgroundEndTimeSpinBox.value())
        for index in self.kineticsDict.keys():
            kinetic = self.kineticsDict[index][0]
            if index == 1 and self.backgroundCheckBox.isChecked():
                backgroundTimes = kinetic.columns[kinetic.columns <= backgroundEndTime]
                background = kinetic[backgroundTimes].mean(axis=1)
            else:
                background = self.kineticsDict[index][1]
            kinetic = kinetic.subtract(background, axis=0)
            self.kineticsDict[index] = kinetic
        self.dataToPlot = self.kineticsDict[1]
        self.plotTimeSlice()
        self.plotKinetic()
        self.removeCosmicRaysButton.setEnabled(False)
        self.backgroundSubtractButton.setEnabled(False)
        self.joinButton.setEnabled(True)
        self.displayStatus('backgrounds subtracted from all files', 'green', msecs=4000)

    def performJoins(self):
        success = self.joinMethod()
        if not success:
            self.noOverlapError()

    def joinMethod(self):
        sfs = pd.DataFrame(index=self.kineticsDict.keys(), columns=['time', 'sf', 'error'])
        for index in self.kineticsDict.keys():
            if index == 1:
                joinedKinetic = self.kineticsDict[index]
            else:
                toJoin = self.kineticsDict[index]
                overlappedTimes = np.intersect1d(np.array(joinedKinetic.columns), np.array(toJoin.columns))
                if overlappedTimes.size == 0:
                    return False
                overlappedTime = min(overlappedTimes)
                alreadyJoinedArray = np.array(joinedKinetic[overlappedTime])
                toJoinArray = np.array(toJoin[overlappedTime])
                overlappedPair = (alreadyJoinedArray, toJoinArray)
                kspl = KineticSplice(overlappedPair)
                scalingFactor, scalingFactorError = kspl.calculateScalingFactor()
                sfs.loc[index, 'time'] = overlappedTime
                sfs.loc[index, 'sf'] = scalingFactor
                sfs.loc[index, 'error'] = scalingFactorError
                self.plot_joins(index, joinedKinetic.index.values, overlappedPair, overlappedTime, scalingFactor)
                toJoin = toJoin*scalingFactor
                self.overlappingTimesList.append(str(overlappedTime))
                joinedKinetic.drop(joinedKinetic.columns[joinedKinetic.columns >= overlappedTime], axis=1, inplace=True)
                joinedKinetic = joinedKinetic.join(toJoin)
                sfs.index.name = 'join'
        sfs.to_csv(os.path.join(self.directory, 'scaling_factors.csv'), header=True, index=True)
        self.completeKinetic = joinedKinetic
        self.dataToPlot = self.completeKinetic.copy()
        self.setupTimeSlicePlot()
        self.plotTimeSlice()
        self.setupKineticsPlot()
        self.plotKinetic()
        self.joinButton.setEnabled(False)
        self.calibrateButton.setEnabled(True)
        self.saveDataButton.setEnabled(True)
        self.saveKineticButton.setEnabled(True)
        self.displayStatus('join successful', 'green', msecs=4000)
        return True
    
    def plot_joins(self, index, x, overlappedPair, overlappedTime, scalingFactor):
        savedir = os.path.join(self.directory, 'kinetic_joins')
        if not os.path.exists(savedir):
            os.makedirs(savedir)
        fig = plt.figure()
        plt.plot(x, overlappedPair[0], 'k-', label='1st')
        plt.plot(x, scalingFactor*overlappedPair[1], 'r-', label='2nd')
        plt.legend()
        plt.title('t = {0} ns'.format(overlappedTime))
        plt.xlabel('wavelength (nm)')
        plt.ylabel('PL (arb.)')
        fig.savefig(os.path.join(savedir, 'join_{0}.png'.format(index)), format='png', dpi=300, bbox_inches='tight')
        plt.close(fig=fig)        

    def noOverlapError(self):
        errorDialog = QtWidgets.QMessageBox()
        errorDialog.setIcon(QtWidgets.QMessageBox.Warning)
        errorDialog.setWindowIcon(QtGui.QIcon('../icon.ico'))
        errorDialog.setWindowTitle('Overlap Warning')
        errorDialog.setText('No Overlapping Time Points Found. App will reset.')
        errorDialog.exec_()
        self.resetApp()

    def applyCalibration(self):
        try:
            spl = Spline(self.calibration.index, self.calibration.values, s=0)
            reindexed_calibration = pd.Series(index=self.completeKinetic.index, data=spl(self.completeKinetic.index))
            self.completeKinetic = self.completeKinetic.mul(reindexed_calibration, axis=0)
            self.plotTimeSlice()
            self.plotKinetic()
            self.calibrateButton.setEnabled(False)
            self.displayStatus('calibration applied', 'green', msecs=4000)
        except AttributeError:
            self.displayStatus('no calibration file loaded', 'blue', msecs=4000)


###############################################################################
#######################    GRAPH PLOTTING METHODS    ##########################
###############################################################################

    def setupTimeSlicePlot(self):
        self.setupSlider(self.dataToPlot.columns)
        self.timeSliceWlMinSpinBox.setValue(np.floor(min(self.dataToPlot.index)))
        self.timeSliceWlMaxSpinBox.setValue(np.ceil(max(self.dataToPlot.index)))

    def setupSlider(self, times):
        for count, time in enumerate(times):
            self.sliderKeys[count] = time
        self.timeSlider.setMinimum(0)
        self.timeSlider.setMaximum(len(times)-1)
        self.timeSlider.setValue(0)

    def scaleButtonClicked(self):
        self.scaleIndividualTimeSlices = True
        self.plotTimeSlice()
        self.scaleIndividualTimeSlices = False

    def plotTimeSlice(self):
        time = self.sliderKeys[int(self.timeSlider.value())]
        data = self.dataToPlot[time]
        ax = self.timeSlicePlot.ax
        ax.cla()
        ax.plot(data.index, data, 'r-')
        ax.set_title('t = {0}ns'.format(time))
        if not self.autoscaleCheckBox.isChecked() and not self.scaleIndividualTimeSlices:
            ax.set_ylim([self.dataToPlot.min().min()-10, self.dataToPlot.max().max()+10])
        xmin = self.timeSliceWlMinSpinBox.value()
        xmax = self.timeSliceWlMaxSpinBox.value()
        ax.set_xlim([xmin, xmax])
        ax.set_xlabel('Wavelength (nm)')
        ax.set_ylabel('Signal (counts)')
        if not self.kineticIntegratedCheckBox.isChecked():
            ax.axvline(self.kineticCentreWlSpinBox.value(), color='0.5', linestyle='-')
            ax.axvline(self.kineticCentreWlSpinBox.value()-self.kineticAveragingSpinBox.value(), color='0.5', linestyle=':')
            ax.axvline(self.kineticCentreWlSpinBox.value()+self.kineticAveragingSpinBox.value(), color='0.5', linestyle=':')
        self.timeSlicePlot.tight_layout()
        self.timeSlicePlot.draw()

    def setupKineticsPlot(self):
        self.kineticCentreWlSpinBox.setValue(np.round(np.mean(self.dataToPlot.index)))
        self.kineticLogTCheckBox.setChecked(True)
        self.kineticLogYCheckBox.setChecked(True)
        self.kineticNormalisedCheckBox.setChecked(True)

    def getKineticSlice(self):
        if self.kineticIntegratedCheckBox.isChecked():
            data = self.dataToPlot.apply(lambda x: np.trapz(x.values, x=x.index.values))
        else:
            centreWavelength = self.kineticCentreWlSpinBox.value()
            plusMinus = self.kineticAveragingSpinBox.value()
            data = self.dataToPlot[self.dataToPlot.index > centreWavelength-plusMinus]
            data = data[data.index < centreWavelength+plusMinus]
            data = data.mean()
        return data

    def plotKinetic(self):
        ms = 4
        mc = 'bo'
        data = self.getKineticSlice()
        if self.kineticNormalisedCheckBox.isChecked():
            data = data/data.max()
            ylabel = 'Normalised Signal'
        else:
            ylabel = 'Signal (counts)'
        ax = self.kineticsPlot.ax
        ax.cla()
        if self.kineticLogTCheckBox.isChecked() and not self.kineticLogYCheckBox.isChecked():
            data = data[data.index > 0]
            ax.semilogx(data.index, data, mc, markersize=ms)
        elif self.kineticLogYCheckBox.isChecked() and not self.kineticLogTCheckBox.isChecked():
            data = data[data > 0]
            ax.semilogy(data.index, data, mc, markersize=ms)
        elif self.kineticLogYCheckBox.isChecked() and self.kineticLogTCheckBox.isChecked():
            data = data[data.index > 0]
            data = data[data > 0]
            ax.loglog(data.index, data, mc, markersize=ms)
        else:
            ax.plot(data.index, data, mc, markersize=ms)
        ax.set_xlabel('Time (ns)')
        ax.set_ylabel(ylabel)
        self.kineticsPlot.tight_layout()
        self.kineticsPlot.draw()

###############################################################################
##########################    SAVING METHODS    ###############################
###############################################################################

    def saveCompleteKinetic(self):
        self.completeKinetic.to_csv(os.path.join(self.directory, 'completeKinetic.csv'))
        savedir = os.path.join(self.directory, 'kinetic_joins')
        if not os.path.exists(savedir):
            os.makedirs(savedir)
        np.savetxt(os.path.join(savedir, 'overlappedTimes.txt'), self.overlappingTimesList, fmt='%s')
        self.displayStatus('data saved to {0}'.format(os.path.join(self.directory, 'completeKinetic.csv')), 'blue', msecs=4000)

    def saveKineticSlice(self):
        data = self.getKineticSlice()
        if self.kineticIntegratedCheckBox.isChecked():
            data.to_csv(os.path.join(self.directory, 'integratedKinetic.csv'))
            self.displayStatus('data saved to {0}'.format(os.path.join(self.directory, 'integratedKinetic.csv')), 'blue', msecs=4000)
        else:
            centreWavelength = self.kineticCentreWlSpinBox.value()
            plusMinus = self.kineticAveragingSpinBox.value()
            data.to_csv(os.path.join(self.directory, 'kineticSlice{0}pm{1}.csv'.format(centreWavelength, plusMinus)))
            self.displayStatus('data saved to {0}'.format(os.path.join(self.directory, 'kineticSlice{0}pm{1}.csv'.format(centreWavelength, plusMinus))), 'blue', msecs=4000)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = App()
    window.showMaximized()
    sys.exit(app.exec_())
