"""sometimes graphviz doesn't install_
"""
import graphviz
from test.test_all import AmiAnyTest

class GraphvizTest(AmiAnyTest):

    def test_smoke(self):
        # Test basic functionality
        try:
            dot = graphviz.Digraph(comment='Test')
            dot.node('A', 'Node A')
            dot.node('B', 'Node B')
            dot.edge('A', 'B')
            print("✅ Graphviz is working correctly!")
            print("Available attributes:", [attr for attr in dir(graphviz) if not attr.startswith('_')])
        except Exception as e:
            print(f"❌ Error: {e}")
            raise e
