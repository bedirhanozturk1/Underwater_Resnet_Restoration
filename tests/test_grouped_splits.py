from pathlib import Path

from src.data.prepare_pairs import remove_exact_pair_duplicates, split_contiguous_source_groups


def test_contiguous_source_groups_are_not_split() -> None:
    filenames = [f"{index}.jpg" for index in range(48)]

    splits, source_groups = split_contiguous_source_groups(filenames, group_size=4)

    groups_by_split = {
        name: {source_groups[filename] for filename in selected}
        for name, selected in splits.items()
    }
    assert not (groups_by_split["train"] & groups_by_split["val"])
    assert not (groups_by_split["train"] & groups_by_split["test"])
    assert not (groups_by_split["val"] & groups_by_split["test"])
    assert sorted(splits["train"] + splits["val"] + splits["test"], key=lambda name: int(Path(name).stem)) == filenames


def test_exact_pair_deduplication_prefers_test(tmp_path: Path) -> None:
    pair_paths = {}
    for filename, clear_data, turbid_data in (
        ("0.jpg", b"clear", b"turbid"),
        ("1.jpg", b"clear", b"turbid"),
        ("2.jpg", b"other-clear", b"other-turbid"),
    ):
        clear_path = tmp_path / f"clear_{filename}"
        turbid_path = tmp_path / f"turbid_{filename}"
        clear_path.write_bytes(clear_data)
        turbid_path.write_bytes(turbid_data)
        pair_paths[filename] = (clear_path, turbid_path)

    cleaned, removed = remove_exact_pair_duplicates(
        {"train": ["0.jpg", "2.jpg"], "val": [], "test": ["1.jpg"]},
        pair_paths,
    )

    assert cleaned == {"train": ["2.jpg"], "val": [], "test": ["1.jpg"]}
    assert removed == {"0.jpg": "exact duplicate of 1.jpg retained in test"}
