# -*- coding: utf-8 -*-
import os
import sys

current_path = os.getcwd()
print("current_path:", current_path)
sys.path.append(current_path)

try:
    from be.view import auth
    print("auth import successfully")
except ModuleNotFoundError as e:
    print(f"import failure: {e}")