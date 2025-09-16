    """sometimes graphviz doesn't install_
    """
import graphviz

def test_digraph
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
