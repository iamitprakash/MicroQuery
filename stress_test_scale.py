from schema_teacher import SchemaTeacher
from micromodel_engine import MicromodelEngine
import pandas as pd
import time

def run_stress_test():
    teacher = SchemaTeacher()
    engine = MicromodelEngine()
    
    schema_context = teacher.get_full_schema_context()
    
    stress_questions = [
        "Top category by total revenue?",
        "Average product rating for each category?",
        "Top 5 customers by order count",
        "Total revenue for the last 30 days?",
        "Names of shippers and their total freight income?"
    ]
    
    for q in stress_questions:
        print(f"\n[?] Question: {q}")
        start_gen = time.time()
        sql = engine.generate_sql(q, schema_context)
        gen_time = time.time() - start_gen
        print(f"[*] Generated SQL ({gen_time:.2f}s):\n{sql}")
        
        start_exec = time.time()
        result = teacher.execute(sql)
        exec_time = time.time() - start_exec
        
        if result["success"]:
            print(f"[+] Execution Success! ({exec_time:.2f}s)")
            df = pd.DataFrame(result["data"])
            print(df.head())
        else:
            print(f"[!] Execution Failed ({exec_time:.2f}s): {result['error']}")

if __name__ == "__main__":
    run_stress_test()
