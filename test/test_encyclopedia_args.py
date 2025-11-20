"""
Tests for EncyclopediaArgs command-line arguments

Tests that ENCYCLOPEDIA subparser is registered and basic functionality works
"""
import unittest
from pathlib import Path
from io import StringIO
import sys
from contextlib import redirect_stdout, redirect_stderr

from amilib.amix import AmiLib
from amilib.ami_encyclopedia_args import EncyclopediaArgs
from test.resources import Resources
from test.test_all import AmiAnyTest


class EncyclopediaArgsTest(AmiAnyTest):
    """Test EncyclopediaArgs command-line functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(Resources.TEMP_DIR, "test", "encyclopedia", "EncyclopediaArgsTest")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def test_encyclopedia_subparser_registered(self):
        """Test that ENCYCLOPEDIA subparser is registered in main parser"""
        amix = AmiLib()
        parser = amix.create_arg_parser()
        
        # Check that ENCYCLOPEDIA is in subparsers
        subparsers = parser._subparsers._group_actions[0]
        assert "ENCYCLOPEDIA" in subparsers.choices, "ENCYCLOPEDIA subparser should be registered"
    
    def test_encyclopedia_help_appears_in_main_help(self):
        """Test that ENCYCLOPEDIA appears in main help text"""
        amix = AmiLib()
        parser = amix.create_arg_parser()
        
        # Capture help output
        help_output = StringIO()
        try:
            parser.print_help(file=help_output)
            help_text = help_output.getvalue()
        except SystemExit:
            help_text = help_output.getvalue()
        
        assert "ENCYCLOPEDIA" in help_text, "ENCYCLOPEDIA should appear in main help"
        assert "normalize and aggregate encyclopedia entries" in help_text or "Encyclopedia operations" in help_text
    
    def test_encyclopedia_help_command(self):
        """Test that ENCYCLOPEDIA --help works"""
        args = ["ENCYCLOPEDIA", "--help"]
        
        # Capture output
        stdout = StringIO()
        stderr = StringIO()
        
        try:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                AmiLib().run_command(args)
        except SystemExit:
            pass  # argparse calls SystemExit on --help
        
        output = stdout.getvalue() + stderr.getvalue()
        assert "--inpath" in output or "-i" in output, "Should show --inpath option"
        assert "--outpath" in output or "-o" in output, "Should show --outpath option"
        assert "--title" in output or "-t" in output, "Should show --title option"
    
    def test_encyclopedia_args_initialization(self):
        """Test that EncyclopediaArgs initializes correctly"""
        args = EncyclopediaArgs()
        
        assert args.subparser_arg == "ENCYCLOPEDIA", "subparser_arg should be ENCYCLOPEDIA"
        assert args.title == "Encyclopedia", "Default title should be Encyclopedia"
        assert args.normalize is True, "Default normalize should be True"
        assert args.aggregate_synonyms is True, "Default aggregate_synonyms should be True"
    
    def test_encyclopedia_args_add_arguments(self):
        """Test that add_arguments() creates parser with correct arguments"""
        args = EncyclopediaArgs()
        args.add_arguments()
        
        assert args.parser is not None, "Parser should be created"
        
        # Check that arguments are registered
        action_names = [action.dest for action in args.parser._actions]
        assert "inpath" in action_names, "inpath argument should be registered"
        assert "outpath" in action_names, "outpath argument should be registered"
        assert "title" in action_names, "title argument should be registered"
        assert "no_normalize" in action_names, "no_normalize argument should be registered"
        assert "no_synonyms" in action_names, "no_synonyms argument should be registered"
        assert "stats" in action_names, "stats argument should be registered"
    
    def test_encyclopedia_args_process_args_missing_inpath(self):
        """Test that process_args() raises error when inpath is missing"""
        args = EncyclopediaArgs()
        args.args = {}  # Empty args dict
        
        with self.assertRaises(ValueError) as context:
            args.process_args()
        
        assert "inpath" in str(context.exception).lower(), "Should raise error about missing inpath"
    
    def test_encyclopedia_args_process_args_with_inpath(self):
        """Test that process_args() processes arguments correctly"""
        # Use a test file that exists
        test_file = Path(Resources.TEST_RESOURCES_DIR, "encyclopedia", "wg1chap03_dict.html")
        if not test_file.exists():
            self.skipTest(f"Test file not found: {test_file}")
        
        args = EncyclopediaArgs()
        args.arg_dict = {
            "inpath": str(test_file),
            "outpath": str(self.temp_dir / "output.html"),
            "title": "Test Title",
            "no_normalize": False,
            "no_synonyms": False,
            "stats": False
        }
        
        args.process_args()
        
        assert args.input_file == test_file, "input_file should be set to test file"
        assert args.output_file == self.temp_dir / "output.html", "output_file should be set"
        assert args.title == "Test Title", "title should be set"
        assert args.normalize is True, "normalize should be True when no_normalize is False"
        assert args.aggregate_synonyms is True, "aggregate_synonyms should be True when no_synonyms is False"
    
    def test_encyclopedia_args_process_args_no_outpath(self):
        """Test that process_args() generates default outpath when not provided"""
        test_file = Path(Resources.TEST_RESOURCES_DIR, "encyclopedia", "wg1chap03_dict.html")
        if not test_file.exists():
            self.skipTest(f"Test file not found: {test_file}")
        
        args = EncyclopediaArgs()
        args.arg_dict = {
            "inpath": str(test_file),
        }
        
        args.process_args()
        
        expected_outpath = test_file.parent / f"{test_file.stem}_normalized.html"
        assert args.output_file == expected_outpath, f"Should generate default outpath: {expected_outpath}"


if __name__ == "__main__":
    unittest.main()



