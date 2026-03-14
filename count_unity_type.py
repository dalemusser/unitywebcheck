import UnityPy
import sys
from collections import Counter


def main():
    if len(sys.argv) < 3:
        print("Usage: python count_unity_type.py <folder_or_file> <type_name>")
        print("Example: python count_unity_type.py extracted/ AudioClip")
        sys.exit(1)

    env = UnityPy.load(sys.argv[1])
    type_name = sys.argv[2]
    counts = Counter()

    for obj in env.objects:
        counts[obj.type.name] += 1

    print(f"{type_name}: {counts[type_name]}")


if __name__ == "__main__":
    main()
