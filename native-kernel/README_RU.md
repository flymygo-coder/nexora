# Nexora Kernel 0.1 — собственное ядро

**Экспериментальная система**, не готовая замена Windows/Linux и не установщик на жёсткий диск. Сборка и тестируются для BIOS x86 в QEMU.

Собственное ядро на C и Assembly, без Linux. Загрузка Multiboot2 через GRUB, графический экран с русским текстом (при поддержке framebuffer), COM1 для диагностики, клавиатура PS/2, карта памяти и самотест.

В графическом экране клавиши **F1–F4** переключают диагностические разделы, **T** меняет тему.

## Сборка (Debian/Ubuntu)

Нужны gcc, binutils, make, python3-pil, fonts-dejavu-core, grub-common, grub-pc-bin, xorriso, mtools:
\`\`\`sh
make iso
qemu-system-i386 -m 256M -vga std -cdrom build/Nexora_Kernel_0.1.iso -serial stdio
\`\`\`

При загрузке ядро пишет в COM1 маркеры NEXORA_KERNEL_ENTRY, NEXORA_SELFTEST_OK, NEXORA_KERNEL_BOOT_OK. В CI загрузка подтверждается только после появления маркера.

**Не поддерживает:** установку на накопитель, многозадачность, файловую систему, Wi-Fi, Интернет, игровые API, приложения Windows и Linux, современную аппаратную графику. Система не сертифицирована по безопасности и не прошла проверку на физических ПК.
