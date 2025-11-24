# Unused Functions Review List

**Date:** November 20, 2025  
**Total Functions Analyzed:** 1,589  
**Potentially Unused:** 237  
**Functions with External Usage (in amiclimate):** 30

---

## Functions WITH External Usage (KEEP - Used by amiclimate)

These functions are used by external packages and should be kept. Consider adding tests.

### amilib/ami_dict.py
- **`name`** (line 149) - Property
  - Used in: `amiclimate/setup.py`, `amiclimate/test/test_misc.py`, `amiclimate/test/test_ipcc.py`, `amiclimate/test/test_unfccc.py`, `amiclimate/climate/ipcc.py`, `amiclimate/climate/amix.py`, `amiclimate/climate/un.py`
- **`wrapper`** (line 81)
  - Used in: `amiclimate/climate/ipcc.py`

### amilib/ami_html.py
- **`create_rawgithub_url`** (line 1444)
  - Used in: `amiclimate/climate/ipcc.py`
- **`is_bold`** (line 4754, 5723, 6449) - Multiple definitions
  - Used in: `amiclimate/climate/ipcc.py`
- **`is_italic`** (line 4767, 5728, 6453) - Multiple definitions
  - Used in: `amiclimate/climate/ipcc.py`
- **`top`** (line 5715)
  - Used in: `amiclimate/test/test_unfccc.py`, `amiclimate/climate/ipcc.py`
- **`left`** (line 5737)
  - Used in: `amiclimate/test/test_unfccc.py`, `amiclimate/climate/ipcc.py`
- **`width`** (line 5743)
  - Used in: `amiclimate/climate/ipcc.py`
- **`height`** (line 5747)
  - Used in: `amiclimate/climate/ipcc.py`

### amilib/amix.py
- **`commandline`** (line 130)
  - Used in: `amiclimate/test/test_ipcc.py`, `amiclimate/climate/amix.py`
- **`run_dict`** (line 60)
  - Used in: `amiclimate/climate/amix.py`
- **`run_pdf`** (line 64)
  - Used in: `amiclimate/climate/amix.py`

### amilib/bbox.py
- **`width`** (line 558)
  - Used in: `amiclimate/climate/ipcc.py`
- **`height`** (line 562)
  - Used in: `amiclimate/climate/ipcc.py`

### amilib/core/util.py
- **`read_pydict_from_json`** (line 149)
  - Used in: `amiclimate/test/test_all.py`
- **`should_make`** (line 397)
  - Used in: `amiclimate/climate/ipcc.py`

### amilib/file_lib.py
- **`get_suffix`** (line 259)
  - Used in: `amiclimate/climate/amix.py`
- **`delete_files`** (line 368)
  - Used in: `amiclimate/climate/amix.py`

### amilib/html_marker.py
- **`create_dir_and_file`** (line 759)
  - Used in: `amiclimate/test/test_unfccc.py`
- **`split_presplit_into_files`** (line 766)
  - Used in: `amiclimate/test/test_unfccc.py`

### amilib/ami_pdf_libs.py
- **`debug_pdf`** (line 960)
  - Used in: `amiclimate/test/test_unfccc.py`

### amilib/util.py
- **`read_pydict_from_json`** (line 146)
  - Used in: `amiclimate/test/test_all.py`
- **`should_make`** (line 475)
  - Used in: `amiclimate/climate/ipcc.py`

### amilib/wikimedia.py
- **`id`** (line 597)
  - Used in: `amiclimate/test/test_ipcc.py`, `amiclimate/climate/ipcc.py`, `amiclimate/climate/un.py`

### amilib/xml_lib.py
- **`make_sections`** (line 182)
  - Used in: `amiclimate/climate/amix.py`
- **`delete_atts`** (line 549)
  - Used in: `amiclimate/climate/ipcc.py`

---

## Functions WITHOUT External Usage (Review for Removal or Testing)

### amilib/ami_args.py (4 functions)
- `get_input_help` (line 46)
- `get_indir_help` (line 49)
- `get_output_help` (line 52)
- `get_outdir_help` (line 55)

### amilib/ami_bib.py (2 functions)
- `read_metadata_json_create_write_html_table` (line 299) - Has docstring
- `is_chapter_or_tech_summary` (line 371)

### amilib/ami_corpus.py (4 functions)
- `root_dir` (line 131) - Property
- `get_datatables_from_eupmc_results` (line 159) - **DEPRECATED** (has docstring)
- `make_globstr` (line 453)
- `child_containers` (line 829) - Property

### amilib/ami_csv.py (2 functions)
- `read_transpose_write` (line 11) - **NOT DEVELOPED** (has docstring)
- `transpose` (line 16)

### amilib/ami_dict.py (18 functions - excluding 2 with external usage)
- `decorator` (line 80)
- `term` (line 153) - Property
- `wikidata_id` (line 157) - Property
- `get_wikipedia_page` (line 161) - Property
- `get_wikidata_ids_for_entries` (line 366) - Has docstring
- `create_semantic_html` (line 483) - Has docstring
- `get_wikipedia_page_child_para` (line 490) - Has docstring
- `add_figures_to_entry_old` (line 546) - **OLD** version
- `get_or_create_multiword_terms` (line 1121)
- `get_xml_and_image_url` (line 1148)
- `match_multiple_word_terms_against_sentences` (line 1170) - Has docstring
- `get_ami_entry_by_id` (line 1221)
- `create_minimal_json_dictionary` (line 1458) - Has docstring
- `disambiguate_wikidata_by_desc` (line 1567)
- `get_disambiguated_raw_wikidata_ids` (line 1581)
- `markup_html_from_dictionary` (line 1648)
- `apply_dicts_and_sparql` (line 1802)
- `print_dicts` (line 2165)

### amilib/ami_encyclopedia_cluster.py (4 functions)
- `get_cluster_labels` (line 258) - **Multiple definitions with same name**
- `get_cluster_labels` (line 303)
- `get_cluster_labels` (line 345)
- `get_cluster_labels` (line 385)

### amilib/ami_encyclopedia_util.py (5 functions)
- `extract_all_link_targets` (line 142)
- `find_shared_article_links` (line 177)
- `validate_wikipedia_links` (line 228)
- `check_link_consistency` (line 279)
- `group_synonyms` (line 348)

### amilib/ami_graph.py (2 functions)
- `create_subgraph` (line 30)
- `add_ids_to_nodes` (line 83)

### amilib/ami_html.py (37 functions - excluding 9 with external usage)
- `get_annotation_class` (line 158)
- `page_number` (line 243)
- `print_pages_div` (line 429)
- `extract_section_ids` (line 1125)
- `annotate_div_spans_write_final_html` (line 1163)
- `add_base_url` (line 1351)
- `add_explicit_head_style` (line 1388)
- `add_link_stylesheet` (line 1798)
- `create_ahref_for_img` (line 2122)
- `create_thumbnail_and_add_div_to_scroller` (line 2177)
- `extract_styles_to_css_file` (line 2668)
- `add_column_with_ahref_pointers_to_figures` (line 2925)
- `add_column_with_ahref_pointers_to_tables` (line 2943)
- `analyze_coordinates` (line 3923)
- `clean_write_html` (line 3962)
- `remove_elements_in_hierarchy_by_xpath` (line 4056)
- `remove_elements_in_hierachy_by_xpaths` (line 4068) - **Note: typo in name**
- `run_extract` (line 4393)
- `class_string` (line 4870)
- `select_chunks_subchunks_nodes` (line 5244)
- `key` (line 5453)
- `start_end` (line 5457)
- `font_family` (line 5711)
- `font_size` (line 5719)
- `bottom` (line 5733)
- `cmky_to_rgb` (line 5858)
- `short_style` (line 6114)
- `get_font_attributes` (line 6123)
- `get_x0` (line 6151)
- `get_x1` (line 6159)
- `get_y1` (line 6163)
- `read_html_element` (line 6206)
- `convert_common_fonts` (line 6388)
- `create_font_edited_style_from_head_style` (line 6394)
- `sort_ids` (line 6556)

### amilib/ami_pdf_libs.py (12 functions - excluding 1 with external usage)
- `create_page_from_ami_spans_from_pdf` (line 153)
- `get_svg_text` (line 237)
- `find_text_breaks_in_pagex` (line 362)
- `debug_span_changed` (line 433)
- `xy` (line 629)
- `write_summary` (line 753)
- `font_size` (line 1047)
- `font_family` (line 1051)
- `create_from_argparse` (line 1102)
- `determine_image_type` (line 1899)
- `save_image` (line 1918)
- `get_font_css` (line 2015)

### amilib/ami_svg.py (1 function)
- `create_canonical_rect` (line 139)

### amilib/ami_util.py (14 functions)
- `check_type_and_existence` (line 24)
- `is_ordered_numbers` (line 41)
- `int2hex` (line 77)
- `is_white` (line 87)
- `is_black` (line 100)
- `col6_to_col3` (line 113)
- `is_gray` (line 126)
- `get_xy_from_sknw_centroid` (line 142)
- `get_angle` (line 174)
- `get_dist` (line 227)
- `float_list` (line 270)
- `swap_yx_to_xy` (line 297)
- `make_unique_points_list` (line 317)
- `write_xy_to_csv` (line 336)

### amilib/amidriver.py (1 function)
- `set_sleep` (line 71)

### amilib/amix.py (1 function - excluding 3 with external usage)
- `module_stem` (line 456)

### amilib/bbox.py (14 functions - excluding 2 with external usage)
- `create_from_points` (line 74)
- `get_ranges` (line 111)
- `add_coordinate` (line 215)
- `create_box` (line 240)
- `set_invalid` (line 318)
- `fits_within` (line 338)
- `min_dimension` (line 357)
- `max_dimension` (line 364)
- `get_point_pair` (line 371)
- `fit_point_pair_within_image` (line 423)
- `create_from_corners` (line 436)
- `centroid` (line 447)
- `assert_xy_ranges` (line 520)
- `extract_edges_in_box` (line 536)

### amilib/core/util.py (12 functions - excluding 2 with external usage)
- `set_logger` (line 93)
- `find_unique_dict_entry` (line 138)
- `add_sys_argv_str` (line 180)
- `print_stacktrace` (line 303)
- `get_urls_from_webpage` (line 312)
- `download_urls` (line 322)
- `open_read_utf8` (line 361)
- `is_base64` (line 369)
- `get_column` (line 386)
- `get_classname` (line 496)
- `make_get_main_url` (line 552)
- `get_href` (line 643)

### amilib/dict_args.py (2 functions)
- `add_descriptions_old` (line 163) - **OLD** version
- `module_stem` (line 346)

### amilib/file_lib.py (3 functions - excluding 2 with external usage)
- `create_absolute_name` (line 211)
- `read_pydictionary_using_ast` (line 227)
- `get_encoding` (line 403)

### amilib/headless_lib.py (2 functions)
- `predict_encoding` (line 23)
- `find_wikidata` (line 297)

### amilib/html_extra.py (2 functions)
- `create_counters` (line 13)
- `create_matched_dict_and_unmatched_keys` (line 30)

### amilib/html_marker.py (8 functions - excluding 2 with external usage)
- `replace_parent` (line 20)
- `add__and_insert_parents` (line 24)
- `find_targets` (line 139)
- `markup_with_regexes` (line 327)
- `move_implicit_children_to_parents_old` (line 619) - **OLD** version
- `add_span` (line 737)
- `split_presplit_and_write_files` (line 818)
- `get_level_index` (line 849)
- `assert_sections` (line 912)
- `extract_group0` (line 1257)

### amilib/pdf_args.py (3 functions)
- `markup_parentheses` (line 485)
- `extract_brackets` (line 497)
- `create_pdf_args_for_chapter` (line 601)

### amilib/search_args.py (1 function)
- `read_html_dictionary_and_markup_html_file` (line 349)

### amilib/util.py (12 functions - excluding 2 with external usage)
- `set_logger` (line 90)
- `find_unique_dict_entry` (line 135)
- `add_sys_argv_str` (line 177)
- `print_stacktrace` (line 310)
- `get_urls_from_webpage` (line 322)
- `download_urls` (line 334)
- `open_read_utf8` (line 410)
- `is_base64` (line 421)
- `get_column` (line 468)
- `get_classname` (line 563)
- `make_get_main_url` (line 650)
- `get_href` (line 905)

### amilib/wikidata_service.py (7 functions)
- `search_wikidata_entity` (line 583)
- `get_wikidata_entity_summary` (line 598)
- `enrich_term_with_wikidata` (line 613)
- `get_disambiguation_options` (line 355)
- `batch_enrich_terms` (line 492)
- `validate_qid` (line 508)
- `clear_cache` (line 576)

### amilib/wikimedia.py (15 functions - excluding 1 with external usage)
- `read_file_and_make_nested_divs_old` (line 286) - **OLD** version
- `property_name` (line 601)
- `get_properties_dict` (line 636)
- `create_wikidata_page_from_response` (line 680)
- `get_image` (line 797)
- `get_property_id_list` (line 828)
- `get_property_name_list` (line 836)
- `get_predicate_object_from_file` (line 858)
- `get_results_xml` (line 1156)
- `number_of_requests` (line 1218)
- `create_html_of_leading_wp_paragraphs` (line 1463)
- `get_qitem_from_wikipedia_page` (line 1505)
- `get_texts` (line 1846)
- `get_tuple_for_first_paragraph` (line 1854)
- `write_mw_content_text` (line 2114)
- `split_into_language_chunks` (line 2135)
- `loookup_wordlist_file_write_html` (line 2382)
- `get_local_description` (line 3105)

### amilib/xml_lib.py (14 functions - excluding 2 with external usage)
- `test_xml` (line 1995) - **TEST** function
- `test_data_table` (line 2000) - **TEST** function
- `test_replace_strings_with_unknown_encodings` (line 2014) - **TEST** function
- `test_replace_element_child_text_with_unknown_encodings` (line 2029) - **TEST** function
- `parse_xml_string_to_root` (line 207)
- `add_UTF8` (line 358)
- `xslt_transform_tostring` (line 457)
- `does_element_equal_serialized_string` (line 476)
- `remove_common_clutter` (line 642)
- `replace_substrings_in_all_child_texts` (line 688)
- `get_sentence_breaks` (line 885)
- `add_sentence_brs` (line 902)
- `get_xpath_results` (line 970)
- `make_row` (line 1690)
- `append_contained_text` (line 1697)
- `write_full_data_tables` (line 1706)

---

## Summary

### Keep (30 functions with external usage)
These are used by `amiclimate` and should be kept. Consider adding tests.

### Review for Removal (207 functions)
- Functions marked **OLD** or **DEPRECATED** - likely safe to remove
- Functions marked **NOT DEVELOPED** - likely incomplete
- Functions marked **TEST** - should be moved to test files
- Functions with docstrings - may be valuable, review carefully
- Properties - may be accessed dynamically, review carefully

### Recommendations
1. **Immediate removal candidates:**
   - Functions marked "OLD" (e.g., `add_figures_to_entry_old`, `add_descriptions_old`)
   - Functions marked "DEPRECATED" (e.g., `get_datatables_from_eupmc_results`)
   - Functions marked "NOT DEVELOPED" (e.g., `read_transpose_write`)
   - Test functions in non-test files (e.g., `test_xml`, `test_data_table`)

2. **Review and test:**
   - Functions with docstrings (likely valuable)
   - Properties (may be accessed via getattr)
   - Functions in core utilities (may be used dynamically)

3. **Keep and add tests:**
   - All 30 functions with external usage
   - Functions that seem valuable based on names/docstrings

