
## quick instructions for experienced users
cd
cd workspace/amilib  # or whatever your top dir
rm -rf dist build amilib.egg-info
# *** EDIT VERSION NUMBER (e.g. 0.0.2) IN amilib/__init__.py ***
python setup.py sdist

twine upload dist/* # <login is pypi, not github> I am petermr

#
# pip install amilib=version # or whatever version
# OR for pre-release versions append --pre (othewise you don't get the latest)r
# pip install --pre amilib==version

# WE MAY HAVE TO DO THIS TWICE TO FLUSH OUT THE OLD VERSION
# pip uninstall amilib
# pip install amilib==version
