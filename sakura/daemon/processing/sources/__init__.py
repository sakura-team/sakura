from sakura.daemon.processing.sources.types import SourceTypes
from sakura.daemon.processing.sources.computed import ChunksComputedSource, ItemsComputedSource
from sakura.daemon.processing.sources.npsource import NumpyArraySource
from sakura.daemon.processing.sources.sqlsource import SQLDatabaseSource, SQLTableSource
from sakura.daemon.processing.sources.join import JoinSource

SourceTypes.ChunksComputedSource = ChunksComputedSource
SourceTypes.ItemsComputedSource = ItemsComputedSource
SourceTypes.NumpyArraySource = NumpyArraySource
SourceTypes.SQLDatabaseSource = SQLDatabaseSource
SourceTypes.SQLTableSource = SQLTableSource
SourceTypes.JoinSource = JoinSource
