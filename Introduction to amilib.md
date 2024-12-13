# `amilib`
`amilib` is a Python library designed for document processing, and dictionary creation. It has tools for finding, cleaning, converting, searching, republishing legacy documents (PDF, PNG, etc.)

## Installation
To install amilib run the following code :

`pip install amilib==0.3.9`
Running this code on the command line or any IDE will install amilib on your local machine
## Commands
The following command will display the help information for the DICT command within the amilib library

`amilib DICT --help`

![Help](https://imgur.com/2O4XgYd.jpg)
## Building Dictionary
amilib can create HTML dictionary from a wordlist with this command

`amilib DICT --words --description wikipedia --dict --figures --operation create`

![dictionary](https://imgur.com/0fJ7FCX.jpg)

## Annotating Documents
We can also create annotated IPCC chapterslinked to the HTML dictionaries with `amilib`
`amilib SEARCH --inpath --dict --outpath --operation annotate`

![annotated chapter](https://imgur.com/yxpYdml.jpg)

## Creating JQuery Datatables

This works alongwith another tool named `pygetpapers`
`pygetpapers` retrieves a scientific literature corpus from EPMC and `amilib` can create a summary of the entire metadata into a tabular form
(Refer pygetpapers here)  [pygetpapers](https://github.com/petermr/pygetpapers)

![JQuery datatable](https://imgur.com/eJVX04E.jpg)

### Reference
Github - [`amilib`](https://github.com/petermr/amilib)
