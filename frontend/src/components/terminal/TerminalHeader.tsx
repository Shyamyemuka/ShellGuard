import React from 'react'

export function TerminalHeader() {
    return (
        <div className="flex items-center px-4 py-2 bg-zinc-900 border-b border-zinc-800">
            {/* Traffic lights */}
            <div className="flex gap-2 mr-4">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                <div className="w-3 h-3 rounded-full bg-green-500" />
            </div>
            <span className="text-sm text-zinc-400 font-mono">
                shellguard — bash
            </span>
        </div>
    )
}
