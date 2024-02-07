# Tests

## Prerequisites

### Create Python virtual environment

Check the instructions on [Creation of virtual environments](https://docs.python.org/3/library/venv.html) page as the steps differ, depending your operating system.

Linux:

```
python -m venv .venv
```

It can be created. and then activated automatically, in VS Code. More info on [Python environments in VS Code](https://code.visualstudio.com/docs/python/environments#_creating-environments) page.

### Install modules

Linux:

```
pip install Kodistubs
pip install parameterized
pip install watchdog
```

Windows:

```
python -m pip install Kodistubs
python -m pip install parameterized
python -m pip install watchdog
```

## How to run tests

### VS Code

One way to run tests is in with VS Code. The tests should be automatically discovered and shown the Test Explorer view. They can be run from that view as well as debugged. More info on [Python testing in Visual Studio Code](https://code.visualstudio.com/docs/python/testing#_configure-tests) page.

### Terminal

The tests can also be run from the terminal.

Linux and Windows:

```
python -m unittest
```
