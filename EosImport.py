#! /usr/bin/python3
"""
*** imports CR2 Files from SD Card
*** and imports them to NAS
*** while renaming
***
*** @28th May 2023
*** tim priesmeier
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
import os.path

__version__ = '0.4'
__date__ = "2nd January 2025"
CONFIG_FILE = os.path.expanduser('~/.EosImport')

def create_configfile():
    config = configparser.ConfigParser()

    # Standardwerte
    default_values = {
        "sdcard": "EOS_DIGITAL",
        "mountpoint": "/run/media",
        "savepath": os.path.expanduser("~/Photos"),
        "camera": "700D",
        "extension": ".cr2"
    }

    # Funktion zum Abfragen von Eingaben mit Standardwerten
    def prompt_input(prompt, default):
        user_input = input(f"{prompt} (Default: {default}): ")
        return user_input if user_input.strip() else default

    # Eingaben sammeln
    sdcard = prompt_input("Default Name of SD-Card", default_values["sdcard"])
    mountpoint = prompt_input("Mountpoint of SD-Card", default_values["mountpoint"])
    savepath = prompt_input("Default path to save the photos in", default_values["savepath"])
    camera = prompt_input("Name of the Camera", default_values["camera"])
    extension = prompt_input("File extension", default_values["extension"])

    # Konfigurationsdaten speichern
    config["General"] = {
        "sdcard": sdcard,
        "mountpoint": mountpoint,
        "savepath": savepath,
        "camera": camera,
        "extension": extension,
    }

    with open(CONFIG_FILE, "w") as file:
        config.write(file)
        print(f"Configfile '{CONFIG_FILE}' created successfully.")

def check_configfile():
	return os.path.exists(CONFIG_FILE)

def read_configfile():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return {key: config.get('General', key) for key in ['sdcard', 'mountpoint', 'savepath', 'camera', 'extension']}

def move_files(raw_files, savepath, camera, extension):
    total_files = len(raw_files)
    number_width = len(str(total_files))  # Anzahl der Ziffern der größten Zahl

    for i, file in enumerate(raw_files, start=1):
        try:
            # Date and file name parsing
            created = datetime.datetime.fromtimestamp(os.path.getmtime(file))
            old_file_name = os.path.splitext(os.path.basename(file))[0]
            subdir = f"{created.year:04d}-{created.month:02d}-{created.day:02d}"
            filename = f"{created.year:04d}{created.month:02d}{created.day:02d}-{old_file_name}_{camera}{extension}"

            # Directory and file paths
            dirpath = os.path.join(savepath, str(created.year), subdir)
            new_file = os.path.join(dirpath, filename)
            number = f"{i:0{number_width}d}/{total_files}"

            # Ensure target directory exists
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)
                print(f"#{number}: {Fore.YELLOW}Creating {dirpath}{Style.RESET_ALL}")

            # Copy file if it doesn't already exist
            if os.path.exists(new_file):
                print(f"#{number}: {Fore.CYAN}{filename} already exists!{Style.RESET_ALL}")
            else:
                shutil.copyfile(file, new_file)
                print(f"#{number}: {Fore.BLUE}{file}{Fore.WHITE} --> {Fore.BLUE}{new_file}{Style.RESET_ALL}")
        except Exception as e:
            print(f"#{number}: {Fore.RED}Error processing {file}: {e}{Style.RESET_ALL}")		

def main(args, configExists = False):
	if not configExists:
		default_data = {
			'sdcard': 'EOS_DIGITAL',
			'mountpoint': f"/run/media/{pwd.getpwuid(os.getuid()).pw_name}/EOS_DIGITAL",
			'savepath': '/media/NAS/Fotos/Meine Fotos/',
			'camera': '600D',
			'extension': '.cr2',
		}
	else:
		default_data = read_configfile()

	sdcard = args.sdcard or default_data['sdcard']
	mountpoint = args.mountpoint or f"{default_data['mountpoint']}/{pwd.getpwuid(os.getuid()).pw_name}/{sdcard}/"
	savepath = os.path.expanduser('~/Dokumente/EosImport') if args.locale else default_data['savepath']
	camera, extension = default_data['camera'], default_data['extension']

	print(f"EosImport v{__version__} from {__date__}")
	print(f"Scanning SD-Card {mountpoint}...")

	raw_files = [
	    os.path.join(root, file)
	    for root, _, files in os.walk(mountpoint)
	    for file in files
	    if file.lower().endswith(extension.lower())
	]
	print(f"{Fore.GREEN}Copy {len(raw_files)} Pictures to {savepath}{Style.RESET_ALL}\n")

	move_files(raw_files, savepath, camera, extension)

	unmount = input("Unmount SD-Card (Y/n)")

	if input("Unmount SD-Card (Y/n) ").lower() in ['y', 'j']:
		try:
			subprocess.run(['sudo', 'umount', mountpoint], check=True)
			print(f"SD-Card {mountpoint} unmounted.")
		except subprocess.CalledProcessError:
			print("SD-Card could not be unmounted.")

	print("Done!")

if(__name__ == "__main__"):
	parser = argparse.ArgumentParser(
		prog='EosImport',
		description='Imports CR2 Files from SD-Card, saves them to a specific path, and renames them.',
	)

	parser.add_argument('-s', '--sdcard', metavar="Name of SD-Card")      # option that takes a value
	parser.add_argument('-m', '--mountpoint', metavar="Mountpoint of SD-Card")
	parser.add_argument('-l', '--locale', action="store_true")
	parser.add_argument('-p', '--path', metavar="Savepath")

	args = parser.parse_args()

	if not check_configfile():
		if input("Config File doesn't exist. Create config file? (Y/n)").lower() in ['y', 'j']:
			create_configfile()
		else:
			main(args, False)
	else:
		main(args, True)
