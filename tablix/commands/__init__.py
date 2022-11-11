
from __future__ import absolute_import
from .commands import setup_metabase
from .migrations import migrate_data

commands = [
	setup_metabase, migrate_data
]
