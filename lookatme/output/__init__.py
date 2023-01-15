"""
lookatme output formats
"""


from typing import Any, Dict, List, Type


from lookatme.output.base import BaseOutputFormat
import lookatme.config as config
from lookatme.pres import Presentation


import lookatme.output.base
import lookatme.output.html
import lookatme.output.html_raw
import lookatme.output.gif


def print_output_options_help():
    print("Available options for output formats:\n")

    for format_name, format_cls in lookatme.output.base.DEFINED_TYPES.items():
        for option_name, option_val in format_cls.DEFAULT_OPTIONS.items():
            if isinstance(option_val, list):
                option_val_str = ",".join(str(x) for x in option_val)
            elif isinstance(option_val, str):
                option_val_str = repr(option_val)
            else:
                option_val_str = str(option_val)

            print(f"    {format_name}.{option_name} = {option_val_str}")


def _get_default_val(option_key) -> Any:
    from lookatme.output.base import DEFINED_TYPES

    if "." not in option_key:
        raise ValueError("Key must have the form <format_name>.<option_name>")

    format_name, option_name = option_key.split(".", 1)
    format_cls = DEFINED_TYPES.get(format_name, None)
    if format_cls is None:
        raise ValueError("Key {!r} must be one of the valid output names:  {}".format(
            format_name,
            ", ".join(DEFINED_TYPES.keys())
        ))
    
    if option_name not in format_cls.DEFAULT_OPTIONS:
        raise ValueError("Format {!r} option {!r} must be one of the valid format options: {}".format(
            format_name,
            option_name,
            ", ".join(format_cls.DEFAULT_OPTIONS.keys())
        ))

    return format_cls.DEFAULT_OPTIONS[option_name]


def _convert_to_matching_type(to_convert: Any, base_type: Any):
    if isinstance(base_type, int):
        return int(to_convert)
    elif isinstance(base_type, bool):
        if isinstance(to_convert, str):
            to_convert = to_convert.lower()
            if to_convert == "true":
                return True
            elif to_convert == "False":
                return False
            else:
                raise ValueError(
                    f"Option value {to_convert!r} could not be converted to a bool"
                )
        return int(to_convert)
    elif isinstance(base_type, str):
        return str(to_convert)
    elif isinstance(base_type, float):
        return float(to_convert)
    elif isinstance(base_type, list):
        if not isinstance(to_convert, str):
            raise ValueError("List option types should be strings")
        return [x.strip() for x in to_convert.split(",")]
    else:
        raise RuntimeError("Base output option type {!r} is not supported yet".format(
            type(base_type),
        ))


def get_format(format_name: str) -> Type["BaseOutputFormat"]:
    from lookatme.output.base import DEFINED_TYPES
    return DEFINED_TYPES[format_name]


def get_all_formats() -> List[str]:
    from lookatme.output.base import DEFINED_TYPES
    return list(sorted(DEFINED_TYPES.keys()))


def get_all_options() -> List[str]:
    from lookatme.output.base import DEFINED_TYPES
    res = []
    for output_type, output_cls in DEFINED_TYPES.items():
        for option in output_cls.DEFAULT_OPTIONS.keys():
            res.append(f"{output_type}.{option}")
    return res


def parse_options(option_strings: List[str]) -> Dict[str, Any]:
    res = {}

    for option in option_strings:
        parts = option.split("=", 1)
        key = parts[0]
        val = True
        if len(parts) > 1:
            val = parts[1]

        try:
            default_val = _get_default_val(key)
        except ValueError as e:
            config.get_log().warn("Output format option error: {}".format(e))
            continue

        val = _convert_to_matching_type(val, default_val)
        res[key] = val

    return res


def output_pres(pres: Presentation, path: str, format: str, options: Dict[str, Any]):
    formatter = get_format(format)()
    formatter.format_pres(pres, path, options)
