"""
for drawing networks/graphs
"""
import re
from pathlib import Path

import graphviz
import lxml.etree as ET
import networkx as nx
from matplotlib import pyplot as plt

from amilib.ami_html import HtmlLib, logger
from amilib.file_lib import FileLib
from test.resources import Resources


class AmiGraph:
    """
    grahs can be nested?
    """

    def __init__(self):
        self.subgraphs = []
        self.graph = None
        self.html_elem = None

    def create_subgraph(self):
        subgraph = AmiGraph()
        self.subgraphs.append(subgraph)

    @classmethod
    def create_nested_uls_from_nested_divs(cls, html_elem):
        """
        treat all divs and their immediate childresn as nodes with
        edges parent->child
        """

        def _iterate_children(elem, new_html, xpath):
            children = elem.xpath(xpath)
            if (nchild := len(children)) == 0:
                return None
            ul = ET.SubElement(new_html, "ul")
            p = ET.SubElement(ul, "p")
            p.text = f"{nchild}.."
            for child in children:
                # print(f"{child.tag} => ({child.get('class')})")
                li = ET.SubElement(ul, "li")
                h = child.xpath("h1 | h2 | h3 | h4 | a")
                if h:
                    h0 = h[0]
                    li.text = h0.text
                    if h0.text is None:
                        print(f"no text for {child.tag}@({child.attrib.get('class')})")
                    else:
                        print(f" ... {h0.text}")
                else:
                    print(f"no title for {child.attrib.get('class')}")
                _iterate_children(child, li, xpath)

        body = HtmlLib.get_body(html_elem)
        new_body, new_html = HtmlLib.create_html_with_body()
        _iterate_children(body, new_body, xpath="div | header | section")
        return new_html


    def create_network_from_toc(self, toc_path):
        """
        Creates the graph from a nested list which is present in toc.html.
        This is a function which is called in 'test_toc_workflow'.

        """
        self.graph = nx.DiGraph()
        html_elem = HtmlLib.parse_html(toc_path)
        root_ul = html_elem.find(".//ul")
        root_ul.attrib["id"] = "root"
        root_ul.attrib["title"] = str(toc_path)
        return self.graph


        def add_ids_to_nodes(html_elem):
            li_nodes = html_elem.findall(".//li")
            for i, li_node in enumerate(li_nodes):
                li_node.attrib["id"] = f"li_{i}"
            print(f"li nodes {len(li_nodes)}")
            ul_nodes = html_elem.findall(".//ul")
            for i, ul_node in enumerate(ul_nodes):
                ul_node.attrib["id"] = f"ul_{i}"
            print(f"ul nodes {len(ul_nodes)}")


    def add_nodes_to_network(self, ul):
        print(f"add_nodes {ul} {ul.attrib.get('id')}")
        ul_id = ul.attrib.get("id")
        for li in ul.findall("./li"):
            li_id = li.attrib.get("id")
            print(f"{li_id}")
            text = li.text.strip() if li.text else li_id
            # Add node to network
            self.graph.add_node(li_id)
            if ul is not None:
                # Adding edge to network
                self.graph.add_edge(ul_id, li_id)
            nested_ul = li.find("./ul")
            if nested_ul is not None:
                self.add_nodes_to_network(nested_ul)

        self.add_nodes_to_network(root_ul)
        return self.graph

    @classmethod
    def visualize_graph_with_networkx(cls, graph, title="Graph", wg=None):
        """
        Visualizes the graph using a fallback layout and saves it as an image.

        Parameters:
            graph: The NetworkX graph to visualize.
            title: Title of the graph.
            wg: Working group name (used for saving files).
            Used layout as spring_layout.
        """

        assert graph is not None
        pos = nx.spring_layout(graph, k=2.0)

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

    @classmethod
    def create_and_display_chapter_toc_network(cls, wg, chapter, infile, gv_output, maxlev=4, engine='fdp'):
        """
        :param wg: "wg1", "wg2", "wg3 etc.
        :param chapter: Chapter01 etc
        :param infile: *.html_with_ids.html at present
        :param gv_output: output Graphviz file
        :param maxlev: maximum depth of sub/subsections (default 4)
        :param engine: layout engine (default fdp)
        """
        logger.info(f"reading from {infile=}")
        # parse infile to HTML object
        html = HtmlLib.parse_html(infile)
        assert html is not None
        # sections to be extracted using regexes
        WANTED_ID_RE = ".*acknowledgements|.*Executive|.*frequently\\-asked\\-questions|(n_)?\\d+(\\_\\d+)*"
        # sections to exclude
        UNWANTED_ID_RE = ".*siblings"
        # highest level div on chapter page
        top_div = html.xpath("/html/body//div[div[@class='h1-container']]")[0]
        assert top_div is not None
        # maximum depth to recurse
        top_id = wg
        if gv_output.exists():
            FileLib.delete_file(gv_output)
            # logger.info(f"file deleted {gv_output.absolute()=}")
        # assert not gv_output.exists(), f"deleted {gv_output.absolute()}"
        graph = graphviz.Digraph(top_id, filename=str(gv_output), engine=engine)
        graph.edge(wg, chapter)
        # iterate over children of top,
        for div in top_div.xpath("div[@class='h1-container']"):
            # get "id" attribute value
            id = cls.get_cleaned_id(div)
            # reject if id is not in selected list or in not-selected list
            if not re.match(WANTED_ID_RE, id) or re.match(UNWANTED_ID_RE, id):
                logger.info(f"skipped {id=}")
                continue
            # logger.info(f"add edge {chap}->{id}")
            graph.edge(chapter, id)
            cls.list_divs_with_ids(div, maxlevel=maxlev, graph=graph)
        if graph is not None:
            """NOTE the PDF viewer caches the displays and does not update
            this wasted a lot of time
            """
            graph.view()

    @classmethod
    def list_divs_with_ids(cls, parent_div, maxlevel, graph=None):

        """
        recursively find descendants and create graph
        :param parent_div:
        :param maxlevel: decremented for each recursion
        :param graph: if not none, adds edges to graph
        """
        UNWANTED_ID_RE = ".*siblings"
        parent_id = cls.get_cleaned_id(parent_div)
        if maxlevel >= 0:
            # find children
            divs = parent_div.xpath("div")
            for div in divs:
                div_id = cls.get_cleaned_id(div)
                if div_id is None or re.match(UNWANTED_ID_RE, div_id):
                    logger.info(f"skipped {div_id=}")
                    continue
                # print(f"add node {div_id=}")
                # logger.info(f"add edge {graph} {parent_id}->{div_id}")
                if graph is not None:
                    graph.edge(parent_id, div_id)
                    # logger.info(f"edge: {graph} {parent_id}->{div_id}")
                cls.list_divs_with_ids(div, maxlevel-1, graph=graph)


    @classmethod
    def get_cleaned_id(self, div):
        """
        I think node ids should not look like (DP) numbers so replace "." and
        prefix with "n_"
        """
        id = div.get("id")
        id = id.replace("-", "_")
        id = id.replace(".", "_")
        id = id.replace("\"", "")
        if ":" in id:
            ids = id.split(":")
            id = ids[0]
        id = f"n_{id}"
        # logger.info(f"{id=}")

        return id




