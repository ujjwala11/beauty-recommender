
---

## 🧹 Data Cleaning Summary

### Products
- Handled missing categorical values using `"Unknown"`
- Preserved meaningful NaNs (ratings, pricing)
- Cleaned ingredient and metadata fields

### Reviews
- Filled text fields with empty strings
- Preserved missing user attributes as `"Unknown"`
- Retained meaningful NaNs in target variables
- Removed exact duplicates (224 rows)
- Handled 10,471 user-product duplicates using **latest-review policy**

### Ingredients
- Filled missing compatibility fields with empty string
- No duplicates or structural issues

---

## 🔁 Duplicate Strategy

### Exact Duplicates
- Removed completely (no additional information)

### User-Product Duplicates
- Kept only the **most recent review**
- Preserves evolving user preferences
- Prevents interaction inflation in recommender systems

---

## 📊 Key Features (Planned)

### Product Features
- price buckets
- ingredient complexity
- popularity score
- category hierarchy
- brand strength

### User Features
- skin type preferences
- brand affinity
- review behavior
- engagement score

### Ingredient Features
- hydration score
- acne suitability
- sensitivity index
- anti-aging strength

---

## 🤖 Machine Learning Tasks

### Regression
- Predict product rating

Models:
- Linear Regression
- Random Forest
- XGBoost / LightGBM

### Classification
- Predict product recommendation

Models:
- Logistic Regression
- Random Forest
- Gradient Boosting
- XGBoost

---

## 🧾 NLP Tasks

- TF-IDF analysis
- Sentence embeddings
- Ingredient similarity
- Review sentiment analysis
- Product similarity scoring

---

## 🎯 Recommendation Systems

### 1. Popularity-Based
Baseline recommender

### 2. Content-Based
Uses:
- ingredients
- categories
- product metadata

### 3. Collaborative Filtering
- User-user similarity
- Item-item similarity
- Matrix factorization

### 4. Hybrid System
Combines:
- content score
- collaborative score
- popularity score
- business rules

---

## 🧪 Evaluation Metrics

### ML Models
- MAE, RMSE, R²
- Accuracy, Precision, Recall, F1
- ROC-AUC, PR-AUC

### Recommenders
- Precision@K
- Recall@K
- MAP@K
- MRR
- NDCG
- Diversity & Coverage

---

## 🧠 Explainability

Every recommendation includes:

- Similar ingredients
- Matching skin concerns
- User preference alignment
- Brand similarity
- Price compatibility
- Popularity signals

---

## 🧴 Final Capabilities

The system will support:

- Product recommendations
- Personalized skincare routines (AM/PM)
- Ingredient-based search
- User preference modeling
- Seasonal trend insights
- Explainable AI outputs

---

## 🛠️ Tech Stack

- Python
- Pandas, NumPy
- Scikit-learn
- NLP (TF-IDF, embeddings)
- XGBoost / LightGBM
- FastAPI
- Streamlit
- Matplotlib / Seaborn

---

## 📌 Project Philosophy

This project is built with:

- Production-level design thinking
- Modular pipeline architecture
- Explainable AI focus
- Real-world data constraints
- Interview-ready ML practices

---

## 📍 Next Steps

- EDA (business insights)
- Feature engineering
- ML modeling
- NLP pipeline
- Recommendation systems
- Deployment (Streamlit + API)

---

## 👨‍💻 Author

End-to-end Data Science + ML Engineering project focused on production-grade recommendation systems.

---
