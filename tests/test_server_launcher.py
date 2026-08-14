import os
import subprocess
import sys
import unittest


@unittest.skipUnless(os.name == "nt", "Windows Job Objects are Windows-only")
class WindowsLauncherTests(unittest.TestCase):
    def test_launcher_exposes_a_server_entrypoint(self):
        from scripts.run_server import run_server

        self.assertTrue(callable(run_server))

    def test_closing_job_terminates_assigned_child_process(self):
        from scripts.run_server import WindowsKillOnCloseJob

        child = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(60)"],
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        job = WindowsKillOnCloseJob()
        try:
            job.assign(child)
            job.close()
            child.wait(timeout=5)
            self.assertIsNotNone(child.returncode)
        finally:
            job.close()
            if child.poll() is None:
                child.kill()
                child.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()
