from datetime import datetime

def take_screenshot(driver, step_name, *, product=None, test_case=None, extra_subfolder=None):
    """Compatibility wrapper. Uses organized saving with optional context."""
    return save_screenshot_organized(
        driver,
        step_name,
        product=product,
        test_case=test_case,
        extra_subfolder=extra_subfolder,
    )
# Additional helpers and organized screenshot saving
import re
import inspect
from pathlib import Path
from typing import Optional
from tests import test_config as C


def _sanitize(name: str) -> str:
    # Keep alphanum, dash, underscore, and dot; replace others with underscore
    name = name.strip()
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name)[:255]


def _strip_png(name: str) -> str:
    return name[:-4] if name.lower().endswith(".png") else name


def _detect_context_from_stack():
    """Return (product, test_case, module_base) inferred from call stack.
    Preference order:
    1) A frame inside omsd_automation/tests where the function starts with 'test_'.
    2) Any frame inside omsd_automation/tests (use its module name).
    Falls back to None values if nothing useful is found. Skips this utility module.
    """
    product = None
    test_case = None
    module_base = None

    try:
        tests_dir = (C.TEST_BASE_DIR / "tests").resolve()  # e.g., omsd_automation/tests
    except Exception:
        tests_dir = None

    current_util = Path(__file__).resolve()
    frames = inspect.stack()

    def _compute_from_module(mb: str, func: str):
        _product = None
        _test_case = None
        # product from module like test_ESG_410_...
        parts = mb.split("_")
        if len(parts) >= 3 and parts[0] == "test" and parts[1].isalpha() and parts[2].isdigit():
            _product = f"{parts[1]}-{parts[2]}"
        # test case from function first, then module name
        if func.startswith("test_"):
            _test_case = func[len("test_"):]
        elif mb.startswith("test_"):
            _test_case = mb[len("test_"):]
        else:
            _test_case = mb
        return _product, _test_case

    # Pass 1: prefer test function frames under tests dir
    if tests_dir:
        for fi in frames:
            try:
                fpath = Path(fi.filename).resolve()
                if fpath == current_util:
                    continue  # skip this utility itself
                if str(fpath).startswith(str(tests_dir)):
                    func = inspect.getframeinfo(fi.frame).function
                    if func.startswith("test_"):
                        mb = fpath.stem
                        module_base = mb
                        p, tc = _compute_from_module(mb, func)
                        product = p or product
                        test_case = tc or test_case
                        return product, test_case, module_base
            except Exception:
                continue

    # Pass 2: any frame under tests dir
    if tests_dir:
        for fi in frames:
            try:
                fpath = Path(fi.filename).resolve()
                if fpath == current_util:
                    continue
                if str(fpath).startswith(str(tests_dir)):
                    func = inspect.getframeinfo(fi.frame).function
                    mb = fpath.stem
                    module_base = mb
                    p, tc = _compute_from_module(mb, func)
                    product = p or product
                    test_case = tc or test_case
                    return product, test_case, module_base
            except Exception:
                continue

    return product, test_case, module_base


def save_screenshot_organized(driver, step_name: str, *, product: Optional[str] = None,
                               test_case: Optional[str] = None, extra_subfolder: Optional[str] = None) -> str:
    """
    Save screenshot under omsd_automation/screenshots organized by product and test case.
    Path layout:
      <SCREENSHOTS_DIR>/<product>/<test_case>/<product>_<test_case>_<step>_<timestamp>.png
    If product or test_case are not given, attempt to infer from the test call stack/module name.
    Returns absolute path as str.
    """
    # Normalize names
    step = _sanitize(_strip_png(str(step_name)))

    # Auto-detect if not provided
    auto_product, auto_case, module_base = _detect_context_from_stack()
    product = _sanitize(product) if product else ( _sanitize(auto_product) if auto_product else None )
    test_case = _sanitize(test_case) if test_case else ( _sanitize(auto_case) if auto_case else None )

    # Build folder path
    base_dir: Path = C.SCREENSHOTS_DIR
    parts = []
    if product:
        parts.append(product)
    if test_case:
        parts.append(test_case)
    if extra_subfolder:
        parts.append(_sanitize(extra_subfolder))

    folder_path = base_dir.joinpath(*parts) if parts else base_dir
    folder_path.mkdir(parents=True, exist_ok=True)

    # Filename with product/test_case prefixes if available
    #timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix_bits = [b for b in [product, test_case] if b]
    prefix = "_".join(prefix_bits) + ("_" if prefix_bits else "")
    filename = f"{prefix}{step}.png"

    full_path = folder_path / filename
    driver.save_screenshot(str(full_path))
    print(f"Screenshot saved: {full_path}")
    return str(full_path)
