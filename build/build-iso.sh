#!/usr/bin/env bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
: "${WORK_DIR:=/tmp/nexora-build}"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"
lb config --mode debian --distribution trixie --architectures amd64 --binary-images iso-hybrid --debian-installer none --archive-areas "main contrib non-free non-free-firmware" --bootappend-live "boot=live components locales=ru_RU.UTF-8 keyboard-layouts=us,ru"
mkdir -p config/package-lists config/includes.chroot/etc/skel/Desktop config/includes.chroot/etc/default config/hooks/live
cat >config/package-lists/nexora.list.chroot <<'EOF'
linux-image-amd64
live-boot
live-config
live-config-systemd
xfce4
xfce4-terminal
xserver-xorg
lightdm
lightdm-gtk-greeter
network-manager
network-manager-gnome
firefox-esr
libreoffice-writer
libreoffice-calc
libreoffice-impress
vlc
thunar
mousepad
file-roller
flatpak
gnome-software
gnome-software-plugin-flatpak
synaptic
apt
python3
locales-all
keyboard-configuration
fonts-noto-core
fonts-dejavu-core
ca-certificates
sudo
polkitd
pkexec
calamares-settings-debian
cryptsetup
rsync
parted
mesa-vulkan-drivers
wine64
winbind
pipewire
wireplumber
pavucontrol
EOF
cat >config/includes.chroot/etc/default/locale <<'EOF'
LANG=ru_RU.UTF-8
LANGUAGE=ru_RU:ru
EOF
cat >config/includes.chroot/etc/default/keyboard <<'EOF'
XKBMODEL="pc105"
XKBLAYOUT="us,ru"
XKBVARIANT=","
XKBOPTIONS="grp:alt_shift_toggle"
BACKSPACE="guess"
EOF
cat >config/includes.chroot/etc/skel/Desktop/install-nexora.desktop <<'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Установить Nexora OS
Exec=pkexec /usr/bin/calamares
Icon=drive-harddisk
Terminal=false
EOF
chmod +x config/includes.chroot/etc/skel/Desktop/install-nexora.desktop
lb build
iso="$(find . -maxdepth 1 -name '*.iso' -type f | head -1)"
test -n "$iso" && test -s "$iso"
mkdir -p "$GITHUB_WORKSPACE/dist"
cp "$iso" "$GITHUB_WORKSPACE/dist/Nexora_OS_Installer_amd64.iso"
(cd "$GITHUB_WORKSPACE/dist" && sha256sum Nexora_OS_Installer_amd64.iso > SHA256SUMS.txt)
