"""
Model Training Script
"""
import logging
import argparse
from pathlib import Path

from app.models.trainer import ModelTrainer
from app.services.service_manager import ServiceManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Train delay prediction models")
    parser.add_argument("--model-type", default="xgboost", choices=["xgboost", "lightgbm", "random_forest"])
    parser.add_argument("--samples", type=int, default=1000, help="Number of training samples")
    parser.add_argument("--test-size", type=float, default=0.2, help="Test set size")
    
    args = parser.parse_args()
    
    logger.info("Starting model training...")
    
    # Initialize trainer
    trainer = ModelTrainer(model_type=args.model_type)
    
    # Generate or load training data
    logger.info(f"Generating {args.samples} training samples...")
    df = trainer.generate_sample_data(args.samples)
    
    # Train models
    logger.info("Training models...")
    metrics = trainer.train(df, test_size=args.test_size)
    
    logger.info("Training completed!")
    logger.info(f"Model Accuracy: {metrics.get('overall_accuracy', 0)*100:.2f}%")
    logger.info(f"Classifier F1 Score: {metrics.get('classifier', {}).get('f1_score', 0):.4f}")
    logger.info(f"Regressor R2 Score: {metrics.get('regressor', {}).get('r2_score', 0):.4f}")


if __name__ == "__main__":
    main()

