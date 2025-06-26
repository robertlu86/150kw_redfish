import subprocess
from typing import Dict, List

class SystemCommandUtil:
    @classmethod
    def exec(cls, linux_cmd: str) -> Dict[str, List[str]]:
        """
        執行Linux命令
        """
        process = subprocess.Popen(linux_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        stdout = stdout.decode("utf-8")
        stderr = stderr.decode("utf-8")

        return {
            "command": linux_cmd,
            "stdout_lines": stdout.splitlines(),
            "stderr_lines": stderr.splitlines()
        }




