# Emotion model training (Colab)

Is folder mein training ki saari files hain:

| file | kya hai |
|---|---|
| `train_emotion_xlmr.ipynb` | training notebook |
| `emotion_en.jsonl` | English data (GoEmotions, Apache-2.0) |
| `emotion_roman_ur.jsonl` | Roman Urdu data (RUEmoCorp, CC-BY-4.0) |
| `stats.json` | frozen test set ke hashes (notebook check karti hai) |

## Steps

1. https://colab.research.google.com -> File -> Upload notebook -> `train_emotion_xlmr.ipynb`
2. Runtime -> Change runtime type -> T4 GPU -> Save
3. Runtime -> Run all. Upload button aaye to isi folder se ye 3 files chunein:
   `emotion_en.jsonl`, `emotion_roman_ur.jsonl`, `stats.json`
4. Tab khula rakhein (andaza: 30-60 minute).
5. `emotion_model.zip` download hogi. Isay `mindmate/ml/export/` mein extract karein.

## Note

- Ye data files `ml/data/processed/` ki copies hain. Agar `ml/data/prepare_datasets.py`
  dobara chalayein, to teeno files yahan dobara copy karein, warna notebook ka
  frozen-hash check fail ho jayega (jo sahi behavior hai).
- `.jsonl` copies git mein nahi jaatin (bari files); scripts se dobara ban jaati hain.
