"""
ShellGuard Session Handler
"""
import asyncio
from uuid import uuid4, UUID
from datetime import datetime
from typing import Optional, Callable, Awaitable
from dataclasses import dataclass, field

from .terminal import PTYManager
from .interceptor import CommandInterceptor, InterceptionResult
from .buffer import CommandBuffer
from data.models import SessionStats, CommandLogEntry, RiskLevel, CommandAction
from data.database import Database

@dataclass
class ShellGuardSession:
    """Manages a complete ShellGuard terminal session"""
    
    id: UUID = field(default_factory=uuid4)
    pty: PTYManager = field(default_factory=PTYManager)
    interceptor: CommandInterceptor = field(default_factory=CommandInterceptor)
    buffer: CommandBuffer = field(default_factory=CommandBuffer)
    stats: SessionStats = field(default_factory=lambda: SessionStats(session_id=uuid4()))
    
    # Callbacks
    on_output: Optional[Callable[[bytes], Awaitable[None]]] = None
    on_warning: Optional[Callable[[InterceptionResult], Awaitable[None]]] = None
    on_blocked: Optional[Callable[[InterceptionResult], Awaitable[None]]] = None
    on_analyzing: Optional[Callable[[str], Awaitable[None]]] = None
    on_analysis_complete: Optional[Callable[[str, InterceptionResult], Awaitable[None]]] = None
    on_stats_update: Optional[Callable[[SessionStats], Awaitable[None]]] = None
    
    _pending_command: Optional[str] = None
    _pending_interception: Optional[InterceptionResult] = None
    _read_task: Optional[asyncio.Task] = None
    _running: bool = False
    _db: Database = field(default_factory=Database)
    _input_chars_count: int = 0  # Track characters in current input line
    
    async def start(self) -> bool:
        """Start the session"""
        self.stats = SessionStats(session_id=self.id)
        self.stats.session_start = datetime.utcnow()
        
        success = await self.pty.start()
        if success:
            self._running = True
            self._read_task = asyncio.create_task(self._read_loop())
            await self._db.create_session(str(self.id))
        return success
    
    async def stop(self) -> None:
        """Stop the session"""
        self._running = False
        if self._read_task:
            self._read_task.cancel()
            try:
                await self._read_task
            except asyncio.CancelledError:
                pass
        await self.pty.stop()
        await self._db.end_session(str(self.id))
    
    async def handle_input(self, data: str) -> None:
        """Handle input from the user"""
        # Check for Enter key - this is when we actually process
        if data in ["\r", "\n"]:
            command = self.buffer.get_command()
            self.buffer.clear()
            self._input_chars_count = 0
            
            if command.strip():
                await self._process_command(command)
            else:
                # Empty command - send to shell for new prompt
                await self.pty.write(b"\r")
        else:
            # Buffer all input but DON'T echo - let xterm.js handle display
            i = 0
            while i < len(data):
                char = data[i]
                
                # Handle escape sequences (e.g., arrow keys, function keys)
                if char == '\x1b' and i + 1 < len(data):
                    # Skip the entire escape sequence
                    if data[i + 1] == '[':
                        # CSI sequence: ESC [ ... letter
                        i += 2
                        while i < len(data) and data[i] not in 'ABCDEFGHJKSTfmnsulh':
                            i += 1
                        i += 1
                        continue
                    elif data[i + 1] == 'O':
                        # SS3 sequence: ESC O letter
                        i += 3
                        continue
                    else:
                        # Other escape sequence
                        i += 2
                        continue
                elif char == '\x1b':
                    # Standalone ESC
                    i += 1
                    continue
                    
                # Track input for backspace protection (buffer handles the actual logic)
                if char in ["\x7f", "\x08"]:
                    if self._input_chars_count > 0:
                        self.buffer.add(char)
                        self._input_chars_count -= 1
                elif ord(char) >= 32 or char == "\t":
                    self.buffer.add(char)
                    self._input_chars_count += 1
                elif char == "\x03":  # Ctrl+C
                    self.buffer.clear()
                    self._input_chars_count = 0
                    await self.pty.write(b"\x03")
                
                i += 1
    
    async def _process_command(self, command: str) -> None:
        """Process an intercepted command"""
        print(f"[DEBUG] Processing command: {repr(command)}")
        
        # Notify analyzing
        if self.on_analyzing:
            await self.on_analyzing(command)
        
        # Intercept and analyze
        result = await self.interceptor.intercept(
            command=command,
            working_directory=await self._get_cwd()
        )
        
        print(f"[DEBUG] Interception result: should_block={result.should_block}, risk_level={result.risk_level}, has_analysis={result.analysis is not None}")
        
        self.stats.total_commands += 1
        
        if result.is_hard_block:
            # Hard blocked - never execute
            self.stats.blocked += 1
            if self.on_blocked:
                await self.on_blocked(result)
            await self._log_command(command, result, CommandAction.BLOCKED)
            # Send Enter to get a new prompt
            await self.pty.write(b"\r")
            await asyncio.sleep(0.1)  # Wait for prompt
        elif result.should_block:
            # Needs user decision
            self.stats.warnings_issued += 1
            self._pending_command = command
            self._pending_interception = result
            if self.on_warning:
                await self.on_warning(result)
        else:
            # Safe - execute immediately
            self.stats.safe_commands += 1
            # Notify analysis complete for safe commands
            if self.on_analysis_complete:
                print(f"[DEBUG] Sending analysis_complete for: {repr(command)}")
                await self.on_analysis_complete(command, result)
            await self._execute_command(command)
            await self._log_command(command, result, CommandAction.EXECUTED)
        
        # Update stats
        if self.on_stats_update:
            await self.on_stats_update(self.stats)
    
    async def approve(self) -> None:
        """User approved the risky command"""
        if self._pending_command:
            self.stats.approved_risky += 1
            await self._execute_command(self._pending_command)
            await self._log_command(
                self._pending_command,
                self._pending_interception,
                CommandAction.APPROVED
            )
            self._clear_pending()
            if self.on_stats_update:
                await self.on_stats_update(self.stats)
    
    async def use_alternative(self, alt_command: str) -> None:
        """User chose the safer alternative"""
        if self._pending_command:
            self.stats.safe_swaps += 1
            await self._execute_command(alt_command)
            await self._log_command(
                self._pending_command,
                self._pending_interception,
                CommandAction.SAFE_SWAP,
                alternative_used=alt_command
            )
            self._clear_pending()
            if self.on_stats_update:
                await self.on_stats_update(self.stats)
    
    async def cancel(self) -> None:
        """User cancelled the command"""
        if self._pending_command:
            self.stats.cancelled += 1
            # Send Enter to get a new prompt
            await self.pty.write(b"\r")
            await asyncio.sleep(0.1)  # Wait for prompt
            await self._log_command(
                self._pending_command,
                self._pending_interception,
                CommandAction.CANCELLED
            )
            self._clear_pending()
            if self.on_stats_update:
                await self.on_stats_update(self.stats)
    
    async def resize(self, rows: int, cols: int) -> None:
        """Resize the terminal"""
        await self.pty.resize(rows, cols)
    
    async def _execute_command(self, command: str) -> None:
        """Execute a command in the PTY"""
        await self.pty.write(f"{command}\r".encode())
        # Give PowerShell a moment to process and output the prompt
        await asyncio.sleep(0.1)
    
    async def _read_loop(self) -> None:
        """Continuously read from PTY and send output"""
        while self._running:
            try:
                data = await self.pty.read(timeout=0.05)
                if data and self.on_output:
                    await self.on_output(data)
                else:
                    await asyncio.sleep(0.001)
            except Exception as e:
                if self._running:
                    print(f"Error in read loop: {e}")
                break
    
    async def _get_cwd(self) -> str:
        """Get current working directory"""
        return "~"  # Simplified for hackathon
    
    async def _log_command(
        self,
        command: str,
        result: Optional[InterceptionResult],
        action: CommandAction,
        alternative_used: Optional[str] = None
    ) -> None:
        """Log command to database"""
        entry = CommandLogEntry(
            session_id=self.id,
            command=command,
            timestamp=datetime.utcnow(),
            risk_level=result.risk_level if result else RiskLevel.SAFE,
            action=action,
            analysis=result.analysis if result else None,
            alternative_used=alternative_used,
            working_directory=await self._get_cwd(),
            analysis_latency_ms=result.analysis_latency_ms if result else 0
        )
        await self._db.log_command(entry)
    
    def _clear_pending(self) -> None:
        """Clear pending command state"""
        self._pending_command = None
        self._pending_interception = None
