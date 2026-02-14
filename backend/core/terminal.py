"""
PTY Session Manager
"""
import os
import pty
import select
import subprocess
import struct
import fcntl
import termios
import asyncio
from typing import Optional, Callable

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
            
            # Fork process
            self.pid = os.fork()
            
            if self.pid == 0:
                # Child process
                os.close(self.master_fd)
                os.setsid()
                
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
                os.write(self.master_fd, data)
            except Exception as e:
                print(f"Error writing to PTY: {e}")
    
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
