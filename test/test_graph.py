"""
tests networks and graphs
"""
import json
import lxml
from pathlib import Path

from amilib.ami_graph import AmiGraph
from amilib.ami_html import HtmlLib
from amilib.util import Util
from amilib.xml_lib import XmlLib
from test.resources import Resources
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

    def test_extract_toc_graph_from_report_toplevel(self):
        """
        read webpage from IPCC report (WG1/2/3) and extract network of components.
        Will probably not work with actual webpages on web because we need to use headless
        browser. Here we use pre-downloaded page in test/ directory
        """
        for wg in ["wg1", "wg2", "wg3"]:
            ar6 = Path(Resources.TEST_RESOURCES_DIR, "ar6")
            IN_WG = Path(ar6, wg)
            OUT_WG = Path(Resources.TEMP_DIR, "ipcc", wg)
            inpath = Path(IN_WG, "toplevel.html")
            assert inpath.exists(), f"inpath {inpath} should exist"
            outpath = Path(OUT_WG, "toplevel.html")
            html_elem = HtmlLib.parse_html(inpath)
            assert html_elem is not None
            commands = Path(ar6, "edit_toplevel.json")
            commands_dict = json.load(open(commands))
            HtmlLib.execute_commands(commands_dict, html_elem)
            HtmlLib.write_html_file(html_elem, outpath, debug=True)


