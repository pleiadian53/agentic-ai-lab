# SQL Agent with Reflection - Query Improvement

This activity demonstrates the reflection design pattern for SQL query generation, where one LLM generates queries and another evaluates and improves them iteratively.

## Overview

The SQL agent follows a reflection-based workflow:
1. **Generate**: Create initial SQL query from natural language question
2. **Execute**: Run the query and capture results
3. **Evaluate**: Have another LLM assess if results answer the question adequately  
4. **Refine**: Improve the SQL query based on evaluation feedback
5. **Final Execute**: Run the refined query for the final result

## Prerequisites

Ensure you have a `.env` file in the root of the repository with API keys for:
- `OPENAI_API_KEY` - OpenAI API access
- `GOOGLE_API_KEY` - Google AI Studio access
- `ANTHROPIC_API_KEY` - Anthropic Claude access
- `TAVILY_API_KEY` - Tavily web search API access

Install dependencies from the root directory:
```bash
pip install -r requirements.txt
```

## Files

- `sql.ipynb` - Main notebook demonstrating SQL reflection workflow
- `utils.py` - Utility functions for database operations
- `products.db` - SQLite database (auto-generated when running notebook)

## Running the Activity

1. **Open and run the notebook**:
   - Open `sql.ipynb` in Jupyter
   - Run all cells sequentially

2. **The notebook will**:
   - Create a sample products database with 100 items
   - Show database schema and sample data
   - Execute the reflection workflow with example queries
   - Display the improvement process step-by-step

3. **Example workflow**:
   ```python
   results = run_sql_workflow("products.db", 
                              "Which color of product has the highest total sales?",
                              model_generation="openai:gpt-4o-mini",
                              model_evaluation="openai:gpt-4o")
   ```

## Database Schema

Auto-generated `products.db` contains:
- **Table**: products
- **Columns**: id, name, brand, category, color, price, stock, total_sales
- **Data**: 100 random products with brands (Nike, Adidas, Puma, etc.), categories (shoes, hoodie, t-shirt, etc.), and colors

## Key Learning Points

- **Reflection Pattern**: How one LLM can evaluate and improve another's SQL generation
- **Error Recovery**: Fixing syntax errors and logical issues through reflection
- **Query Optimization**: Improving query structure based on evaluation feedback
- **Multi-Model Cooperation**: Using different models for generation vs evaluation
- **Iterative Improvement**: Systematic refinement of database queries

## Expected Outputs

The workflow shows progression through reflection:

1. **Initial Query**: May contain formatting issues or logical errors
2. **Evaluation Feedback**: LLM assessment of query quality and result adequacy
3. **Refined Query**: Improved version based on feedback
4. **Comparison**: Side-by-side view of original vs improved results

## Example Improvements

Common issues fixed by reflection:
- Removing SQL markdown formatting (````sql`)
- Fixing column name errors
- Improving query logic and structure
- Ensuring proper aggregation functions