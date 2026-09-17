"""Run every tests/test_*.py without needing pytest: python3 run_tests.py"""
import importlib, os, sys, traceback
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
failed = total = 0
for fname in sorted(os.listdir(os.path.join(ROOT, "tests"))):
    if not (fname.startswith("test_") and fname.endswith(".py")):
        continue
    mod = importlib.import_module("tests." + fname[:-3])
    for name in dir(mod):
        if name.startswith("test_") and callable(getattr(mod, name)):
            total += 1
            try:
                getattr(mod, name)()
            except Exception:
                failed += 1
                print(f"FAIL  {fname}::{name}")
                traceback.print_exc()
print(f"{total - failed}/{total} tests passed")
sys.exit(1 if failed else 0)
