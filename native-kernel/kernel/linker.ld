ENTRY(_start)
SECTIONS
{
  . = 1M;
  .multiboot ALIGN(8) : { KEEP(*(.multiboot)) }
  .text ALIGN(4096) : { *(.text*) }
  .rodata ALIGN(4096) : { *(.rodata*) }
  .data ALIGN(4096) : { *(.data*) }
  .bss ALIGN(4096) : { *(COMMON) *(.bss*) }
}
