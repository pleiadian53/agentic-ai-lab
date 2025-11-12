"""
Train tumor classification model on TCGA data.

Trains an XGBoost classifier to predict cancer type from gene expression data.
"""

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import LabelEncoder
import joblib
import json
from pathlib import Path
import logging
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROCESSED_DATA_DIR, MODELS_DIR, TEST_SIZE, RANDOM_STATE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TumorClassifier:
    """Train and evaluate tumor classification model"""
    
    def __init__(self, model_type='xgboost'):
        self.model_type = model_type
        self.model = None
        self.label_encoder = LabelEncoder()
        self.feature_names = None
        self.class_names = None
    
    def load_data(self, data_path: Path):
        """Load processed TCGA data"""
        logger.info(f"Loading data from {data_path}")
        df = pd.read_csv(data_path)
        
        # Separate features and target
        X = df.drop('cancer_type', axis=1)
        y = df['cancer_type']
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)
        self.class_names = self.label_encoder.classes_.tolist()
        self.feature_names = X.columns.tolist()
        
        logger.info(f"Data shape: {X.shape}")
        logger.info(f"Classes: {self.class_names}")
        logger.info(f"Class distribution:\n{pd.Series(y).value_counts()}")
        
        return X.values, y_encoded
    
    def train(self, X, y):
        """Train the model"""
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
        )
        
        logger.info(f"Training set: {X_train.shape[0]} samples")
        logger.info(f"Test set: {X_test.shape[0]} samples")
        
        # Train model
        if self.model_type == 'xgboost':
            logger.info("Training XGBoost classifier...")
            self.model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=RANDOM_STATE,
                eval_metric='mlogloss',
                use_label_encoder=False
            )
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        # Fit model
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Model Performance")
        logger.info(f"{'='*60}")
        logger.info(f"Accuracy: {accuracy:.4f}")
        
        # Classification report
        logger.info("\nClassification Report:")
        report = classification_report(
            y_test, y_pred,
            target_names=self.class_names,
            digits=4
        )
        logger.info(f"\n{report}")
        
        # Confusion matrix
        logger.info("\nConfusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        logger.info(f"\n{cm}")
        
        # Cross-validation
        logger.info("\nCross-validation (5-fold):")
        cv_scores = cross_val_score(self.model, X_train, y_train, cv=5)
        logger.info(f"CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        # Feature importance
        if hasattr(self.model, 'feature_importances_'):
            feature_importance = pd.DataFrame({
                'gene': self.feature_names,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            logger.info("\nTop 10 Most Important Genes:")
            for idx, row in feature_importance.head(10).iterrows():
                logger.info(f"  {row['gene']}: {row['importance']:.4f}")
            
            # Save feature importance
            importance_file = MODELS_DIR / "feature_importance.csv"
            feature_importance.to_csv(importance_file, index=False)
            logger.info(f"\nSaved feature importance to {importance_file}")
        
        return {
            'accuracy': accuracy,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'classification_report': report,
            'confusion_matrix': cm.tolist()
        }
    
    def save_model(self, output_path: Path, metrics: dict):
        """Save trained model"""
        model_data = {
            'model': self.model,
            'label_encoder': self.label_encoder,
            'feature_names': self.feature_names,
            'class_names': self.class_names,
            'model_type': self.model_type,
            'metrics': metrics,
            'version': '1.0.0'
        }
        
        joblib.dump(model_data, output_path)
        logger.info(f"\nModel saved to {output_path}")
        
        # Save metadata
        metadata = {
            'model_type': self.model_type,
            'version': '1.0.0',
            'n_features': len(self.feature_names),
            'n_classes': len(self.class_names),
            'class_names': self.class_names,
            'accuracy': metrics['accuracy'],
            'cv_accuracy': metrics['cv_mean']
        }
        
        metadata_file = output_path.parent / "model_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Model metadata saved to {metadata_file}")


def main():
    """Main training pipeline"""
    logger.info("=" * 60)
    logger.info("TCGA Tumor Classification Model Training")
    logger.info("=" * 60)
    
    # Check if processed data exists
    data_file = PROCESSED_DATA_DIR / "tcga_processed.csv"
    if not data_file.exists():
        logger.error(f"Processed data not found: {data_file}")
        logger.error("Please run download_tcga_data.py first!")
        return
    
    # Initialize classifier
    classifier = TumorClassifier(model_type='xgboost')
    
    # Load data
    X, y = classifier.load_data(data_file)
    
    # Train model
    logger.info("\n" + "=" * 60)
    logger.info("Training Model")
    logger.info("=" * 60)
    metrics = classifier.train(X, y)
    
    # Save model
    logger.info("\n" + "=" * 60)
    logger.info("Saving Model")
    logger.info("=" * 60)
    model_path = MODELS_DIR / "tumor_classifier.pkl"
    classifier.save_model(model_path, metrics)
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ Model training complete!")
    logger.info("=" * 60)
    logger.info(f"\nModel saved to: {model_path}")
    logger.info(f"Test accuracy: {metrics['accuracy']:.4f}")
    logger.info(f"\nReady to serve predictions!")


if __name__ == "__main__":
    main()
