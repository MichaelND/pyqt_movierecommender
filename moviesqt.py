# Michael Wang
# October 6, 2017
# Programming Paradigms: PyQt

import sys
import requests
import json
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class MoviesQT(QMainWindow):
	def __init__(self):
		super(MoviesQT, self).__init__()
		self.setWindowTitle("Movie Recommender")

		#Central
		self.central = MoviesCentral(parent = self)
		self.setCentralWidget(self.central)
		self.setGeometry(100, 100, 500, 500)

		#Add menu bar option - File
		self.filemenu = self.menuBar().addMenu("File")
		fileExitAction = QAction("Exit", self)
		self.filemenu.addAction(fileExitAction)
		self.connect(fileExitAction, SIGNAL("triggered()"), self.exit_program)

		#Add menu bar option - User
		self.filemenu = self.menuBar().addMenu("User")

		#User option (View profile)
		fileViewProfileAction = QAction("View Profile", self)
		self.filemenu.addAction(fileViewProfileAction)
		self.connect(fileViewProfileAction, SIGNAL("triggered()"), self.view_profile)

		#User option (Set user)
		fileSetUserAction = QAction("Set User", self)
		self.filemenu.addAction(fileSetUserAction)
		self.connect(fileSetUserAction, SIGNAL("triggered()"), self.set_user)
		
	def view_profile(self):
		#main dialogue
		self.dialogWindow = QDialog()
		self.dialogWindow.setGeometry(100, 100, 200, 200)
		self.dialogWindow.setWindowTitle("View Profile")

		#get info from user url
		req 	= requests.get(self.central.USERS_URL + str(self.central.uid))
		user 	= json.loads(req.content.decode())

		#set labels
		self.title 		= QLabel()
		self.gender 	= QLabel()
		self.zipcode 	= QLabel()
		self.age 		= QLabel()
		self.okButton 	= QPushButton("OK", self.dialogWindow)

		#listener for ok button clicked
		self.okButton.clicked.connect(self.closeWindow)

		#set text for labels
		self.title.setText("Profile")
		self.gender.setText("Gender: " + user['gender'])
		self.zipcode.setText("Zipcode: " + user['zipcode'])
		self.age.setText("Age: " + str(user['age']))

		#add widgets to the layout 
		layout = QVBoxLayout()
		layout.addWidget(self.title)
		layout.addWidget(self.gender)
		layout.addWidget(self.zipcode)
		layout.addWidget(self.age)
		layout.addWidget(self.okButton)

		#set layout and exec
		self.dialogWindow.setLayout(layout)
		self.dialogWindow.exec()

	def closeWindow(self):
		self.dialogWindow.accept()

	def set_user(self):
		uid, ok = QInputDialog.getInt(self, "Input", "User ID: ")
		if ok:
			self.central.uid = uid

	def exit_program(self):
		app.quit()

class MoviesCentral(QWidget):
	def __init__(self, parent=None):
		super(MoviesCentral, self).__init__(parent)

		#uid and mid
		self.uid = 5
		self.mid = None

		#urls
		self.SITE_URL				= 'http://student04.cse.nd.edu:51001'
		self.RECOMMENDATIONS_URL 	= self.SITE_URL + '/recommendations/'
		self.MOVIES_URL 			= self.SITE_URL + '/movies/'
		self.USERS_URL				= self.SITE_URL + '/users/'
		self.RATINGS_URL			= self.SITE_URL + '/ratings/'

		#add buttons and labels
		self.Title 			= QLabel()
		self.Image 			= QLabel()
		self.Genre			= QLabel()
		self.movieLayout    = QVBoxLayout()
		self.Rating			= QLabel()
		self.upButton 		= QPushButton("UP")
		self.downButton		= QPushButton("DOWN")

		#Align Labels in order vertically
		self.verticalLayout = QVBoxLayout()
		self.Title.setAlignment(Qt.AlignCenter)
		self.Image.setAlignment(Qt.AlignCenter)
		self.Genre.setAlignment(Qt.AlignCenter)
		self.Rating.setAlignment(Qt.AlignCenter)

		#Add widgets to vertical layout
		self.verticalLayout.addWidget(self.Title)
		self.verticalLayout.addWidget(self.Image)
		self.verticalLayout.addWidget(self.Genre)
		self.verticalLayout.addWidget(self.Rating)

		#Listeners for up and down buttons
		self.upButton.clicked.connect(self.upClick)
		self.downButton.clicked.connect(self.downClick)

		#Align buttons with image horizontally
		horizontalLayout = QHBoxLayout()
		horizontalLayout.addWidget(self.upButton)
		horizontalLayout.addLayout(self.verticalLayout)
		horizontalLayout.addWidget(self.downButton)

		#set layout
		self.setLayout(horizontalLayout)

		self.update_movie()

	def update_movie(self):
		#get movie from recommendations based on uid
		r = requests.get(self.RECOMMENDATIONS_URL + str(self.uid))
		resp = json.loads(r.content.decode())
		self.mid = resp['movie_id']

		#get movie info based on mid
		r = requests.get(self.MOVIES_URL + str(self.mid))
		movie = json.loads(r.content.decode())

		#set title
		self.Title.setText(movie['title'])
		
		#set image
		self.IMAGE_DIR = QImage('/home/paradigms/images/' + movie['img'])
		self.Image.setPixmap(QPixmap.fromImage(self.IMAGE_DIR))

		#set genre
		self.Genre.setText(movie['genres'])

		#get movie rating
		r = requests.get(self.RATINGS_URL + str(self.mid))
		rating = json.loads(r.content.decode())

		#set rating
		self.Rating.setText(str(round(rating['rating'], 2)))

	def upClick(self):
		payload = {'movie_id': self.mid, 'rating': '5'}
		r = requests.put(self.RECOMMENDATIONS_URL + str(self.uid), data=json.dumps(payload))
		movie = json.loads(r.content.decode())
		if movie['result'] == 'success':
			self.update_movie()

	def downClick(self):
		payload = {'movie_id': self.mid, 'rating': '1'}
		r = requests.put(self.RECOMMENDATIONS_URL + str(self.uid), data=json.dumps(payload))
		movie = json.loads(r.content.decode())
		if movie['result'] == 'success':
			self.update_movie()

if __name__ == "__main__":
	app = QApplication(sys.argv)
	gui = MoviesQT()
	gui.show()
	sys.exit(app.exec_())
