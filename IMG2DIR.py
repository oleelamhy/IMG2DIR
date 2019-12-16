"""
Version 1.2.0
NOTE: remember to change [self.appVersion] when version is changed

Functionality
    1. Select folder with images, display the first and second image, and previous processed image if exists
    2. Scan the first level of sub-directories, display it as labels for later use
    3. Allow user to input new labels, will automatically create corresponding subdirectory
    4. Allow user to re-do as long as the user have not selected new directory to process
    5. Display remaining images, and current image name

History
    v1.0.0 (28.08.2018): First prototype.
    v1.0.1 (29.08.2018): Improve the GUI for processing the last image. Fixed problem for having only one image in the selected folder.
	v1.0.2 (30.08.2018): Improve the GUI for displaying info of the last image.
    v1.0.3 (18.09.2018): Fixed text label for previous image.
    v1.0.4 (13.11.2018): Added ".tif" to extension list
    v1.1.0 (14.12.2019): Rename application from Image Labeling Tool to IMG2DIR.
    v1.1.1 (15.12.2019): Embedded .ico into single executable compiled by PyInstaller 3.4
    v1.2.0 (15.12.2019): Modified error messages for failed to load images. Cleaned codes.
"""
import sys, os, shutil
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.MainWindow = MainWindow
        self.appVersion = "1.2.0"
        self.imgDir = ""
        self.imgList = []
        self.newImgList = []
        self.labelList = []
        self.labels = {}
        self.btn_labels = {}

        self.boolUndo = False
        self.bool_noNewImg = False

        MainWindow.setWindowTitle('IMG2DIR (v{})'.format(self.appVersion))
        MainWindow.setFixedSize(1900, 900)

        # set window icon for single executable compiled with PyInstaller 3.4
        if hasattr(sys, '_MEIPASS'):
            MainWindow.setWindowIcon(QIcon(os.path.join(sys._MEIPASS, "img/IMG2DIR.ico")))

        # set window icon for simply executing .py file
        else:
            MainWindow.setWindowIcon(QIcon("img/IMG2DIR.ico"))

        self.status = QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.status)

        self.run(MainWindow)

        message = "Initialization completed."
        # print(message)
        self.status.showMessage(message)

        MainWindow.show()

    def run(self, MainWindow):
        widget_main = QWidget(MainWindow)

        '''Header'''
        widget_header = QWidget(widget_main)
        widget_header.setGeometry(QRect(0, 0, 1900, 65))
        header = QFormLayout(widget_header)
        header.setContentsMargins(10, 10, 10, 10)

        self.label_seletedFolder = QLabel("...", widget_header)

        header.setWidget(0, QFormLayout.FieldRole, self.label_seletedFolder)

        btn_selectFolder = QPushButton("Select folder", widget_header)
        btn_selectFolder.setToolTip("Select the folder containing the images.")
        btn_selectFolder.resize(btn_selectFolder.sizeHint())
        btn_selectFolder.clicked.connect(self.openFolderDialog)

        header.setWidget(0, QFormLayout.LabelRole, btn_selectFolder)


        '''Image Preview'''
        widget_imagePreview = QWidget(widget_main)
        widget_imagePreview.setGeometry(QRect(0, 60, 990, 810))
        hbox_imagePreview = QHBoxLayout(widget_imagePreview)
        hbox_imagePreview.setContentsMargins(10, 10, 10, 10)

        gb_imagePreview = QGroupBox("Image Preview", widget_imagePreview)

        self.label_imgName = QLabel(gb_imagePreview)
        self.label_imgName.resize(500, 25)
        self.label_imgName.move(10, 755)
        self.label_imgName.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)

        self.label_imgNum = QLabel(gb_imagePreview)
        self.label_imgNum.resize(250, 25)
        self.label_imgNum.move(700, 755)
        self.label_imgNum.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.label_imagePreview = QLabel(gb_imagePreview)
        self.label_imagePreview.setGeometry(QRect(10, 30, 950, 710))
        self.label_imagePreview.setAlignment(Qt.AlignCenter)

        hbox_imagePreview.addWidget(gb_imagePreview)


        '''Image Preview for Previous and Next'''
        widget_preview = QWidget(widget_main)
        widget_preview.setGeometry(QRect(990, 60, 910, 415))
        hbox_preview = QHBoxLayout(widget_preview)
        hbox_preview.setContentsMargins(10, 10, 10, 10)

        gb_preview = QGroupBox("Preview", widget_preview)

        self.label_imagePrevious = QLabel(gb_preview)
        self.label_imagePrevious.setGeometry(QRect(10, 30, 435, 325))
        self.label_imagePrevious.setAlignment(Qt.AlignCenter)

        self.label_imgPrevious = QLabel(gb_preview)
        self.label_imgPrevious.setText("Previous Image")
        self.label_imgPrevious.resize(500, 25)
        self.label_imgPrevious.move(10, 360)
        self.label_imgPrevious.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)

        btn_undoPrevious = QPushButton("Undo Previous", gb_preview)
        btn_undoPrevious.setToolTip("Undo the labeling of the previous image")
        btn_undoPrevious.resize(btn_undoPrevious.sizeHint())
        btn_undoPrevious.move(350, 360)
        btn_undoPrevious.clicked.connect(self.undoPreviousImage)


        self.label_imageNext = QLabel(gb_preview)
        self.label_imageNext.setGeometry(QRect(450, 30, 435, 325))
        self.label_imageNext.setAlignment(Qt.AlignCenter)

        self.label_imgNext = QLabel(gb_preview)
        self.label_imgNext.setText("Next Image")
        self.label_imgNext.resize(500, 25)
        self.label_imgNext.move(450, 360)
        self.label_imgNext.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)

        hbox_preview.addWidget(gb_preview)


        '''Labels'''
        widget_label = QWidget(widget_main)
        widget_label.setGeometry(QRect(990, 470, 910, 400))
        vbox_label = QHBoxLayout(widget_label)
        vbox_label.setContentsMargins(10, 10, 10, 10)

        gb_label = QGroupBox("Labels", widget_label)

        # create the first column of labels and buttons
        for x in range(1, 11):
            self.labels[x] = QLineEdit(gb_label)
            self.labels[x].resize(400, 25)
            self.labels[x].move(10, (30*x + 5*(x-1)))
            self.labels[x].setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            self.labelList.append(self.labels[x])

            self.btn_labels[x] = QPushButton(">>", gb_label)
            self.btn_labels[x].setObjectName(str(x))
            self.btn_labels[x].setToolTip("Move the current image to the subdirectory")
            self.btn_labels[x].resize(25, 27)
            self.btn_labels[x].move(415, (30*x + 5*(x-1))-1)
            self.btn_labels[x].clicked.connect(self.moveImage)

        # create the second column of labels and buttons
        for x in range(11, 21):
            self.labels[x] = QLineEdit(gb_label)
            self.labels[x].resize(400, 25)
            self.labels[x].move(450, (30*(x-10) + 5*(x-11)))
            self.labels[x].setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
            self.labelList.append(self.labels[x])

            self.btn_labels[x] = QPushButton(">>", gb_label)
            self.btn_labels[x].setObjectName(str(x))
            self.btn_labels[x].setToolTip("Move the current image to the subdirectory")
            self.btn_labels[x].resize(25, 27)
            self.btn_labels[x].move(855, (30*(x-10) + 5*(x-11))-1)
            self.btn_labels[x].clicked.connect(self.moveImage)

        vbox_label.addWidget(gb_label)

        MainWindow.setCentralWidget(widget_main)


    def openFolderDialog(self):
        try:
            # set bool_noNewImg to False
            self.bool_noNewImg = False

            # if Undo button is not pressed
            # reset self.newImgList and previous image preview
            if (self.boolUndo == False):
                cwd = str(os.getcwd())
                self.imgDir = QFileDialog.getExistingDirectory(None, "Select Folder", cwd, QFileDialog.ShowDirsOnly)

                # display the name of folder in python console, statusbar and label
                message = '{} is selected.'.format(self.imgDir)
                # print(message)
                self.label_seletedFolder.setText(str(self.imgDir))
                self.status.showMessage(message)

                self.newImgList = []
                self.label_imagePrevious.clear()


            # get the size of image set in the directory
            self.imgList = []
            imageExtenstions = ["jpg", "png", "JPG", "tif"]
            tmp_imgList = [fn for fn in os.listdir(self.imgDir)
                         if any(fn.endswith(ext) for ext in imageExtenstions)]        # used wihen there is no subdirectories
            self.imgList += tmp_imgList

            imgListSize = len(self.imgList)

            # print the number of images and the image list in the python console
            print('{} images found in {}'.format(imgListSize, self.imgDir))

            # display image on QGraphicsScene
            self.img = os.path.join(self.imgDir, self.imgList[0])

            # display the first image in the folder
            self.label_imagePreview.clear()
            self.label_imagePreview.setPixmap(QPixmap(self.img).scaled(self.label_imagePreview.size(), Qt.KeepAspectRatio))

            # display the next image in the folder
            if (len(self.imgList) > 1):
                self.nextImg = os.path.join(self.imgDir, self.imgList[1])
                self.label_imageNext.clear()
                self.label_imageNext.setPixmap(QPixmap(self.nextImg).scaled(self.label_imageNext.size(), Qt.KeepAspectRatio))

            # display the name of the image on the label and the "progress counter" on the other label
            self.imgName = self.imgList[0]
            self.label_imgName.setText(str(self.imgName))
            self.label_imgNum.setText('{} images remaining'.format(len(self.imgList)))

            # get the list of subfolders' name
            subfolders = [f.name for f in os.scandir(self.imgDir) if f.is_dir()]
            print(subfolders)

            # clear the labelList
            for i in range(len(self.labelList)):
                self.labelList[i].clear()

            # display the subfolders' names on the labels b columns
            if (len(subfolders) < 20):
                for i in range(len(subfolders)):
                    self.labelList[i].setText(str(subfolders[i]))

            else:
                message = "More than 20 subdirectories are found. Only the first 20 are displayed as label."
                # print(message)
                self.status.showMessage(message)

            # reset the boolean for undo to False
            self.boolUndo = False

        except:
            # if there is no image in the selected folder
            if (len(self.imgList) == 0 and os.path.isdir(self.imgDir)):
                message = 'No images found in the selected folder {}'.format(self.imgDir)
                # print(message)
                self.status.showMessage(message)

            # if no folder is selected or if the dialog is closed, display the message on python console and statusbar
            else:
                message = "No directory is selected. Failed to load images."
                # print(message)
                self.status.showMessage(message)

            # reset the label of selected folder, image name and "progress counter"
            self.label_seletedFolder.setText("...")
            self.imgName = ""
            self.label_imgName.setText("")
            self.label_imgNum.setText("")

            # clear the QGraphicsView
            self.label_imagePreview.clear()
            self.label_imagePrevious.clear()
            self.label_imageNext.clear()

            # clear the image name of previous image
            self.label_imgPrevious.setText('Previous Image')

            # clear the labels
            for i in range(len(self.labelList)):
                self.labelList[i].clear()

            pass


    def displayNextImage(self):
        self.status.showMessage("")
        try:
            imgIndex = self.imgList.index(self.imgName)

            if (imgIndex < len(self.imgList)-2):
                self.img = os.path.join(self.imgDir, self.imgList[imgIndex+1])

                # display the next image on the image previewer
                self.label_imagePreview.clear()
                self.label_imagePreview.setPixmap(QPixmap(self.img).scaled(self.label_imagePreview.size(), Qt.KeepAspectRatio))

                self.imgName = self.imgList[imgIndex+1]
                self.label_imgName.setText(str(self.imgName))
                self.label_imgNum.setText('{} images remaining'.format(len(self.imgList) - (imgIndex+1)))

                # display the next next image on the next image previewer
                self.nextImg = os.path.join(self.imgDir, self.imgList[imgIndex+2])
                self.label_imageNext.clear()
                self.label_imageNext.setPixmap(QPixmap(self.nextImg).scaled(self.label_imageNext.size(), Qt.KeepAspectRatio))

            elif (imgIndex < len(self.imgList)-1):
                self.img = os.path.join(self.imgDir, self.imgList[imgIndex+1])

                # display the next image on the image previewer
                self.label_imagePreview.clear()
                self.label_imagePreview.setPixmap(QPixmap(self.img).scaled(self.label_imagePreview.size(), Qt.KeepAspectRatio))

                self.imgName = self.imgList[imgIndex+1]
                self.label_imgName.setText(str(self.imgName))
                self.label_imgNum.setText('{} images remaining'.format(len(self.imgList) - (imgIndex+1)))

                # clear the next image preview
                self.label_imageNext.clear()

            else:
                # clear the current and next image preview
                self.label_imagePreview.clear()
                self.label_imageNext.clear()

                # update the label of the image name and remaining image
                self.label_imgName.setText("")
                self.label_imgNum.setText('0 images remaining')

                # set the bool_noNewImg to True
                self.bool_noNewImg = True

                message = "This is the last image in this folder."
                # print(message)
                self.status.showMessage(message)

        except:
            message = "Please select a folder to proceed."
            # print(message)
            self.status.showMessage(message)

            pass


    def displayPreviousImage(self):
        self.status.showMessage("")

        try:
            self.label_imagePrevious.clear()

            if (len(self.newImgList) > 0):
                self.previousImg = os.path.join(self.imgDir, self.newImgList[-1])
                self.label_imagePrevious.setPixmap(QPixmap(self.previousImg).scaled(self.label_imagePrevious.size(), Qt.KeepAspectRatio))

        except:
            self.label_imagePrevious.clear()

            message = "There is no previous image."
            # print(message)
            self.status.showMessage(message)

            pass


    def undoPreviousImage(self):
        self.status.showMessage("")

        try:
            # set the boolUndo to True so it won't invoke the code to ask for folder nor clear newImgList
            self.boolUndo = True

            # get the previously processed image from the newImgList last element
            # move this image back to the imgDir
            previousImgPath = os.path.join(self.imgDir, self.newImgList[-1])
            shutil.move(previousImgPath, os.path.join(self.imgDir, os.path.basename(previousImgPath)))
            print('Image moved to {}'.format(os.path.join(self.imgDir, os.path.basename(previousImgPath))))

            # remove the last element of the newImgList
            self.newImgList = self.newImgList[:-1]

            if (len(self.newImgList) > 0):
                self.label_imgPrevious.setText('Previous Image: {}'.format(self.newImgList[-1]))

            elif(len(self.newImgList) == 0):
                self.label_imgPrevious.setText('Previous Image')

            # "refresh" the previous image preview
            # and run the openFolderDialog to get the new imgList,
            # which will update the current display and next image preview
            self.displayPreviousImage()
            self.openFolderDialog()

        except:
            message = "There is no previous image to undo."
            # print(message)
            self.status.showMessage(message)

            self.label_imgPrevious.setText('Previous Image')

            # set the boolUndo to False
            self.boolUndo = False

            pass


    def moveImage(self):
        self.status.showMessage("")

        try:
            # get the current image index and path
            imgIndex = self.imgList.index(self.imgName)
            self.img = os.path.join(self.imgDir, self.imgList[imgIndex])

            # get the button's object name and convert it into label index
            # get the label text
            sender_button = self.MainWindow.sender()

            labelIndex = int(sender_button.objectName())
            labelText = self.labelList[labelIndex-1].text()

            # only if the label text is not NULL, rename the image path
            # save the new path (subdir + imgName) into newImgList
            if (labelText != ""):
                labelTextDir = os.path.join(self.imgDir, labelText)

                # create subdirectory is not already existed
                if not os.path.exists(labelTextDir):
                    os.makedirs(labelTextDir)
                    print('{} is created.'.format(labelTextDir))

                self.newImg = os.path.join(labelText, self.imgList[imgIndex])
                self.newImgList.append(self.newImg)

                # move the image to the subdirectory
                shutil.move(self.img, os.path.join(self.imgDir, self.newImg))

                # print message on console and statusbar
                message = 'Image moved to {}'.format(self.newImgList[-1])
                # print(message)
                self.status.showMessage(message)

                # display the processed image (previous image) and the next image
                self.displayNextImage()
                self.displayPreviousImage()

                self.label_imgPrevious.setText('Previous Image: {}'.format(self.newImgList[-1]))

            # if the labelText is empty, display message on console and statusbar
            elif(labelText == ""):
                message = "Label is empty. Please enter a label name to proceed."
                # print(message)
                self.status.showMessage(message)

        except:
            if (self.bool_noNewImg == True):
                message = "No more images to move. Please select a new folder to proceed."
                # print(message)
                self.status.showMessage(message)

            else:
                message = "Image is not moved."
                # print(message)
                self.status.showMessage(message)

            pass


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
