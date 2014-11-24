# Batch computation like twitter_in, but define the non-demanding
# query function to be a mere alias to the query function.
# This avoids the tiny overhead of calling the NODEMAND no-op at
# runtime.

from .twitter_in import *

do_query_nodemand = do_query
