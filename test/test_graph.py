"""
tests networks and graphs
"""
import json
from pathlib import Path
import re

import graphviz
import networkx as nx

from amilib.ami_graph import AmiGraph
from amilib.ami_html import HtmlLib, HtmlEditor
from amilib.file_lib import FileLib
from amilib.util import Util
from amilib.xml_lib import XmlLib
from test.resources import Resources
from test.test_all import AmiAnyTest

logger = Util.get_logger(__name__)
class AmiGraphTest(AmiAnyTest):
    """
    collection of tests for `amilib.graph`
    """

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
            logger.info(f"json commands {json_path=}")
            editor.read_commands(json_path)
            editor.execute_commands()
            editor.add_element(parent_xpath="/html/head", tag="style", text="div {border: solid 1px red; margin: 5px;}")

            outpath = Path(OUT_WG, "toplevel.html")
            HtmlLib.write_html_file(editor.html_elem, outpath, debug=True)
            assert outpath.exists()

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
        collects the components above together
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
            assert outfile.exists()


    def test_chapter_graph(self):
        """
        simple example of extracting tree from chapter
        """
        wg = "wg2"
        chap = "Chapter05"
        # create filename from test/resources
        infile = Path(Resources.TEST_RESOURCES_DIR, "ipcc", "cleaned_content", wg, chap, "html_with_ids.html")
        logger.info(f"reading from {infile=}")
        # outfile = Path(Resources.TEMP_DIR, "ipcc", wg, chap, "network.svg")
        
        # parse infile to HTML object
        html = HtmlLib.parse_html(infile)
        assert html is not None
        # sections to be extracted using regexes
        WANTED_ID_RE = "acknowledgements|Executive|frequently\\-asked\\-questions|\\d+\\.\\d+"
        # sections to exclude
        UNWANTED_ID_RE = ".*siblings"
        # highest level div on chapter page
        top_div = html.xpath("/html/body//div[div[@class='h1-container']]")[0]
        assert top_div is not None
        # maximum depth to recurse
        maxlev = 99
        top_id = wg
        gv_output = Path(Resources.TEMP_DIR, "ipcc", wg, chap, f"toc.gv")
        if gv_output.exists():
            FileLib.delete_file(gv_output)
            logger.info(f"file deleted {gv_output.absolute()=}")
        assert not gv_output.exists(), f"deleted {gv_output.absolute()}"
        graph = graphviz.Graph(top_id, filename=str(gv_output), engine='fdp')

        graph.edge(wg, chap)

        # iterate over children of top,
        for div in top_div.xpath("div[@class='h1-container']"):
            # get "id" attribute value
            id = self.get_cleaned_id(div)
            # reject if id is not in selected list or in not-selected list
            if not re.match(WANTED_ID_RE, id) or re.match(UNWANTED_ID_RE, id):
                continue
            logger.info(f"add edge {chap}->{id}")
            graph.edge(chap, id)
            self.list_divs_with_ids(div, maxlevel=maxlev, graph=graph)

        if graph is not None:
            graph.view()

    def get_cleaned_id(self, div):
        id = div.get("id")
        id = id.replace("-", "_")
        id = id.replace("\"", "")
        id = id.split(":")[0]
        logger.info(f"{id=}")

        return id

    """
            import graphviz
            gv_output = 'fdpclust.gv'
            ipcc = graphviz.Graph('IPCC', filename=gv_output, engine='fdp')
    
    
            with ipcc.subgraph(name='clusterIPCC') as a:
                a.edge('toc1', 'ipcc')
    
    
            ipcc.view()
    """


# """
# There are two files which are used:-
# 1. TEMP Directory - Resources.TEMP_DIR, "ipcc"
# 2. Original Directory - Resources.TEST_RESOURCES_DIR, "ar6"
#
# Thus, confusion in directory path led to not forming of wg2 and wg3 toc.
# Now, solved by simply changing the directory at required places.
# """

# def test_extract_toc_graph_from_report_toplevel1(self):
#     """
#     read webpage from IPCC report (WG1/2/3) and extract network of components.
#     Will probably not work with actual webpages on web because we need to use headless
#     browser. Here we use pre-downloaded page in test/ directory
#     """
#     editor = HtmlEditor()
#     for wg in ["wg1", "wg2", "wg3"]:
#         ar6 = Path(Resources.TEST_RESOURCES_DIR, "ar6")
#         IN_WG = Path(ar6, wg)
#         OUT_WG = Path(Resources.TEMP_DIR, "ipcc", wg)
#         inpath = Path(IN_WG, "toplevel.html")
#
#         editor.read_html(inpath)
#         json_path = Path(ar6, "edit_toplevel.json")
#         logger.info(f"json commands {json_path}")
#         editor.read_commands(json_path)
#
#         #Checking whether the execute command is working or not
#         try:
#             logger.info(f"Executing commands for {wg} using {json_path}")
#             editor.execute_commands()
#         except Exception as e:
#             logger.error(f"Error while executing commands for {wg}: {e}")
#         editor.add_element(parent_xpath="/html/head", tag="style", text="div {border: solid 1px red; margin: 5px;}")
#
#         #Constructs the output file path inside the TEMP directory
#         outpath = Path(OUT_WG, "toplevel.html")
#         HtmlLib.write_html_file(editor.html_elem, outpath, debug=True)
#
#         #Constructs a path to save the edited HTML in the original Working Group folder
#         edited_path = Path(IN_WG, "edited_toplevel.html")
#         HtmlLib.write_html_file(editor.html_elem, edited_path, debug=True)
#
# def test_strip_single_child_divs1(self):
#     """
#     takes result of applying json commands ("edited_toplevel.html") and
#     strips single_child divs
#     """
#     for wg in ["wg1" , "wg2", "wg3"]:
#
#         """
#         "toplevel.html" and "edited_toplevel.html" is similar, there is no difference.
#         Thus, for classification using a single file, i.e. "edited_toplevel.html"
#         Just there is difference of directory.
#         """
#
#         inpath = Path(Resources.TEST_RESOURCES_DIR, "ar6", wg, "edited_toplevel.html")
#         #Check if the file exists before proceeding
#         if not inpath.exists():
#             logger.error(f"Missing file: {inpath}, skipping {wg}")
#             continue #Skip this WG if the file doesn't exist
#
#         html_elem = HtmlLib.parse_html(inpath)
#         HtmlLib.remove_single_child_divs(html_elem)
#         outfile = Path(Resources.TEMP_DIR, "ipcc", wg, "stripped_toplevel.html")
#         HtmlLib.write_html_file(html_elem, outfile, debug=True)

    def test_junk(self):
        pass

    def test_create_toc_tree_graphviz1(self):
        """
        wg1 toplevel page with nested divs
        experimental
        """
        for wg in ["wg1", "wg2", "wg3"]:
            """ 
                        Taking the output from function 'test_strip_single_child_divs'.
                        The output file is in 'ipcc' directory not in 'ar6'.
                        In this function we are taking the 'ar6' directory, thus creating problem.
                        Changed the directory to the 'ipcc'.
            """

            print(f"**** current wg {wg}")

            #Changing 'Resources.TEST_RESOURCES_DIR' to the 'Resources.TEMP_DIR'
            inpath = Path(Resources.TEMP_DIR, "ipcc", wg, "stripped_toplevel.html")
            html_elem = HtmlLib.parse_html(inpath)
            ul = AmiGraph.create_nested_uls_from_nested_divs(html_elem)
            outfile = Path(Resources.TEMP_DIR, "ipcc", wg, "toc.html")
            HtmlLib.write_html_file(ul, outfile, debug=True)


    def test_toc_workflow1(self):
        """
        creates tocs and trees from toplevel HTML
        adds the components above together
        NEEDS TIDYING
        """
        editor = HtmlEditor()
        networks = {}
        # wgs = ["wg1", "wg2", "wg3"]
        wgs = ["wg1"]

        for wg in wgs:
            logger.info(f"**** current wg {wg}")
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
            """
            Parsing the edited_toplevel.html to remove the unnecessary tags.
            making it stripped_toplevel.html
            """
            inpath = outpath
            html_elem = HtmlLib.parse_html(inpath)
            HtmlLib.remove_single_child_divs(html_elem)
            outfile = Path(Resources.TEMP_DIR, "ipcc", wg, "stripped_toplevel.html")
            HtmlLib.write_html_file(html_elem, outfile, debug=True)


            # read what we have written
            """
            Taking the 'stripped_toplevel.html' and converting into nested list.
            """
            inpath = outpath
            html_elem = HtmlLib.parse_html(inpath)
            ul = AmiGraph.create_nested_uls_from_nested_divs(html_elem)
            outfile = Path(Resources.TEMP_DIR, "ipcc", wg, "toc.html")
            HtmlLib.write_html_file(ul, outfile, debug=True)


            """
            Taking the toc.html and creating graph by the function - 'create_graph_from_toc' that uses "Networkx".
            """
            # Parse the toc.html and create a graph
            toc_path = Path(Resources.TEMP_DIR, "ipcc", wg, "toc.html")
            ami_graph = AmiGraph()
            network = ami_graph.create_network_from_toc(toc_path)


            """
            Made a dictionary to take different working group (wg1, wg2, wg3)
            """
            networks[wg] = network


            """
            Visualization of the network after creating it.
            Saved it in png format.
            """
            #Visualize the network for each wg using Networkx
            for wg, network in networks.items():
                print(f"Visualizing graphs for {wg}")
                AmiGraph.visualize_graph_with_networkx(network, title = f"Network for {wg}", wg = wg)




    def list_divs_with_ids(self, parent_div, maxlevel, graph=None):
        UNWANTED_ID_RE = ".*siblings"
        parent_id = self.get_cleaned_id(parent_div)
        if maxlevel >= 0:
            # find children
            divs = parent_div.xpath("div")
            for div in divs:
                div_id = div.get('id')
                div_id = div_id.replace("-", "_")
                if div_id is None or re.match(UNWANTED_ID_RE, div_id):
                    continue
                # print(f"add node {div_id=}")
                logger.info(f"add edge {parent_id}->{div_id}")
                if graph is not None:
                    graph.edge(parent_id, div_id)
                # TODO write nodes and edges to filesystem for input to network
                # use context manager
                # with open(node_edge_file, "r") as f:
                #     for node in nodes:
                #         f.write(node)
                #     for edge in edges:
                #         f.write(edge)
                self.list_divs_with_ids(div, maxlevel-1, graph=graph)


    def test_graphviz2(self):
        """
        probably a duplicate
        """
        import graphviz
        gv_output = 'fdpclust.gv'
        ipcc = graphviz.Graph('IPCC', filename=gv_output, engine='fdp')

        # glossary = ipcc.node('glossaryx', URL='https://ipcc.ch')
        ipcc.edge('ipcc', 'glossary')

        with ipcc.subgraph(name='clusterIPCC') as a:
            a.edge('toc1', 'ipcc')

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
