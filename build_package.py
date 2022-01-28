#!/usr/bin/env python3
# Copyright (c) 2019 Blake Covarrubias
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""Build a zipapp package for k3s-helmchart-generate.py"""

import os
import shutil
import subprocess
import sys
import tempfile
import zipapp


def main():
    """Main function"""

    # Create a temporary directory to build the app
    with tempfile.TemporaryDirectory() as build_dir:
        program_name = "k3s-helmchart-generate.py"

        shutil.copy(src=program_name, dst=os.path.join(build_dir, "__main__.py"))

        pip_install_cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--requirement",
            "requirements.txt",
            "--target",
            build_dir,
        ]
        subprocess.check_call(pip_install_cmd)

        zipapp.create_archive(
            source=build_dir,
            target=f"{program_name}z",
            interpreter="/usr/bin/env python3",
            compressed=True,
        )


if __name__ == "__main__":
    main()
