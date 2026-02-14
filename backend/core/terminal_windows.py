"""
Windows-compatible Terminal Manager using subprocess
"""
import asyncio
import subprocess
import sys
import shutil
from typing import Optional
import threading
import queue

class WindowsPTYManager:
    """Windows-compatible terminal manager using subprocess"""
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.running: bool = False
        self.output_queue: queue.Queue = queue.Queue()
        self.stdin_queue: queue.Queue = queue.Queue()
        self._read_thread: Optional[threading.Thread] = None
        self._write_thread: Optional[threading.Thread] = None
        
    async def start(self, shell: str = "powershell") -> bool:
        """Start a new subprocess terminal session"""
        try:
            # Detect available shell on Windows
            if shell in ["/bin/bash", "bash"]:
                # Try to find bash (Git Bash on Windows)
                bash_path = shutil.which("bash")
                if bash_path and subprocess.os.path.exists(bash_path):
                    shell_cmd = bash_path
                else:
                    # Fall back to PowerShell on Windows
                    shell_cmd = "powershell.exe"
            elif shell == "powershell":
                shell_cmd = "powershell.exe"
            else:
                shell_cmd = shell
            
            print(f"Starting shell: {shell_cmd}")
            
            self.process = subprocess.Popen(
                shell_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=0,
                shell=False,
                env={
                    **subprocess.os.environ,
                    'TERM': 'xterm-256color',
                    'PYTHONUNBUFFERED': '1',
                }
            )
            
            self.running = True
            
            # Start reader thread
            self._read_thread = threading.Thread(target=self._read_output, daemon=True)
            self._read_thread.start()
            
            # Start writer thread
            self._write_thread = threading.Thread(target=self._write_input, daemon=True)
            self._write_thread.start()
            
            return True
            
        except Exception as e:
            print(f"Error starting Windows terminal: {e}")
            return False
    
    def _read_output(self):
        """Background thread to read process output"""
        try:
            while self.running and self.process:
                data = self.process.stdout.read(1)
                if not data:
                    break
                # Pass through all output from the shell
                self.output_queue.put(data)
        except Exception as e:
            if self.running:
                print(f"Error reading output: {e}")
    
    def _write_input(self):
        """Background thread to write process input"""
        try:
            while self.running and self.process:
                try:
                    data = self.stdin_queue.get(timeout=0.1)
                    if data:
                        self.process.stdin.write(data)
                        self.process.stdin.flush()
                except queue.Empty:
                    continue
        except Exception as e:
            if self.running:
                print(f"Error writing input: {e}")
    
    async def write(self, data: bytes) -> None:
        """Write data to the process stdin"""
        if self.process and self.running:
            try:
                # Pass all data directly to stdin without manipulation
                # Let the shell handle echoing, backspace, and special keys natively
                self.stdin_queue.put(data)
            except Exception as e:
                print(f"Error writing to Windows terminal: {e}")
    
    async def read(self, timeout: float = 0.01) -> Optional[bytes]:
        """Read data from the process output"""
        if not self.running:
            return None
            
        try:
            # Try to get data without blocking too long
            data = self.output_queue.get(timeout=timeout)
            return data
        except queue.Empty:
            return None
        except Exception:
            return None
    
    async def resize(self, rows: int, cols: int) -> None:
        """Resize the terminal (no-op on Windows)"""
        pass
    
    async def stop(self) -> None:
        """Stop the terminal session"""
        self.running = False
        
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except:
                try:
                    self.process.kill()
                except:
                    pass
            self.process = None
    
    def is_running(self) -> bool:
        """Check if terminal is running"""
        if not self.running or not self.process:
            return False
        return self.process.poll() is None
