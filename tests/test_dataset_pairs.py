from pathlib import Path

from PIL import Image

from src.data.prepare_pairs import collect_pairs, split_pairs, write_splits


def test_collect_pairs_reports_matches_and_missing_files(tmp_path: Path) -> None:
    clear_dir = tmp_path / "clear"
    turbid_dir = tmp_path / "turbid"
    clear_dir.mkdir()
    turbid_dir.mkdir()

    _save_image(clear_dir / "1.jpg")
    _save_image(clear_dir / "2.jpg")
    _save_image(turbid_dir / "1.jpg")
    _save_image(turbid_dir / "3.jpg")

    pairs, report = collect_pairs(clear_dir, turbid_dir)

    assert [pair[0] for pair in pairs] == ["1.jpg"]
    assert report.clear_count == 2
    assert report.turbid_count == 2
    assert report.matched_count == 1
    assert report.missing_clear == ("3.jpg",)
    assert report.missing_turbid == ("2.jpg",)


def test_split_pairs_is_reproducible_and_complete(tmp_path: Path) -> None:
    filenames = [f"{idx}.jpg" for idx in range(20)]

    first = split_pairs(filenames, seed=7)
    second = split_pairs(filenames, seed=7)

    assert first == second
    assert len(first["train"]) == 16
    assert len(first["val"]) == 2
    assert len(first["test"]) == 2
    assert sorted(first["train"] + first["val"] + first["test"]) == sorted(filenames)

    write_splits(first, tmp_path / "splits")
    assert (tmp_path / "splits" / "train.txt").exists()
    assert (tmp_path / "splits" / "val.txt").exists()
    assert (tmp_path / "splits" / "test.txt").exists()


def _save_image(path: Path) -> None:
    Image.new("RGB", (8, 8), (128, 128, 128)).save(path)
