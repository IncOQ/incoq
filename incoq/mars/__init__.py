"""IncOQ compiler."""


# Exports.

from .symbol.config import get_argparser, extract_options
from .transform.apply import (
    transform_source, transform_file, transform_filename)

invoke = transform_filename
