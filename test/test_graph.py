"""
tests networks and graphs
"""
import json
from pathlib import Path


import networkx as nx
from matplotlib import pyplot as plt

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

    """
    There are two files which are used:-
    1. TEMP Directory - Resources.TEMP_DIR, "ipcc"
    2. Original Directory - Resources.TEST_RESOURCES_DIR, "ar6"
    
    Thus, confusion in directory path led to not forming of wg2 and wg3 toc.
    Now, solved by simply changing the directory at required places.
    """

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

            #Checking whether the execute command is working or not
            try:
                logger.info(f"Executing commands for {wg} using {json_path}")
                editor.execute_commands()
            except Exception as e:
                logger.error(f"Error while executing commands for {wg}: {e}")
            editor.add_element(parent_xpath="/html/head", tag="style", text="div {border: solid 1px red; margin: 5px;}")

            #Constructs the output file path inside the TEMP directory
            outpath = Path(OUT_WG, "toplevel.html")
            HtmlLib.write_html_file(editor.html_elem, outpath, debug=True)

            #Constructs a path to save the edited HTML in the original Working Group folder
            edited_path = Path(IN_WG, "edited_toplevel.html")
            HtmlLib.write_html_file(editor.html_elem, edited_path, debug=True)

    def test_strip_single_child_divs(self):
        """
        takes result of applying json commands ("edited_toplevel.html") and
        strips single_child divs
        """
        for wg in ["wg1" , "wg2", "wg3"]:

            """
            "toplevel.html" and "edited_toplevel.html" is similar, there is no difference.
            Thus, for classification using a single file, i.e. "edited_toplevel.html"
            Just there is difference of directory.
            """

            inpath = Path(Resources.TEST_RESOURCES_DIR, "ar6", wg, "edited_toplevel.html")
            #Check if the file exists before proceeding
            if not inpath.exists():
                logger.error(f"Missing file: {inpath}, skipping {wg}")
                continue #Skip this WG if the file doesn't exist

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
    """
    This is the main function where the overall workflow is executed.
    1. Reading of toplevel.html and processing with help of json file(edit_toplevel.json) to modify the html file.
    2. The output file is parsed again to clean up unnecessary tags(Html.remove_single_child_divs).
    3. Then again the output is further processed to create a nested list (<ul> and <li>). The html file is in format - toc.html
    4. Then graph is created and visualized by taking the toc.html 
    These all process is looped through all the three working groups (wg1, wg2, wg3).
    
    REQUIREMENTS:- 1. Networkx
                   2. Matplotlib
    """

    def test_toc_workflow(self):
        """
        creates tocs and trees from toplevel HTML
        adds the components above together
        NEEDS TIDYING
        """
        editor = HtmlEditor()
        networks = {}
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
            network = self.create_network_from_toc(toc_path)


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
                self.visualize_graph_with_networkx(network, title = f"Network for {wg}", wg = wg)



    def create_network_from_toc(self, toc_path):
        """
        Creates the graph from a nested list which is present in toc.html.
        This is a function which is called in 'test_toc_workflow'.

        """
        graph = nx.DiGraph()
        html_elem = HtmlLib.parse_html(toc_path)
        root_ul = html_elem.find(".//ul")

        def add_nodes_to_network(ul, parent = None):
            for li in ul.findall(".//li"):
                text = li.text.strip() if li.text else ""
                # Add node to network
                graph.add_node(text)
                if parent:
                    # Adding edge to network
                    graph.add_edge(parent, text)
                nested_ul = li.find(".//ul")
                if nested_ul is not None:
                    add_nodes_to_network(nested_ul, parent = text)

        add_nodes_to_network(root_ul)
        return graph


    def visualize_graph_with_networkx(self, graph, title="Graph", wg=None):
        """
        Visualizes the graph using a fallback layout and saves it as an image.

        Parameters:
            graph: The NetworkX graph to visualize.
            title: Title of the graph.
            wg: Working group name (used for saving files).
            Used layout as spring_layout.
        """

        pos = nx.spring_layout(graph,  k=2.0)

        """
        Attributes to draw the network
        """
        plt.figure(figsize=(12, 8))
        nx.draw(
            graph,
            pos,
            with_labels=True,
            node_size=2000,
            node_color="skyblue",
            font_size=10,
            font_weight="bold",
            edge_color="gray",
            arrows=True,
            width=1.5
        )
        plt.title(title)

        """
        Saving the network as png.
        """
        if wg:
            image_path = Path(Resources.TEMP_DIR, "ipcc", wg, f"{wg}_nxgraph.png")
            plt.savefig(image_path, format="PNG", bbox_inches="tight")
            print(f"Graph image saved as {image_path}")
        """
        To Save the graph as a DOT file
        if wg:
            dot_path = Path(Resources.TEMP_DIR, "ipcc", wg, f"{wg}_graph.dot")
            nx.nx_pydot.write_dot(graph, dot_path)
            print(f"Graph saved as DOT file: {dot_path}")

        To Save the graph as a GML file
        if wg:
            gml_path = Path(Resources.TEMP_DIR, "ipcc", wg, f"{wg}_graph.gml")
            nx.write_gml(graph, gml_path)
            print(f"Graph saved as GML file: {gml_path}")

        To Show the graph (optional)
        plt.show()
        """

