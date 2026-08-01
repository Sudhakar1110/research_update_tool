from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")
install_requires = [r for r in install_requires if r and not r.startswith("#")]

# get version from __version__ variable in team_update_tool/__init__.py
from team_update_tool import __version__ as version

setup(
	name="team_update_tool",
	version=version,
	description="Team Update Tool - Track completed team projects, GitHub links and screenshots with role based Admin/Viewer access, for Frappe Framework and ERPNext v15+.",
	author="Team Update Tool Contributors",
	author_email="balaji-001-gif@users.noreply.github.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires,
)
