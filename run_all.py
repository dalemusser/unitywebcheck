import subprocess
import sys
import os
import time


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_all.py <path_to_unityweb_file>")
        print("Example: python run_all.py /path/to/unit4.data.unityweb")
        sys.exit(1)

    unityweb_path = os.path.abspath(sys.argv[1])
    if not os.path.isfile(unityweb_path):
        print(f"Error: file not found: {unityweb_path}")
        sys.exit(1)

    # Create an output folder based on the filename and timestamp
    base_name = os.path.splitext(os.path.splitext(os.path.basename(unityweb_path))[0])[0]
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{base_name}_{timestamp}")
    extracted_dir = os.path.join(output_dir, "extracted")

    os.makedirs(output_dir, exist_ok=True)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    python = sys.executable

    # Step 1: Extract with uwdtool
    print(f"Extracting: {unityweb_path}")
    result = subprocess.run(
        ["uwdtool", "--unpack", "-i", unityweb_path, "-o", extracted_dir],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"Error extracting: {result.stderr}")
        sys.exit(1)
    print(f"Extracted to: {extracted_dir}")

    # Step 2: Run each report and save output
    reports = [
        ("getinfo.txt", [python, os.path.join(script_dir, "getinfo.py"), extracted_dir]),
        ("count_unity_types.txt", [python, os.path.join(script_dir, "count_unity_types.py"), extracted_dir]),
        ("count_audioclip.txt", [python, os.path.join(script_dir, "count_unity_type.py"), extracted_dir, "AudioClip"]),
        ("report_unity_types.txt", [python, os.path.join(script_dir, "report_unity_types.py"), extracted_dir]),
    ]

    # Also save the uwdtool inspect output
    print("Running: uwdtool --inspect")
    result = subprocess.run(
        ["uwdtool", "--inspect", "-i", unityweb_path],
        capture_output=True, text=True,
    )
    inspect_path = os.path.join(output_dir, "uwdtool_inspect.txt")
    with open(inspect_path, "w") as f:
        f.write(result.stdout)
    print(f"  Saved: {inspect_path}")

    for filename, cmd in reports:
        script_name = os.path.basename(cmd[1])
        print(f"Running: {script_name}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        out_path = os.path.join(output_dir, filename)
        with open(out_path, "w") as f:
            f.write(result.stdout)
            if result.stderr:
                f.write("\n--- ERRORS ---\n")
                f.write(result.stderr)
        print(f"  Saved: {out_path}")

    print()
    print(f"All reports saved to: {output_dir}")


if __name__ == "__main__":
    main()
