#include <stdint.h>
#include <stddef.h>
#include "font.h"

/* Nexora Kernel: freestanding 32-bit Multiboot2 microprototype. No Linux code. */
#define MAGIC 0x36D76289u
#define SERIAL 0x3F8
#define FB_TAG 8u
#define MMAP_TAG 6u

static inline void outb(uint16_t p,uint8_t v){__asm__ volatile("outb %0,%1"::"a"(v),"Nd"(p));}
static inline uint8_t inb(uint16_t p){uint8_t v;__asm__ volatile("inb %1,%0":"=a"(v):"Nd"(p));return v;}
static void serial_init(void){outb(SERIAL+1,0);outb(SERIAL+3,0x80);outb(SERIAL,3);outb(SERIAL+1,0);outb(SERIAL+3,3);outb(SERIAL+2,0xC7);outb(SERIAL+4,0x0B);}
static void serial_msg(const char*s){while(*s){while(!(inb(SERIAL+5)&0x20)){}outb(SERIAL,(uint8_t)*s++);}}
static uint32_t fb_addr,pitch,sw,sh;
static uint8_t rpos,gpos,bpos;
static uint32_t memory_mb=0,regions=0;
static int frame_ready;
static uint8_t current_view=0,last_key=0,diagnostics_ok=0;
static int theme_dark=1;
static uint32_t col(uint8_t r,uint8_t g,uint8_t b){return ((uint32_t)r<<rpos)|((uint32_t)g<<gpos)|((uint32_t)b<<bpos);}
static void rect(uint32_t x,uint32_t y,uint32_t w,uint32_t h,uint32_t c){
 if(x>=sw||y>=sh)return;
 if(w>sw-x)w=sw-x;
 if(h>sh-y)h=sh-y;
 for(uint32_t yy=0;yy<h;yy++){
  volatile uint32_t *p=(volatile uint32_t*)(uintptr_t)(fb_addr+(y+yy)*pitch+x*4);
  for(uint32_t xx=0;xx<w;xx++)p[xx]=c;
 }
}
static void roundrect(uint32_t x,uint32_t y,uint32_t w,uint32_t h,uint32_t rad,uint32_t c){
 for(uint32_t yy=0;yy<h;yy++){
  uint32_t inset=0;
  if(yy<rad)inset=rad-yy;
  else if(h-yy<=rad)inset=rad-(h-yy-1);
  if(inset>w/2)inset=w/2;
  rect(x+inset,y+yy,w-inset*2,1,c);
 }
}
static void glyph(uint32_t x,uint32_t y,uint32_t cp,uint32_t c,uint32_t scale){
 const glyph_t*g=0;
 for(size_t k=0;k<sizeof(font_glyphs)/sizeof(font_glyphs[0]);k++){
  if(font_glyphs[k].cp==cp){g=&font_glyphs[k];break;}
 }
 if(!g)return;
 for(uint32_t row=0;row<18;row++)for(uint32_t bit=0;bit<12;bit++)
  if(g->bits[row]&(1u<<(11-bit)))rect(x+bit*scale,y+row*scale,scale,scale,c);
}
static void text(uint32_t x,uint32_t y,const char*s,uint32_t c,uint32_t scale){
 uint32_t xx=x;
 while(*s){
  uint32_t cp=(uint8_t)*s++;
  if(cp>=0xC2&&cp<=0xDF){uint32_t lo=(uint8_t)*s++;cp=((cp&31)<<6)|(lo&63);}
  else if(cp>=0xE0&&cp<=0xEF){uint32_t a=(uint8_t)*s++,b=(uint8_t)*s++;cp=((cp&15)<<12)|((a&63)<<6)|(b&63);}
  if(cp=='\n'){xx=x;y+=21*scale;continue;}
  glyph(xx,y,cp,c,scale);xx+=12*scale;
  if(xx+12*scale>=sw)break;
 }
}
static void uintstr(uint32_t v,char*dest){
 char temp[16];unsigned n=0;
 if(!v){dest[0]='0';dest[1]=0;return;}
 while(v){temp[n++]=(char)('0'+v%10);v/=10;}
 for(unsigned i=0;i<n;i++)dest[i]=temp[n-i-1];
 dest[n]=0;
}
static void card(uint32_t x,uint32_t y,uint32_t w,uint32_t h,const char*title,const char*body){
 roundrect(x,y,w,h,14,theme_dark?col(26,39,65):col(234,239,249));
 rect(x+19,y+23,4,25,col(76,179,252));
 text(x+36,y+23,title,theme_dark?col(246,249,255):col(22,35,63),1);
 text(x+23,y+76,body,theme_dark?col(177,197,223):col(66,77,101),1);
}
static void draw(void){
 if(!frame_ready)return;
 for(uint32_t y=0;y<sh;y++){
  uint8_t t=(uint8_t)(y*18/sh);
  rect(0,y,sw,1,theme_dark?col(9+t/3,17+t/2,36+t):col(236-t/4,243-t/5,252-t/8));
 }
 const uint32_t ink=theme_dark?col(242,247,255):col(20,34,64);
 const uint32_t sub=theme_dark?col(156,183,217):col(65,81,109);
 rect(0,0,sw,72,theme_dark?col(14,25,47):col(225,235,249));
 roundrect(27,15,47,42,10,col(63,149,240));
 text(39,26,"N",col(255,255,255),1);
 text(93,25,"NEXORA",ink,2);
 text(93,52,"KERNEL 0.1  •  32-bit / Multiboot2",sub,1);
 roundrect(sw-219,18,196,34,10,col(42,105,91));
 text(sw-205,28,"ЯДРО ЗАПУЩЕНО",col(225,255,232),1);
 text(42,110,"Собственное ядро Nexora",ink,2);
 text(44,160,"Без Linux и Windows. Интерфейс работает напрямую с видеопамятью.",sub,1);
 const char*menu[]={"F1  Система","F2  Память","F3  Устройства","F4  Самотест"};
 for(uint32_t i=0;i<4;i++){
  roundrect(40+i*237,209,220,50,10,(i==current_view)?col(49,116,201):(theme_dark?col(28,42,69):col(218,227,243)));
  text(54+i*237,226,menu[i],(i==current_view)?col(255,255,255):ink,1);
 }
 if(current_view==0){
  card(41,290,450,170,"Архитектура","Собственное 32-битное ядро C / ASM");
  card(514,290,469,170,"Загрузка","GRUB Multiboot2, графический буфер");
  card(41,485,942,117,"Управление","F1–F4: разделы    T: тема    Клавиатура PS/2");
 }
 if(current_view==1){
  char n[20];uintstr(memory_mb,n);card(41,290,942,170,"Доступная память (MiB)",n);
  char m[20];uintstr(regions,m);card(41,485,942,117,"Области памяти в карте Multiboot2",m);
 }
 if(current_view==2){
  card(41,290,942,170,"Устройства","VGA / VBE framebuffer, COM1, PS/2 keyboard");
  card(41,485,942,117,"Ограничения","Нет файловой системы, сети и драйвера GPU");
 }
 if(current_view==3){
  card(41,290,942,170,"Проверка целостности памяти",diagnostics_ok?"ТЕСТ ПРОЙДЕН — OK":"Нажмите F4 для повторной проверки");
  card(41,485,942,117,"Встроенные подсистемы","Графика, сериал, клавиатура, карта RAM");
 }
 rect(0,sh-53,sw,53,theme_dark?col(12,25,44):col(226,235,248));
 text(32,sh-34,"Nexora Kernel • технический прототип, не ОС для повседневной работы",sub,1);
}
static void parse_mb(uint32_t info){
 if(info==0)return;
 uint8_t*ptr=(uint8_t*)(uintptr_t)info;
 uint32_t total=*(uint32_t*)ptr;
 if(total<16||total>(1u<<23))return;
 for(uint32_t p=8;p+8<=total;){
  uint32_t type=*(uint32_t*)(ptr+p),sz=*(uint32_t*)(ptr+p+4);
  if(sz<8||sz>total-p)break;
  if(type==0)break;
  if(type==FB_TAG&&sz>=38){
   uint8_t*v=ptr+p;
   uint64_t addr=*(uint64_t*)(v+8);
   uint32_t pi=*(uint32_t*)(v+16);
   uint32_t width=*(uint32_t*)(v+20),height=*(uint32_t*)(v+24);
   uint8_t bits=v[28],mode=v[29];
   if((addr>>32)==0&&bits==32&&mode==1&&width>=800&&height>=600&&width<=4096&&height<=2160&&pi>=width*4){
    fb_addr=(uint32_t)addr;pitch=pi;sw=width;sh=height;
    rpos=v[32];gpos=v[34];bpos=v[36];
    if(rpos<=24&&gpos<=24&&bpos<=24)frame_ready=1;
   }
  }
  if(type==MMAP_TAG&&sz>=16){
   uint32_t ent=*(uint32_t*)(ptr+p+8);
   if(ent>=24){
    for(uint32_t o=16;o+ent<=sz;o+=ent){
     uint8_t*v=ptr+p+o;
     uint64_t length=*(uint64_t*)(v+8);
     uint32_t kind=*(uint32_t*)(v+16);
     regions++;
     if(kind==1){uint64_t avail=(uint64_t)memory_mb*1048576ULL+length;memory_mb=(uint32_t)(avail/1048576ULL);}
    }
   }
  }
  p+=(sz+7u)&~7u;
 }
}
static void memory_test(void){
 static volatile uint32_t buf[1024];
 int good=1;
 for(uint32_t i=0;i<1024;i++)buf[i]=0xA5A50000u^i;
 for(uint32_t i=0;i<1024;i++)if(buf[i]!=(0xA5A50000u^i))good=0;
 diagnostics_ok=(uint8_t)good;
 serial_msg(good?"NEXORA_SELFTEST_OK\n":"NEXORA_SELFTEST_FAIL\n");
}
void kernel_main(uint32_t magic,uint32_t info){
 serial_init();serial_msg("NEXORA_KERNEL_ENTRY\n");
 if(magic!=MAGIC){serial_msg("NEXORA_BOOT_BAD_MAGIC\n");for(;;)__asm__ volatile("hlt");}
 parse_mb(info);memory_test();
 if(frame_ready){draw();serial_msg("NEXORA_KERNEL_BOOT_OK\n");}
 else serial_msg("NEXORA_NO_FRAMEBUFFER\n");
 for(;;){
  if(inb(0x64)&1){
   uint8_t key=inb(0x60);
   if(!(key&0x80)&&key!=last_key){
    if(key>=0x3B&&key<=0x3E){current_view=(uint8_t)(key-0x3B);if(current_view==3)memory_test();draw();}
    else if(key==0x14){theme_dark=!theme_dark;draw();}
   }
   last_key=key;
  }
  for(volatile unsigned i=0;i<140000;i++)__asm__ volatile("pause");
 }
}
