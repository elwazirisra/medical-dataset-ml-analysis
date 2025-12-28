# Model Compatibility Issue - Retraining Required

## Problem

You're seeing this error:
```
node array from the pickle has an incompatible dtype
```

This happens when models were saved with a different version of scikit-learn than what you're currently using.

## Solution

Simply retrain the models with your current scikit-learn version:

```bash
python train_models.py
```

This will:
1. Load the Breast Cancer Wisconsin dataset
2. Train all three models (Logistic Regression, Random Forest, Gradient Boosting)
3. Save them with the current scikit-learn version
4. Generate all required metadata files

## Why This Happens

scikit-learn models contain internal data structures that can change between versions. When you upgrade or change scikit-learn versions, old model files may not be compatible.

## Prevention

- Keep your `requirements.txt` up to date
- Retrain models after updating scikit-learn
- Consider version pinning in production: `scikit-learn==1.3.0`

