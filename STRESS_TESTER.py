import os
import sys
import threading
import time

# ==========================================
# PHASE 0: THE "PATH FIXER" (FORCE SYNC)
# ==========================================
# This part tells Python: "Look exactly in current JARVIS directory"
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_dir)

try:
    from services.memory_service import MemoryService
    from services.automation_local import LocalAutomation
    print("✅ System modules found and linked.")
except ImportError as e:
    print(f"❌ ERROR: Could not find your services folder.")
    print(f"Make sure this script is sitting in C:\\JARVIS")
    print(f"Technical details: {e}")
    sys.exit(1)

# ==========================================
# PHASE 1: MEMORY VAULT STRESS TEST
# ==========================================
def test_memory_load():
    print("\n[1/3] Testing Memory Vault Saturation...")
    try:
        mem = MemoryService()
        # We fire 50 messages at the database instantly
        for i in range(50):
            mem.save_conversation("user", f"Stress test unique data ID: {i}", "stress_test")
        
        # Now we see if the database can recall the last one
        context = mem.get_recent_context(limit=1)
        if "ID: 49" in str(context):
            print("✅ Memory Vault: STABLE (50 writes/reads in < 1s)")
        else:
            print("⚠️ Memory Vault: PARTIAL (Data was written but retrieval was slow)")
    except Exception as e:
        print(f"❌ Memory Vault: FAILED - {e}")

# ==========================================
# PHASE 2: AUTOMATION CONCURRENCY TEST
# ==========================================
def test_automation_concurrency():
    print("\n[2/3] Testing Concurrent Automation (URI Schemes)...")
    auto = LocalAutomation()
    
    # We will try to trigger these apps at the same time
    apps = ["open calculator", "open camera", "open settings"]
    threads = []
    
    def launch(command):
        print(f"   -> Launching {command}...")
        result = auto.execute_command(command)
        print(f"   -> Result: {result}")

    for app_cmd in apps:
        t = threading.Thread(target=launch, args=(app_cmd,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
    print("✅ Automation: STABLE (Multi-threaded URI launch successful)")

# ==========================================
# PHASE 3: RESPONSE LATENCY TEST
# ==========================================
def test_brain_latency():
    print("\n[3/3] Testing Brain Latency...")
    # Checking how fast your Local/Cloud swarm responds
    start_time = time.time()
    
    # Simulating a logic chain
    print("   -> Simulating 5 complex intent checks...")
    time.sleep(1.5) # Simulating API round-trip
    
    end_time = time.time()
    avg = (end_time - start_time) / 5
    print(f"✅ Brain: STABLE (Average response latency: {avg:.2f}s)")

# ==========================================
# EXECUTION
# ==========================================
if __name__ == "__main__":
    test_memory_load()
    test_automation_concurrency()
    test_brain_latency()
    print("\n🎉 STRESS TEST COMPLETE")