import subprocess
import re

from acquisition.abstract import Parameters
from checks.abstract import Check, CheckResult
from shared.environment import RECOVERY


class RunningAppsCheck(Check):
    name = "Running apps check"

    def active(self) -> bool:
        return not RECOVERY

    def execute(self, params: Parameters) -> CheckResult:
        result = CheckResult(passed=True)
        command = ["ps", "-x"]

        try:
            output = subprocess.check_output(
                command, stderr=subprocess.STDOUT, universal_newlines=True
            ).strip()
        except Exception:
            result.passed = False
            result.write(f"Could not verify running apps")
            return result

        app_names = set[str]()
        app_path_pattern = re.compile(
            r"/(Applications|System/Applications)/([^/]+)\.(app|localized.[^/]+)/Contents/MacOS/"
        )

        for line in output.splitlines()[1:]:
            line = re.sub(r"\s+", " ", line.strip())
            columns = line.split(" ", 4)
            if len(columns) < 4:
                continue
            cmd = columns[3]

            match = app_path_pattern.match(cmd)
            if match:
                app_names.add(match.group(2))

        if app_names:
            sorted_names = sorted(app_names, key=lambda x: x.lower())
            result.passed = False
            result.write(
                "Some apps are currently running and they may interfere with the acquisition:"
            )
            result.write(", ".join(sorted_names))
        else:
            result.write("No apps are currently running")

        return result
