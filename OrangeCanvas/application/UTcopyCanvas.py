"""
Michael Ortega, 18 jan 2016
"""

import sys
import os
import shutil
import zipfile

src= sys.argv[1]
dst = sys.argv[2]
c_dir = src[0:-12]
dir_tmp = os.path.join(src, "tmp")
dir_tmp_2 = os.path.join(dir_tmp, "OrangeCanvas")

# 1 - Copy current folder
shutil.copytree(src, dst)

# 2 - Erase current folder
try:
	for root, dirs, files in os.walk(src):
		for f in files:
			os.unlink(os.path.join(root, f))
		for d in dirs:
			shutil.rmtree(os.path.join(root, d))
except Exception, e:
	pass
	
# 3 - Unzip new folder
try:
	z = zipfile.ZipFile(sys.argv[3], 'r')
	z.extractall(dir_tmp)
	z.close()
except Exception, e:
	pass

# 4 - copy
for item in os.listdir(dir_tmp_2):
	s = os.path.join(dir_tmp_2,item)
	d = os.path.join(src,item)
	if os.path.isdir(s):
		shutil.copytree(s, d)
	else:
		shutil.copy2(s, d)
	
# 5 - cleaning
shutil.rmtree(dir_tmp_2)
shutil.rmtree(dir_tmp)

print "update_done"

