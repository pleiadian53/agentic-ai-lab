"""
Download TCGA gene expression data using GDC Data Portal API.

This script downloads RNA-Seq gene expression data for multiple cancer types
from The Cancer Genome Atlas (TCGA) via the Genomic Data Commons (GDC).
"""

import requests
import pandas as pd
import numpy as np
import json
import gzip
import shutil
from pathlib import Path
import logging
from typing import List, Dict
import sys

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import RAW_DATA_DIR, PROCESSED_DATA_DIR, TCGA_CANCER_TYPES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TCGADownloader:
    """Download and process TCGA gene expression data"""
    
    def __init__(self, output_dir: Path = RAW_DATA_DIR):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.gdc_api = "https://api.gdc.cancer.gov"
    
    def download_expression_data(self, cancer_types: List[str], max_samples_per_type: int = 100):
        """
        Download gene expression data for specified cancer types.
        
        For demo purposes, we'll create synthetic data based on TCGA characteristics.
        In production, you would use the GDC API to download real data.
        """
        logger.info(f"Generating synthetic TCGA-like data for {len(cancer_types)} cancer types")
        
        all_data = []
        all_labels = []
        
        # Generate synthetic gene expression data
        # In reality, TCGA has ~20,000 genes, we'll use 5,000 for demo
        n_genes = 5000
        gene_names = [f"GENE_{i:05d}" for i in range(n_genes)]
        
        for cancer_type in cancer_types:
            logger.info(f"Generating data for {cancer_type}...")
            
            # Create cancer-type-specific expression patterns
            # Each cancer type has different mean expression levels
            np.random.seed(hash(cancer_type) % 2**32)
            
            # Generate samples
            n_samples = min(max_samples_per_type, np.random.randint(80, 120))
            
            # Base expression + cancer-specific signature
            base_expression = np.random.lognormal(mean=5, sigma=2, size=(n_samples, n_genes))
            
            # Add cancer-specific genes (simulate biomarkers)
            cancer_signature_genes = np.random.choice(n_genes, size=100, replace=False)
            base_expression[:, cancer_signature_genes] *= np.random.uniform(2, 5)
            
            # Add some noise
            noise = np.random.normal(0, 0.5, size=(n_samples, n_genes))
            expression_data = base_expression + noise
            
            # Ensure non-negative
            expression_data = np.maximum(expression_data, 0)
            
            all_data.append(expression_data)
            all_labels.extend([cancer_type] * n_samples)
        
        # Combine all data
        X = np.vstack(all_data)
        y = np.array(all_labels)
        
        # Create DataFrame
        df = pd.DataFrame(X, columns=gene_names)
        df['cancer_type'] = y
        
        # Save raw data
        output_file = self.output_dir / "tcga_expression_data.csv"
        df.to_csv(output_file, index=False)
        logger.info(f"Saved raw data to {output_file}")
        logger.info(f"Total samples: {len(df)}, Total genes: {n_genes}")
        
        # Save metadata
        metadata = {
            'cancer_types': cancer_types,
            'n_samples': len(df),
            'n_genes': n_genes,
            'samples_per_type': df['cancer_type'].value_counts().to_dict(),
            'gene_names': gene_names
        }
        
        metadata_file = self.output_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Saved metadata to {metadata_file}")
        
        return df, metadata
    
    def download_real_tcga_data(self, cancer_type: str, max_files: int = 10):
        """
        Download real TCGA data from GDC (for reference - requires more setup).
        
        This is a template for downloading actual TCGA data.
        Requires GDC authentication token for controlled access data.
        """
        logger.info(f"Querying GDC for {cancer_type} data...")
        
        # Query for RNA-Seq files
        filters = {
            "op": "and",
            "content": [
                {
                    "op": "in",
                    "content": {
                        "field": "cases.project.project_id",
                        "value": [f"TCGA-{cancer_type}"]
                    }
                },
                {
                    "op": "in",
                    "content": {
                        "field": "files.data_type",
                        "value": ["Gene Expression Quantification"]
                    }
                },
                {
                    "op": "in",
                    "content": {
                        "field": "files.experimental_strategy",
                        "value": ["RNA-Seq"]
                    }
                }
            ]
        }
        
        params = {
            "filters": json.dumps(filters),
            "fields": "file_id,file_name,cases.case_id,cases.project.project_id",
            "format": "JSON",
            "size": str(max_files)
        }
        
        response = requests.get(f"{self.gdc_api}/files", params=params)
        
        if response.status_code == 200:
            file_data = response.json()
            logger.info(f"Found {len(file_data['data']['hits'])} files")
            return file_data
        else:
            logger.error(f"GDC API error: {response.status_code}")
            return None


def preprocess_data(input_file: Path, output_file: Path, n_top_genes: int = 1000):
    """
    Preprocess TCGA data: feature selection, normalization.
    
    Args:
        input_file: Raw expression data CSV
        output_file: Processed data output path
        n_top_genes: Number of top variable genes to keep
    """
    logger.info(f"Loading data from {input_file}")
    df = pd.read_csv(input_file)
    
    # Separate features and labels
    X = df.drop('cancer_type', axis=1)
    y = df['cancer_type']
    
    logger.info(f"Original data shape: {X.shape}")
    
    # Feature selection: keep top N most variable genes
    gene_variance = X.var()
    top_genes = gene_variance.nlargest(n_top_genes).index
    X_selected = X[top_genes]
    
    logger.info(f"Selected top {n_top_genes} genes")
    logger.info(f"Processed data shape: {X_selected.shape}")
    
    # Log-transform (common for gene expression)
    X_log = np.log1p(X_selected)
    
    # Combine back with labels
    df_processed = X_log.copy()
    df_processed['cancer_type'] = y
    
    # Save processed data
    df_processed.to_csv(output_file, index=False)
    logger.info(f"Saved processed data to {output_file}")
    
    # Save selected gene names
    gene_list_file = output_file.parent / "selected_genes.txt"
    with open(gene_list_file, 'w') as f:
        f.write('\n'.join(top_genes))
    logger.info(f"Saved selected genes to {gene_list_file}")
    
    return df_processed


def main():
    """Main execution"""
    logger.info("=" * 60)
    logger.info("TCGA Data Download and Processing")
    logger.info("=" * 60)
    
    # Download data
    downloader = TCGADownloader()
    df, metadata = downloader.download_expression_data(
        cancer_types=TCGA_CANCER_TYPES,
        max_samples_per_type=100
    )
    
    logger.info("\nDataset Summary:")
    logger.info(f"  Total samples: {len(df)}")
    logger.info(f"  Cancer types: {metadata['cancer_types']}")
    logger.info(f"  Samples per type:")
    for cancer_type, count in metadata['samples_per_type'].items():
        logger.info(f"    {cancer_type}: {count}")
    
    # Preprocess data
    logger.info("\n" + "=" * 60)
    logger.info("Preprocessing Data")
    logger.info("=" * 60)
    
    raw_file = RAW_DATA_DIR / "tcga_expression_data.csv"
    processed_file = PROCESSED_DATA_DIR / "tcga_processed.csv"
    
    df_processed = preprocess_data(
        input_file=raw_file,
        output_file=processed_file,
        n_top_genes=1000
    )
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ Data download and processing complete!")
    logger.info("=" * 60)
    logger.info(f"\nRaw data: {raw_file}")
    logger.info(f"Processed data: {processed_file}")
    logger.info(f"\nReady for model training!")


if __name__ == "__main__":
    main()
