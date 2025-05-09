
## quick instructions for experienced users
cd
cd workspace/amilib  # or whatever your top dir
rm -rf dist build amilib.egg-info
# make sure build is installed 
# *** EDIT VERSION NUMBER (e.g. 0.0.2) IN setup.cfg AND amilib/amix.version() ***
python3 -m build
twine upload dist/* # <login is pypi, not github> I am petermr

# if there are problems pkgimporter on install see stackoverflow
# https://stackoverflow.com/questions/77364550/attributeerror-module-pkgutil-has-no-attribute-impimporter-did-you-mean
# upgrade pip to python 3.12
# python -m ensurepip --upgrade
  #python -m pip install --upgrade setuptools
  #python -m pip install <module>
  #In your virtual environment:
  #
  #pip install --upgrade setuptools
# pip install --pre amilib==version

# WE MAY HAVE TO DO THIS TWICE TO FLUSH OUT THE OLD VERSION
# pip uninstall amilib
# pip install amilib==version
