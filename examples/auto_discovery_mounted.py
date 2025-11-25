from pathlib import Path

from runixinstall.lib.disk.device_handler import device_handler
from runixinstall.lib.models.device import DiskLayoutConfiguration, DiskLayoutType

root_mount_dir = Path('/mnt/runixinstall')

mods = device_handler.detect_pre_mounted_mods(root_mount_dir)

disk_config = DiskLayoutConfiguration(
	DiskLayoutType.Pre_mount,
	device_modifications=mods,
)
