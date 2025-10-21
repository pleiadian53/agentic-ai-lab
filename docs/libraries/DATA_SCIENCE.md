# Data Science & Analysis Libraries

Documentation for data analysis, visualization, and database libraries.

## Overview

These libraries enable data manipulation, analysis, visualization, and storage for the agentic AI project.

---

## Data Manipulation

### pandas

**Data Analysis and Manipulation**

```python
import pandas as pd

# Create DataFrame
df = pd.DataFrame({
    'task_id': ['task-1', 'task-2', 'task-3'],
    'model': ['gpt-4', 'claude-3', 'gpt-4'],
    'tokens': [1500, 2000, 1800],
    'cost': [0.045, 0.060, 0.054]
})

# Basic operations
print(df.head())
print(df.describe())
print(df['model'].value_counts())

# Filtering
gpt4_tasks = df[df['model'] == 'gpt-4']
high_cost = df[df['cost'] > 0.05]

# Grouping and aggregation
by_model = df.groupby('model').agg({
    'tokens': ['mean', 'sum'],
    'cost': ['mean', 'sum']
})

# Time series
df['timestamp'] = pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03'])
df.set_index('timestamp', inplace=True)
daily_cost = df.resample('D')['cost'].sum()

# Read/write data
df.to_csv('tasks.csv', index=False)
df.to_json('tasks.json', orient='records')
df_loaded = pd.read_csv('tasks.csv')
```

**Key Features:**
- DataFrame and Series data structures
- Data cleaning and transformation
- Time series analysis
- Grouping and aggregation
- I/O for CSV, JSON, Excel, SQL, etc.

**Use Cases:**
- Analyze agent performance metrics
- Process research results
- Generate reports
- Data cleaning and preparation

**Common Operations:**
```python
# Missing data
df.fillna(0)
df.dropna()

# Merging
pd.merge(df1, df2, on='task_id')
pd.concat([df1, df2])

# Sorting
df.sort_values('cost', ascending=False)

# Apply functions
df['cost_usd'] = df['cost'].apply(lambda x: f'${x:.2f}')
```

---

## Visualization

### matplotlib

**Plotting and Visualization**

```python
import matplotlib.pyplot as plt
import numpy as np

# Line plot
plt.figure(figsize=(10, 6))
plt.plot(dates, costs, marker='o', label='Daily Cost')
plt.xlabel('Date')
plt.ylabel('Cost ($)')
plt.title('Agent Cost Over Time')
plt.legend()
plt.grid(True)
plt.savefig('cost_trend.png', dpi=300, bbox_inches='tight')
plt.show()

# Multiple subplots
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Subplot 1: Line plot
axes[0, 0].plot(x, y1)
axes[0, 0].set_title('Token Usage')

# Subplot 2: Bar plot
axes[0, 1].bar(models, counts)
axes[0, 1].set_title('Model Usage')

# Subplot 3: Scatter plot
axes[1, 0].scatter(tokens, cost)
axes[1, 0].set_title('Tokens vs Cost')

# Subplot 4: Histogram
axes[1, 1].hist(response_times, bins=20)
axes[1, 1].set_title('Response Time Distribution')

plt.tight_layout()
plt.savefig('dashboard.png')

# Customization
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12
```

**Key Features:**
- Publication-quality plots
- Multiple plot types (line, bar, scatter, histogram, etc.)
- Subplots and layouts
- Customization (colors, styles, fonts)
- Export to PNG, PDF, SVG

**Use Cases:**
- Visualize agent performance
- Create dashboards
- Generate reports
- Analyze trends

**Plot Types:**
- Line: Trends over time
- Bar: Comparisons
- Scatter: Relationships
- Histogram: Distributions
- Pie: Proportions
- Box: Statistical summaries

---

### seaborn

**Statistical Data Visualization**

```python
import seaborn as sns
import matplotlib.pyplot as plt

# Set style
sns.set_theme(style="whitegrid")
sns.set_palette("husl")

# Distribution plot
sns.histplot(data=df, x='cost', kde=True, bins=30)
plt.title('Cost Distribution')
plt.show()

# Box plot
sns.boxplot(data=df, x='model', y='tokens')
plt.title('Token Usage by Model')
plt.show()

# Violin plot (distribution + box plot)
sns.violinplot(data=df, x='model', y='cost')
plt.show()

# Scatter plot with regression
sns.regplot(data=df, x='tokens', y='cost')
plt.title('Tokens vs Cost')
plt.show()

# Pair plot (multiple variables)
sns.pairplot(df[['tokens', 'cost', 'response_time']], 
             hue='model', diag_kind='kde')
plt.show()

# Heatmap (correlation matrix)
corr = df[['tokens', 'cost', 'response_time']].corr()
sns.heatmap(corr, annot=True, cmap='coolwarm', center=0)
plt.title('Feature Correlation')
plt.show()

# Count plot
sns.countplot(data=df, x='model', order=df['model'].value_counts().index)
plt.title('Model Usage Count')
plt.xticks(rotation=45)
plt.show()

# Time series
sns.lineplot(data=df, x='date', y='cost', hue='model', marker='o')
plt.title('Cost Trend by Model')
plt.show()
```

**Key Features:**
- Statistical plots
- Beautiful default styles
- Built on matplotlib
- Automatic legends and labels
- Faceted plots

**Use Cases:**
- Statistical analysis visualization
- Compare model performance
- Identify correlations
- Distribution analysis

**Advantages over matplotlib:**
- Higher-level API
- Better defaults
- Statistical functions built-in
- Easier for complex plots

---

## Databases

### duckdb

**In-Process Analytical Database**

```python
import duckdb
import pandas as pd

# Connect (in-memory or file)
con = duckdb.connect('analytics.db')  # or ':memory:'

# Create table from pandas
df = pd.DataFrame({
    'task_id': ['t1', 't2', 't3'],
    'model': ['gpt-4', 'claude', 'gpt-4'],
    'tokens': [1500, 2000, 1800]
})
con.execute("CREATE TABLE tasks AS SELECT * FROM df")

# SQL queries
result = con.execute("""
    SELECT model, 
           COUNT(*) as count,
           AVG(tokens) as avg_tokens,
           SUM(tokens) as total_tokens
    FROM tasks
    GROUP BY model
    ORDER BY total_tokens DESC
""").fetchdf()

print(result)

# Query pandas directly
result = con.execute("""
    SELECT * FROM df WHERE tokens > 1600
""").fetchdf()

# Read Parquet files
con.execute("CREATE TABLE data AS SELECT * FROM 'data.parquet'")

# Join multiple sources
result = con.execute("""
    SELECT t.*, m.cost_per_token
    FROM tasks t
    JOIN models m ON t.model = m.name
""").fetchdf()

# Window functions
result = con.execute("""
    SELECT task_id, tokens,
           AVG(tokens) OVER (PARTITION BY model) as model_avg,
           ROW_NUMBER() OVER (ORDER BY tokens DESC) as rank
    FROM tasks
""").fetchdf()

# Export results
con.execute("COPY (SELECT * FROM tasks) TO 'output.parquet'")
con.execute("COPY (SELECT * FROM tasks) TO 'output.csv'")
```

**Key Features:**
- SQL interface for analytics
- Fast analytical queries
- Parquet support
- Direct pandas integration
- No server needed

**Use Cases:**
- Analyze large datasets
- Complex aggregations
- Data warehousing
- ETL pipelines

**Performance:**
- Much faster than pandas for large data
- Columnar storage
- Parallel execution
- Efficient joins

---

### tinydb

**Lightweight Document Database**

```python
from tinydb import TinyDB, Query

# Create database
db = TinyDB('cache.json')

# Insert documents
db.insert({'task_id': 't1', 'result': 'cached result', 'timestamp': '2024-01-01'})
db.insert_multiple([
    {'task_id': 't2', 'result': 'result 2'},
    {'task_id': 't3', 'result': 'result 3'}
])

# Query
Task = Query()
result = db.search(Task.task_id == 't1')
results = db.search(Task.timestamp.exists())

# Update
db.update({'status': 'completed'}, Task.task_id == 't1')

# Delete
db.remove(Task.task_id == 't2')

# Get all
all_docs = db.all()

# Tables (collections)
cache_table = db.table('cache')
results_table = db.table('results')

cache_table.insert({'key': 'value'})

# Custom queries
from tinydb import where
results = db.search(
    (Task.status == 'completed') & (Task.cost < 0.1)
)

# Upsert
db.upsert({'task_id': 't1', 'result': 'updated'}, Task.task_id == 't1')
```

**Key Features:**
- Pure Python, no dependencies
- JSON storage
- Simple query language
- No server needed
- Thread-safe

**Use Cases:**
- Caching
- Configuration storage
- Small datasets
- Prototyping

**When to Use:**
- Small to medium data (<10k records)
- Simple queries
- No complex relationships
- Easy setup needed

**When NOT to Use:**
- Large datasets (use DuckDB or PostgreSQL)
- Complex queries (use SQL database)
- High concurrency (use proper database)

---

### tabulate

**Pretty-Print Tabular Data**

```python
from tabulate import tabulate

# Data
data = [
    ['GPT-4', 1500, 0.045],
    ['Claude-3', 2000, 0.060],
    ['Mistral', 1200, 0.024]
]

headers = ['Model', 'Tokens', 'Cost']

# Simple table
print(tabulate(data, headers=headers))

# Markdown format
print(tabulate(data, headers=headers, tablefmt='github'))

# HTML format
html = tabulate(data, headers=headers, tablefmt='html')

# Grid format
print(tabulate(data, headers=headers, tablefmt='grid'))

# With pandas
import pandas as pd
df = pd.DataFrame(data, columns=headers)
print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))

# Custom formatting
print(tabulate(
    data,
    headers=headers,
    tablefmt='fancy_grid',
    floatfmt='.3f',
    numalign='right',
    stralign='left'
))

# Available formats
formats = [
    'plain', 'simple', 'github', 'grid', 'fancy_grid',
    'pipe', 'orgtbl', 'jira', 'presto', 'pretty',
    'psql', 'rst', 'mediawiki', 'moinmoin', 'youtrack',
    'html', 'latex', 'latex_raw', 'latex_booktabs'
]
```

**Key Features:**
- Multiple output formats
- Alignment options
- Number formatting
- Works with pandas
- No dependencies

**Use Cases:**
- Console output
- Reports
- Logging
- Documentation

**Output Examples:**

```
# Simple
Model      Tokens    Cost
-------  --------  ------
GPT-4        1500   0.045
Claude-3     2000   0.060
Mistral      1200   0.024

# Grid
+-----------+----------+--------+
| Model     |   Tokens |   Cost |
+===========+==========+========+
| GPT-4     |     1500 |  0.045 |
+-----------+----------+--------+
| Claude-3  |     2000 |  0.060 |
+-----------+----------+--------+
| Mistral   |     1200 |  0.024 |
+-----------+----------+--------+
```

---

## Integration Examples

### Analysis Pipeline

```python
import pandas as pd
import duckdb
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv('agent_logs.csv')

# DuckDB for complex queries
con = duckdb.connect(':memory:')
con.execute("CREATE TABLE logs AS SELECT * FROM df")

# Aggregate with SQL
daily_stats = con.execute("""
    SELECT 
        DATE(timestamp) as date,
        model,
        COUNT(*) as tasks,
        SUM(tokens) as total_tokens,
        AVG(cost) as avg_cost
    FROM logs
    GROUP BY date, model
    ORDER BY date, model
""").fetchdf()

# Visualize with seaborn
plt.figure(figsize=(12, 6))
sns.lineplot(data=daily_stats, x='date', y='total_tokens', hue='model')
plt.title('Daily Token Usage by Model')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('token_usage.png')

# Summary table
summary = daily_stats.groupby('model').agg({
    'tasks': 'sum',
    'total_tokens': 'sum',
    'avg_cost': 'mean'
})

from tabulate import tabulate
print(tabulate(summary, headers='keys', tablefmt='github'))
```

### Caching Layer

```python
from tinydb import TinyDB, Query
import hashlib
import json

class ResultCache:
    def __init__(self, db_path='cache.json'):
        self.db = TinyDB(db_path)
        self.cache = self.db.table('results')
    
    def _hash_key(self, prompt, model):
        key = f"{prompt}:{model}"
        return hashlib.md5(key.encode()).hexdigest()
    
    def get(self, prompt, model):
        """Get cached result"""
        key = self._hash_key(prompt, model)
        Query_ = Query()
        result = self.cache.get(Query_.key == key)
        return result['value'] if result else None
    
    def set(self, prompt, model, value):
        """Cache result"""
        key = self._hash_key(prompt, model)
        self.cache.upsert(
            {'key': key, 'value': value, 'prompt': prompt, 'model': model},
            Query().key == key
        )
    
    def clear(self):
        """Clear cache"""
        self.cache.truncate()

# Usage
cache = ResultCache()

# Check cache
result = cache.get("Explain AI", "gpt-4")
if result is None:
    # Call LLM
    result = llm.generate("Explain AI")
    cache.set("Explain AI", "gpt-4", result)
```

---

## Best Practices

### Data Analysis Workflow

```python
# 1. Load data
df = pd.read_csv('data.csv')

# 2. Explore
print(df.info())
print(df.describe())
print(df.head())

# 3. Clean
df = df.dropna()
df = df[df['cost'] > 0]  # Remove invalid data

# 4. Transform
df['cost_usd'] = df['cost'].apply(lambda x: f'${x:.2f}')
df['date'] = pd.to_datetime(df['timestamp'])

# 5. Analyze (use DuckDB for complex queries)
con = duckdb.connect(':memory:')
results = con.execute("SELECT ... FROM df ...").fetchdf()

# 6. Visualize
sns.lineplot(data=results, x='date', y='metric')

# 7. Export
results.to_csv('analysis_results.csv')
```

### Performance Tips

```python
# Use DuckDB for large datasets
# Faster than pandas for aggregations
con = duckdb.connect(':memory:')
result = con.execute("SELECT ... FROM large_df ...").fetchdf()

# Use categorical data types in pandas
df['model'] = df['model'].astype('category')  # Saves memory

# Chunk large files
for chunk in pd.read_csv('large.csv', chunksize=10000):
    process(chunk)

# Use Parquet for storage (faster than CSV)
df.to_parquet('data.parquet')
df = pd.read_parquet('data.parquet')
```

---

## See Also

- [Complete Dependencies](DEPENDENCIES.md)
- [Agent & LLM Tools](AGENT_LLM_TOOLS.md)
- [Web Framework](WEB_FRAMEWORK.md)
- [Jupyter Environment](JUPYTER.md)
