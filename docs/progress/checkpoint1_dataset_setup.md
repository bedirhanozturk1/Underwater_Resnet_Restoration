# Checkpoint 1: Dataset And Project Setup

Status: completed

## Completed

- Repository skeleton created.
- Implementation plan added.
- Dataset pair verification utility implemented.
- Checkpoint 1 runnable verification script implemented.
- Reproducible train/validation/test split files generated locally.
- Pair sample visualization generated locally.

## Tests / Checks

- `tests/test_dataset_pairs.py` passed.

## Dataset Verification Result

```text
Clear images: 3672
Turbid images: 3672
Matched pairs: 3672
Missing clear images: 0
Missing turbid images: 0
Train split: 2937
Validation split: 367
Test split: 368
```

## Expected Evidence

- `results/checkpoint1/dataset_report.txt`
- `results/checkpoint1/dataset_pair_samples.png`

These files are generated locally and ignored by Git because result files should not be committed to the repository.

## Next Step

Start Checkpoint 2: implement the paired PyTorch DataLoader and forward diffusion sanity visualization.
