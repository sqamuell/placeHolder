project: placeHolder
author:  Sam Losi

project takes two 360-degree images, triangulates their position in 3d space, then constructs 3d geometry from them

project is started simply by running the interface.py file
	confirm that edgeDetection.py,constructGeometry.py,pickPoints.py,drawGeometry.py are located in the same folder
	when prompted, pairing like images from the assets library is 'highly' recommended
	
once in 3d model:
	'e' activates/deactivates the mouse, 
	use mouse to look around,
	arrow keys to move,
	space for up, shift for down

neccesary libraries are:
	openCV
	openGL
	Tkinter
	PIL
	numpy