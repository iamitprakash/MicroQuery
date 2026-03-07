from schema_teacher import SchemaTeacher
from micromodel_engine import MicromodelEngine
import pandas as pd

def run_test():
    teacher = SchemaTeacher()
    engine = MicromodelEngine()
    
    schema_context = teacher.get_full_schema_context()
    
    test_questions = [
        "What are the top 5 products by total sales revenue?",
        "Which city has the highest number of customers?",
        "Show me the names of employees who have handled more than 50 orders.",
        "What is the total revenue for the 'Electronics' category?"
    ]
    
    for q in test_questions:
        print(f"\n[?] Question: {q}")
        sql = engine.generate_sql(q, schema_context)
        print(f"[*] Generated SQL:\n{sql}")
        
        result = teacher.execute(sql)
        if result["success"]:
            print("[+] Execution Success!")
            df = pd.DataFrame(result["data"])
            print(df.head())
        else:
            print(f"[!] Execution Failed: {result['error']}")

if __name__ == "__main__":
    run_test()
