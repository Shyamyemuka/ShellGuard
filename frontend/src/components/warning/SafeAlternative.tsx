import React from 'react'
import { CheckCircle } from 'lucide-react'

interface Props {
    command: string
    explanation: string
}

export function SafeAlternative({ command, explanation }: Props) {
    return (
        <div className="space-y-2">
            <h4 className="text-xs font-semibold text-green-400 uppercase tracking-wider flex items-center gap-1">
                <CheckCircle className="w-3 h-3" />
                Safer Alternative
            </h4>
            <div className="bg-green-950/50 border border-green-800/50 rounded-lg p-3">
                <code className="text-sm font-mono text-green-200 break-all">{command}</code>
            </div>
            {explanation && (
                <p className="text-xs text-green-300/70">{explanation}</p>
            )}
        </div>
    )
}
