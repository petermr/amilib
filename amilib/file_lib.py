"""
standalone library from pyamihtml
"""
import glob
import json
import logging
import os
import re
import shutil
from pathlib import Path, PurePath, PurePosixPath

import chardet
import requests

logging.debug("loading file_lib")

# wildcards
STARS = "**"
STAR = "*"

# suffixes
S_PDF = "pdf"
S_PNG = "png"
S_SVG = "pdf"
S_TXT = "txt"
S_XML = "xml"

# markers for processing
# _NULL = "_NULL"
# _REQD = "_REQD"

# known section names
# SVG = "svg"
# PDFIMAGES = "pdfimages"
# RESULTS = "results"
# SECTIONS = "sections"

# subsects
# IMAGE_STAR = "image*"

# subsects
# OCTREE = "*octree"

# results
# SEARCH = "search"
# WORD = "word"
# EMPTY = "empty"

# files
# FULLTEXT_PAGE = "fulltext-page*"
# CHANNEL_STAR = "channel*"
# RAW = "raw"




class FileLib:

    logger = logging.getLogger("file_lib")

    @classmethod
    def force_mkdir(cls, dirx):
        """ensure dirx and its parents exist
        :dirx: directory
        """
        path = Path(dirx)
        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
                assert (f := path).exists(), f"dir {path} should now exist"
            except Exception as e:
                cls.logger.error(f"cannot make dirx {dirx} , {e}")
                print(f"cannot make dirx {dirx}, {e}")



    @classmethod
    def force_mkparent(cls, file):
        """ensure parent directory exists

        :path: whose parent directory is to be created if absent
        """
        if file is not None:
            cls.force_mkdir(cls.get_parent_dir(file))

    @classmethod
    def force_write(cls, file, data, overwrite=True):
        """:write path, creating directory if necessary
        :path: path to write to
        :data: str data to write
        :overwrite: force write if path exists

        may throw exception from write
        """
        if file is not None:
            if os.path.exists(file) and not overwrite:
                logging.warning(f"not overwriting existsnt path {file}")
            else:
                cls.force_mkparent(file)
                with open(file, "w", encoding="utf-8") as f:
                    f.write(data)

    @classmethod
    def copy_file_or_directory(cls, dest_path, src_path, overwrite):
        if dest_path.exists():
            if not overwrite:
                file_type = "dirx" if dest_path.is_dir() else "path"
                raise TypeError(
                    str(dest_path), f"cannot overwrite existing {file_type} (str({dest_path})")

        else:
            # assume directory
            cls.logger.warning(f"create directory {dest_path}")
            dest_path.mkdir(parents=True, exist_ok=True)
            cls.logger.info(f"created directory {dest_path}")
        if src_path.is_dir():
            if os.path.exists(dest_path):
                shutil.rmtree(dest_path)
            shutil.copytree(src_path, dest_path)
            cls.logger.info(f"copied directory {src_path} to {dest_path}")
        else:
            try:
                shutil.copy(src_path, dest_path)  # will overwrite
                cls.logger.info(f"copied path {src_path} to {dest_path}")
            except Exception as e:
                cls.logger.fatal(f"Cannot copy direcctory {src_path} to {dest_path} because {e}")

    @staticmethod
    def create_absolute_name(file):
        """create absolute/relative name for a path relative to pyamihtmlx

        TODO this is messy
        """
        absolute_file = None
        if file is not None:
            file_dir = FileLib.get_parent_dir(__file__)
            absolute_file = os.path.join(os.path.join(file_dir, file))
        return absolute_file

    def get_parent_dir(cls, file):
        return None if file is None else PurePath(file).parent

    @classmethod
    def read_pydictionary(cls, file):
        """read a JSON path into a python dictionary
        :param file: JSON file to read
        :return: JSON dictionary (created by ast.literal_eval)
        """
        import ast
        with open(file, "r") as f:
            pydict = ast.literal_eval(f.read())
        return pydict

    @classmethod
    def punct2underscore(cls, text):
        """ replace all ASCII punctuation except '.' , '-', '_' by '_'

        usually used for filenames
        :param text: input string
        :return: substituted string

        """
        # this is non-trivial https://stackoverflow.com/questions/10017147/removing-a-list-of-characters-in-string

        non_file_punct = '\t \n{}!@#$%^&*()[]:;\'",|\\~+=/`'
        # [unicode(x.strip()) if x is not None else '' for x in row]

        text0 = TextUtil.replace_chars(text, non_file_punct, "_")
        return text0

    @classmethod
    def get_suffix(cls, file):
        """get suffix of filename
        :param file: filename
        :return: suffix including the '.'

        """
        _suffix = None if file is None else Path(file).suffix
        return _suffix

    @staticmethod
    def check_exists(file):
        """
        raise exception on null value or non-existent path
        """
        if file is None:
            raise Exception("null path")

        if os.path.isdir(file):
            # print(path, "is directory")
            pass
        elif os.path.isfile(file):
            # print(path, "is path")
            pass
        else:
            try:
                f = open(file, "r")
                print("tried to open", file)
                f.close()
            except Exception:
                raise FileNotFoundError(str(file) + " should exist")

    @classmethod
    def copyanything(cls, src, dst):
        """copy file or directory
        (from StackOverflow)
        :param src: source file/directory
        :param dst: destination
        """
        try:
            shutil.copytree(src, dst)
        except OSError as exc:  # python >2.5
            if exc.errno in (errno.ENOTDIR, errno.EINVAL):
                shutil.copy(src, dst)
            else:
                raise exc

    @classmethod
    def copy_file(cls, file, src, dst):
        """
        :param file: filename in src dir
        :param src: source directory
        :oaram dst: destinatiom diecrtory
        """
        FileLib.copyanything(Path(src, file), Path(dst, file))

    @classmethod
    def delete_directory_contents(cls, dirx, delete_directory=False):
        """
        deletes directories recursively using shutil.rmtree
        :param dirx: directory tree to delete
        :param delete_directory: If True, delete dirx
        :return None:
        """
        if not dirx or not Path(dirx).exists():
            print (f"no directory given or found {dirx}")
            return
        if delete_directory:
            shutil.rmtree(dirx)
        else:
            for path in Path(dirx).glob("**/*"):
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    shutil.rmtree(path)

    @classmethod
    def delete_files(cls, dirx, globstr):
        """
        delete files in directory
        :param dirx: directory containing files
        :param globstr: glob string, e.g. "*.html"
        :return: list of deleted files (Paths)

        """
        files = []
        for path in Path(dirx).glob(globstr):
            if path.is_file():
                path.unlink()
                files.append(path)
        return files

    @classmethod
    def list_files(cls, dirx, globstr):
        """
        list files in directory
        :param dirx: directory containing files
        :param globstr: glob string, e.g. "*.html"
        :return: list of files (Paths)
        """
        return [path for path in Path(dirx).glob(globstr) if path.is_file()]

    @classmethod
    def size(cls, file):
        """
        get size of file
        :param file:
        :return: file size bytes else None if not exist
        """
        return None if file is None or not file.exists() else os.path.getsize(file)

    @classmethod
    def get_encoding(cls, file):
        """tries to guess (text) encoding
        :param file: to read
        :return: {'encoding': Guess, 'confidence': d.d, 'language': Lang}"""
        with open(file, "rb") as f:
            rawdata = f.read()
            return cls.get_encoding_from_bytes(rawdata)

    @classmethod
    def get_encoding_from_bytes(cls, rawdata):
        chardet.detect(rawdata)
        encode = chardet.UniversalDetector()
        encode.close()
        return encode.result

    @classmethod
    def expand_glob_list(cls, file_list):
        """
        :param file_list: list of paths including globs
        :return: flattened globbed list wwith posix names
        """
        if type(file_list) is not list:
            file_list = [file_list]
        files = []
        for file in file_list:
            globbed_files = FileLib.posix_glob(str(file))
            files.extend(globbed_files)
        return cls.convert_files_to_posix(files)

    @classmethod
    def convert_files_to_posix(cls, file_list):
        """converts list of files to posix form (i.e. all files have / not backslash)
        """
        if file_list is None:
            return None
        posix_files = [PurePosixPath(f) for f in file_list]
        return posix_files


    @classmethod
    def delete_file(cls, file):
        """delete file (uses unlink) and asserts it has worked
        ;param file: to delete"""
        if file.exists():
            file.unlink()
        assert not file.exists()

    @classmethod
    def write_dict(cls, dikt, path, debug=False, indent=2):
        """write dictionary as JSON object
        :param dikt: python dictionary
        :param path: path to write to
        :param debug:
        :param indent:
        """

        with open(str(path), "w") as f:
            json.dump(dikt, f, indent=indent)
        if debug:
            print(f"wrote dictionary to {path}")

    @classmethod
    def read_string_with_user_agent(self, url, user_agent='my-app/0.0.1', encoding="UTF-8", encoding_scheme="chardet", debug=False):
        """
        allows request.get() to use a user_agent
        :param url: url to read
        :param encoding_scheme: id "chardet uses chardet else response.appenent_encoding
        :return: decoded string
        """
        if not url:
            return None
        if debug:
            print(f"reading {url}")
        response = requests.get(url, headers={'user-agent': user_agent})
        if debug:
            print(f"response: {response} content: {response.content[:400]}")
        content = response.content
        if debug:
            print(f"apparent encoding: {response.apparent_encoding}")
        if encoding is None:
            encoding = chardet.detect(content)['encoding'] if encoding_scheme == "chardet" else response.apparent_encoding
        content = content.decode(encoding)
        return content, encoding

    @classmethod
    def join_dir_and_file_as_posix(cls, indir, input):
        """
        joins indir (directory) and input (descendants) to make a list of full filenames
        if indir or input is null, no action
        if indir is a list no action, returns input unchanged
        if input is absolute (starts with "/") no action

        if input is string, creates PosixPath(indir, input) VIA PosixPath
        if input is list of strings creates:
            f"{indir}/{input1}"
            f"{indir}/{input2}"
            ...
            it skips any input strings starting with "/"
        :param indir: input directory
        :param input: single file or list
        :return: single filke or files AS posix strings
        """
        if not indir or not input:
            return input
        # cannot manage multiple directories (?yet)
        if type(indir) is list and len(indir) > 1:
            return input

        if type(input) is str:
            # single input
            if input[0] != "/":
                output = PurePosixPath(indir, input)
                return str(output)
        elif type(input) is list:
            # list of inputs
            outputs = []
            for input_item in input:
                if input_item[0] != "/":
                    posix = PurePosixPath(indir, input_item)
                    outputs.append(str(posix))
            return outputs

    @classmethod
    def posix_glob(cls, glob_str, recursive = True):
        """expands glob and ensure all output is posix
        :param glob_str: glob or list of globs to expand
        :param recursive: use recursive glob
        :return: list of files in posix format"""
        files = []
        if glob_str is None:
            return files
        if type(glob_str) is str:
            glob_str = [glob_str]
        for globx in glob_str:
            ff = glob.glob(globx, recursive=recursive)
            files.extend(ff)
        files = FileLib.convert_files_to_posix(files)
        return files

    @classmethod
    def assert_exist_size(cls, file, minsize, abort=True):
        """asserts a file exists and is of sufficient size
        :param file: file or path
        :param minsize: minimum size
        """
        path = Path(file)
        try:
            assert path.exists(), f"file {path} must exist"
            assert (s := path.stat().st_size) > minsize, f"file {file} size = {s} must be above {minsize}"
        except AssertionError as e:
            if abort:
                raise e


    @classmethod
    def get_home(cls):
        """
        gets home directory os.path.expanduser("~")
        """
        home = os.path.expanduser("~")
        return home



# see https://realpython.com/python-pathlib/

def main():
    print("started file_lib")
    # test_templates()

    print("finished file_lib")


if __name__ == "__main__":
    print("running file_lib main")
    main()
else:
    #    print("running file_lib main anyway")
    #    main()
    pass

# examples of regex for filenames


def glob_re(pattern, strings):
    return filter(re.compile(pattern).match, strings)


filenames = glob_re(r'.*(abc|123|a1b).*\.txt', os.listdir())
