import ollama
import sys

class MicromodelEngine:
    """
    Manages the local micromodel (via Ollama) and handles SQL generation.
    Optimized for specialized Text-to-SQL tasks.
    """
    def __init__(self, model_name="phi3.5:latest"):
        self.model_name = model_name
        self._ensure_model()

    def _ensure_model(self):
        """Verify the model exists in Ollama, pull if missing."""
        try:
            ollama.show(self.model_name)
        except Exception:
            print(f"[*] Micromodel '{self.model_name}' not found locally. Pulling... (Please wait)")
            try:
                ollama.pull(self.model_name)
            except Exception as e:
                print(f"[!] Error pulling model: {e}")
                sys.exit(1)

    def generate_sql(self, question, schema_context):
        """
        Translates natural language to T-SQL using the micromodel.
        """
        system_prompt = f"""You are a specialized Text-to-SQL micromodel. 
Your task is to generate a valid MSSQL (T-SQL) query based on the user's question and the provided schema.

### Database Schema Context:
{schema_context}

### Rules:
1. Output ONLY the raw SQL code. No explanation, no markdown backticks.
2. If the user asks for something that cannot be answered by the schema, respond with "-- ERROR: Schema doesn't contain this data".
3. Use standard PostgreSQL syntax (use double quotes for identifiers only if necessary).
4. Ensure the query is compatible with PostgreSQL.
"""

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': question}
                ],
                options={'temperature': 0} # Deterministic for SQL
            )
            
            sql = response['message']['content'].strip()
            # Clean up unintended markdown or common LLM prefixes
            sql = sql.replace("```sql", "").replace("```", "").strip()
            if sql.lower().startswith("sql"):
                sql = sql[3:].strip()
                
            return sql
        except Exception as e:
            return f"-- ERROR: Model failure: {str(e)}"

if __name__ == "__main__":
    # Test block
    engine = MicromodelEngine()
    test_schema = "Table: [Employees] (ID, Name, Salary)"
    print(engine.generate_sql("Who makes the most money?", test_schema))
