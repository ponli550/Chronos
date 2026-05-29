import io
import os
import sys
import base64
import importlib.util
import inspect
import time
import runpy
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .registry import SIMULATIONS_DIR, scan_labs

MISSING_DEP_HINTS = {
    "qiskit": "pip install qiskit qiskit-aer",
    "qiskit_aer": "pip install qiskit-aer",
    "qutip": "pip install qutip",
    "matplotlib": "pip install matplotlib",
    "scipy": "pip install scipy",
    "skimage": "pip install scikit-image",
    "torch": "pip install torch",
    "tensorflow": "pip install tensorflow",
}

COMMON_DEPS = ["numpy", "matplotlib", "scipy", "qiskit", "qutip", "skimage", "torch"]


def check_dependencies() -> dict:
    available = {}
    for dep in COMMON_DEPS:
        try:
            mod = importlib.import_module(dep)
            ver = getattr(mod, "__version__", None)
            available[dep] = ver or True
        except ImportError:
            available[dep] = False
    return available


def _get_spec_and_mod(lab_id: str):
    path = SIMULATIONS_DIR / f"{lab_id}.py"
    if not path.exists():
        return None, None, f"Lab {lab_id} not found"

    spec = importlib.util.spec_from_file_location(lab_id, str(path))
    if spec is None or spec.loader is None:
        return None, None, "Failed to load module"

    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    # chdir so that relative imports like "from simulations.qho import ..."
    # resolve correctly when the script uses the simulations package.
    old_cwd_mod = os.getcwd()
    os.chdir(str(SIMULATIONS_DIR.parent))
    try:
        spec.loader.exec_module(mod)
    except ImportError as e:
        hint = MISSING_DEP_HINTS.get(e.name, f"pip install {e.name}")
        return None, None, f"Missing dependency: {e.name}. Try: {hint}"
    except Exception as e:
        return None, None, f"Module load error: {e}"
    finally:
        os.chdir(old_cwd_mod)

    labs = scan_labs()
    lab = next((l for l in labs if l.id == lab_id), None)
    if not lab or not lab.main_function:
        return None, None, "No main function found"

    func = getattr(mod, lab.main_function, None)
    if func is None:
        return None, None, f"Function {lab.main_function} not found"

    return spec, func, None


def _infer_type(param, default):
    annotation = param.annotation if param.annotation is not inspect.Parameter.empty else None

    if annotation is not None:
        if annotation is float:
            return "float"
        if annotation is int:
            return "int"
        if annotation is bool:
            return "bool"
        if annotation is str:
            return "str"
        if annotation is list:
            return "list"
        return "number"

    if isinstance(default, bool):
        return "bool"
    if isinstance(default, int):
        return "int"
    if isinstance(default, float):
        return "float"
    if isinstance(default, str):
        return "str"
    return "number"


def _cast_value(val, param):
    annotation = param.annotation if param.annotation is not inspect.Parameter.empty else None

    if annotation is int or (annotation is None and isinstance(val, bool)):
        return int(val)

    if annotation is bool:
        return bool(val)

    if annotation is float:
        return float(val)

    if annotation is str:
        return str(val)

    # For unannotated params, try int first (common for N, depth, steps, etc.)
    # then float, then fall back to raw value.
    if isinstance(val, float):
        if val == int(val):
            return int(val)
        return val

    if isinstance(val, str):
        for caster in (int, float):
            try:
                return caster(val)
            except (ValueError, TypeError):
                continue
        return val

    return val


def get_sim_params(lab_id: str) -> list[dict] | None:
    _, func, err = _get_spec_and_mod(lab_id)
    if err:
        return None

    try:
        sig = inspect.signature(func)
    except (ValueError, TypeError):
        return []

    params = []
    for name, param in sig.parameters.items():
        if name == "self":
            continue
        default = param.default if param.default is not inspect.Parameter.empty else None
        params.append({
            "name": name,
            "type": _infer_type(param, default),
            "default": default,
            "required": default is None,
        })

    return params


def _find_plot_functions(mod):
    return [(name, obj) for name, obj in inspect.getmembers(mod, inspect.isfunction)
            if name.startswith("plot_") or name.startswith("animate_")]


def _call_target_function(func, result, resolved):
    try:
        sig = inspect.signature(func)
        kwargs = {}
        for pname in list(sig.parameters.keys()):
            if pname in resolved:
                kwargs[pname] = resolved[pname]
        if isinstance(result, tuple):
            func(*result, **kwargs)
        else:
            func(result, **kwargs)
    except Exception:
        pass


def _call_plot_functions(mod, result, resolved):
    for _, plot_func in _find_plot_functions(mod):
        _call_target_function(plot_func, result, resolved)


def _find_gif(lab_id: str) -> str | None:
    import glob
    dirs = [str(SIMULATIONS_DIR), str(SIMULATIONS_DIR.parent / "simulations")]
    for d in dirs:
        matches = glob.glob(os.path.join(d, "*.gif"))
        # prefer exact match first, then partial match
        for p in matches:
            if os.path.splitext(os.path.basename(p))[0] == lab_id:
                return p
        for p in matches:
            if lab_id in os.path.basename(p):
                return p
        if matches:
            return matches[0]
    return None


def _gif_first_frame_as_base64(lab_id: str) -> str | None:
    """If an animated simulation saved a .gif, extract the first frame as base64 PNG."""
    try:
        from PIL import Image
        gif_path = _find_gif(lab_id)
        if not gif_path:
            return None
        with Image.open(gif_path) as img:
            buf = io.BytesIO()
            img.seek(0)
            img.save(buf, format="PNG")
            return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return None


def run_simulation(lab_id: str, user_params: dict) -> dict:
    t0 = time.time()
    spec, func, err = _get_spec_and_mod(lab_id)
    if err:
        return {"error": err}

    sig = inspect.signature(func)
    resolved = {}
    for name, param in sig.parameters.items():
        if name == "self":
            continue
        if name in user_params:
            resolved[name] = _cast_value(user_params[name], param)
        elif param.default is not inspect.Parameter.empty:
            resolved[name] = param.default
        else:
            return {"error": f"Missing required parameter: {name}"}

    try:
        plt.close("all")
        old_cwd = os.getcwd()
        os.chdir(str(SIMULATIONS_DIR.parent))

        result = func(**resolved)
        mod = sys.modules[func.__module__]
        _call_plot_functions(mod, result, resolved)

        os.chdir(old_cwd)

        def _capture_figs():
            buf = io.BytesIO()
            if plt.get_fignums():
                plt.savefig(buf, format="png", dpi=120, bbox_inches="tight")
                plt.close("all")
                buf.seek(0)
                return base64.b64encode(buf.read()).decode()
            return ""

        img_b64 = _capture_figs()
        if not img_b64:
            img_b64 = _gif_first_frame_as_base64(lab_id) or ""

        # Fallback: run script as __main__ for sims with no importable
        # functions (helium_atom) or param-name mismatches (complex_atoms).
        if not img_b64:
            old_path = list(sys.path)
            try:
                runpy.run_path(str(SIMULATIONS_DIR / f"{lab_id}.py"),
                               run_name="__main__")
            except Exception:
                pass
            sys.path[:] = old_path
            img_b64 = _capture_figs()
            if not img_b64:
                img_b64 = _gif_first_frame_as_base64(lab_id) or ""

        elapsed = time.time() - t0

        output: dict = {"compute_time_s": round(elapsed, 3)}
        if img_b64:
            output["image"] = img_b64
        if result is not None:
            if isinstance(result, (str, int, float)):
                output["text"] = str(result)
            elif isinstance(result, dict):
                txt = {}
                for k, v in result.items():
                    try:
                        txt[k] = str(v)[:200]
                    except Exception:
                        txt[k] = str(type(v).__name__)
                output["data"] = txt
            elif isinstance(result, list):
                output["text"] = f"list[{len(result)} items]"
            else:
                try:
                    output["text"] = str(result)[:500]
                except Exception:
                    output["text"] = str(type(result).__name__)

        return output

    except Exception as e:
        os.chdir(old_cwd)
        plt.close("all")
        return {"error": f"Simulation error: {e}"}
