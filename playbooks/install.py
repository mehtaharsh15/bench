# wget setup_frappe.py | python
import os
import sys
import subprocess

from distutils.spawn import find_executable

bench_repo = '/usr/local/frappe/bench-repo'

def install_bench(args):
	# pre-requisites for bench repo cloning
	install_pip()
	install_ansible()
	install_git()

	if is_sudo_user():
		raise Exception("Please run this script as a non-root user with sudo privileges, but without using sudo")

	# clone bench repo
	clone_bench_repo()

	if args.develop:
		run_playbook('develop/install.yml', sudo=True)

def install_python27():
	version = (sys.version_info[0], sys.version_info[1])

	if version == (2, 7):
		return

	print "Installing Python 2.7"

	# install python 2.7
	success = run_os_command({
		"apt-get": "sudo apt-get install -y python2.7",
		"yum": "sudo yum install -y python27",
		"brew": "brew install python"
	})

	if not success:
		could_not_install("Python 2.7")

	# replace current python with python2.7
	os.execvp("python2.7", ([] if is_sudo_user() else ["sudo"]) + ["python2.7", __file__] + sys.argv[1:])

def install_git():
	if find_executable("git"):
		# git already installed
		return

	print "Installing Git"

	success = run_os_command({
		"apt-get": "sudo apt-get install -y git",
		"yum": "sudo yum install -y git",
		"brew": "brew install git"
	})

	if not success:
		could_not_install("Git")

def install_pip():
	"""Install pip for the user or upgrade to latest version if already present"""
	try:
		import pip

	except ImportError:
		print "Installing Pip"

		success = run_os_command({
			"apt-get": "sudo apt-get install -y build-essential python-setuptools python-dev python-pip",
		})

		if not success:
			could_not_install("Python Pip")

		# replace current python with python2.7
		os.execvp("python2.7", ([] if is_sudo_user() else ["sudo"]) + ["python2.7", __file__] + sys.argv[1:])

def install_ansible():
	try:
		import ansible
	except ImportError:
		import pip
		pip.main(["install", "ansible"])

def clone_bench_repo():
	"""Clones the bench repository in the user folder"""

	if os.path.exists(bench_repo):
		return 0

	os.makedirs('/usr/local/frappe')
	success = run_os_command(
		{"git": "git clone https://github.com/frappe/bench {bench_repo} --depth 1 --branch new-install".format(bench_repo=bench_repo)}
	)

	return success

def run_os_command(command_map):
	"""command_map is a dictionary of {"executable": command}. For ex. {"apt-get": "sudo apt-get install -y python2.7"} """
	success = False
	for executable, command in command_map.items():
		if find_executable(executable):
			returncode = subprocess.check_call(command.split())
			success = ( returncode == 0 )
			break

	return success

def could_not_install(package):
	raise Exception("Could not install {0}. Please install it manually.".format(package))

def is_sudo_user():
	return os.geteuid() == 0

def run_playbook(playbook_name, sudo=False):
	args = ["ansible-playbook", "-c", "local",  playbook_name]
	if sudo:
		args.append('-K')

	success = subprocess.check_call(args, cwd=os.path.join(bench_repo, 'playbooks'))
	return success

def parse_commandline_args():
	import argparse

	parser = argparse.ArgumentParser(description='Frappe Installer')
	parser.add_argument('--develop', dest='develop', action='store_true', default=False,
						help="Install developer setup")
	args = parser.parse_args()

	return args

if __name__ == "__main__":
	try:
		import argparse
	except ImportError:
		# install python2.7
		install_python27()

	args = parse_commandline_args()

	install_bench(args)
