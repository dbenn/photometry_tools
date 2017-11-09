# Remove leading zeros from file names in the current directory, subtract
# an optional offset value from the sequence number in each, and copy the
# file to a temporary directory.
#
# Nov 2014, dbenn@computer.org

import os
import re
import shutil
import sys

def main():
  files = os.listdir('.')

  filepat = re.compile('([^0-9]+)([0-9]+)\.(\w+)')

  if len(sys.argv) == 2:
    offset = int(sys.argv[1])
  else:
    offset = 0

  dest_dir = 'temp'

  if os.path.exists(dest_dir):
    os.rmdir(dest_dir)
  
  os.mkdir(dest_dir)

  for file in files:
    match = filepat.match(file)
    if match is not None:
      seq_num = int(match.group(2))
      new_seq_num = seq_num - offset
      prefix = match.group(1)
      suffix = match.group(3)
      new_file = "{0}{1}.{2}".format(prefix, new_seq_num, suffix)
      new_path = os.path.join(dest_dir, new_file)
      shutil.copyfile(file, new_path)
      print("{0} => {1}".format(file, new_path))

if __name__ == "__main__":
    main()
