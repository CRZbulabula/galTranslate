import  os
if __name__ == '__main__':
    from PyInstaller.__main__ import run
    opts=['subtitle.py', '-F']
    run(opts)