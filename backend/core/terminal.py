"""
PTY Session Manager
"""
import os
import sys
import asyncio
from typing import Optional, Callable

# Detect platform and import appropriate modules
if sys.platform == 'win32':
    from .terminal_windows import WindowsPTYManager as PTYManager
else:
    import pty
    import select
    import subprocess
    import struct
    import fcntl
    import termios
    
    class PTYManager:
        """Manages a pseudo-terminal session"""
        
        def __init__(self):
            self.master_fd: Optional[int] = None
            self.slave_fd: Optional[int] = None
            self.pid: Optional[int] = None
            self.running: bool = False
            
        async def start(self, shell: str = "/bin/bash") -> bool:
            """Start a new PTY session"""
            try:
                # Create pseudo-terminal pair
                self.master_fd, self.slave_fd = pty.openpty()
                
                # Configure terminal attributes for proper echo in raw mode
                try:
                    attrs = termios.tcgetattr(self.slave_fd)
                    # Enable local echo while in raw mode
                    attrs[3] = attrs[3] | termios.ECHO | termios.ECHOE | termios.ECHOK | termios.ECHONL
                    # Disable canonical mode for character-by-character input
                    attrs[3] = attrs[3] & ~termios.ICANON
                    # Enable output processing for proper newline handling
                    attrs[1] = attrs[1] | termios.OPOST | termios.ONLCR
                    # Set minimum characters for non-canonical read
                    attrs[6][termios.VMIN] = 1
                    attrs[6][termios.VTIME] = 0
                    termios.tcsetattr(self.slave_fd, termios.TCSANOW, attrs)
                except Exception as e:
                    print(f"Warning: Could not set terminal attributes: {e}")
                
                # Fork process
                self.pid = os.fork()
                
                if self.pid == 0:
                    # Child process
                    os.close(self.master_fd)
                    os.setsid()
                    
                    # Change to sandbox directory if enabled
                    from config import settings
                    if settings.sandbox_mode and os.path.exists(settings.sandbox_dir):
                        try:
                            os.chdir(settings.sandbox_dir)
                        except Exception as e:
                            print(f"Warning: Could not change to sandbox dir: {e}")
                    
                    # Set up slave as controlling terminal
                    os.dup2(self.slave_fd, 0)
                    os.dup2(self.slave_fd, 1)
                    os.dup2(self.slave_fd, 2)
                    
                    if self.slave_fd > 2:
                        os.close(self.slave_fd)
                    
                    # Set environment
                    env = os.environ.copy()
                    env["TERM"] = "xterm-256color"
                    env["SHELL"] = shell
                    env["PS1"] = r"\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ "
                    
                    # Execute shell
                    os.execvpe(shell, [shell], env)
                else:
                    # Parent process
                    os.close(self.slave_fd)
                    self.slave_fd = None
                    self.running = True
                    
                    # Set non-blocking
                    flags = fcntl.fcntl(self.master_fd, fcntl.F_GETFL)
                    fcntl.fcntl(self.master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
                    
                    return True
                    
            except Exception as e:
                print(f"Error starting PTY: {e}")
                return False
        
        async def write(self, data: bytes) -> None:
            """Write data to the PTY"""
            if self.master_fd and self.running:
                try:
                    written = os.write(self.master_fd, data)
                    if written < len(data):
                        print(f"Warning: Partial write to PTY ({written}/{len(data)} bytes)")
                except OSError as e:
                    print(f"Error writing to PTY: {e}")
                except Exception as e:
                    print(f"Unexpected error writing to PTY: {e}")
        
        async def read(self, timeout: float = 0.01) -> Optional[bytes]:
            """Read data from the PTY"""
            if not self.master_fd or not self.running:
                return None
                
            try:
                ready, _, _ = select.select([self.master_fd], [], [], timeout)
                if ready:
                    return os.read(self.master_fd, 4096)
            except Exception:
                pass
            return None
        
        async def resize(self, rows: int, cols: int) -> None:
            """Resize the PTY"""
            if self.master_fd and self.running:
                try:
                    winsize = struct.pack("HHHH", rows, cols, 0, 0)
                    fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, winsize)
                except Exception as e:
                    print(f"Error resizing PTY: {e}")
        
        async def stop(self) -> None:
            """Stop the PTY session"""
            self.running = False
            
            if self.master_fd:
                try:
                    os.close(self.master_fd)
                except:
                    pass
                self.master_fd = None
                
            if self.pid:
                try:
                    os.kill(self.pid, 9)
                    os.waitpid(self.pid, 0)
                except:
                    pass
                self.pid = None
        
        def is_running(self) -> bool:
            """Check if PTY is running"""
            if not self.running or not self.pid:
                return False
            try:
                os.kill(self.pid, 0)
                return True
            except OSError:
                return False
