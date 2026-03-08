import ollama
import sys

class MicromodelEngine:
    """
    Manages the local micromodel (via Ollama) and handles SQL generation.
    Optimized for specialized Text-to-SQL tasks.
    """
    def __init__(self, model_name="phi3.5:latest"):
        self.model_name = model_name
        self.sql_cache = {} # Natural Language -> SQL

    def _ensure_model(self):
        """Verify the model exists in Ollama."""
        try:
            ollama.show(self.model_name)
            return True
        except Exception:
            return False

    def get_relevant_tables(self, question, all_tables_list):
        """Step 1: Identify which tables are needed for the question."""
        prompt = f"""Identify the minimal set of database tables required to answer this question.
Question: {question}
Available Tables: {', '.join(all_tables_list)}

Output ONLY a comma-separated list of table names. No explanation."""
        
        try:
            import ollama
            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0}
            )
            tables_str = response['message']['content'].strip()
            # Clean up and validate
            found_tables = [t.strip() for t in tables_str.split(',') if t.strip() in all_tables_list]
            return found_tables if found_tables else all_tables_list
        except:
            return all_tables_list

    def generate_sql(self, question, teacher):
        """
        Translates natural language to SQL using Pruning and Caching.
        """
        # 1. Runtime model check
        if not self._ensure_model():
            return f"-- ERROR: Model '{self.model_name}' not found in Ollama. Run 'ollama pull {self.model_name}'."

        # 2. Check Cache
        if question in self.sql_cache:
            return self.sql_cache[question]

        # 2. Schema Pruning
        from sqlalchemy import inspect
        all_tables = inspect(teacher.engine).get_table_names()
        relevant_tables = self.get_relevant_tables(question, all_tables)
        schema_context = teacher.get_table_schema_context(relevant_tables)

        system_prompt = f"""You are a specialized Text-to-SQL micromodel. 
Generate valid PostgreSQL query based on the schema.

### Schema:
{schema_context}

### Rules:
1. Output RAW SQL only. No markdown.
2. PostgreSQL syntax.
3. Always suggest a chart if numeric values exist. 
   Formats: 
   -- CHART: <Bar|Line|Area|Pie|Donut|Heatmap> | REASON: <Explanation>
   Use Donut for composition, Heatmap for multi-metric correlations.
"""

        try:
            import ollama
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': question}
                ],
                options={'temperature': 0}
            )
            
            sql = response['message']['content'].strip()
            sql = sql.replace("```sql", "").replace("```", "").strip()
            if sql.lower().startswith("sql"):
                sql = sql[3:].strip()
            
            # Simple extractor for SQL statements
            import re
            parts = re.split(r'\n\s*\n', sql)
            if parts and parts[0].upper().startswith(("SELECT", "WITH")):
                 sql = parts[0]
            if ";" in sql:
                sql = sql.split(";")[0] + ";"
            
            final_sql = sql.strip()
            self.sql_cache[question] = final_sql # Cache it
            return final_sql
        except Exception as e:
            return f"-- ERROR: Model failure: {str(e)}"

if __name__ == "__main__":
    # Test block
    engine = MicromodelEngine()
    test_schema = "Table: [Employees] (ID, Name, Salary)"
    print(engine.generate_sql("Who makes the most money?", test_schema))
