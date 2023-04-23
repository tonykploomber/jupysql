from sql import plot
from sql.ggplot.geom.geom import geom
from sql.telemetry import telemetry
from sql.store import store


class geom_histogram(geom):
    """
    Histogram plot

    Parameters
    ----------
    bins: int
        Number of bins

    fill : str
        Create a stacked graph which is a combination of
        'x' and 'fill'

    cmap : str, default 'viridis
        Apply a color map to the stacked graph
    """

    def __init__(self, bins=None, fill=None, cmap=None, **kwargs):
        self.bins = bins
        self.fill = fill
        self.cmap = cmap
        super().__init__(**kwargs)

    @telemetry.log_call("ggplot-histogram")
    def draw(self, gg, ax=None, facet=None):
        return self._draw(gg, ax, facet)
        # print ("with in geom_histogram: ", store._data[gg.table]._query)
        # print ("is Interactive mode: ", store._data[gg.table]._is_interactive)
        # # Access local name space
        # # Create function to be reactive
        # plot.histogram(
        #     table=gg.table,
        #     column=gg.mapping.x,
        #     cmap=self.cmap,
        #     bins=self.bins,
        #     conn=gg.conn,
        #     with_=gg.with_,
        #     category=self.fill,
        #     color=gg.mapping.fill,
        #     edgecolor=gg.mapping.color,
        #     facet=facet,
        #     ax=ax or gg.axs[0],
        # )
        # return gg

# interact
    @telemetry.log_call("ggplot-histogram")
    def _draw(self, gg, ax=None, facet=None):
        print ("with in geom_histogram: ", store._data[gg.table]._query)
        print ("is Interactive mode: ", store._data[gg.table]._is_interactive)
        # Access local name space
        # Create function to be reactive
        plot.histogram(
            table=gg.table,
            column=gg.mapping.x,
            cmap=self.cmap,
            bins=self.bins,
            conn=gg.conn,
            with_=gg.with_,
            category=self.fill,
            color=gg.mapping.fill,
            edgecolor=gg.mapping.color,
            facet=facet,
            ax=ax or gg.axs[0],
        )
        return gg