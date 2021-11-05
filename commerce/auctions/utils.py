from auctions.models import Auction


def is_listing_watchlisted(listing_pk, user):

    if user.is_authenticated:
        try:
            user.watchlist.get(pk=listing_pk)
            return True
        except Auction.DoesNotExist:
            return False
    else:
        return False
