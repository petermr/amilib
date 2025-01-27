"""
tests networks and graphs
"""
import json
from pathlib import Path

from amilib.ami_graph import AmiGraph
from amilib.ami_html import HtmlLib, HtmlEditor
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
        editor = HtmlEditor()
        for wg in ["wg1", "wg2", "wg3"]:
            ar6 = Path(Resources.TEST_RESOURCES_DIR, "ar6")
            IN_WG = Path(ar6, wg)
            OUT_WG = Path(Resources.TEMP_DIR, "ipcc", wg)
            inpath = Path(IN_WG, "toplevel.html")

            editor.read_html(inpath)
            json_path = Path(ar6, "edit_toplevel.json")
            logger.info(f"json commands {json_path}")
            editor.read_commands(json_path)
            editor.execute_commands()
            editor.add_element(parent_xpath="/html/head", tag="style", text="div {border: solid 1px red; margin: 5px;}")

            outpath = Path(OUT_WG, "toplevel.html")
            HtmlLib.write_html_file(editor.html_elem, outpath, debug=True)

    def test_strip_single_child_divs(self):
        """
        takes result of applying json commands ("edited_toplevel.html") and
        strips single_child divs
        """
        for wg in ["wg1" , "wg2", "wg3"]:
            inpath = Path(Resources.TEST_RESOURCES_DIR, "ar6", wg, "edited_toplevel.html")
            html_elem = HtmlLib.parse_html(inpath)
            HtmlLib.remove_single_child_divs(html_elem)
            outfile = Path(Resources.TEMP_DIR, "ipcc", wg, "stripped_toplevel.html")
            HtmlLib.write_html_file(html_elem, outfile, debug=True)

    def test_create_toc_tree_graphviz(self):
        """
        wg1 toplevel page with nested divs
        experimental
        """
        for wg in ["wg1", "wg2", "wg3"]:
            print(f"**** current wg {wg}")
            inpath = Path(Resources.TEST_RESOURCES_DIR, "ar6", wg, "stripped_toplevel.html")
            html_elem = HtmlLib.parse_html(inpath)
            ul = AmiGraph.create_nested_uls_from_nested_divs(html_elem)
            outfile = Path(Resources.TEMP_DIR, "ipcc", wg, "toc.html")
            HtmlLib.write_html_file(ul, outfile, debug=True)

    def test_toc_workflow(self):
        """
        creates tocs and trees from toplevel HTML
        adds the components above together
        NEEDS TIDYING
        """
        editor = HtmlEditor()
        for wg in ["wg1", "wg2", "wg3"]:
            print(f"**** current wg {wg}")
            ar6 = Path(Resources.TEST_RESOURCES_DIR, "ar6")
            IN_WG = Path(ar6, wg)
            OUT_WG = Path(Resources.TEMP_DIR, "ipcc", wg)
            inpath = Path(IN_WG, "toplevel.html")

            # apply edit commands
            editor.read_html(inpath)
            json_path = Path(ar6, "edit_toplevel.json")
            logger.info(f"json commands {json_path}")
            editor.read_commands(json_path)
            editor.execute_commands()
            # add box style (not yet implemented in commands
            editor.add_element(parent_xpath="/html/head", tag="style", text="div {border: solid 1px red; margin: 5px;}")

            outpath = Path(OUT_WG, "edited_toplevel.html")
            HtmlLib.write_html_file(editor.html_elem, outpath, debug=True)

            #  read what we have written

            inpath = outpath
            html_elem = HtmlLib.parse_html(inpath)
            HtmlLib.remove_single_child_divs(html_elem)
            outfile = Path(Resources.TEMP_DIR, "ipcc", wg, "stripped_toplevel.html")
            HtmlLib.write_html_file(html_elem, outfile, debug=True)

            # read what we have written
            inpath = outpath
            html_elem = HtmlLib.parse_html(inpath)
            ul = AmiGraph.create_nested_uls_from_nested_divs(html_elem)
            outfile = Path(Resources.TEMP_DIR, "ipcc", wg, "toc.html")
            HtmlLib.write_html_file(ul, outfile, debug=True)






