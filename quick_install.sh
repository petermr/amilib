
## quick instructions for experienced users
cd
cd workspace/amilib  # or whatever your top dir
rm -rf dist
# *** EDIT VERSION NUMBER (e.g. 0.0.2) IN setup.py AND amilib/amix.PyAMI.version() ***
python setup.py sdist

twine upload dist/* # <login is pypi, not github> I am petermr

#
# version = "0.0.1a1"
# pip install amilib=version # or whatever version
# OR for pre-release versions append --pre (othewise you don't get the latest)r
# pip install --pre amilib==version

# WE MAY HAVE TO DO THIS TWICE TO FLUSH OUT THE OLD VERSION
# pip uninstall amilib
# pip install amilib==version
