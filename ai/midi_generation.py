from pathlib import Path


def write_basic_midi_placeholder(notes: list[dict], output_path: Path) -> Path:
    """Create a placeholder MIDI artifact for the MVP export flow.

    A production implementation should replace this with Basic Pitch output or
    a real MIDI writer such as pretty-midi once export UX is added.
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(str(notes), encoding="utf-8")
    return output_path
