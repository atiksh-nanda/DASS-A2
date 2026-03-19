import pytest

from moneypoly.bank import Bank
from moneypoly.board import Board
from moneypoly.config import GO_SALARY, JAIL_FINE
from moneypoly.game import Game
from moneypoly.player import Player
from moneypoly.property import Property


def test_board_tile_type_covers_special_property_and_blank():
    board = Board()
    assert board.get_tile_type(0) == "go"
    assert board.get_tile_type(1) == "property"
    assert board.get_tile_type(12) == "blank"


def test_board_is_purchasable_branches_for_none_owned_and_mortgaged():
    board = Board()
    prop = board.get_property_at(1)
    other = Player("Owner")

    assert board.is_purchasable(12) is False
    assert board.is_purchasable(1) is True

    prop.owner = other
    assert board.is_purchasable(1) is False

    prop.owner = None
    prop.is_mortgaged = True
    assert board.is_purchasable(1) is False


def test_buy_property_succeeds_when_balance_above_price():
    game = Game(["A", "B"])
    player = game.players[0]
    prop = game.board.get_property_at(1)

    result = game.buy_property(player, prop)

    assert result is True
    assert prop.owner == player
    assert prop in player.properties


def test_buy_property_should_allow_exact_balance_purchase():
    game = Game(["A", "B"])
    player = game.players[0]
    prop = game.board.get_property_at(1)
    player.balance = prop.price

    result = game.buy_property(player, prop)

    assert result is True
    assert prop.owner == player


def test_pay_rent_branch_mortgaged_property_collects_nothing():
    game = Game(["A", "B"])
    tenant = game.players[0]
    owner = game.players[1]
    prop = game.board.get_property_at(1)
    prop.owner = owner
    prop.is_mortgaged = True

    tenant_before = tenant.balance
    owner_before = owner.balance
    game.pay_rent(tenant, prop)

    assert tenant.balance == tenant_before
    assert owner.balance == owner_before


def test_pay_rent_should_transfer_money_to_owner():
    game = Game(["A", "B"])
    tenant = game.players[0]
    owner = game.players[1]
    prop = game.board.get_property_at(1)
    prop.owner = owner

    rent = prop.get_rent()
    tenant_before = tenant.balance
    owner_before = owner.balance

    game.pay_rent(tenant, prop)

    assert tenant.balance == tenant_before - rent
    assert owner.balance == owner_before + rent


def test_trade_fails_when_seller_does_not_own_property():
    game = Game(["A", "B"])
    seller, buyer = game.players
    prop = game.board.get_property_at(1)

    assert game.trade(seller, buyer, prop, 100) is False


def test_trade_fails_when_buyer_cannot_afford_cash_amount():
    game = Game(["A", "B"])
    seller, buyer = game.players
    prop = game.board.get_property_at(1)

    prop.owner = seller
    seller.add_property(prop)
    buyer.balance = 10

    assert game.trade(seller, buyer, prop, 100) is False


def test_trade_should_credit_seller_and_transfer_property():
    game = Game(["A", "B"])
    seller, buyer = game.players
    prop = game.board.get_property_at(1)

    prop.owner = seller
    seller.add_property(prop)

    seller_before = seller.balance
    buyer_before = buyer.balance

    ok = game.trade(seller, buyer, prop, 100)

    assert ok is True
    assert prop.owner == buyer
    assert prop in buyer.properties
    assert prop not in seller.properties
    assert buyer.balance == buyer_before - 100
    assert seller.balance == seller_before + 100


def test_mortgage_property_requires_ownership_and_prevents_double_mortgage():
    game = Game(["A", "B"])
    owner, other = game.players
    prop = game.board.get_property_at(1)
    prop.owner = owner
    owner.add_property(prop)

    assert game.mortgage_property(other, prop) is False
    assert game.mortgage_property(owner, prop) is True
    assert game.mortgage_property(owner, prop) is False


def test_unmortgage_property_branches_for_owner_and_balance():
    game = Game(["A", "B"])
    owner, other = game.players
    prop = game.board.get_property_at(1)
    prop.owner = owner
    owner.add_property(prop)
    prop.is_mortgaged = True

    assert game.unmortgage_property(other, prop) is False

    owner.balance = 0
    assert game.unmortgage_property(owner, prop) is False


def test_apply_card_collect_and_pay_branches_modify_money():
    game = Game(["A", "B"])
    player = game.players[0]

    before = player.balance
    game._apply_card(player, {"description": "Collect", "action": "collect", "value": 50})
    assert player.balance == before + 50

    before = player.balance
    game._apply_card(player, {"description": "Pay", "action": "pay", "value": 25})
    assert player.balance == before - 25


def test_apply_card_none_and_unknown_action_do_not_crash_or_change_balance():
    game = Game(["A", "B"])
    player = game.players[0]

    before = player.balance
    game._apply_card(player, None)
    game._apply_card(player, {"description": "Unknown", "action": "other", "value": 999})
    assert player.balance == before


def test_apply_card_move_to_passes_go_and_handles_property(monkeypatch):
    game = Game(["A", "B"])
    player = game.players[0]
    player.position = 39
    before = player.balance

    game._apply_card(player, {"description": "Advance to Go", "action": "move_to", "value": 0})

    assert player.position == 0
    assert player.balance == before + GO_SALARY


def test_property_group_should_require_all_properties_owned_for_double_rent():
    board = Board()
    group = board.groups["brown"]
    first = group.properties[0]
    second = group.properties[1]
    owner = Player("Owner")

    first.owner = owner
    second.owner = None

    assert first.get_rent() == first.base_rent


def test_player_move_should_pay_salary_when_passing_go_not_only_landing():
    player = Player("A")
    player.position = 39
    start_balance = player.balance

    player.move(2)

    assert player.position == 1
    assert player.balance == start_balance + GO_SALARY


def test_try_pay_jail_fine_should_deduct_player_balance(monkeypatch):
    game = Game(["A", "B"])
    player = game.players[0]
    player.in_jail = True

    monkeypatch.setattr("moneypoly.ui.confirm", lambda _prompt: True)
    monkeypatch.setattr(game.dice, "roll", lambda: 4)
    monkeypatch.setattr(Game, "_move_and_resolve", lambda self, _player, _steps: None)

    before = player.balance
    paid = game._try_pay_jail_fine(player)

    assert paid is True
    assert player.balance == before - JAIL_FINE
    assert player.in_jail is False


def test_serve_jail_turn_branches_before_and_after_third_turn(monkeypatch):
    game = Game(["A", "B"])
    player = game.players[0]
    player.in_jail = True
    player.jail_turns = 1

    game._serve_jail_turn(player)
    assert player.in_jail is True
    assert player.jail_turns == 2

    monkeypatch.setattr(game.dice, "roll", lambda: 3)
    monkeypatch.setattr(Game, "_move_and_resolve", lambda self, _player, _steps: None)

    before = player.balance
    game._serve_jail_turn(player)

    assert player.in_jail is False
    assert player.jail_turns == 0
    assert player.balance == before - JAIL_FINE


def test_check_bankruptcy_eliminates_player_and_releases_properties():
    game = Game(["A", "B"])
    player = game.players[0]
    prop = game.board.get_property_at(1)

    prop.owner = player
    prop.is_mortgaged = True
    player.add_property(prop)
    player.balance = 0

    game._check_bankruptcy(player)

    assert player.is_eliminated is True
    assert player not in game.players
    assert prop.owner is None
    assert prop.is_mortgaged is False


def test_find_winner_should_return_highest_net_worth_player():
    game = Game(["A", "B", "C"])
    game.players[0].balance = 500
    game.players[1].balance = 2500
    game.players[2].balance = 1000

    winner = game.find_winner()

    assert winner == game.players[1]


def test_bank_collect_should_ignore_negative_amounts():
    bank = Bank()
    start = bank.get_balance()

    bank.collect(-100)

    assert bank.get_balance() == start


def test_dice_roll_should_use_standard_six_sided_range(monkeypatch):
    calls = []

    def fake_randint(low, high):
        calls.append((low, high))
        return 3

    monkeypatch.setattr("moneypoly.dice.random.randint", fake_randint)

    from moneypoly.dice import Dice

    dice = Dice()
    dice.roll()

    assert calls[0] == (1, 6)
    assert calls[1] == (1, 6)


def test_auction_property_winner_path_and_invalid_bid_branches(monkeypatch):
    game = Game(["A", "B", "C"])
    prop = game.board.get_property_at(1)
    bids = iter([50, 55, 40])

    monkeypatch.setattr("moneypoly.ui.safe_int_input", lambda _prompt, default=0: next(bids))

    game.auction_property(prop)

    winner = game.players[0]
    assert prop.owner == winner
    assert prop in winner.properties


def test_auction_property_no_bids_leaves_property_unowned(monkeypatch):
    game = Game(["A", "B"])
    prop = game.board.get_property_at(1)
    bids = iter([0, 0])

    monkeypatch.setattr("moneypoly.ui.safe_int_input", lambda _prompt, default=0: next(bids))

    game.auction_property(prop)

    assert prop.owner is None


def test_handle_property_tile_branches_for_buy_auction_skip_self_and_other(monkeypatch):
    game = Game(["A", "B"])
    active = game.players[0]
    other = game.players[1]
    prop = game.board.get_property_at(1)

    events = {"buy": 0, "auction": 0, "rent": 0}

    monkeypatch.setattr(Game, "buy_property", lambda self, _player, _prop: events.__setitem__("buy", events["buy"] + 1))
    monkeypatch.setattr(Game, "auction_property", lambda self, _prop: events.__setitem__("auction", events["auction"] + 1))
    monkeypatch.setattr(Game, "pay_rent", lambda self, _player, _prop: events.__setitem__("rent", events["rent"] + 1))

    monkeypatch.setattr("builtins.input", lambda _prompt: "b")
    prop.owner = None
    game._handle_property_tile(active, prop)

    monkeypatch.setattr("builtins.input", lambda _prompt: "a")
    prop.owner = None
    game._handle_property_tile(active, prop)

    monkeypatch.setattr("builtins.input", lambda _prompt: "s")
    prop.owner = None
    game._handle_property_tile(active, prop)

    prop.owner = active
    game._handle_property_tile(active, prop)

    prop.owner = other
    game._handle_property_tile(active, prop)

    assert events["buy"] == 1
    assert events["auction"] == 1
    assert events["rent"] == 1
