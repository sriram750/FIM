import sys
from pathlib import Path

# Add agent-windows/src to sys.path
agent_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(agent_root))
sys.path.insert(0, str(agent_root / "src"))
