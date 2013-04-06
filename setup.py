# We will be using py2exe to build the binaries.
# You may use other tools, but I know this one.

from distutils.core import setup
import py2exe
import shutil
import os

from distutils.filelist import findall
import os
import matplotlib
matplotlibdatadir = matplotlib.get_data_path()
matplotlibdata = findall(matplotlibdatadir)
matplotlibdata_files = []
for f in matplotlibdata:
    dirname = os.path.join('matplotlibdata', f[len(matplotlibdatadir)+1:])
    matplotlibdata_files.append((os.path.split(dirname)[0], [f]))


data_files = matplotlib.get_py2exe_datafiles() + [
            ('phonon_backend', [
                'C:\Python27\Lib\site-packages\PyQt4\plugins\phonon_backend\phonon_ds94.dll'
                ]),
            ('imageplugins', [
            'c:\Python27\lib\site-packages\PyQt4\plugins\imageformats\qgif4.dll',
            'c:\Python27\lib\site-packages\PyQt4\plugins\imageformats\qjpeg4.dll',
            'c:\Python27\lib\site-packages\PyQt4\plugins\imageformats\qsvg4.dll',
            ])]
# Now you need to pass arguments to setup
# windows is a list of scripts that have their own UI and
# thus don't need to run in a console.

setup(windows=[{'script':'MetroMathPlot.py','icon_resources':[(1,"images/DMathPlot.ico")]}],
      options={

# And now, configure py2exe by passing more options;

          'py2exe': {

# This is magic: if you don't add these, your .exe may
# or may not work on older/newer versions of windows.

              "dll_excludes": [
                  "MSVCP90.dll",
                  "MSWSOCK.dll",
                  "mswsock.dll",
                  "powrprof.dll",
                  ],

# Py2exe will not figure out that you need these on its own.
# You may need one, the other, or both.

              'includes': [
                  'sip',
                  'PyQt4',
                  'PyQt4.QtGui',
                  'PyQt4.QtCore',
                  'matplotlib.backends',
                  'matplotlib.backends.backend_qt4agg',
                  'matplotlib.figure'],
              'excludes': [
                  '_gtkagg',
                  '_tkagg',
                  '_agg2',
                  '_cairo',
                  '_cocoaagg',
                  '_fltkagg',
                  '_gtk',
                  '_gtkcairo', ],
# Optional: make one big exe with everything in it, or
# a folder with many things in it. Your choice
#             'bundle_files': 1,
          }
      },

# Qt's dynamically loaded plugins and py2exe really don't
# get along.

data_files=data_files

# If you choose the bundle above, you may want to use this, too.
#     zipfile=None,
)

shutil.copytree(os.getcwd() + os.sep + 'icons', os.getcwd() + os.sep + os.sep.join(['dist', 'icons']))
shutil.copytree(os.getcwd() + os.sep + 'images', os.getcwd() + os.sep + os.sep.join(['dist', 'images']))
shutil.copytree(os.getcwd() + os.sep + 'skin', os.getcwd() + os.sep + os.sep.join(['dist', 'skin']))
