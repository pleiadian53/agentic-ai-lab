"""Data access layer for chart generation.

Provides unified interface for loading and describing datasets from various sources:
- CSV files
- SQLite databases
- pandas DataFrames
- Excel files

Similar to CustomerServiceStore but optimized for chart generation workflows.
"""

from __future__ import annotations

import json
import sqlite3
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional

import pandas as pd

try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False


class ChartDataset(ABC):
    """Abstract base class for chart data sources."""
    
    @abstractmethod
    def load_dataframe(self) -> pd.DataFrame:
        """Load the dataset as a pandas DataFrame."""
        pass
    
    @abstractmethod
    def get_schema_description(self) -> str:
        """Get human-readable schema description for LLM prompts."""
        pass
    
    @abstractmethod
    def get_sample_data(self, rows: int = 5) -> str:
        """Get sample rows as JSON string for LLM prompts."""
        pass
    
    def get_summary_stats(self) -> dict[str, Any]:
        """Get summary statistics for the dataset."""
        df = self.load_dataframe()
        return {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
        }


class CSVDataset(ChartDataset):
    """Dataset loaded from CSV file."""
    
    def __init__(
        self,
        file_path: str | Path,
        encoding: str = "utf-8",
        **read_csv_kwargs
    ):
        """Initialize CSV dataset.
        
        Args:
            file_path: Path to CSV file
            encoding: File encoding (default: utf-8)
            **read_csv_kwargs: Additional arguments passed to pd.read_csv
        """
        self.file_path = Path(file_path)
        self.encoding = encoding
        self.read_csv_kwargs = read_csv_kwargs
        self._df: Optional[pd.DataFrame] = None
    
    def load_dataframe(self) -> pd.DataFrame:
        """Load CSV as DataFrame with caching."""
        if self._df is None:
            self._df = pd.read_csv(
                self.file_path,
                encoding=self.encoding,
                **self.read_csv_kwargs
            )
            # Auto-parse dates if column names suggest date/time
            self._df = self._auto_parse_dates(self._df)
        return self._df.copy()
    
    def _auto_parse_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Automatically parse date columns based on column names."""
        date_keywords = ['date', 'time', 'datetime', 'timestamp', 'day', 'month', 'year']
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in date_keywords):
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except Exception:
                    pass  # Keep original if parsing fails
        return df
    
    def get_schema_description(self) -> str:
        """Generate schema description."""
        df = self.load_dataframe()
        if df.empty:
            return "The dataset is empty."
        
        lines = [f"Dataset: {self.file_path.name}"]
        lines.append(f"Rows: {len(df)}, Columns: {len(df.columns)}")
        lines.append("\nColumn Schema:")
        
        for col in df.columns:
            dtype = df[col].dtype
            null_count = df[col].isnull().sum()
            null_pct = (null_count / len(df)) * 100 if len(df) > 0 else 0
            
            # Get value range for numeric columns
            if pd.api.types.is_numeric_dtype(dtype):
                min_val = df[col].min()
                max_val = df[col].max()
                lines.append(
                    f"  - {col}: {dtype} (range: {min_val} to {max_val}, "
                    f"nulls: {null_pct:.1f}%)"
                )
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                min_val = df[col].min()
                max_val = df[col].max()
                lines.append(
                    f"  - {col}: datetime (range: {min_val} to {max_val}, "
                    f"nulls: {null_pct:.1f}%)"
                )
            else:
                unique_count = df[col].nunique()
                lines.append(
                    f"  - {col}: {dtype} ({unique_count} unique values, "
                    f"nulls: {null_pct:.1f}%)"
                )
        
        return "\n".join(lines)
    
    def get_sample_data(self, rows: int = 5) -> str:
        """Get sample rows as JSON."""
        df = self.load_dataframe()
        if df.empty:
            return "[]"
        
        sample = df.head(rows)
        # Convert to JSON-serializable format
        records = json.loads(sample.to_json(orient="records", date_format="iso"))
        return json.dumps(records, indent=2)


class SQLiteDataset(ChartDataset):
    """Dataset loaded from SQLite database query."""
    
    def __init__(
        self,
        db_path: str | Path,
        query: Optional[str] = None,
        table_name: Optional[str] = None
    ):
        """Initialize SQLite dataset.
        
        Args:
            db_path: Path to SQLite database file
            query: SQL query to execute (optional)
            table_name: Table name to load (used if query not provided)
        """
        if query is None and table_name is None:
            raise ValueError("Either query or table_name must be provided")
        
        self.db_path = Path(db_path)
        self.query = query or f"SELECT * FROM {table_name}"
        self.table_name = table_name
        self._df: Optional[pd.DataFrame] = None
    
    def load_dataframe(self) -> pd.DataFrame:
        """Load query results as DataFrame with caching."""
        if self._df is None:
            with sqlite3.connect(self.db_path) as conn:
                self._df = pd.read_sql_query(self.query, conn)
        return self._df.copy()
    
    def get_schema_description(self) -> str:
        """Generate schema description."""
        df = self.load_dataframe()
        if df.empty:
            return "The query returned no results."
        
        lines = [f"Database: {self.db_path.name}"]
        if self.table_name:
            lines.append(f"Table: {self.table_name}")
        lines.append(f"Rows: {len(df)}, Columns: {len(df.columns)}")
        lines.append("\nColumn Schema:")
        
        for col in df.columns:
            dtype = df[col].dtype
            null_count = df[col].isnull().sum()
            null_pct = (null_count / len(df)) * 100 if len(df) > 0 else 0
            
            if pd.api.types.is_numeric_dtype(dtype):
                min_val = df[col].min()
                max_val = df[col].max()
                lines.append(
                    f"  - {col}: {dtype} (range: {min_val} to {max_val}, "
                    f"nulls: {null_pct:.1f}%)"
                )
            else:
                unique_count = df[col].nunique()
                lines.append(
                    f"  - {col}: {dtype} ({unique_count} unique values, "
                    f"nulls: {null_pct:.1f}%)"
                )
        
        return "\n".join(lines)
    
    def get_sample_data(self, rows: int = 5) -> str:
        """Get sample rows as JSON."""
        df = self.load_dataframe()
        if df.empty:
            return "[]"
        
        sample = df.head(rows)
        records = json.loads(sample.to_json(orient="records", date_format="iso"))
        return json.dumps(records, indent=2)


class DataFrameDataset(ChartDataset):
    """Dataset from existing pandas DataFrame."""
    
    def __init__(self, df: pd.DataFrame, name: str = "dataframe"):
        """Initialize DataFrame dataset.
        
        Args:
            df: pandas DataFrame
            name: Descriptive name for the dataset
        """
        self._df = df.copy()
        self.name = name
    
    def load_dataframe(self) -> pd.DataFrame:
        """Return copy of DataFrame."""
        return self._df.copy()
    
    def get_schema_description(self) -> str:
        """Generate schema description."""
        df = self._df
        if df.empty:
            return "The dataframe is empty."
        
        lines = [f"DataFrame: {self.name}"]
        lines.append(f"Rows: {len(df)}, Columns: {len(df.columns)}")
        lines.append("\nColumn Schema:")
        
        for col in df.columns:
            dtype = df[col].dtype
            null_count = df[col].isnull().sum()
            null_pct = (null_count / len(df)) * 100 if len(df) > 0 else 0
            
            if pd.api.types.is_numeric_dtype(dtype):
                min_val = df[col].min()
                max_val = df[col].max()
                lines.append(
                    f"  - {col}: {dtype} (range: {min_val} to {max_val}, "
                    f"nulls: {null_pct:.1f}%)"
                )
            else:
                unique_count = df[col].nunique()
                lines.append(
                    f"  - {col}: {dtype} ({unique_count} unique values, "
                    f"nulls: {null_pct:.1f}%)"
                )
        
        return "\n".join(lines)
    
    def get_sample_data(self, rows: int = 5) -> str:
        """Get sample rows as JSON."""
        if self._df.empty:
            return "[]"
        
        sample = self._df.head(rows)
        records = json.loads(sample.to_json(orient="records", date_format="iso"))
        return json.dumps(records, indent=2)


class DuckDBDataset(ChartDataset):
    """Dataset with DuckDB backend for efficient SQL queries on large data.
    
    This is the recommended approach for complex/large datasets because:
    - Fast SQL queries without loading full dataset
    - Efficient aggregations and filtering
    - LLM can use SQL for data preparation
    - Seamless integration with pandas
    
    Example:
        # For large TSV file
        dataset = DuckDBDataset("data/splice_sites_enhanced.tsv")
        
        # For genomic data with mixed-type columns (e.g., chr: 1,2,3,X,Y)
        dataset = DuckDBDataset(
            "data/splice_sites_enhanced.tsv",
            all_varchar=True  # Prevents type inference errors
        )
        
        # Query subset for visualization
        df = dataset.query("SELECT * FROM data WHERE score > 0.8 LIMIT 1000")
        
        # Or let chart agent work with full dataset
        result = chart_agent(dataset, "Show distribution of scores by class")
    """
    
    def __init__(
        self,
        source: str | Path | pd.DataFrame,
        table_name: str = "data",
        connection: Optional[Any] = None,
        **read_kwargs
    ):
        """Initialize DuckDB dataset.
        
        Args:
            source: Path to CSV/TSV/Parquet file, or pandas DataFrame
            table_name: Name to register table as (default: "data")
            connection: Existing DuckDB connection (optional, creates new if None)
            **read_kwargs: Additional arguments for file reading (e.g., sep='\t' for TSV)
        """
        if not DUCKDB_AVAILABLE:
            raise ImportError(
                "DuckDB is required for DuckDBDataset. "
                "Install with: pip install duckdb"
            )
        
        self.source = source
        self.table_name = table_name
        self.read_kwargs = read_kwargs
        self._con = connection or duckdb.connect()
        self._df: Optional[pd.DataFrame] = None
        self._setup_table()
    
    def _setup_table(self):
        """Register data source as DuckDB table."""
        if isinstance(self.source, pd.DataFrame):
            # Register DataFrame directly
            self._con.register(self.table_name, self.source)
        else:
            # Load from file
            source_path = Path(self.source)
            
            # Detect file type and load appropriately
            if source_path.suffix.lower() in ['.csv', '.tsv', '.txt']:
                # Use DuckDB's efficient CSV reader
                sep = self.read_kwargs.get('sep', '\t' if source_path.suffix == '.tsv' else ',')
                
                # For genomic data, force all columns to VARCHAR to avoid type inference issues
                # (e.g., chromosome "X", "Y" vs "1", "2")
                all_varchar = self.read_kwargs.get('all_varchar', False)
                
                if all_varchar:
                    self._con.execute(
                        f"CREATE TABLE {self.table_name} AS "
                        f"SELECT * FROM read_csv_auto('{source_path}', delim='{sep}', "
                        f"all_varchar=true)"
                    )
                else:
                    self._con.execute(
                        f"CREATE TABLE {self.table_name} AS "
                        f"SELECT * FROM read_csv_auto('{source_path}', delim='{sep}')"
                    )
            elif source_path.suffix.lower() == '.parquet':
                self._con.execute(
                    f"CREATE TABLE {self.table_name} AS "
                    f"SELECT * FROM read_parquet('{source_path}')"
                )
            else:
                # Fallback: load with pandas then register
                df = pd.read_csv(source_path, **self.read_kwargs)
                self._con.register(self.table_name, df)
    
    def load_dataframe(self) -> pd.DataFrame:
        """Load full dataset as DataFrame (cached)."""
        if self._df is None:
            self._df = self._con.execute(f"SELECT * FROM {self.table_name}").df()
        return self._df.copy()
    
    def query(self, sql: str) -> pd.DataFrame:
        """Execute SQL query and return results as DataFrame.
        
        This allows efficient data preparation before visualization:
        
        Examples:
            # Get top 100 rows
            df = dataset.query("SELECT * FROM data LIMIT 100")
            
            # Aggregate by category
            df = dataset.query(
                "SELECT category, COUNT(*) as count, AVG(score) as avg_score "
                "FROM data GROUP BY category"
            )
            
            # Filter and sort
            df = dataset.query(
                "SELECT * FROM data WHERE score > 0.5 "
                "ORDER BY score DESC LIMIT 1000"
            )
        
        Args:
            sql: SQL query (use table name from self.table_name)
            
        Returns:
            Query results as pandas DataFrame
        """
        return self._con.execute(sql).df()
    
    def get_schema_description(self) -> str:
        """Generate schema description with SQL capability note."""
        # Get schema from DuckDB
        schema_df = self._con.execute(
            f"DESCRIBE {self.table_name}"
        ).df()
        
        # Get row count efficiently
        row_count = self._con.execute(
            f"SELECT COUNT(*) as count FROM {self.table_name}"
        ).df()['count'][0]
        
        lines = [f"DuckDB Dataset: {self.table_name}"]
        lines.append(f"Rows: {row_count:,}, Columns: {len(schema_df)}")
        lines.append("\nColumn Schema:")
        
        for _, row in schema_df.iterrows():
            col_name = row['column_name']
            col_type = row['column_type']
            
            # Get basic stats for numeric columns
            # Quote column name to handle reserved keywords (e.g., "end", "start")
            quoted_col = f'"{col_name}"'
            
            if 'INT' in col_type.upper() or 'FLOAT' in col_type.upper() or 'DOUBLE' in col_type.upper():
                stats = self._con.execute(
                    f"SELECT MIN({quoted_col}) as min, MAX({quoted_col}) as max, "
                    f"COUNT(*) - COUNT({quoted_col}) as nulls "
                    f"FROM {self.table_name}"
                ).df().iloc[0]
                null_pct = (stats['nulls'] / row_count) * 100 if row_count > 0 else 0
                lines.append(
                    f"  - {col_name}: {col_type} "
                    f"(range: {stats['min']} to {stats['max']}, nulls: {null_pct:.1f}%)"
                )
            else:
                # Get distinct count for categorical
                distinct = self._con.execute(
                    f"SELECT COUNT(DISTINCT {quoted_col}) as distinct, "
                    f"COUNT(*) - COUNT({quoted_col}) as nulls "
                    f"FROM {self.table_name}"
                ).df().iloc[0]
                null_pct = (distinct['nulls'] / row_count) * 100 if row_count > 0 else 0
                lines.append(
                    f"  - {col_name}: {col_type} "
                    f"({distinct['distinct']} unique values, nulls: {null_pct:.1f}%)"
                )
        
        lines.append("\nSQL CAPABILITY: This dataset supports SQL queries for efficient data preparation.")
        lines.append(f"Use: dataset.query('SELECT ... FROM {self.table_name} ...')")
        
        return "\n".join(lines)
    
    def get_sample_data(self, rows: int = 5) -> str:
        """Get sample rows as JSON."""
        sample_df = self._con.execute(
            f"SELECT * FROM {self.table_name} LIMIT {rows}"
        ).df()
        
        if sample_df.empty:
            return "[]"
        
        records = json.loads(sample_df.to_json(orient="records", date_format="iso"))
        return json.dumps(records, indent=2)
    
    def get_summary_stats(self) -> dict[str, Any]:
        """Get summary statistics efficiently using SQL."""
        row_count = self._con.execute(
            f"SELECT COUNT(*) as count FROM {self.table_name}"
        ).df()['count'][0]
        
        schema_df = self._con.execute(f"DESCRIBE {self.table_name}").df()
        
        return {
            "row_count": int(row_count),
            "column_count": len(schema_df),
            "columns": schema_df['column_name'].tolist(),
            "dtypes": dict(zip(schema_df['column_name'], schema_df['column_type'])),
            "table_name": self.table_name,
            "sql_enabled": True,
        }
    
    def close(self):
        """Close DuckDB connection."""
        if self._con:
            self._con.close()
    
    def __enter__(self):
        """Context manager support."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close connection on context exit."""
        self.close()


class ExcelDataset(ChartDataset):
    """Dataset loaded from Excel file."""
    
    def __init__(
        self,
        file_path: str | Path,
        sheet_name: str | int = 0,
        **read_excel_kwargs
    ):
        """Initialize Excel dataset.
        
        Args:
            file_path: Path to Excel file
            sheet_name: Sheet name or index (default: 0)
            **read_excel_kwargs: Additional arguments passed to pd.read_excel
        """
        self.file_path = Path(file_path)
        self.sheet_name = sheet_name
        self.read_excel_kwargs = read_excel_kwargs
        self._df: Optional[pd.DataFrame] = None
    
    def load_dataframe(self) -> pd.DataFrame:
        """Load Excel sheet as DataFrame with caching."""
        if self._df is None:
            self._df = pd.read_excel(
                self.file_path,
                sheet_name=self.sheet_name,
                **self.read_excel_kwargs
            )
        return self._df.copy()
    
    def get_schema_description(self) -> str:
        """Generate schema description."""
        df = self.load_dataframe()
        if df.empty:
            return "The sheet is empty."
        
        lines = [f"Excel File: {self.file_path.name}"]
        lines.append(f"Sheet: {self.sheet_name}")
        lines.append(f"Rows: {len(df)}, Columns: {len(df.columns)}")
        lines.append("\nColumn Schema:")
        
        for col in df.columns:
            dtype = df[col].dtype
            null_count = df[col].isnull().sum()
            null_pct = (null_count / len(df)) * 100 if len(df) > 0 else 0
            
            if pd.api.types.is_numeric_dtype(dtype):
                min_val = df[col].min()
                max_val = df[col].max()
                lines.append(
                    f"  - {col}: {dtype} (range: {min_val} to {max_val}, "
                    f"nulls: {null_pct:.1f}%)"
                )
            else:
                unique_count = df[col].nunique()
                lines.append(
                    f"  - {col}: {dtype} ({unique_count} unique values, "
                    f"nulls: {null_pct:.1f}%)"
                )
        
        return "\n".join(lines)
    
    def get_sample_data(self, rows: int = 5) -> str:
        """Get sample rows as JSON."""
        df = self.load_dataframe()
        if df.empty:
            return "[]"
        
        sample = df.head(rows)
        records = json.loads(sample.to_json(orient="records", date_format="iso"))
        return json.dumps(records, indent=2)
