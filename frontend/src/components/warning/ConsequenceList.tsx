import React from 'react'
import { AlertTriangle } from 'lucide-react'

interface Props {
    consequences: string[]
}

export function ConsequenceList({ consequences }: Props) {
    return (
        <div className="space-y-1">
            <h4 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider flex items-center gap-1">
                <AlertTriangle className="w-3 h-3" />
                Consequences
            </h4>
            <ul className="space-y-1">
                {consequences.map((c, i) => (
                    <li key={i} className="text-sm text-zinc-300 flex items-start gap-2">
                        <span className="text-red-400 mt-0.5">•</span>
                        {c}
                    </li>
                ))}
            </ul>
        </div>
    )
}
