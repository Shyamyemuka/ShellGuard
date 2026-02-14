"""
Command Line Input Buffer
"""

class CommandBuffer:
    """Buffers command line input"""
    
    def __init__(self):
        self._buffer: str = ""
        self._cursor_pos: int = 0
    
    def add(self, data: str) -> None:
        """Add data to the buffer"""
        for char in data:
            # Skip escape sequences - they're handled separately
            if char == '\x1b':
                continue
            if char == "\x7f" or char == "\x08":  # Backspace (DEL or BS)
                if self._cursor_pos > 0:
                    self._buffer = (
                        self._buffer[:self._cursor_pos - 1] +
                        self._buffer[self._cursor_pos:]
                    )
                    self._cursor_pos -= 1
            elif char == "\x03":  # Ctrl+C
                self.clear()
            elif char == "\x15":  # Ctrl+U
                self.clear()
            elif char == "\x17":  # Ctrl+W - delete word
                self._delete_word()
            elif ord(char) >= 32 or char == "\t":  # Printable or tab
                self._buffer = (
                    self._buffer[:self._cursor_pos] +
                    char +
                    self._buffer[self._cursor_pos:]
                )
                self._cursor_pos += 1
    
    def _delete_word(self) -> None:
        """Delete the last word"""
        # Skip trailing spaces
        while self._cursor_pos > 0 and self._buffer[self._cursor_pos - 1] == " ":
            self._buffer = (
                self._buffer[:self._cursor_pos - 1] +
                self._buffer[self._cursor_pos:]
            )
            self._cursor_pos -= 1
        
        # Delete until space
        while self._cursor_pos > 0 and self._buffer[self._cursor_pos - 1] != " ":
            self._buffer = (
                self._buffer[:self._cursor_pos - 1] +
                self._buffer[self._cursor_pos:]
            )
            self._cursor_pos -= 1
    
    def get_command(self) -> str:
        """Get the current command"""
        return self._buffer.strip()
    
    def is_incomplete(self) -> bool:
        """Check if command appears incomplete (multi-line continuation)"""
        cmd = self._buffer.strip()
        if not cmd:
            return False
        
        # Check for trailing backslash (line continuation)
        if cmd.endswith('\\'):
            return True
        
        # Check for trailing pipes or logical operators
        incomplete_patterns = [
            '|', '&&', '||', '&'
        ]
        for pattern in incomplete_patterns:
            if cmd.endswith(pattern):
                return True
        
        # Check for unclosed quotes
        single_quotes = cmd.count("'") - cmd.count("\\'")
        double_quotes = cmd.count('"') - cmd.count('\\"')
        if single_quotes % 2 != 0 or double_quotes % 2 != 0:
            return True
        
        return False
    
    def clear(self) -> None:
        """Clear the buffer"""
        self._buffer = ""
        self._cursor_pos = 0
    
    def __len__(self) -> int:
        return len(self._buffer)
    
    def __str__(self) -> str:
        return self._buffer
