import UnityPy
import sys
import os


def mb(n):
    return n / (1024 * 1024)


def safe_name(data):
    for attr in ("name", "m_Name"):
        if hasattr(data, attr):
            v = getattr(data, attr)
            if isinstance(v, str):
                return v
    return ""


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


def get_texture_size(data, obj):
    # Prefer external/streamed payload if present
    if hasattr(data, "m_StreamData"):
        s = get_stream_size(data.m_StreamData)
        if s > 0:
            return s, "stream"

    # Fallbacks for inline image data
    for attr in ("image_data", "m_ImageData"):
        if hasattr(data, attr):
            try:
                raw = getattr(data, attr)
                if raw:
                    return len(raw), "inline"
            except Exception:
                pass

    return getattr(obj, "byte_size", 0), "object"


def get_audioclip_size(data, obj):
    for attr in ("m_Resource", "m_AudioData", "audio_data"):
        if hasattr(data, attr):
            val = getattr(data, attr)
            if hasattr(val, "m_Size") or hasattr(val, "size"):
                s = get_stream_size(val)
                if s > 0:
                    return s, attr
            try:
                if val:
                    return len(val), attr
            except Exception:
                pass

    if hasattr(data, "m_Stream"):
        s = get_stream_size(data.m_Stream)
        if s > 0:
            return s, "m_Stream"

    return getattr(obj, "byte_size", 0), "object"


def get_textasset_size(data, obj):
    for attr in ("script", "m_Script"):
        if hasattr(data, attr):
            try:
                raw = getattr(data, attr)
                if raw is not None:
                    if isinstance(raw, str):
                        return len(raw.encode("utf-8")), attr
                    return len(raw), attr
            except Exception:
                pass
    return getattr(obj, "byte_size", 0), "object"


def get_mesh_size(data, obj):
    total = 0

    if hasattr(data, "m_StreamData"):
        total += get_stream_size(data.m_StreamData)

    for attr in (
        "m_VertexData",
        "m_IndexBuffer",
        "m_BakedConvexCollisionMesh",
        "m_BakedTriangleCollisionMesh",
    ):
        if hasattr(data, attr):
            try:
                val = getattr(data, attr)
                if hasattr(val, "__len__"):
                    total += len(val)
            except Exception:
                pass

    if total > 0:
        return total, "mesh-data"

    return getattr(obj, "byte_size", 0), "object"


def get_generic_size(data, obj):
    return getattr(obj, "byte_size", 0), "object"


def classify_and_size(obj):
    try:
        data = obj.read()
    except Exception:
        return None

    t = obj.type.name
    name = safe_name(data)

    if t == "Texture2D":
        size, source = get_texture_size(data, obj)
    elif t == "AudioClip":
        size, source = get_audioclip_size(data, obj)
    elif t == "TextAsset":
        size, source = get_textasset_size(data, obj)
    elif t == "Mesh":
        size, source = get_mesh_size(data, obj)
    else:
        size, source = get_generic_size(data, obj)

    return {
        "type": t,
        "name": name,
        "size": int(size or 0),
        "source": source,
        "path_id": getattr(obj, "path_id", 0),
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python getinfo.py <folder_or_file>")
        sys.exit(1)

    env = UnityPy.load(sys.argv[1])
    rows = []

    for obj in env.objects:
        row = classify_and_size(obj)
        if row:
            rows.append(row)

    rows.sort(key=lambda r: r["size"], reverse=True)

    print(f"{'MB':>10}  {'Type':20}  {'Source':10}  Name")
    print("-" * 90)
    for r in rows:
        print(f"{mb(r['size']):10.2f}  {r['type']:20}  {r['source']:10}  {r['name']}")


if __name__ == "__main__":
    main()
