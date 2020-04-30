from rosterbot.utils.ranks import Rank

class SingleUnit:
    def __init__(self, name=None, steam_id=None, user_id=None, activity_check = False, loa = False, long_loa = False, row_number = None):
        self.name = name
        # name_components = self.name.split()
        # rank_in_name = #[Rank._missing_value_(component) for component in name_components if Rank.has_value(component)]
        self.rank = Rank.get_rank(name)
        # if (len(rank_in_name) > 0):
        #     self.rank = rank_in_name[0]
        # else:
        #     self.rank = Rank.NINE
        self.steam_id = steam_id
        self.user_id = str(user_id)
        self.loa = loa
        self.long_loa = long_loa
        self.activity_check = activity_check
        self.row_number = row_number