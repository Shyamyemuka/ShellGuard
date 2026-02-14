import React from 'react'

interface Props {
    code: string
    language?: string
}

export function CodeBlock({ code, language = 'bash' }: Props) {
    return (
        <div className="bg-black/40 rounded-lg p-3 overflow-x-auto">
            <code className="text-sm font-mono text-zinc-200 whitespace-pre">{code}</code>
        </div>
    )
}
