"""
Dangerous Command Patterns Registry
"""

DANGER_PATTERNS = {
    "critical": [
        {
            "pattern": r"rm\s+-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*\s+/\s*$",
            "is_regex": True,
            "category": "filesystem_destruction",
            "description": "Recursive force delete on root filesystem",
            "hard_block": True,
            "block_message": "⛔ BLOCKED: This command would permanently destroy your entire filesystem."
        },
        {
            "pattern": ":(){ :|:& };:",
            "is_regex": False,
            "category": "fork_bomb",
            "description": "Fork bomb - will crash the system",
            "hard_block": True,
            "block_message": "⛔ BLOCKED: Fork bomb detected. This would crash your system immediately."
        },
        {
            "pattern": r"dd\s+if=/dev/(zero|random|urandom)\s+of=/dev/sd[a-z]",
            "is_regex": True,
            "category": "disk_destruction",
            "description": "Writing random/zero data to disk",
            "hard_block": True,
            "block_message": "⛔ BLOCKED: This would overwrite your disk, destroying all data."
        },
        {
            "pattern": r"mv\s+/\s+/dev/null",
            "is_regex": True,
            "category": "filesystem_destruction",
            "description": "Moving root filesystem to null device",
            "hard_block": True,
            "block_message": "⛔ BLOCKED: This would effectively delete your entire filesystem."
        },
        {
            "pattern": r"chmod\s+-R\s+777\s+/\s*$",
            "is_regex": True,
            "category": "permission_catastrophe",
            "description": "Making entire filesystem world-writable",
            "hard_block": True,
            "block_message": "⛔ BLOCKED: This would remove all security permissions from every file."
        },
        {
            "pattern": r">\s*/dev/sd[a-z]",
            "is_regex": True,
            "category": "disk_destruction",
            "description": "Redirecting output to block device",
            "hard_block": True,
            "block_message": "⛔ BLOCKED: This would corrupt your disk's data."
        },
        {
            "pattern": r"wget.*\|\s*sudo\s+bash",
            "is_regex": True,
            "category": "untrusted_execution",
            "description": "Piping remote script to sudo bash",
            "hard_block": True,
            "block_message": "⛔ BLOCKED: Piping untrusted remote content to sudo bash is extremely dangerous."
        },
        {
            "pattern": r"curl.*\|\s*sudo\s+bash",
            "is_regex": True,
            "category": "untrusted_execution",
            "description": "Piping remote content to sudo bash",
            "hard_block": True,
            "block_message": "⛔ BLOCKED: Piping untrusted remote content to sudo bash is extremely dangerous."
        }
    ],
    "high": [
        {
            "pattern": r"rm\s+-[a-zA-Z]*r[a-zA-Z]*f",
            "is_regex": True,
            "category": "recursive_delete",
            "description": "Recursive force delete"
        },
        {
            "pattern": r"rm\s+-[a-zA-Z]*r",
            "is_regex": True,
            "category": "recursive_delete",
            "description": "Recursive delete"
        },
        {
            "pattern": r"(DROP|drop)\s+(TABLE|DATABASE|SCHEMA)",
            "is_regex": True,
            "category": "database_destruction",
            "description": "Database structure deletion"
        },
        {
            "pattern": r"kill\s+-9",
            "is_regex": True,
            "category": "process_kill",
            "description": "Force kill process"
        },
        {
            "pattern": r"killall",
            "is_regex": True,
            "category": "process_kill",
            "description": "Kill all processes by name"
        },
        {
            "pattern": r"curl\s+.*\|\s*(sudo\s+)?bash",
            "is_regex": True,
            "category": "untrusted_execution",
            "description": "Piping remote content to bash"
        },
        {
            "pattern": r"wget\s+.*\|\s*(sudo\s+)?sh",
            "is_regex": True,
            "category": "untrusted_execution",
            "description": "Piping downloaded content to shell"
        },
        {
            "pattern": r"(shutdown|reboot|halt|poweroff)",
            "is_regex": True,
            "category": "system_control",
            "description": "System shutdown/reboot"
        },
        {
            "pattern": r"init\s+[06]",
            "is_regex": True,
            "category": "system_control",
            "description": "System runlevel change"
        },
        {
            "pattern": r"chmod\s+777",
            "is_regex": True,
            "category": "permission_change",
            "description": "Making files world-writable"
        },
        {
            "pattern": r"TRUNCATE\s+TABLE",
            "is_regex": True,
            "category": "database_destruction",
            "description": "Truncating database table"
        }
    ],
    "medium": [
        {
            "pattern": r"chmod\s+",
            "is_regex": True,
            "category": "permission_change",
            "description": "Permission modification"
        },
        {
            "pattern": r"chown\s+-R",
            "is_regex": True,
            "category": "ownership_change",
            "description": "Recursive ownership change"
        },
        {
            "pattern": r"iptables\s+-F",
            "is_regex": True,
            "category": "firewall_change",
            "description": "Flushing firewall rules"
        },
        {
            "pattern": r"ufw\s+disable",
            "is_regex": True,
            "category": "firewall_change",
            "description": "Disabling firewall"
        },
        {
            "pattern": r"systemctl\s+(stop|disable|mask)",
            "is_regex": True,
            "category": "service_management",
            "description": "Stopping or disabling system service"
        },
        {
            "pattern": r"service\s+\S+\s+stop",
            "is_regex": True,
            "category": "service_management",
            "description": "Stopping system service"
        },
        {
            "pattern": r"docker\s+(system\s+prune|rm|rmi)",
            "is_regex": True,
            "category": "container_cleanup",
            "description": "Docker resource removal"
        },
        {
            "pattern": r"apt\s+(remove|purge)",
            "is_regex": True,
            "category": "package_removal",
            "description": "Package removal"
        },
        {
            "pattern": r"pip\s+uninstall",
            "is_regex": True,
            "category": "package_removal",
            "description": "Python package removal"
        },
        {
            "pattern": r"npm\s+uninstall",
            "is_regex": True,
            "category": "package_removal",
            "description": "Node package removal"
        },
        {
            "pattern": r"git\s+push\s+.*--force",
            "is_regex": True,
            "category": "git_destructive",
            "description": "Force push to git remote"
        },
        {
            "pattern": r"git\s+reset\s+--hard",
            "is_regex": True,
            "category": "git_destructive",
            "description": "Hard reset git history"
        },
        {
            "pattern": r"git\s+clean\s+-[a-zA-Z]*f",
            "is_regex": True,
            "category": "git_destructive",
            "description": "Force clean untracked git files"
        },
        {
            "pattern": r"git\s+branch\s+-D",
            "is_regex": True,
            "category": "git_destructive",
            "description": "Force delete git branch"
        },
        {
            "pattern": r"git\s+rebase\s+-i.*--force",
            "is_regex": True,
            "category": "git_destructive",
            "description": "Force interactive rebase"
        },
        {
            "pattern": r"yarn\s+remove",
            "is_regex": True,
            "category": "package_removal",
            "description": "Yarn package removal"
        },
        {
            "pattern": r"DELETE\s+FROM\s+\w+(\s|;|$)",
            "is_regex": True,
            "category": "database_destruction",
            "description": "SQL DELETE without WHERE clause"
        },
        {
            "pattern": r"ifconfig\s+\w+\s+down",
            "is_regex": True,
            "category": "network_disruption",
            "description": "Disabling network interface"
        },
        {
            "pattern": r"ip\s+link\s+set\s+\w+\s+down",
            "is_regex": True,
            "category": "network_disruption",
            "description": "Bringing down network link"
        },
        {
            "pattern": r"ip\s+route\s+del",
            "is_regex": True,
            "category": "network_disruption",
            "description": "Deleting IP routes"
        },
        {
            "pattern": r"crontab\s+-r",
            "is_regex": True,
            "category": "automation_removal",
            "description": "Removing all cron jobs"
        },
        {
            "pattern": r"systemctl\s+mask",
            "is_regex": True,
            "category": "service_management",
            "description": "Masking systemd service"
        },
        {
            "pattern": r"pkill\s+-9",
            "is_regex": True,
            "category": "process_kill",
            "description": "Force kill processes by name"
        }
    ],
    "low": [
        {
             "pattern": r"rm\s+",
             "is_regex": True,
             "category": "file_deletion",
             "description": "Regular file deletion"
        },
        {
            "pattern": r"sudo\s+",
            "is_regex": True,
            "category": "elevated_privilege",
            "description": "Running with elevated privileges"
        },
        {
            "pattern": r"(vim|nano|vi)\s+/etc/",
            "is_regex": True,
            "category": "config_edit",
            "description": "Editing system configuration file"
        }
    ]
}
