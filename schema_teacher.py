import sqlalchemy
from sqlalchemy import create_engine, inspect, text
import os
from dotenv import load_dotenv

load_dotenv()

class SchemaTeacher:
    """
    Extracts MSSQL schema metadata and formats it for the Micromodel.
    Also handles the execution of generated SQL.
    """
    def __init__(self, connection_string=None):
        self.connection_string = connection_string or os.getenv("DATABASE_URL")
        if not self.connection_string:
            raise ValueError("DATABASE_URL environment variable is not set. Please check your .env file.")
        
        self.engine = create_engine(self.connection_string)

    def get_full_schema_context(self):
        """
        Returns a string representation of the database schema (Tables, Columns, Types, FKs).
        This is what 'teaches' the Micromodel about your specific database.
        """
        inspector = inspect(self.engine)
        context_parts = []
        
        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            col_strings = [f"{c['name']} ({c['type']})" for c in columns]
            
            table_info = f"Table: [{table_name}]\nColumns: {', '.join(col_strings)}"
            
            # Foreign keys for relationship awareness
            fks = inspector.get_foreign_keys(table_name)
            fk_strings = [f"{table_name}.[{fk['constrained_columns'][0]}] references {fk['referred_table']}.[{fk['referred_columns'][0]}]" for fk in fks]
            
            if fk_strings:
                table_info += f"\nRelationships: {'; '.join(fk_strings)}"
            
            context_parts.append(table_info)
            
        return "\n\n".join(context_parts)

    def execute(self, sql):
        """Executes the SQL query and returns rows + headers."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                headers = list(result.keys())
                rows = [dict(r) for r in result.mappings()]
                return {"success": True, "data": rows, "headers": headers}
        except Exception as e:
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # Internal test
    st = SchemaTeacher()
    print("Extracted Schema Context:")
    print(st.get_full_schema_context())
