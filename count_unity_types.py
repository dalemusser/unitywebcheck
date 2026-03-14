import UnityPy
import sys
from collections import Counter, defaultdict


def format_size(byte_count):
    if byte_count >= 1024 * 1024 * 1024:
        return f"{byte_count / (1024**3):.2f} GB"
    if byte_count >= 1024 * 1024:
        return f"{byte_count / (1024**2):.2f} MB"
    if byte_count >= 1024:
        return f"{byte_count / 1024:.1f} KB"
    return f"{byte_count} B"


def main():
    if len(sys.argv) < 2:
        print("Usage: python count_unity_types.py <folder_or_file>")
        sys.exit(1)

    env = UnityPy.load(sys.argv[1])
    counts = Counter()
    sizes = defaultdict(int)

    for obj in env.objects:
        counts[obj.type.name] += 1
        sizes[obj.type.name] += getattr(obj, "byte_size", 0)

    if not counts:
        print("No objects found.")
        sys.exit(0)

    total_count = sum(counts.values())
    total_size = sum(sizes.values())
    name_width = max(len(name) for name in counts)

    print(f"{'Type':<{name_width}}  {'Count':>8}  {'Total Size':>12}")
    print(f"{'-' * name_width}  {'-' * 8}  {'-' * 12}")
    for name, count in counts.most_common():
        print(f"{name:<{name_width}}  {count:>8}  {format_size(sizes[name]):>12}")
    print(f"{'-' * name_width}  {'-' * 8}  {'-' * 12}")
    print(f"{'TOTAL':<{name_width}}  {total_count:>8}  {format_size(total_size):>12}")


if __name__ == "__main__":
    main()
