from typing import override

from runixinstall.default_profiles.profile import GreeterType, ProfileType
from runixinstall.default_profiles.xorg import XorgProfile
from runixinstall.lib.installer import Installer


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
