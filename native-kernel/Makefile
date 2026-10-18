CC=gcc
LD=ld
CFLAGS=-m32 -std=c11 -ffreestanding -O2 -Wall -Wextra -Werror -fno-pie -fno-pic -fno-stack-protector -fno-builtin -fno-tree-loop-distribute-patterns -fno-asynchronous-unwind-tables -Ibuild
.PHONY: all iso clean
all: build/nexora.elf
build:
	mkdir -p build
build/font.h: tools/make_font.py | build
	python3 tools/make_font.py $@
build/main.o: kernel/main.c build/font.h
	$(CC) $(CFLAGS) -c $< -o $@
build/boot.o: kernel/boot.S | build
	$(CC) -m32 -c $< -o $@
build/nexora.elf: build/main.o build/boot.o kernel/linker.ld
	$(LD) -m elf_i386 -T kernel/linker.ld -o $@ build/boot.o build/main.o
iso: build/nexora.elf
	grub-file --is-x86-multiboot2 build/nexora.elf
	mkdir -p build/isodir/boot/grub
	cp build/nexora.elf build/isodir/boot/nexora.elf
	printf 'set timeout=0\nset default=0\nset gfxmode=1024x768x32\nset gfxpayload=keep\nterminal_output gfxterm\nmenuentry "Nexora Kernel 0.1" {\n multiboot2 /boot/nexora.elf\n boot\n}\n' > build/isodir/boot/grub/grub.cfg
	grub-mkrescue -o build/Nexora_Kernel_0.1.iso build/isodir
clean:
	rm -rf build
