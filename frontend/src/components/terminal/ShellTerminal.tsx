"use client";

import React, {
  useEffect,
  useRef,
  forwardRef,
  useImperativeHandle,
} from "react";

export interface ShellTerminalRef {
  write: (data: string) => void;
  fit: () => void;
  getTerminal: () => any;
}

interface Props {
  writeToTerminal: (data: string) => void;
}

export const ShellTerminal = forwardRef<ShellTerminalRef, Props>(
  function ShellTerminal({ writeToTerminal }, ref) {
    const containerRef = useRef<HTMLDivElement>(null);
    const terminalRef = useRef<any>(null);
    const fitAddonRef = useRef<any>(null);
    const initialized = useRef(false);

    useImperativeHandle(ref, () => ({
      write: (data: string) => {
        terminalRef.current?.write(data);
      },
      fit: () => {
        fitAddonRef.current?.fit();
      },
      getTerminal: () => terminalRef.current,
    }));

    useEffect(() => {
      if (initialized.current || !containerRef.current) return;
      initialized.current = true;

      const initTerminal = async () => {
        const { Terminal } = await import("xterm");
        const { FitAddon } = await import("xterm-addon-fit");

        const fitAddon = new FitAddon();
        fitAddonRef.current = fitAddon;

        const terminal = new Terminal({
          cursorBlink: true,
          cursorStyle: "block",
          fontSize: 14,
          fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
          theme: {
            background: "#0a0a0a",
            foreground: "#fafafa",
            cursor: "#00ff88",
            cursorAccent: "#0a0a0a",
            selectionBackground: "#22c55e33",
            black: "#09090b",
            red: "#ef4444",
            green: "#22c55e",
            yellow: "#eab308",
            blue: "#3b82f6",
            magenta: "#a855f7",
            cyan: "#06b6d4",
            white: "#fafafa",
            brightBlack: "#52525b",
            brightRed: "#f87171",
            brightGreen: "#4ade80",
            brightYellow: "#facc15",
            brightBlue: "#60a5fa",
            brightMagenta: "#c084fc",
            brightCyan: "#22d3ee",
            brightWhite: "#ffffff",
          },
          allowProposedApi: true,
          scrollback: 5000,
        });

        terminal.loadAddon(fitAddon);
        terminal.open(containerRef.current!);
        fitAddon.fit();
        terminalRef.current = terminal;

        // Track current input line and cursor position
        let currentInput = "";
        let cursorPos = 0; // Position within currentInput

        // Handle terminal input with local echo and cursor management
        terminal.onData((data: string) => {
          const code = data.charCodeAt(0);
          
          // Enter key
          if (data === "\r" || data === "\n") {
            terminal.write("\r\n");
            writeToTerminal(data);
            currentInput = "";
            cursorPos = 0;
          }
          // Backspace / Delete (Ctrl+H or DEL)
          else if (code === 127 || code === 8) {
            if (cursorPos > 0) {
              // Remove character before cursor
              currentInput = currentInput.slice(0, cursorPos - 1) + currentInput.slice(cursorPos);
              cursorPos--;
              
              // Visual update: backspace, write rest of line, clear to end, reposition cursor
              terminal.write("\b");
              const remaining = currentInput.slice(cursorPos);
              terminal.write(remaining + " ");
              // Move cursor back
              if (remaining.length > 0) {
                terminal.write(`\x1b[${remaining.length + 1}D`);
              } else {
                terminal.write("\b");
              }
              
              writeToTerminal(data);
            }
          }
          // Ctrl+C
          else if (code === 3) {
            terminal.write("^C\r\n");
            currentInput = "";
            cursorPos = 0;
            writeToTerminal(data);
          }
          // Escape sequences (arrow keys, home, end, delete, etc.)
          else if (data.startsWith("\x1b[") || data.startsWith("\x1bO")) {
            // Parse escape sequence
            if (data === "\x1b[D") {
              // Left arrow
              if (cursorPos > 0) {
                cursorPos--;
                terminal.write("\x1b[D");
              }
            } else if (data === "\x1b[C") {
              // Right arrow
              if (cursorPos < currentInput.length) {
                cursorPos++;
                terminal.write("\x1b[C");
              }
            } else if (data === "\x1b[H" || data === "\x1b[1~") {
              // Home key - move to beginning
              if (cursorPos > 0) {
                terminal.write(`\x1b[${cursorPos}D`);
                cursorPos = 0;
              }
            } else if (data === "\x1b[F" || data === "\x1b[4~") {
              // End key - move to end
              const moveCount = currentInput.length - cursorPos;
              if (moveCount > 0) {
                terminal.write(`\x1b[${moveCount}C`);
                cursorPos = currentInput.length;
              }
            } else if (data === "\x1b[3~") {
              // Delete key - delete character at cursor
              if (cursorPos < currentInput.length) {
                currentInput = currentInput.slice(0, cursorPos) + currentInput.slice(cursorPos + 1);
                
                // Visual update
                const remaining = currentInput.slice(cursorPos);
                terminal.write(remaining + " ");
                if (remaining.length > 0) {
                  terminal.write(`\x1b[${remaining.length + 1}D`);
                } else {
                  terminal.write("\b");
                }
              }
            }
            // Send to backend for tracking
            writeToTerminal(data);
          }
          // Printable characters
          else if (code >= 32 || data === "\t") {
            // Insert character at cursor position
            currentInput = currentInput.slice(0, cursorPos) + data + currentInput.slice(cursorPos);
            cursorPos++;
            
            // Visual update: write character and rest of line, then reposition cursor
            const remaining = currentInput.slice(cursorPos);
            terminal.write(data + remaining);
            if (remaining.length > 0) {
              terminal.write(`\x1b[${remaining.length}D`);
            }
            
            writeToTerminal(data);
          }
          // Other control characters
          else {
            writeToTerminal(data);
          }
        });

        // Handle resize
        const handleResize = () => {
          fitAddon.fit();
        };
        window.addEventListener("resize", handleResize);

        return () => {
          window.removeEventListener("resize", handleResize);
          terminal.dispose();
        };
      };

      initTerminal();
    }, [writeToTerminal]);

    return (
      <div
        ref={containerRef}
        className="w-full h-full bg-terminal-bg"
        style={{ minHeight: "400px" }}
      />
    );
  },
);
