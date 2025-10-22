#!/usr/bin/env python3
"""
Experiment: Does role assignment matter in SQL generation prompts?

Tests three prompt styles:
1. With explicit role ("You are a SQL assistant")
2. Without role (direct instruction)
3. Minimal prompt (just schema + question)
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv(project_root / ".env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Test schema
SCHEMA = """
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT,
    salary INTEGER,
    hire_date DATE
);

CREATE TABLE departments (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    budget INTEGER
);
"""

# Test questions
TEST_QUESTIONS = [
    "Find all employees in the Engineering department",
    "What is the average salary by department?",
    "List employees hired after 2020 with salary > 100000",
    "Show departments with total employee salary exceeding their budget",
]


def generate_sql_with_role(question: str, schema: str, model: str = "gpt-3.5-turbo") -> str:
    """Original prompt with explicit role assignment."""
    prompt = f"""
You are a SQL assistant. Given the schema and the user's question, write a SQL query for SQLite.

Schema:
{schema}

User question:
{question}

Respond with the SQL only.
"""
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return response.choices[0].message.content.strip()


def generate_sql_without_role(question: str, schema: str, model: str = "gpt-3.5-turbo") -> str:
    """Direct instruction without role assignment."""
    prompt = f"""
Given the schema and the user's question, write a SQL query for SQLite.

Schema:
{schema}

User question:
{question}

Respond with the SQL only.
"""
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return response.choices[0].message.content.strip()


def generate_sql_minimal(question: str, schema: str, model: str = "gpt-3.5-turbo") -> str:
    """Minimal prompt - just schema and question."""
    prompt = f"""
Schema:
{schema}

Question: {question}

SQL:
"""
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return response.choices[0].message.content.strip()


def clean_sql(sql: str) -> str:
    """Remove markdown code blocks and extra whitespace."""
    sql = sql.strip()
    if sql.startswith("```sql"):
        sql = sql[6:]
    elif sql.startswith("```"):
        sql = sql[3:]
    if sql.endswith("```"):
        sql = sql[:-3]
    return sql.strip()


def compare_prompts():
    """Compare SQL generation with different prompt styles."""
    print("=" * 80)
    print("EXPERIMENT: Role Assignment Importance in SQL Generation")
    print("=" * 80)
    print(f"\nTesting with {len(TEST_QUESTIONS)} questions")
    print(f"Model: gpt-3.5-turbo")
    print()
    
    results = []
    
    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\n{'─' * 80}")
        print(f"Question {i}: {question}")
        print(f"{'─' * 80}")
        
        # Generate with all three styles
        sql_with_role = clean_sql(generate_sql_with_role(question, SCHEMA))
        sql_without_role = clean_sql(generate_sql_without_role(question, SCHEMA))
        sql_minimal = clean_sql(generate_sql_minimal(question, SCHEMA))
        
        print("\n1️⃣  WITH ROLE ('You are a SQL assistant'):")
        print(f"   {sql_with_role}")
        
        print("\n2️⃣  WITHOUT ROLE (direct instruction):")
        print(f"   {sql_without_role}")
        
        print("\n3️⃣  MINIMAL (schema + question only):")
        print(f"   {sql_minimal}")
        
        # Compare results
        all_same = (sql_with_role == sql_without_role == sql_minimal)
        role_vs_no_role = (sql_with_role == sql_without_role)
        
        print("\n📊 Comparison:")
        if all_same:
            print("   ✅ All three prompts produced IDENTICAL SQL")
        elif role_vs_no_role:
            print("   ⚠️  Role vs No-Role: SAME")
            print("   ⚠️  Minimal: DIFFERENT")
        else:
            print("   ❌ All three prompts produced DIFFERENT SQL")
        
        results.append({
            'question': question,
            'all_same': all_same,
            'role_vs_no_role': role_vs_no_role,
            'with_role': sql_with_role,
            'without_role': sql_without_role,
            'minimal': sql_minimal,
        })
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    all_same_count = sum(1 for r in results if r['all_same'])
    role_vs_no_role_count = sum(1 for r in results if r['role_vs_no_role'])
    
    print(f"\n✅ All three identical: {all_same_count}/{len(TEST_QUESTIONS)} ({all_same_count/len(TEST_QUESTIONS)*100:.0f}%)")
    print(f"⚖️  Role vs No-Role same: {role_vs_no_role_count}/{len(TEST_QUESTIONS)} ({role_vs_no_role_count/len(TEST_QUESTIONS)*100:.0f}%)")
    
    print("\n📌 Key Findings:")
    if all_same_count == len(TEST_QUESTIONS):
        print("   • Role assignment has NO IMPACT on SQL generation")
        print("   • The model understands the task from context alone")
        print("   • You can safely remove 'You are a SQL assistant'")
    elif role_vs_no_role_count == len(TEST_QUESTIONS):
        print("   • Role assignment has MINIMAL IMPACT")
        print("   • Direct instruction works just as well")
        print("   • Minimal prompts may need more structure")
    else:
        print("   • Role assignment DOES affect output")
        print("   • Consider keeping it for consistency")
        print("   • May help with edge cases")
    
    print("\n💡 Recommendation:")
    if all_same_count >= len(TEST_QUESTIONS) * 0.75:
        print("   For SQL generation with modern LLMs, role assignment is OPTIONAL.")
        print("   Focus on clear schema and question formatting instead.")
    else:
        print("   Role assignment provides some benefit - consider keeping it.")
        print("   It may help with consistency across different query types.")
    
    return results


if __name__ == "__main__":
    try:
        results = compare_prompts()
        print("\n✅ Experiment completed successfully!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
