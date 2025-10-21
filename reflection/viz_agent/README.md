# Visualization Agent with Reflection - Chart Improvement

This activity demonstrates the reflection design pattern for data visualization, where one LLM generates matplotlib charts and another critiques and improves them through iterative feedback.

## Overview

The visualization agent follows a reflection-based workflow:
1. **Generate**: Create matplotlib code from natural language instruction
2. **Execute**: Run the code to generate the initial chart
3. **Evaluate**: Have another LLM critique the chart by analyzing the image
4. **Refine**: Improve the visualization code based on feedback
5. **Compare**: Generate side-by-side comparison of original vs improved charts

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

- `visualization.ipynb` - Main notebook demonstrating visualization reflection workflow
- `utils.py` - Utility functions for image processing and chart generation
- `coffee_sales.csv` - Sample dataset with coffee shop sales data
- Generated outputs:
  - `original_chart.jpg` - Initial visualization
  - `refined_chart.jpg` - Improved visualization after feedback
  - `side_by_side_*.jpg` - Comparison images
  - `logs_*.txt` - Evaluation feedback logs

## Data Schema

`coffee_sales.csv` contains:
- `date` (M/D/YY) - Sale date
- `time` (HH:MM) - Sale time
- `cash_type` - Payment method (card/cash)
- `card` - Credit card identifier
- `price` - Sale amount in dollars
- `coffee_name` - Type of coffee drink
- Calculated: `quarter`, `month`, `year`

## Running the Activity

1. **Open and run the notebook**:
   - Open `visualization.ipynb` in Jupyter
   - Run all cells sequentially

2. **The notebook will**:
   - Load coffee sales data
   - Execute visualization workflows with different model combinations
   - Generate charts and improvement feedback
   - Create side-by-side comparisons

3. **Example workflow**:
   ```python
   results = run_workflow("coffee_sales.csv", 
                          "Create a chart showing year-over-year Q1 sales by drink type.", 
                          generation_model="openai:gpt-4o-mini", 
                          evaluation_model="anthropic:claude-3-5-sonnet-20241022")
   ```

## Key Learning Points

- **Visual Reflection**: How LLMs can critique visual content through image analysis
- **Code Improvement**: Iterative enhancement of matplotlib code based on feedback
- **Multi-Modal AI**: Using vision-capable models to evaluate chart quality
- **Model Specialization**: Different models for generation vs evaluation tasks
- **Comparative Analysis**: Side-by-side evaluation of improvements

## Expected Outputs

The workflow demonstrates visual improvement through reflection:

1. **Original Chart**: Initial visualization with potential issues (formatting, clarity, etc.)
2. **Evaluation Feedback**: Detailed critique of chart quality, readability, and effectiveness
3. **Refined Chart**: Improved version addressing the feedback points
4. **Side-by-Side Comparison**: Visual comparison showing the improvements
5. **Feedback Logs**: Detailed evaluation reasoning saved to text files

## Example Improvements

Common enhancements made through reflection:
- Better color schemes and contrast
- Improved axis labels and titles
- Enhanced data presentation clarity
- More professional styling and formatting
- Better chart type selection for the data

## Model Combinations Tested

The notebook compares different LLM pairings:
- GPT-4o-mini (generation) + Claude-3.5-Sonnet (evaluation)
- GPT-4o-mini (generation) + GPT-4o (evaluation)

This demonstrates how different AI models can collaborate effectively in a multi-agent reflection system.