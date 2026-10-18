# NEXORA OS

Два независимых направления разработки.

## Nexora Kernel — собственное ядро, не Linux

Независимое ядро на C и Assembly. Реализованы загрузка Multiboot2, русскоязычный графический интерфейс, карта памяти, самотест, PS/2-клавиатура, переключение разделов и темы, диагностический порт COM1.

[Скачать проверенный ISO с собственным ядром](https://github.com/flymygo-coder/nexora/actions/workflows/kernel-iso.yml) — внутри последнего успешного запуска артефакт Nexora-Kernel-Own-Kernel-ISO. Он содержит Nexora_Kernel_0.1.iso, SHA256SUMS.txt, скриншоты QEMU и журнал загрузки.

[Исходники и инструкция](native-kernel/README_RU.md).

**Важно:** это прототип для QEMU и тестовых BIOS x86. Нет установщика на диск, сети, Windows/Linux-приложений, игр, современных видеодрайверов и многозадачности. Он не подходит на замену основной ОС.

## Nexora Linux Preview — отдельный дистрибутив Linux

Экспериментальная Live-сборка Debian 13, XFCE, Calamares, Firefox, LibreOffice, Wine и системного центра программ. Использует ядро Linux, а не Nexora Kernel.

[Проверить сборку Linux ISO](https://github.com/flymygo-coder/nexora/actions/workflows/build-iso.yml).

Обе системы находятся в стадии разработки и не прошли комплексный аудит безопасности. Перед испытаниями установки делайте резервную копию диска.
