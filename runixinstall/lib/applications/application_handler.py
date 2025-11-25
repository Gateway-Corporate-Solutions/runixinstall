from typing import TYPE_CHECKING

from runixinstall.applications.audio import AudioApp
from runixinstall.applications.bluetooth import BluetoothApp
from runixinstall.lib.models import Audio
from runixinstall.lib.models.application import ApplicationConfiguration
from runixinstall.lib.models.users import User

if TYPE_CHECKING:
	from runixinstall.lib.installer import Installer


class ApplicationHandler:
	def __init__(self) -> None:
		pass

	def install_applications(self, install_session: 'Installer', app_config: ApplicationConfiguration, users: list['User'] | None = None) -> None:
		if app_config.bluetooth_config and app_config.bluetooth_config.enabled:
			BluetoothApp().install(install_session)

		if app_config.audio_config and app_config.audio_config.audio != Audio.NO_AUDIO:
			AudioApp().install(
				install_session,
				app_config.audio_config,
				users,
			)


application_handler = ApplicationHandler()
