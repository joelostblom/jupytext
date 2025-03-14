"""
In this file the various text notebooks formats are defined. Please contribute
new formats here!
"""

import os
import re
import nbformat
from .header import header_to_metadata_and_cell, insert_or_test_version_number
from .cell_reader import MarkdownCellReader, RMarkdownCellReader, \
    LightScriptCellReader, RScriptCellReader, DoublePercentScriptCellReader, HydrogenCellReader, \
    SphinxGalleryScriptCellReader
from .cell_to_text import MarkdownCellExporter, RMarkdownCellExporter, \
    LightScriptCellExporter, BareScriptCellExporter, RScriptCellExporter, DoublePercentCellExporter, \
    HydrogenCellExporter, SphinxGalleryCellExporter
from .metadata_filter import metadata_filter_as_string
from .stringparser import StringParser
from .languages import _SCRIPT_EXTENSIONS, _COMMENT_CHARS
from .pandoc import pandoc_version, is_pandoc_available


class JupytextFormatError(ValueError):
    """Error in the specification of the format for the text notebook"""


class NotebookFormatDescription:
    """Description of a notebook format"""

    def __init__(self,
                 format_name,
                 extension,
                 header_prefix,
                 cell_reader_class,
                 cell_exporter_class,
                 current_version_number,
                 min_readable_version_number=None):
        self.format_name = format_name
        self.extension = extension
        self.header_prefix = header_prefix
        self.cell_reader_class = cell_reader_class
        self.cell_exporter_class = cell_exporter_class
        self.current_version_number = current_version_number
        self.min_readable_version_number = min_readable_version_number


JUPYTEXT_FORMATS = \
    [
        NotebookFormatDescription(
            format_name='markdown',
            extension='.md',
            header_prefix='',
            cell_reader_class=MarkdownCellReader,
            cell_exporter_class=MarkdownCellExporter,
            # Version 1.0 on 2018-08-31 - jupytext v0.6.0 : Initial version
            # Version 1.1 on 2019-03-24 - jupytext v1.1.0 : Markdown regions and cell metadata
            current_version_number='1.1',
            min_readable_version_number='1.0'),

        NotebookFormatDescription(
            format_name='markdown',
            extension='.markdown',
            header_prefix='',
            cell_reader_class=MarkdownCellReader,
            cell_exporter_class=MarkdownCellExporter,
            current_version_number='1.1',
            min_readable_version_number='1.0'),

        NotebookFormatDescription(
            format_name='rmarkdown',
            extension='.Rmd',
            header_prefix='',
            cell_reader_class=RMarkdownCellReader,
            cell_exporter_class=RMarkdownCellExporter,
            # Version 1.0 on 2018-08-22 - jupytext v0.5.2 : Initial version
            # Version 1.1 on 2019-03-24 - jupytext v1.1.0 : Markdown regions and cell metadata
            current_version_number='1.1',
            min_readable_version_number='1.0')] + \
    [
        NotebookFormatDescription(
            format_name='light',
            extension=ext,
            header_prefix=_SCRIPT_EXTENSIONS[ext]['comment'],
            cell_reader_class=LightScriptCellReader,
            cell_exporter_class=LightScriptCellExporter,
            # Version 1.4 on 2019-03-30 - jupytext v1.1.0 - custom cell markers allowed
            # Version 1.3 on 2018-09-22 - jupytext v0.7.0rc0 : Metadata are
            # allowed for all cell types (and then include 'cell_type')
            # Version 1.2 on 2018-09-05 - jupytext v0.6.3 : Metadata bracket
            # can be omitted when empty, if previous line is empty #57
            # Version 1.1 on 2018-08-25 - jupytext v0.6.0 : Cells separated
            # with one blank line #38
            # Version 1.0 on 2018-08-22 - jupytext v0.5.2 : Initial version
            current_version_number='1.4',
            min_readable_version_number='1.1') for ext in _SCRIPT_EXTENSIONS] + \
    [
        NotebookFormatDescription(
            format_name='bare',
            extension=ext,
            header_prefix=_SCRIPT_EXTENSIONS[ext]['comment'],
            cell_reader_class=LightScriptCellReader,
            cell_exporter_class=BareScriptCellExporter,
            current_version_number='1.0',
            min_readable_version_number='1.0') for ext in _SCRIPT_EXTENSIONS] + \
    [
        NotebookFormatDescription(
            format_name='percent',
            extension=ext,
            header_prefix=_SCRIPT_EXTENSIONS[ext]['comment'],
            cell_reader_class=DoublePercentScriptCellReader,
            cell_exporter_class=DoublePercentCellExporter,
            # Version 1.2 on 2018-11-18 - jupytext v0.8.6: Jupyter magics are commented by default #126, #132
            # Version 1.1 on 2018-09-23 - jupytext v0.7.0rc1 : [markdown] and
            # [raw] for markdown and raw cells.
            # Version 1.0 on 2018-09-22 - jupytext v0.7.0rc0 : Initial version
            current_version_number='1.2',
            min_readable_version_number='1.1') for ext in _SCRIPT_EXTENSIONS] + \
    [
        NotebookFormatDescription(
            format_name='hydrogen',
            extension=ext,
            header_prefix=_SCRIPT_EXTENSIONS[ext]['comment'],
            cell_reader_class=HydrogenCellReader,
            cell_exporter_class=HydrogenCellExporter,
            # Version 1.2 on 2018-12-14 - jupytext v0.9.0: same as percent - only magics are not commented by default
            current_version_number='1.2',
            min_readable_version_number='1.1') for ext in _SCRIPT_EXTENSIONS] + \
    [
        NotebookFormatDescription(
            format_name='spin',
            extension=ext,
            header_prefix="#'",
            cell_reader_class=RScriptCellReader,
            cell_exporter_class=RScriptCellExporter,
            # Version 1.0 on 2018-08-22 - jupytext v0.5.2 : Initial version
            current_version_number='1.0') for ext in ['.r', '.R']] + \
    [
        NotebookFormatDescription(
            format_name='sphinx',
            extension='.py',
            header_prefix='#',
            cell_reader_class=SphinxGalleryScriptCellReader,
            cell_exporter_class=SphinxGalleryCellExporter,
            # Version 1.0 on 2018-09-22 - jupytext v0.7.0rc0 : Initial version
            current_version_number='1.1')
    ]

if is_pandoc_available():
    JUPYTEXT_FORMATS.append(NotebookFormatDescription(
        format_name='pandoc',
        extension='.md',
        header_prefix='',
        cell_reader_class=None,
        cell_exporter_class=None,
        current_version_number=pandoc_version()))

NOTEBOOK_EXTENSIONS = list(dict.fromkeys(['.ipynb'] + [fmt.extension for fmt in JUPYTEXT_FORMATS]))
EXTENSION_PREFIXES = ['.lgt', '.spx', '.pct', '.hyd', '.nb']


def get_format_implementation(ext, format_name=None):
    """Return the implementation for the desired format"""
    # remove pre-extension if any
    ext = '.' + ext.split('.')[-1]

    formats_for_extension = []
    for fmt in JUPYTEXT_FORMATS:
        if fmt.extension == ext:
            if fmt.format_name == format_name or not format_name:
                return fmt
            formats_for_extension.append(fmt.format_name)

    if formats_for_extension:
        if ext == '.md' and format_name == 'pandoc':
            raise JupytextFormatError('Please install pandoc>=2.7.2')

        raise JupytextFormatError("Format '{}' is not associated to extension '{}'. "
                                  "Please choose one of: {}.".format(format_name, ext,
                                                                     ', '.join(formats_for_extension)))
    raise JupytextFormatError("No format associated to extension '{}'".format(ext))


def read_metadata(text, ext):
    """Return the header metadata"""
    ext = '.' + ext.split('.')[-1]
    lines = text.splitlines()

    if ext in ['.md', '.Rmd']:
        comment = ''
    else:
        comment = _SCRIPT_EXTENSIONS.get(ext, {}).get('comment', '#')

    metadata, _, _, _ = header_to_metadata_and_cell(lines, comment, ext)
    if ext in ['.r', '.R'] and not metadata:
        metadata, _, _, _ = header_to_metadata_and_cell(lines, "#'", ext)

    return metadata


def read_format_from_metadata(text, ext):
    """Return the format of the file, when that information is available from the metadata"""
    metadata = read_metadata(text, ext)
    rearrange_jupytext_metadata(metadata)
    return format_name_for_ext(metadata, ext, explicit_default=False)


def guess_format(text, ext):
    """Guess the format and format options of the file, given its extension and content"""
    lines = text.splitlines()

    metadata = read_metadata(text, ext)

    if 'text_representation' in metadata.get('jupytext', {}):
        return format_name_for_ext(metadata, ext), {}

    # Is this a Hydrogen-like script?
    # Or a Sphinx-gallery script?
    if ext in _SCRIPT_EXTENSIONS:
        comment = _SCRIPT_EXTENSIONS[ext]['comment']
        twenty_hash = ''.join(['#'] * 20)
        magic_re = re.compile(r'^(%|%%|%%%)[a-zA-Z]')
        double_percent_re = re.compile(r'^{}( %%|%%)$'.format(comment))
        double_percent_and_space_re = re.compile(r'^{}( %%|%%)\s'.format(comment))
        nbconvert_script_re = re.compile(r'^{}( <codecell>| In\[[0-9 ]*\]:?)'.format(comment))
        vim_folding_markers_re = re.compile(r'^{}\s*'.format(comment) + '{{{')
        vscode_folding_markers_re = re.compile(r'^{}\s*region'.format(comment))

        twenty_hash_count = 0
        double_percent_count = 0
        magic_command_count = 0
        rspin_comment_count = 0
        vim_folding_markers_count = 0
        vscode_folding_markers_count = 0

        parser = StringParser(language='R' if ext in ['.r', '.R'] else 'python')
        for line in lines:
            parser.read_line(line)
            if parser.is_quoted():
                continue

            # Don't count escaped Jupyter magics (no space between %% and command) as cells
            if double_percent_re.match(line) or double_percent_and_space_re.match(line) or \
                    nbconvert_script_re.match(line):
                double_percent_count += 1

            if magic_re.match(line):
                magic_command_count += 1

            if line.startswith(twenty_hash) and ext == '.py':
                twenty_hash_count += 1

            if line.startswith("#'") and ext in ['.R', '.r']:
                rspin_comment_count += 1

            if vim_folding_markers_re.match(line):
                vim_folding_markers_count += 1

            if vscode_folding_markers_re.match(line):
                vscode_folding_markers_count += 1

        if double_percent_count >= 1:
            if magic_command_count:
                return 'hydrogen', {}
            return 'percent', {}

        if vim_folding_markers_count:
            return 'light', {'cell_markers': '{{{,}}}'}

        if vscode_folding_markers_count:
            return 'light', {'cell_markers': 'region,endregion'}

        if twenty_hash_count >= 2:
            return 'sphinx', {}

        if rspin_comment_count >= 1:
            return 'spin', {}

    if ext == '.md':
        for line in lines:
            if line.startswith(':::'):  # Pandoc div
                return 'pandoc', {}

    # Default format
    return get_format_implementation(ext).format_name, {}


def divine_format(text):
    """Guess the format of the notebook, based on its content #148"""
    try:
        nbformat.reads(text, as_version=4)
        return 'ipynb'
    except nbformat.reader.NotJSONError:
        pass

    lines = text.splitlines()
    for comment in ['', '#'] + _COMMENT_CHARS:
        metadata, _, _, _ = header_to_metadata_and_cell(lines, comment)
        ext = metadata.get('jupytext', {}).get('text_representation', {}).get('extension')
        if ext:
            return ext[1:] + ':' + guess_format(text, ext)[0]

    # No metadata, but ``` on at least one line => markdown
    for line in lines:
        if line == '```':
            return 'md'

    return 'py:' + guess_format(text, '.py')[0]


def check_file_version(notebook, source_path, outputs_path):
    """Raise if file version in source file would override outputs"""
    if not insert_or_test_version_number():
        return

    _, ext = os.path.splitext(source_path)
    if ext.endswith('.ipynb'):
        return
    version = notebook.metadata.get('jupytext', {}).get('text_representation', {}).get('format_version')
    format_name = format_name_for_ext(notebook.metadata, ext)

    fmt = get_format_implementation(ext, format_name)
    current = fmt.current_version_number

    # Missing version, still generated by jupytext?
    if notebook.metadata and not version:
        version = current

    # Same version? OK
    if version == fmt.current_version_number:
        return

    # Version larger than minimum readable version
    if (fmt.min_readable_version_number or current) <= version <= current:
        return

    raise JupytextFormatError("File {} is in format/version={}/{} (current version is {}). "
                              "It would not be safe to override the source of {} with that file. "
                              "Please remove one or the other file."
                              .format(os.path.basename(source_path),
                                      format_name, version, current,
                                      os.path.basename(outputs_path)))


def format_name_for_ext(metadata, ext, cm_default_formats=None, explicit_default=True):
    """Return the format name for that extension"""
    # Is the format information available in the text representation?
    text_repr = metadata.get('jupytext', {}).get('text_representation', {})
    if text_repr.get('extension', '').endswith(ext) and text_repr.get('format_name'):
        return text_repr.get('format_name')

    # Format from jupytext.formats
    formats = metadata.get('jupytext', {}).get('formats', '') or cm_default_formats
    formats = long_form_multiple_formats(formats)
    for fmt in formats:
        if fmt['extension'] == ext:
            if (not explicit_default) or fmt.get('format_name'):
                return fmt.get('format_name')

    if (not explicit_default) or ext in ['.Rmd', '.md']:
        return None

    return get_format_implementation(ext).format_name


def identical_format_path(fmt1, fmt2):
    """Do the two (long representation) of formats target the same file?"""
    for key in ['extension', 'prefix', 'suffix']:
        if fmt1.get(key) != fmt2.get(key):
            return False
    return True


def update_jupytext_formats_metadata(metadata, new_format):
    """Update the jupytext_format metadata in the Jupyter notebook"""
    new_format = long_form_one_format(new_format)
    formats = long_form_multiple_formats(metadata.get('jupytext', {}).get('formats', ''))
    if not formats:
        return

    for fmt in formats:
        if identical_format_path(fmt, new_format):
            fmt['format_name'] = new_format.get('format_name')
            break

    metadata.setdefault('jupytext', {})['formats'] = short_form_multiple_formats(formats)


def rearrange_jupytext_metadata(metadata):
    """Convert the jupytext_formats metadata entry to jupytext/formats, etc. See #91"""

    # Backward compatibility with nbrmd
    for key in ['nbrmd_formats', 'nbrmd_format_version']:
        if key in metadata:
            metadata[key.replace('nbrmd', 'jupytext')] = metadata.pop(key)

    jupytext_metadata = metadata.pop('jupytext', {})

    if 'jupytext_formats' in metadata:
        jupytext_metadata['formats'] = metadata.pop('jupytext_formats')
    if 'jupytext_format_version' in metadata:
        jupytext_metadata['text_representation'] = {'format_version': metadata.pop('jupytext_format_version')}
    if 'main_language' in metadata:
        jupytext_metadata['main_language'] = metadata.pop('main_language')
    for entry in ['encoding', 'executable']:
        if entry in metadata:
            jupytext_metadata[entry] = metadata.pop(entry)

    filters = jupytext_metadata.pop('metadata_filter', {})
    if 'notebook' in filters:
        jupytext_metadata['notebook_metadata_filter'] = filters['notebook']
    if 'cells' in filters:
        jupytext_metadata['cell_metadata_filter'] = filters['cells']

    for filter_level in ['notebook_metadata_filter', 'cell_metadata_filter']:
        if filter_level in jupytext_metadata:
            jupytext_metadata[filter_level] = metadata_filter_as_string(jupytext_metadata[filter_level])

    if jupytext_metadata.get('text_representation', {}).get('jupytext_version', '').startswith('0.'):
        formats = jupytext_metadata.get('formats')
        if formats:
            jupytext_metadata['formats'] = ','.join(['.' + fmt if fmt.rfind('.') > 0 else fmt
                                                     for fmt in formats.split(',')])

    # auto to actual extension
    formats = jupytext_metadata.get('formats')
    if formats:
        jupytext_metadata['formats'] = short_form_multiple_formats(long_form_multiple_formats(formats, metadata))

    if jupytext_metadata:
        metadata['jupytext'] = jupytext_metadata


def long_form_one_format(jupytext_format, metadata=None, update=None, auto_ext_requires_language_info=True):
    """Parse 'sfx.py:percent' into {'suffix':'sfx', 'extension':'py', 'format_name':'percent'}"""
    if isinstance(jupytext_format, dict):
        if update:
            jupytext_format.update(update)
        return validate_one_format(jupytext_format)

    if not jupytext_format:
        return {}

    common_name_to_ext = {'notebook': 'ipynb',
                          'rmarkdown': 'Rmd',
                          'markdown': 'md',
                          'script': 'auto',
                          'c++': 'cpp'}
    if jupytext_format.lower() in common_name_to_ext:
        jupytext_format = common_name_to_ext[jupytext_format.lower()]

    fmt = {}

    if jupytext_format.rfind('/') > 0:
        fmt['prefix'], jupytext_format = jupytext_format.rsplit('/', 1)

    if jupytext_format.rfind(':') >= 0:
        ext, fmt['format_name'] = jupytext_format.rsplit(':', 1)
    else:
        ext = jupytext_format

    if ext.rfind('.') > 0:
        fmt['suffix'], ext = os.path.splitext(ext)

    if not ext.startswith('.'):
        ext = '.' + ext

    if ext == '.auto':
        ext = auto_ext_from_metadata(metadata) if metadata is not None else '.auto'
        if not ext:
            if auto_ext_requires_language_info:
                raise JupytextFormatError("No language information in this notebook. Please replace 'auto' with "
                                          "an actual script extension.")
            ext = '.auto'

    fmt['extension'] = ext
    if update:
        fmt.update(update)
    return validate_one_format(fmt)


def long_form_multiple_formats(jupytext_formats, metadata=None, auto_ext_requires_language_info=True):
    """Convert a concise encoding of jupytext.formats to a list of formats, encoded as dictionaries"""
    if not jupytext_formats:
        return []

    if not isinstance(jupytext_formats, list):
        jupytext_formats = [fmt for fmt in jupytext_formats.split(',') if fmt]

    jupytext_formats = [long_form_one_format(fmt, metadata,
                                             auto_ext_requires_language_info=auto_ext_requires_language_info)
                        for fmt in jupytext_formats]

    if not auto_ext_requires_language_info:
        jupytext_formats = [fmt for fmt in jupytext_formats if fmt['extension'] != '.auto']

    return jupytext_formats


def short_form_one_format(jupytext_format):
    """Represent one jupytext format as a string"""
    if not isinstance(jupytext_format, dict):
        return jupytext_format
    fmt = jupytext_format['extension']
    if 'suffix' in jupytext_format:
        fmt = jupytext_format['suffix'] + fmt
    elif fmt.startswith('.'):
        fmt = fmt[1:]

    if 'prefix' in jupytext_format:
        fmt = jupytext_format['prefix'] + '/' + fmt

    if jupytext_format.get('format_name'):
        if jupytext_format['extension'] not in ['.md', '.Rmd'] or jupytext_format['format_name'] == 'pandoc':
            fmt = fmt + ':' + jupytext_format['format_name']

    return fmt


def short_form_multiple_formats(jupytext_formats):
    """Convert jupytext formats, represented as a list of dictionaries, to a comma separated list"""
    if not isinstance(jupytext_formats, list):
        return jupytext_formats

    jupytext_formats = [short_form_one_format(fmt) for fmt in jupytext_formats]
    return ','.join(jupytext_formats)


_VALID_FORMAT_INFO = ['extension', 'format_name', 'suffix', 'prefix']
_BINARY_FORMAT_OPTIONS = ['comment_magics', 'split_at_heading', 'rst2md']
_VALID_FORMAT_OPTIONS = _BINARY_FORMAT_OPTIONS + ['notebook_metadata_filter', 'cell_metadata_filter', 'cell_markers']


def validate_one_format(jupytext_format):
    """Validate extension and options for the given format"""
    if not isinstance(jupytext_format, dict):
        raise JupytextFormatError('Jupytext format should be a dictionary')

    for key in jupytext_format:
        if key not in _VALID_FORMAT_INFO + _VALID_FORMAT_OPTIONS:
            raise JupytextFormatError("Unknown format option '{}' - should be one of '{}'".format(
                key, "', '".join(_VALID_FORMAT_OPTIONS)))
        value = jupytext_format[key]
        if key in _BINARY_FORMAT_OPTIONS:
            if not isinstance(value, bool):
                raise JupytextFormatError("Format option '{}' should be a bool, not '{}'".format(key, str(value)))

    if 'extension' not in jupytext_format:
        raise JupytextFormatError('Missing format extension')
    ext = jupytext_format['extension']
    if ext not in NOTEBOOK_EXTENSIONS + ['.auto']:
        raise JupytextFormatError("Extension '{}' is not a notebook extension. Please use one of '{}'.".format(
            ext, "', '".join(NOTEBOOK_EXTENSIONS + ['.auto'])))

    return jupytext_format


def auto_ext_from_metadata(metadata):
    """Script extension from kernel information"""
    auto_ext = metadata.get('language_info', {}).get('file_extension')
    if auto_ext == '.r':
        return '.R'
    return auto_ext
