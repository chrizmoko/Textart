"""
File: textart/__main__.py

The package entry point of the program.
"""


import sys
import os.path


# Path resolution to allow package modules to be referenced as "textart.*"
package_path = os.path.dirname(__file__)
path, _ = os.path.split(package_path)
if path not in sys.path:
    sys.path.insert(0, path)


from textart.gui import main


if __name__ == '__main__':
    # TODO: Consider implementing a command line entry
    main()