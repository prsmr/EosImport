#! /usr/bin/python3
"""
*** imports CR2 Files from SD Card
*** and imports them to NAS
*** while renaming
***
*** @28th May 2023
*** by tim priesmeier
*** prsmr.de
"""
import os
import pwd
import datetime
import shutil
from colorama import Fore, Back, Style
import argparse
import subprocess
import configparser

__version__ = '0.3'
__date__ = "18. September 2023"

sdcard = 'EOS_DIGITAL' # Name of the SD Card
mountpoint = '/run/media/' + str(pwd.getpwuid(os.getuid()).pw_name) + '/' + sdcard # Mountpoint of SD Card
savepath = '/media/NAS/Fotos/Meine Fotos/' # Path the pictures are copied to
camera = '600D' # Camera Name
extension = '.cr2' # File Extension
locale = 0

parser = argparse.ArgumentParser(
                    prog='EosImport',
                    description='Importiert CR2 Dateien von einer SD Karte',
                    epilog='---')

parser.add_argument('-s', '--sdcard', metavar="Name der SD-Karte", default=sdcard)      # option that takes a value
parser.add_argument('-m', '--mountpoint', default=mountpoint, metavar="Mountpunkt der SD-Karte")
parser.add_argument('-l', '--locale', action="store_true")
parser.add_argument('-p', '--path', default=savepath, metavar="Speicherort der Fotos")
parser.add_argument('-a', '--ask', action="store_false")

args = parser.parse_args()

sdcard = args.sdcard
mountpoint = args.mountpoint

if(args.locale == True):
	savepath = "/home/tim/Dokumente/EosImport/"
else:
	savepath = args.path

raw_files = []

print("EosImport v" + __version__ + " vom " + __date__)
print("Scanne SD-Karte " + sdcard + "...")
# Scan SD Card for files using os.walk
for r, d, f in os.walk(mountpoint):
    for file in f:
        if file.endswith(".CR2"):
            raw_files.append(os.path.join(r, file))

# Hint with Green Color
print(Fore.GREEN +'Kopiere ' + str(len(raw_files)) + ' Bilder nach ' + savepath + Style.RESET_ALL)
print()
i = 1

# Move files...
for file in raw_files:
	created = datetime.datetime.fromtimestamp(os.path.getmtime(file)) # Date picture was created
	old_file = (file.split("/")[-1]).split(".") # Name of old File, splitted by "." to get the name without file extension
	subdir = str(created.year) + '-' + '{:02d}'.format(created.month) + '-' + '{:02d}'.format(created.day) # Subdir 
	filename = str(created.year) + '{:02d}'.format(created.month) + '{:02d}'.format(created.day) + '-'+ old_file[0] + "" + '_' + camera + extension

	dirpath = savepath + str(created.year) + "/" + subdir + '/'
	new_file = dirpath + filename

	if(i < 10):
		number = '0' + str(i) + '/' + str(len(raw_files))
	else:
		number = str(i) + '/' + str(len(raw_files))		

	if(os.path.exists(dirpath)):
		if(os.path.exists(new_file)):
			print('#' + number + ': ' + Fore.CYAN + filename + " bereits vorhanden!" + Style.RESET_ALL)
		else:
			try:
				shutil.copyfile(file, new_file)
				print('#' + number + ': ' + Fore.BLUE + file + Fore.WHITE + " --> " + Fore.BLUE + new_file + Style.RESET_ALL)
			except:
				print('#' + number + ': ' + Fore.RED + "Fehler beim Kopieren von " + oldfile + ".CR2" + Style.RESET_ALL)
	else:
		os.makedirs(dirpath)
		print('#' + number + ': ' + Fore.YELLOW + "Erstelle " + dirpath + Style.RESET_ALL)
		try:
			shutil.copyfile(file, new_file)
			print('#' + number + ': ' + Fore.BLUE + file + Fore.WHITE + " --> " + Fore.BLUE + new_file + Style.RESET_ALL)
		except:
			print('#' + number + ': ' + Fore.RED + "Fehler beim Kopieren von " + oldfile + ".CR2" + Style.RESET_ALL)

	i = i+1

unmount = input("SD-Karte auswerfen? (J/n)")

if(unmount == "J" or unmount == "j" or unmount == "Y" or unmount == "y"):
	print("Werfe SD-Karte " + mountpoint + " aus...")
	try:
		cmd = 'sudo umount ' + mountpoint
		subprocess.Popen(str(cmd), shell=True, stdout=subprocess.PIPE).stdout.read()
	except:
		print("SD-Karte konnte nicht ausgeworfen werden")

print("Fertig!")
