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

        // Handle terminal input - no local echo, let backend/shell handle it
        terminal.onData((data: string) => {
          writeToTerminal(data);
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
