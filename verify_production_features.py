from micromodel_engine import MicromodelEngine
from schema_teacher import SchemaTeacher
import time

def verify_advanced_features():
    teacher = SchemaTeacher()
    engine = MicromodelEngine(model_name="phi3.5")
    
    print("[*] 1. Testing Intelligent Schema Pruning...")
    question = "What are the names of our customers?"
    all_tables = ["customers", "orders", "order_details", "products", "categories", "suppliers", "shippers", "product_reviews", "employees"]
    
    start = time.time()
    relevant_tables = engine.get_relevant_tables(question, all_tables)
    print(f"[+] Pruning identified tables: {relevant_tables} (Time: {time.time() - start:.2f}s)")
    
    print("\n[*] 2. Testing SQL Generation with Pruned Schema...")
    sql = engine.generate_sql(question, teacher)
    print(f"[+] Generated SQL:\n{sql}")
    
    print("\n[*] 3. Testing SQL Caching...")
    start_cache = time.time()
    cached_sql = engine.generate_sql(question, teacher)
    cache_time = time.time() - start_cache
    print(f"[+] Cached SQL retrieval: {cache_time:.4f}s")
    if cache_time < 0.01:
        print("[PASS] Cache hit confirmed!")
    else:
        print("[FAIL] Cache miss.")

    print("\n[+] Advanced Features Verification Complete!")

if __name__ == "__main__":
    verify_advanced_features()
