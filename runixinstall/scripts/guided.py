import os
from pathlib import Path

from runixinstall import SysInfo
from runixinstall.lib.applications.application_handler import application_handler
from runixinstall.lib.args import arch_config_handler
from runixinstall.lib.authentication.authentication_handler import auth_handler
from runixinstall.lib.configuration import ConfigurationOutput
from runixinstall.lib.disk.filesystem import FilesystemHandler
from runixinstall.lib.disk.utils import disk_layouts
from runixinstall.lib.global_menu import GlobalMenu
from runixinstall.lib.installer import Installer, accessibility_tools_in_use, run_custom_user_commands
from runixinstall.lib.interactions.general_conf import PostInstallationAction, ask_post_installation
from runixinstall.lib.models import Bootloader
from runixinstall.lib.models.device import (
	DiskLayoutType,
	EncryptionType,
)
from runixinstall.lib.models.users import User
from runixinstall.lib.output import debug, error, info
from runixinstall.lib.packages.packages import check_package_upgrade
from runixinstall.lib.profile.profiles_handler import profile_handler
from runixinstall.lib.translationhandler import tr
from runixinstall.tui import Tui


def ask_user_questions() -> None:
	"""
	First, we'll ask the user for a bunch of user input.
	Not until we're satisfied with what we want to install
	will we continue with the actual installation steps.
	"""

	title_text = None

	upgrade = check_package_upgrade('runixinstall')
	if upgrade:
		text = tr('New version available') + f': {upgrade}'
		title_text = f'  ({text})'

	with Tui():
		global_menu = GlobalMenu(arch_config_handler.config)

		if not arch_config_handler.args.advanced:
			global_menu.set_enabled('parallel_downloads', False)

		global_menu.run(additional_title=title_text)


def perform_installation(mountpoint: Path) -> None:
	"""
	Performs the installation steps on a block device.
	Only requirement is that the block devices are
	formatted and setup prior to entering this function.
	"""
	info('Starting installation...')

	config = arch_config_handler.config

	if not config.disk_config:
		error('No disk configuration provided')
		return

	disk_config = config.disk_config
	run_mkinitcpio = not config.bootloader_config or not config.bootloader_config.uki
	locale_config = config.locale_config
	optional_repositories = config.mirror_config.optional_repositories if config.mirror_config else []
	mountpoint = disk_config.mountpoint if disk_config.mountpoint else mountpoint

	with Installer(
		mountpoint,
		disk_config,
		kernels=config.kernels,
	) as installation:
		# Mount all the drives to the desired mountpoint
		if disk_config.config_type != DiskLayoutType.Pre_mount:
			installation.mount_ordered_layout()

		installation.sanity_check()

		if disk_config.config_type != DiskLayoutType.Pre_mount:
			if disk_config.disk_encryption and disk_config.disk_encryption.encryption_type != EncryptionType.NoEncryption:
				# generate encryption key files for the mounted luks devices
				installation.generate_key_files()

		if mirror_config := config.mirror_config:
			installation.set_mirrors(mirror_config, on_target=False)

		installation.minimal_installation(
			optional_repositories=optional_repositories,
			mkinitcpio=run_mkinitcpio,
			hostname=arch_config_handler.config.hostname,
			locale_config=locale_config,
		)

		os.system("echo \"[runix-packages]\" >> /etc/pacman.conf")
		os.system("echo \"SigLevel = Optional TrustAll\" >> /etc/pacman.conf")
		os.system("echo \"Server = file:///etc/repos\" >> /etc/pacman.conf")

		os.system("cp /etc/pacman.conf /mnt/etc/pacman.conf")
		os.system("mkdir -p /mnt/etc/repos")
		os.system("cp -r /etc/repos/* /mnt/etc/repos/")

		if mirror_config := config.mirror_config:
			installation.set_mirrors(mirror_config, on_target=True)

		if config.swap:
			installation.setup_swap('zram')

		if config.bootloader_config and config.bootloader_config.bootloader != Bootloader.NO_BOOTLOADER:
			if config.bootloader_config.bootloader == Bootloader.Grub and SysInfo.has_uefi():
				installation.add_additional_packages('grub')
				os.system('mkdir -p /mnt/usr/share/grub/themes')
				os.system('cp -r /usr/share/grub/themes/fluent /mnt/usr/share/grub/themes/fluent')
				os.system('cp /etc/default/grub /mnt/etc/default/grub')

			installation.add_bootloader(config.bootloader_config.bootloader, config.bootloader_config.uki, config.bootloader_config.removable)

		# If user selected to copy the current ISO network configuration
		# Perform a copy of the config
		network_config = config.network_config

		if network_config:
			network_config.install_network_config(
				installation,
				config.profile_config,
			)

		if config.auth_config:
			if config.auth_config.users:
				installation.create_users(config.auth_config.users)
				auth_handler.setup_auth(installation, config.auth_config, config.hostname)
				for user in config.auth_config.users:
					if user.username == 'root':
						continue
					installation.user_set_shell(user.username, "/bin/zsh")
					os.system(f"cp -r /etc/userdefaults/* /home/{user.username}/")
					os.system(f"chown -R {user.username}:{user.username} /home/{user.username}/")

		if app_config := config.app_config:
			application_handler.install_applications(installation, app_config)

		if profile_config := config.profile_config:
			profile_handler.install_profile_config(installation, profile_config)

		installation.run_command("if pacman -Qi sddm > /dev/null 2>&1; then "
			+ "echo \"[Theme]\" >> /etc/sddm.conf.d/theme.conf; "
			+ "echo \"Current=breeze\" >> /etc/sddm.conf.d/theme.conf; "
			+ "fi")

		if config.packages and config.packages[0] != '':
			installation.add_additional_packages(config.packages)

		if timezone := config.timezone:
			installation.set_timezone(timezone)

		if config.ntp:
			installation.activate_time_synchronization()

		if accessibility_tools_in_use():
			installation.enable_espeakup()

		if config.auth_config and config.auth_config.root_enc_password:
			root_user = User('root', config.auth_config.root_enc_password, False)
			installation.set_user_password(root_user)

#		Disabled for now, as post_install is not implemented for profiles
#		if (profile_config := config.profile_config) and profile_config.profile:
#			profile_config.profile.post_install(installation)

		# If the user provided a list of services to be enabled, pass the list to the enable_service function.
		# Note that while it's called enable_service, it can actually take a list of services and iterate it.
		if servies := config.services:
			installation.enable_service(servies)

		if disk_config.has_default_btrfs_vols():
			btrfs_options = disk_config.btrfs_options
			snapshot_config = btrfs_options.snapshot_config if btrfs_options else None
			snapshot_type = snapshot_config.snapshot_type if snapshot_config else None
			if snapshot_type:
				bootloader = config.bootloader_config.bootloader if config.bootloader_config else None
				installation.setup_btrfs_snapshot(snapshot_type, bootloader)

		# If the user provided custom commands to be run post-installation, execute them now.
		if cc := config.custom_commands:
			run_custom_user_commands(cc, installation)

		installation.genfstab()

		debug(f'Disk states after installing:\n{disk_layouts()}')

		if not arch_config_handler.args.silent:
			with Tui():
				action = ask_post_installation()

			match action:
				case PostInstallationAction.EXIT:
					pass
				case PostInstallationAction.REBOOT:
					os.system('reboot')
				case PostInstallationAction.CHROOT:
					try:
						installation.drop_to_shell()
					except Exception:
						pass


def guided() -> None:
	if not arch_config_handler.args.silent:
		ask_user_questions()

	config = ConfigurationOutput(arch_config_handler.config)
	config.write_debug()
	config.save()

	if arch_config_handler.args.dry_run:
		exit(0)

	if not arch_config_handler.args.silent:
		aborted = False
		with Tui():
			if not config.confirm_config():
				debug('Installation aborted')
				aborted = True

		if aborted:
			return guided()

	if arch_config_handler.config.disk_config:
		fs_handler = FilesystemHandler(arch_config_handler.config.disk_config)
		fs_handler.perform_filesystem_operations()

	perform_installation(arch_config_handler.args.mountpoint)


guided()
