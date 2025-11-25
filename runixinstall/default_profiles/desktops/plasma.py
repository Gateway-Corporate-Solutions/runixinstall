from typing import override

from archinstall.default_profiles.profile import GreeterType, ProfileType
from archinstall.default_profiles.xorg import XorgProfile
from archinstall.lib.installer import Installer


class PlasmaProfile(XorgProfile):
	def __init__(self) -> None:
		super().__init__('KDE Plasma', ProfileType.DesktopEnv)

	@property
	@override
	def packages(self) -> list[str]:
		return [
			'plasma-meta',
			'konsole',
			'kate',
			'dolphin',
			'ark',
			'plasma-workspace',
		]

	@property
	@override
	def default_greeter_type(self) -> GreeterType:
		return GreeterType.Sddm
	
	@property
	@override
	def post_install(self, install_session: Installer) -> None:
		install_session.run_command("mkdir -p /etc/sddm.conf.d")
		install_session.run_command("echo [Theme] >> /etc/sddm.conf.d/theme.conf")
		install_session.run_command("echo Current=breeze >> /etc/sddm.conf.d/theme.conf")
		return super().post_install(install_session)
