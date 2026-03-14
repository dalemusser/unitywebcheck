import UnityPy
import sys
from collections import defaultdict


def mb(n):
    return n / (1024 * 1024)


def safe_str(data, *attrs):
    """Return the first string attribute found on data, or ''."""
    for attr in attrs:
        if hasattr(data, attr):
            v = getattr(data, attr)
            if isinstance(v, str) and v:
                return v
    return ""


def safe_int(data, *attrs):
    """Return the first integer-like attribute found on data, or None."""
    for attr in attrs:
        if hasattr(data, attr):
            try:
                v = int(getattr(data, attr) or 0)
                if v > 0:
                    return v
            except Exception:
                pass
    return None


def get_object_size(obj):
    return getattr(obj, "byte_size", 0)


def get_stream_size(stream):
    if not stream:
        return 0
    for attr in ("size", "m_Size"):
        if hasattr(stream, attr):
            try:
                return int(getattr(stream, attr) or 0)
            except Exception:
                pass
    return 0


def get_details(obj):
    """Read an object and return a dict of interesting details for its type."""
    try:
        data = obj.read()
    except Exception:
        return None

    type_name = obj.type.name
    name = safe_str(data, "name", "m_Name")
    size = get_object_size(obj)
    details = {"name": name, "size": size}

    if type_name == "AudioClip":
        details["channels"] = safe_int(data, "m_Channels")
        details["frequency"] = safe_int(data, "m_Frequency")
        details["bits_per_sample"] = safe_int(data, "m_BitsPerSample")
        details["length_sec"] = None
        if hasattr(data, "m_Length"):
            try:
                length = float(data.m_Length)
                if length > 0:
                    details["length_sec"] = round(length, 2)
            except Exception:
                pass
        for attr in ("m_Resource", "m_AudioData", "audio_data"):
            if hasattr(data, attr):
                val = getattr(data, attr)
                s = get_stream_size(val) if (hasattr(val, "m_Size") or hasattr(val, "size")) else 0
                if s > 0:
                    details["data_size"] = s
                    break

    elif type_name == "Texture2D":
        details["width"] = safe_int(data, "m_Width")
        details["height"] = safe_int(data, "m_Height")
        details["format"] = safe_str(data, "m_TextureFormat")
        if not details["format"]:
            fmt = getattr(data, "m_TextureFormat", None)
            if fmt is not None:
                details["format"] = str(fmt)
        details["mipmaps"] = safe_int(data, "m_MipCount")
        if hasattr(data, "m_StreamData"):
            s = get_stream_size(data.m_StreamData)
            if s > 0:
                details["data_size"] = s

    elif type_name == "Mesh":
        details["vertices"] = safe_int(data, "m_VertexCount")
        details["submeshes"] = None
        if hasattr(data, "m_SubMeshes"):
            try:
                details["submeshes"] = len(data.m_SubMeshes)
            except Exception:
                pass

    elif type_name == "AnimationClip":
        details["length_sec"] = None
        if hasattr(data, "m_Length"):
            try:
                length = float(data.m_Length)
                if length > 0:
                    details["length_sec"] = round(length, 2)
            except Exception:
                pass
        details["sample_rate"] = None
        if hasattr(data, "m_SampleRate"):
            try:
                sr = float(data.m_SampleRate)
                if sr > 0:
                    details["sample_rate"] = round(sr, 1)
            except Exception:
                pass
        details["wrap_mode"] = safe_str(data, "m_WrapMode")
        if not details["wrap_mode"]:
            wm = getattr(data, "m_WrapMode", None)
            if wm is not None:
                details["wrap_mode"] = str(wm)

    elif type_name == "TextAsset":
        script_size = None
        for attr in ("script", "m_Script"):
            if hasattr(data, attr):
                try:
                    raw = getattr(data, attr)
                    if raw is not None:
                        if isinstance(raw, str):
                            script_size = len(raw.encode("utf-8"))
                        else:
                            script_size = len(raw)
                        break
                except Exception:
                    pass
        if script_size is not None:
            details["data_size"] = script_size

    elif type_name == "Shader":
        pass  # name and size are usually what matters

    elif type_name == "Material":
        details["shader"] = ""
        if hasattr(data, "m_Shader"):
            shader_ref = data.m_Shader
            if hasattr(shader_ref, "read"):
                try:
                    shader_data = shader_ref.read()
                    details["shader"] = safe_str(shader_data, "name", "m_Name")
                except Exception:
                    pass

    elif type_name == "Sprite":
        if hasattr(data, "m_Rect"):
            rect = data.m_Rect
            try:
                details["width"] = int(rect.width)
                details["height"] = int(rect.height)
            except Exception:
                pass

    elif type_name == "Font":
        details["font_size"] = safe_int(data, "m_FontSize")

    return details


def format_size(byte_count):
    """Format a byte count as a human-readable string."""
    if byte_count >= 1024 * 1024 * 1024:
        return f"{byte_count / (1024**3):.2f} GB"
    if byte_count >= 1024 * 1024:
        return f"{byte_count / (1024**2):.2f} MB"
    if byte_count >= 1024:
        return f"{byte_count / 1024:.1f} KB"
    return f"{byte_count} B"


def print_summary(type_groups):
    """Print the summary table of all types."""
    summary = []
    for type_name, items in type_groups.items():
        count = len(items)
        total_size = sum(item["size"] for item in items)
        summary.append((type_name, count, total_size))

    summary.sort(key=lambda x: x[2], reverse=True)

    total_objects = sum(s[1] for s in summary)
    total_bytes = sum(s[2] for s in summary)

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"{'Type':<30}  {'Count':>8}  {'Total Size':>14}")
    print("-" * 70)
    for type_name, count, total_size in summary:
        print(f"{type_name:<30}  {count:>8}  {format_size(total_size):>14}")
    print("-" * 70)
    print(f"{'TOTAL':<30}  {total_objects:>8}  {format_size(total_bytes):>14}")
    print()


def print_type_detail(type_name, items):
    """Print a detail section for one asset type."""
    items_sorted = sorted(items, key=lambda x: x["size"], reverse=True)

    print("=" * 70)
    print(f"{type_name}  ({len(items)} objects)")
    print("=" * 70)

    if type_name == "AudioClip":
        print(f"  {'Name':<35} {'Size':>10} {'Ch':>4} {'Rate':>7} {'Length':>8}")
        print(f"  {'-'*35} {'-'*10} {'-'*4} {'-'*7} {'-'*8}")
        for item in items_sorted:
            data_size = format_size(item.get("data_size") or item["size"])
            ch = item.get("channels") or ""
            freq = item.get("frequency") or ""
            if freq:
                freq = f"{freq}Hz"
            length = item.get("length_sec")
            length_str = f"{length}s" if length else ""
            print(f"  {item['name']:<35} {data_size:>10} {str(ch):>4} {str(freq):>7} {length_str:>8}")

    elif type_name == "Texture2D":
        print(f"  {'Name':<30} {'Size':>10} {'Dimensions':>14} {'Format':<16} {'Mips':>4}")
        print(f"  {'-'*30} {'-'*10} {'-'*14} {'-'*16} {'-'*4}")
        for item in items_sorted:
            data_size = format_size(item.get("data_size") or item["size"])
            w = item.get("width") or "?"
            h = item.get("height") or "?"
            dims = f"{w}x{h}"
            fmt = item.get("format") or ""
            mips = item.get("mipmaps") or ""
            print(f"  {item['name']:<30} {data_size:>10} {dims:>14} {str(fmt):<16} {str(mips):>4}")

    elif type_name == "Mesh":
        print(f"  {'Name':<40} {'Size':>10} {'Vertices':>10} {'SubMeshes':>10}")
        print(f"  {'-'*40} {'-'*10} {'-'*10} {'-'*10}")
        for item in items_sorted:
            sz = format_size(item["size"])
            verts = item.get("vertices") or ""
            subs = item.get("submeshes") or ""
            print(f"  {item['name']:<40} {sz:>10} {str(verts):>10} {str(subs):>10}")

    elif type_name == "AnimationClip":
        print(f"  {'Name':<45} {'Size':>10} {'Length':>8} {'SampleRate':>11}")
        print(f"  {'-'*45} {'-'*10} {'-'*8} {'-'*11}")
        for item in items_sorted:
            sz = format_size(item["size"])
            length = item.get("length_sec")
            length_str = f"{length}s" if length else ""
            sr = item.get("sample_rate")
            sr_str = str(sr) if sr else ""
            print(f"  {item['name']:<45} {sz:>10} {length_str:>8} {sr_str:>11}")

    elif type_name == "TextAsset":
        print(f"  {'Name':<50} {'Data Size':>12}")
        print(f"  {'-'*50} {'-'*12}")
        for item in items_sorted:
            data_size = format_size(item.get("data_size") or item["size"])
            print(f"  {item['name']:<50} {data_size:>12}")

    elif type_name == "Material":
        print(f"  {'Name':<40} {'Size':>10} {'Shader':<25}")
        print(f"  {'-'*40} {'-'*10} {'-'*25}")
        for item in items_sorted:
            sz = format_size(item["size"])
            shader = item.get("shader") or ""
            print(f"  {item['name']:<40} {sz:>10} {shader:<25}")

    elif type_name == "Sprite":
        print(f"  {'Name':<40} {'Size':>10} {'Dimensions':>14}")
        print(f"  {'-'*40} {'-'*10} {'-'*14}")
        for item in items_sorted:
            sz = format_size(item["size"])
            w = item.get("width") or "?"
            h = item.get("height") or "?"
            dims = f"{w}x{h}"
            print(f"  {item['name']:<40} {sz:>10} {dims:>14}")

    elif type_name == "Font":
        print(f"  {'Name':<50} {'Size':>10} {'FontSize':>9}")
        print(f"  {'-'*50} {'-'*10} {'-'*9}")
        for item in items_sorted:
            sz = format_size(item["size"])
            fs = item.get("font_size") or ""
            print(f"  {item['name']:<50} {sz:>10} {str(fs):>9}")

    else:
        # Generic: just name and size
        print(f"  {'Name':<55} {'Size':>12}")
        print(f"  {'-'*55} {'-'*12}")
        for item in items_sorted:
            sz = format_size(item["size"])
            print(f"  {item['name']:<55} {sz:>12}")

    print()


def main():
    if len(sys.argv) < 2:
        print("Usage: python report_unity_types.py <folder_or_file>")
        sys.exit(1)

    path = sys.argv[1]
    print(f"Loading: {path}")
    env = UnityPy.load(path)

    type_groups = defaultdict(list)
    read_errors = 0

    for obj in env.objects:
        details = get_details(obj)
        if details is not None:
            type_groups[obj.type.name].append(details)
        else:
            read_errors += 1

    if not type_groups:
        print("No objects found.")
        sys.exit(0)

    print(f"Found {sum(len(v) for v in type_groups.values())} objects across {len(type_groups)} types")
    if read_errors:
        print(f"({read_errors} objects could not be read)")
    print()

    # Print summary first
    print_summary(type_groups)

    # Then print details for each type, ordered by total size descending
    type_order = sorted(
        type_groups.keys(),
        key=lambda t: sum(item["size"] for item in type_groups[t]),
        reverse=True,
    )
    for type_name in type_order:
        print_type_detail(type_name, type_groups[type_name])


if __name__ == "__main__":
    main()
