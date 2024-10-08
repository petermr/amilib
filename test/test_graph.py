"""
tests networks and graphs
"""
from amilib.ami_graph import AmiGraph
from amilib.util import Util
from test.test_all import AmiAnyTest

logger = Util.get_logger(__name__)
class AmiGraphTest(AmiAnyTest):

    def test_create_report(self):
        import graphviz

        ipcc = graphviz.Graph('IPCC', filename='fdpclust.gv', engine='fdp')

        glossary = ipcc.node('glossaryx', URL='https://ipcc.ch')
        ipcc.edge('ipcc','glossary')


        with ipcc.subgraph(name='clusterIPCC') as a:
            a.edge('toc1', 'ipcc')
            # {rank = same;
            # wg1.Chap01;
            # wg1.Chap02;
            # wg1.Chap03;
            # wg1.Chap04;
            # wg1.Chap05;
            # wg1.Chap06;}

            with a.subgraph(name='clusterWG1') as wg1:
                wg1.edge('wg1.Chap01', 'toc1')
                wg1.edge('wg1.Chap02', 'toc1')
                wg1.edge('wg1.Chap03', 'toc1')
                wg1.edge('wg1.Chap04', 'toc1')
                wg1.edge('wg1.Chap05', 'toc1')
                wg1.edge('wg1.Chap06', 'toc1')
            a.edge('toc2', 'ipcc')
            with a.subgraph(name='clusterWG2') as wg2:
                wg2.edge('wg2.Chap01', 'toc2')
                wg2.edge('wg2.Chap02', 'toc2')
                wg2.edge('wg2.Chap03', 'toc2')
                wg2.edge('wg2.Chap04', 'toc2')
                wg2.edge('wg2.Chap05', 'toc2')
                wg2.edge('wg2,Chap06', 'toc2')
            a.edge('toc3', 'ipcc')
            with a.subgraph(name='clusterWG3') as wg3:
                wg3.edge('wg3.Chap01', 'toc3')
                wg3.edge('wg3.Chap02', 'toc3')
                wg3.edge('wg3.Chap03', 'toc3')
                wg3.edge('wg3.Chap04', 'toc3')
                wg3.edge('wg3.Chap05', 'toc3')
                wg3.edge('wg3,Chap06', 'toc3')

        ipcc.view()

