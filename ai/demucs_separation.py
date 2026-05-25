from pathlib import Path
import subprocess


def separate_instruments(audio_path: Path, output_dir: Path) -> Path:
    """Run Demucs when installed and return the output directory.

    Demucs is intentionally invoked as a subprocess because its model downloads
    are large and should be controlled outside the request thread in production.
    """

    output_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["python", "-m", "demucs", "-o", str(output_dir), str(audio_path)],
        check=True,
    )
    return output_dir
