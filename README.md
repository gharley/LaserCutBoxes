# LaserCutBoxes
### Python utility for generating patterns for laser cut boxes (a work in progress)

This little app is for designing laser cut boxes for different material thicknesses.
I have found a number of cool box designs online but invariably they were designed for a different thickness
of material than I have on hand and resizing is non-trivial. So I wrote this app to allow me to create a box
with any material thickness.

The app creates a basic "tabbed" box with optional slots to allow for an inset lid. Simply 
enter the inside dimension of the box, the material thicknesses, tab width and number of tabs for each side. 
The app will then generate drawings for each side selected, that can then be exported to .SVG files for 
laser cutting.

It is **very important** that you measure the thickness of your material (preferably with calipers) 
to be sure the tabs will fit together. (HINT: round up a bit to be sure there's room.)</br></br>

### Installation
Just download the appropriate file from the dist folder, .EXE for windows or the other for Linux. 
If running on Linux, be sure to give the file "execute" permissions. The app may take a while to
open on Windows.

### Build
If you wish to build/modify the app, download all the source files and run lc_box.py with Python. 
You will need to have Python 3.x installed with PyQt5, lxml and numpy as well as QT 5.x.

### Have Fun!!
Once you have exported files you can import them into an app like LightBurn or RDWorks and then
apply your own designs to the sides. 
Also, consider trying other materials. Acrylic should work well.

I hope you find these macros useful, feel free to modify the code to make it your own and please let 
me know if you find better ways of doing things.

### FreeCAD Users
If you are a user of FreeCAD, I have written a couple of macros you can download 
[here](https://github.com/gharley/FreeCAD_Macros). One of them will 
design a "living-hinge" box.  I hope to eventually incorporate that code into this app.

