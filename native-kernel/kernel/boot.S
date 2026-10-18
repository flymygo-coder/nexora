.section .multiboot,"a"
.align 8
mb_start:
    .long 0xE85250D6
    .long 0
    .long mb_end - mb_start
    .long -(0xE85250D6 + (mb_end - mb_start))
    .align 8
    .short 5
    .short 1
    .long 20
    .long 1024
    .long 768
    .long 32
    .align 8
    .short 0
    .short 0
    .long 8
mb_end:
.section .bss,"aw",@nobits
.align 16
stack_bottom:
    .skip 32768
stack_top:
.section .text,"ax"
.global _start
.extern kernel_main
_start:
    cli
    mov $stack_top, %esp
    push %ebx
    push %eax
    call kernel_main
1:  hlt
    jmp 1b
