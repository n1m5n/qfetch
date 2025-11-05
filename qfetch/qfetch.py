#!/usr/bin/env python3

# Copyright (C) 2025 qvipin
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import os
import platform
import subprocess
import re
import random
import argparse


"""Argparse code"""

about = (
    "qfetch is a simple, no-fuss CLI tool written in Python that gives you a clean "
    "snapshot of your system info on Linux and macOS. It shows details like your OS, "
    "architecture, packages, shell version, terminal type, memory usage, disk usage, uptime, "
    "and even throws in some fun ASCII art for good measure. It’s designed to be straightforward "
    "and looks good right out of the box.\n\n(Designed/Tested for Ubuntu, Debian, and MacOS)\n\n"
    "Made with ❤️ by qvipin"
)

parser = argparse.ArgumentParser(description=about, formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument(
    "--art",
    "-a",
    metavar="<Playboy-Bunny, Tux, Phoenix, Robot, Cat, Random-Art>",
    choices=["Playboy-Bunny", "Tux", "Phoenix", "Robot", "Cat", "Random-Art"],
    help='select the ASCII Art you want qfetch to use.',
    required=False,
)

parser.add_argument(
    "--sys-info",
    "-s",
    metavar="<sys_info_default, sys_info_no_nerd_font>",
    choices=["sys_info_default", "sys_info_no_nerd_font"],
    help='select how you want qfetch to present your sysinfo',
    required=False,
)

parser.add_argument(
    "--theme",
    "-t",
    metavar="<default, red, green, blue, yellow, cyan, magenta>",
    choices=["default", "red", "green", "blue", "yellow", "cyan", "magenta"],
    help="select a color theme for side bars and symbols",
    required=False,
)

args = parser.parse_args()


"""ASCII Art"""

# The top line of ascii art is tabbed by 1 to work with the side printing logic
art = [
    r'''    |\ |\    
    \ \| |
     \ | |
   .--''/
  /o     \
  \      /
   {>o<}='
''',
    r'''    .---.
   /     \
   \.@-@./
   /`\_/`\
  //  _  \\
 | \     )|_
/`\_`>  <_/ \
\__/'---'\__/
''',
    r''' .\\            //.
. \ \          / /.
.\  ,\     /` /,.- 
 -.   \  /'/ /  .
 ` -   `-'  \  -
   '.       /.\`
      -    .-
      :`//.'
      .`.'
      .'
''',
    r'''       __
   _  |@@|
  / \ \--/ __
  ) O|----|  |   __
 / / \ }{ /\ )_ / _\
 )/  /\__/\ \__O (__ 
|/  (--/\--)    \__/
 /   _)(  )(_
   `---''---`
''',
    r'''
   |\---/|
   | ,_, |
    \_`_/-..----.
 ___/ `   ' ,""+ \
(__...'   __\    |`.___.';
  (_,...'(_,.`__)/'.....+
'''
]

rand_art = random.choice(art)  # Random art choice


"""OS Check"""

def os_check():
    operating_sys = platform.system()
    if operating_sys == "Darwin":
        return "macOS"
    elif operating_sys == "Windows":
        return "Windows"
    elif operating_sys == "Linux":
        return "Linux"
    else:
        raise Exception(
            "[!] Couldn't detect operating system, make a Github Issue if you're on MacOS or Linux"
        )


"""Art-related Code"""

def theme_color_code():
    """Return ANSI light color code based on theme"""
    colors = {
        "default": "95",
        "red": "91",
        "green": "92",
        "yellow": "93",
        "blue": "94",
        "magenta": "95",
        "cyan": "96",
    }
    return colors.get(args.theme or "default")


def ascii_art():
    """Return ASCII art string based on user selection"""
    final_art = art[2]

    if args.art:
        art_dict = {
            "Playboy-Bunny": art[0],
            "Tux": art[1],
            "Phoenix": art[2],
            "Robot": art[3],
            "Cat": art[4],
            "Random-Art": rand_art,
        }
        final_art = art_dict.get(args.art)

    return final_art


def longest_line():
    """Determine the longest line in the ASCII art"""
    art_lines = ascii_art().splitlines()
    l_line = len(art_lines[0])
    for line in art_lines:
        if len(line) > l_line:
            l_line = len(line)
    return l_line


"""System information elements"""

def package_count():
    if os_check() == "macOS":
        brew_count = len(os.listdir("/opt/homebrew/cellar"))
        final_count = str(brew_count) + " (brew)"
    elif os_check() == "Linux":
        apt_count = subprocess.check_output(
            "dpkg --get-selections | wc -l", shell=True, text=True
        ).strip()
        final_count = str(apt_count) + " (apt)"
    return final_count


def shell_ver():
    if os_check() in ["macOS", "Linux"]:
        shell = subprocess.check_output("echo $SHELL", shell=True, text=True).strip()
        is_wsl = "microsoft" in platform.release().lower()

        if "zsh" in shell:
            zsh_ver = subprocess.check_output("zsh --version", shell=True, text=True).strip()
            return str(zsh_ver.split()[1])
        elif "bash" in shell:
            if is_wsl:
                return "bash (WSL)"
            else:
                bash_ver = subprocess.check_output("bash --version", shell=True, text=True).strip()
                return "bash " + bash_ver.split()[3]
    else:
        raise Exception("[!] This operating system isn't supported by qfetch.")


def find_term():
    if os_check() in ["macOS", "Linux"]:
        term = subprocess.check_output("echo $TERM", shell=True, text=True).strip()
        return term
    else:
        raise Exception("[!] This operating system isn't supported by qfetch.")


def memory_current():
    if os_check() == "macOS":
        mem_total = int(subprocess.check_output("sysctl -n hw.memsize", shell=True, text=True).strip()) // (1024 ** 2)
        page_size = int(subprocess.check_output("sysctl -n vm.pagesize", shell=True, text=True).strip())
        vm_stat_output = subprocess.check_output("vm_stat", shell=True, text=True).strip()

        pages_active = int(re.search(r"Pages active:\s+(\d+)", vm_stat_output).group(1))
        pages_wired = int(re.search(r"Pages wired down:\s+(\d+)", vm_stat_output).group(1))
        pages_speculative = int(re.search(r"Pages speculative:\s+(\d+)", vm_stat_output).group(1))

        mem_used = ((pages_active + pages_wired + pages_speculative) * page_size) // (1024 * 1024)
        return f"{mem_used}MiB / {mem_total}MiB"

    elif os_check() == "Linux":
        linux_mem = subprocess.check_output(
            "free -m | awk '/Mem:/ {printf \"%dMiB / %dMiB\\n\", $3, $2}'",
            shell=True,
            text=True,
        ).strip()
        return linux_mem

    else:
        raise Exception("[!] This operating system isn't supported by qfetch.")


def uptime():
    if os_check() in ['macOS', 'Linux']:
        uptime_command = subprocess.check_output("uptime", shell=True, text=True)
        match = re.search(
            r"\d{1,2}:\d{2}\s+up\s+(?:(\d+)\s+day(?:s)?,\s+)?(?:(\d+):(\d+))?(?:(\d+)\s+min(?:ute)?s?)?",
            uptime_command,
        )

        if not match:
            raise Exception("[!] Something went wrong, your uptime might be broken. Please make a Github Issue.")

        days = int(match.group(1) or 0)
        hours = int(match.group(2) or 0) if match.group(2) else 0
        minutes = int(match.group(3) or 0) if match.group(3) else int(match.group(4) or 0)

        def p(val, unit):
            return f"{val} {unit}{'' if val == 1 else 's'}"

        return f"{p(days, 'Day')}, {p(hours, 'Hour')}, {p(minutes, 'Minute')}"
    else:
        raise Exception("[!] This operating system isn't supported by qfetch.")


def disk_usage():
    if os_check() in ["Linux", "macOS"]:
        usage = subprocess.check_output(
            "df -h / | awk 'NR==2 {print $3 \" / \" $2}'",
            shell=True,
            text=True,
        ).strip()
        return usage
    return "N/A"


def print_color_palette():
    lines = []
    for i in range(2):
        line = ""
        for j in range(8):
            color = 30 + j
            if i == 1:
                color += 60
            block = f"\033[{color}m█\033[0m"
            line += block * 3
        lines.append(line)
    return lines


def theme_bar():
    """Return colored side bar"""
    code = theme_color_code()
    return f"\033[{code}m▐\033[0m"


def colored_symbol(symbol):
    """Return symbol colored with the theme"""
    code = theme_color_code()
    return f"\033[{code}m{symbol}\033[0m"


"""Main system information function"""

def sysinfo():
    bar = theme_bar()

    sys_info_default = [
        f"{colored_symbol('') if os_check() == 'macOS' else colored_symbol('')}  {bar}  {platform.platform(terse=True)}",
        f"{colored_symbol('')}  {bar}  {platform.machine()}",
        f"{colored_symbol('')}  {bar}  {package_count()}",
        f"{colored_symbol('')}  {bar}  {shell_ver()}",
        f"{colored_symbol('')}  {bar}  {find_term()}",
        f"{colored_symbol('')}  {bar}  {memory_current()}",
        f"{colored_symbol('')}  {bar}  {disk_usage()}",
        f"{colored_symbol('')}  {bar}  {uptime()}",
        "",
        *print_color_palette(),
    ]

    sys_info_no_nerd_font = [
        f"OS: {platform.platform(terse=True)}",
        f"Arch: {platform.machine()}",
        f"Packages: {package_count()}",
        f"Shell: {shell_ver()}",
        f"Term: {find_term()}",
        f"Memory: {memory_current()}",
        f"Disk: {disk_usage()}",
        f"Uptime: {uptime()}",
        "",
        *print_color_palette(),
    ]

    if args.sys_info == "sys_info_default":
        return sys_info_default
    elif args.sys_info == "sys_info_no_nerd_font":
        return sys_info_no_nerd_font
    else:
        return sys_info_default


"""Main Function"""

def main():
    if os_check() == "Windows":
        print("[!] Oops! qfetch doesn't support Windows yet.")

    art_lines = ascii_art().splitlines()

    width = max(longest_line() + 3, 15)

    for i, stat in enumerate(sysinfo()):
        line = art_lines[i] if i < len(art_lines) else ""
        spacing = ' ' * (width - len(line))
        colored_line = f"\033[{theme_color_code()}m{line}\033[0m"
        final_line = colored_line + spacing + str(stat)
        print(final_line)


if __name__ == "__main__":
    main()

