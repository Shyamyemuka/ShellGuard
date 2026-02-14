"""
Safer Alternative Suggestion
"""
from typing import Optional, Dict

# Static safer alternatives for common dangerous patterns
ALTERNATIVES: Dict[str, Dict[str, str]] = {
    "rm -rf": {
        "pattern": "rm -rf",
        "alternative": "rm -ri",
        "explanation": "Uses interactive mode, prompting for confirmation before each deletion"
    },
    "rm -r": {
        "pattern": "rm -r",
        "alternative": "rm -ri",
        "explanation": "Uses interactive mode for confirmation"
    },
    "chmod 777": {
        "pattern": "chmod 777",
        "alternative": "chmod 755",
        "explanation": "Gives owner full access but limits group and others to read/execute only"
    },
    "kill -9": {
        "pattern": "kill -9",
        "alternative": "kill -15",
        "explanation": "Sends SIGTERM allowing graceful shutdown instead of forcing immediate termination"
    },
    "git push --force": {
        "pattern": "git push --force",
        "alternative": "git push --force-with-lease",
        "explanation": "Fails if remote has commits you haven't seen, preventing accidental overwrites"
    },
    "git reset --hard": {
        "pattern": "git reset --hard",
        "alternative": "git stash",
        "explanation": "Saves changes temporarily instead of discarding them permanently"
    }
}

class AlternativeGenerator:
    """Generates safer command alternatives"""
    
    def suggest(self, command: str) -> Optional[Dict[str, str]]:
        """Suggest a safer alternative for a command"""
        command_lower = command.lower()
        
        for pattern, suggestion in ALTERNATIVES.items():
            if pattern in command_lower:
                # Generate specific alternative by replacing pattern
                alt_command = command.replace(
                    pattern,
                    suggestion["alternative"]
                )
                return {
                    "safer_alternative": alt_command,
                    "alternative_explanation": suggestion["explanation"]
                }
        
        return None
