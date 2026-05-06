#  AI-Powered Sentiment Analysis
## Comparative Study of Transformer-Based Models on Customer Review Data

---

## Project Overview

This project fine-tunes and compares three transformer-based models — **BERT**, **DistilBERT**, and **RoBERTa** — for binary sentiment classification on the IMDb movie review dataset. The goal is to evaluate trade-offs between accuracy, F1 score, precision, recall, and model size (parameter efficiency).

---

## Project Structure

```
├── Sentiment_Analysis_Transformer_Comparison_fixed.ipynb   ← Main notebook (run top to bottom)
├── README.md                                               ← This file
└── outputs/ (generated at runtime)
    ├── eda_plots.png
    ├── model_comparison.png
    ├── confusion_matrices.png
    ├── model_size.png
    └── model_comparison_results.csv
```

---

## Requirements

- Python 3.8+
- Google Colab with **T4 GPU** runtime (strongly recommended)
- Internet access (for downloading models and dataset from HuggingFace)

### Python Libraries

```
transformers
datasets
scikit-learn
seaborn
matplotlib
torch
torchvision
accelerate
pandas
numpy
```

---

## How to Run

### Option A — Google Colab (Recommended)

1. Open [Google Colab](https://colab.research.google.com)
2. Go to **Runtime > Change runtime type > T4 GPU**
3. Upload `Sentiment_Analysis_Transformer_Comparison_fixed.ipynb`
4. Run all cells **top to bottom**

> ⚠️ With `SUBSAMPLE = True` (default), total runtime is approximately **30–45 minutes** on T4 GPU.  
> For full dataset training, set `SUBSAMPLE = False` — expect **3–5 hours**.

### Option B — Local Machine

```bash
# 1. Install dependencies
pip install transformers datasets scikit-learn seaborn matplotlib torch torchvision accelerate

# 2. Launch Jupyter and open the notebook
jupyter notebook Sentiment_Analysis_Transformer_Comparison_fixed.ipynb
```

---

## Notebook Cell Structure

| Description |
|-------------------|
| Cell 1 | Install dependencies |
| Cell 2 | Imports |
| Cell 3 | Set random seeds for reproducibility (seed = 42) |
| Cell 4 | Load IMDb dataset from HuggingFace |
| Cell 5 | EDA — class distribution & review length histogram |
| Cell 6 | Preprocessing & subsampling configuration |
| Cell 7 | Custom `SentimentDataset` class (PyTorch) |
| Cell 8 | `compute_metrics` function (accuracy, F1, precision, recall) |
| Cell 9 | Reusable `train_model` function |
| Cell 10 | Train all three models sequentially |
| Cell 11 | Results summary table (sorted by F1) |
| Cell 12 | Bar chart — performance comparison across all metrics |
| Cell 13 | Confusion matrices for all three models |
| Cell 14 | Per-class classification report |
| Cell 15 | Inference demo — predict sentiment on custom text |
| Cell 16 | Save results to CSV |

---

## Configuration

In **Cell 6**, you can control the dataset size:

| Variable | Default | Description |
|----------|---------|-------------|
| `SUBSAMPLE` | `True` | Enable subsampling for faster runs |
| `TRAIN_SIZE` | `2000` | Number of training samples |
| `VAL_SIZE` | `500` | Number of validation samples |
| `TEST_SIZE` | `500` | Number of test samples |

In **Cell 9** (`train_model` function), you can adjust:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_length` | `256` | Max token length per input |
| `batch_size` | `16` | Training and evaluation batch size |
| `epochs` | `3` | Number of training epochs |
| `lr` | `2e-5` | Learning rate |

Additional training settings (configured inside `TrainingArguments`):
- `warmup_ratio = 0.1`
- `weight_decay = 0.01`
- `eval_strategy = "epoch"`
- `load_best_model_at_end = True` (based on F1)
- `fp16 = True` (when GPU is available)
- Early stopping with `patience = 2`

---

## Models Compared

| Model | HuggingFace Checkpoint | Parameters | Architecture |
|-------|----------------------|------------|--------------|
| BERT | `bert-base-uncased` | ~110M | Bidirectional Transformer |
| DistilBERT | `distilbert-base-uncased` | ~66M | Knowledge-distilled BERT |
| RoBERTa | `roberta-base` | ~125M | Robustly Optimised BERT |

All models use `AutoModelForSequenceClassification` with `num_labels=2`, fine-tuned from HuggingFace pretrained checkpoints.

---

## Dataset

**IMDb Movie Reviews** — loaded via HuggingFace `datasets`:
- 25,000 training reviews (balanced: 50% positive, 50% negative)
- 25,000 test reviews
- Binary labels: `0 = Negative`, `1 = Positive`
- No built-in validation split — validation set is carved out from training data using `train_test_split(test_size=0.1, seed=42)`
- Source: `load_dataset("imdb")`

---

## Outputs Generated

| File | Description |
|------|-------------|
| `eda_plots.png` | Class distribution bar chart + review length histogram |
| `model_comparison.png` | Grouped bar chart comparing Accuracy, F1, Precision, Recall |
| `confusion_matrices.png` | 3-panel confusion matrix (one per model) with percentages |
| `model_size.png` | Horizontal bar chart of parameter counts per model |
| `model_comparison_results.csv` | Numerical results table sorted by F1 score |

---

## Expected Results (Approximate)

| Model | Accuracy | F1 Score |
|-------|----------|----------|
| BERT-base | ~0.91 | ~0.91 |
| DistilBERT | ~0.89 | ~0.89 |
| RoBERTa-base | ~0.93 | ~0.93 |

> Actual results may vary slightly based on subsampling randomness and hardware.

The best-performing model (by F1 score) is automatically selected for the **inference demo** in Cell 15.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| CUDA out of memory | Reduce `batch_size` to `8` in `train_model` |
| Slow training | Enable GPU runtime in Colab (T4) |
| Model download fails | Check internet connection; HuggingFace servers may be busy |
| `accelerate` version error | Run `!pip install accelerate -U` |
| `eval_strategy` deprecation warning | Already handled — `evaluation_strategy` replaced with `eval_strategy` |

---

## Academic Use

This project was developed for a final-term NLP assessment.  
All code is original. The IMDb dataset and pretrained transformer models are used under their respective open licences (Apache 2.0 / MIT).

---

## Author

- **Course**: NLP Final Term Examination
- **Framework**: HuggingFace Transformers + PyTorch
- **Platform**: Google Colab (T4 GPU)
- **Seed**: 42 (all experiments reproducible)
