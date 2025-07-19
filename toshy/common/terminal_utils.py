__version__ = "20250713"

"""
Terminal utilities for Toshy applications.

Simple terminal emulator detection and command execution with optional
desktop environment awareness for optimal terminal selection.
"""

import shutil
import subprocess

from toshy_common.logger import debug


class TerminalNotFoundError(RuntimeError):
    """Raised when no suitable terminal emulator can be found"""
    pass


# List of common terminal emulators in descending order of preference.
# Each element is a tuple: (command_name, args_list, supported_DEs)
TERMINAL_APPS = [
    ('gnome-terminal',          ['--'],     ['gnome', 'unity', 'cinnamon']     ),
    ('ptyxis',                  ['--'],     ['gnome', 'unity', 'cinnamon']     ),
    ('konsole',                 ['-e'],     ['kde']                            ),
    ('xfce4-terminal',          ['-e'],     ['xfce']                           ),
    ('mate-terminal',           ['-e'],     ['mate']                           ),
    ('qterminal',               ['-e'],     ['lxqt']                           ),
    ('lxterminal',              ['-e'],     ['lxde']                           ),
    ('terminology',             ['-e'],     ['enlightenment']                  ),
    ('cosmic-term',             ['-e'],     ['cosmic']                         ),
    ('io.elementary.terminal',  ['-e'],     ['pantheon']                       ),
    ('kitty',                   ['-e'],     []                                 ),
    ('alacritty',               ['-e'],     []                                 ),
    ('tilix',                   ['-e'],     []                                 ),
    ('terminator',              ['-e'],     []                                 ),
    ('xterm',                   ['-e'],     []                                 ),
    ('rxvt',                    ['-e'],     []                                 ),
    ('urxvt',                   ['-e'],     []                                 ),
    ('st',                      ['-e'],     []                                 ),
    ('kgx',                     ['-e'],     []                                 ),  # GNOME Console
]


def run_cmd_lst_in_terminal(command_list, desktop_env: str=None):
    """
    Execute a command in the most appropriate terminal emulator.
    
    Tries to find the default terminal first, then DE-specific terminals,
    then falls back to any available terminal.
    
    Args:
        command_list: List of strings - command and arguments to execute
        desktop_env: String or None - desktop environment (e.g., 'gnome', 'kde')
                    If None, skips DE-specific terminal selection
        
    Returns:
        Boolean - True if command was successfully launched, False otherwise
    """

    # Validate input
    if not isinstance(command_list, list) or not all(isinstance(item, str) for item in command_list):
        debug('run_cmd_lst_in_terminal() expects a list of strings.')
        return False

    if not command_list:
        debug('run_cmd_lst_in_terminal() received empty command list.')
        return False

    def _try_terminal(terminal_cmd, args_list):
        """Try to run command in a specific terminal. Returns True if successful."""
        terminal_path = shutil.which(terminal_cmd)
        if not terminal_path:
            return False

        full_command = [terminal_path] + args_list + command_list
        try:
            subprocess.Popen(full_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            debug(f"Successfully launched command in {terminal_cmd}")
            return True
        except subprocess.SubprocessError as e:
            debug(f'Error launching {terminal_cmd}: {e}')
            return False

    # First: Try to get the default terminal from environment/session
    default_terminals = []
    
    # Check TERMINAL environment variable
    if os.environ.get('TERMINAL'):
        default_terminals.append((os.environ['TERMINAL'], ['-e'], []))
        debug(f"Found TERMINAL env var: {os.environ['TERMINAL']}")
    
    # Check x-terminal-emulator (Debian/Ubuntu default)
    if shutil.which('x-terminal-emulator'):
        default_terminals.append(('x-terminal-emulator', ['-e'], []))
        debug("Found x-terminal-emulator")
    
    # Check for common Wayland terminals first (since you use foot)
    wayland_terminals = [
        ('foot', ['-e'], []),
        ('alacritty', ['-e'], []),
        ('kitty', ['-e'], []),
        ('wezterm', ['start', '--'], []),
    ]
    
    # Try default terminals first
    for terminal_cmd, args_list, _ in default_terminals:
        if _try_terminal(terminal_cmd, args_list):
            return True
    
    # Try Wayland terminals (modern, likely to work better)
    for terminal_cmd, args_list, _ in wayland_terminals:
        if _try_terminal(terminal_cmd, args_list):
            return True

    # Second pass: Try DE-specific terminals if desktop_env is provided
    if desktop_env:
        desktop_env = desktop_env.casefold()
        for terminal_cmd, args_list, de_list in TERMINAL_APPS:
            if desktop_env in de_list:
                if _try_terminal(terminal_cmd, args_list):
                    return True

    # Third pass: Try any available terminal (excluding problematic ones)
    for terminal_cmd, args_list, _ in TERMINAL_APPS:
        # Skip terminology as it's been crashing
        if terminal_cmd == 'terminology':
            continue
        if _try_terminal(terminal_cmd, args_list):
            return True

    # If we reach here, no terminal was found
    message = 'No suitable terminal emulator could be found.'
    debug(f"ERROR: {message} (terminal_utils)")
    raise TerminalNotFoundError(message)
