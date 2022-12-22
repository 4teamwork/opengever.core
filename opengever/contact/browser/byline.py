from opengever.base.viewlets.byline import BylineBase


class TeamByline(BylineBase):
    """Hidden byline for TeamWrapper objects.
    There is no sensible byline data for team objects - so we hide them.
    """

    def show(self):
        return False
