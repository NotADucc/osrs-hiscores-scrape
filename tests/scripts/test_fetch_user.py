from unittest.mock import Mock, patch

import pytest

from osrs_hiscore_scrape.request.hs_account_types import HSAccountTypes
from osrs_hiscore_scrape.request.records import PlayerRecord
from scripts.fetch_user import main


@pytest.fixture
def patch_hiscore():
    with patch("osrs_hiscore_scrape.request.request.Requests.get_user_stats") as mock:
        yield mock


def make_player(overall):
    record = Mock(spec=PlayerRecord)
    record.get_stat.return_value = overall
    record.to_dict.return_value = {
        "username": "bob",
    }
    return record


def make_fake_backend(overrides):
    async def fake_get_user_stats(*args, **kwargs):
        acct = kwargs["player_req"].account_type
        return overrides.get(acct)
    return fake_get_user_stats


@pytest.mark.asyncio
async def test_main_prediction(patch_hiscore):
    patch_hiscore.side_effect = make_fake_backend({
        HSAccountTypes.main: make_player(2000),
    })

    result = await main("bob", HSAccountTypes.main, None)

    assert result["source_account_type"] == HSAccountTypes.main.name
    assert set(result["predicted_account_type"]) == {
        HSAccountTypes.main.name,
    }
    assert "de_ironed" not in result
    assert "de_ulted" not in result
    assert "dead_hc" not in result
    assert "ruined_pure" not in result
    assert "ruined_skiller" not in result


@pytest.mark.asyncio
async def test_skiller_prediction(patch_hiscore):
    patch_hiscore.side_effect = make_fake_backend({
        HSAccountTypes.main: make_player(2000),
        HSAccountTypes.skiller: make_player(2000),
    })

    result = await main("bob", HSAccountTypes.skiller, None)

    assert result["source_account_type"] == HSAccountTypes.skiller.name
    assert set(result["predicted_account_type"]) == {
        HSAccountTypes.skiller.name,
    }
    assert "de_ironed" not in result
    assert "de_ulted" not in result
    assert "dead_hc" not in result
    assert "ruined_pure" not in result
    assert result["ruined_skiller"] is False


@pytest.mark.asyncio
async def test_ruined_skiller(patch_hiscore):
    patch_hiscore.side_effect = make_fake_backend({
        HSAccountTypes.main: make_player(2000),
        HSAccountTypes.skiller: make_player(1900),
    })

    result = await main("bob", HSAccountTypes.skiller, None)

    assert result["source_account_type"] == HSAccountTypes.skiller.name
    assert set(result["predicted_account_type"]) == {
        HSAccountTypes.main.name,
    }
    assert "de_ironed" not in result
    assert "de_ulted" not in result
    assert "dead_hc" not in result
    assert "ruined_pure" not in result
    assert result["ruined_skiller"] is True


@pytest.mark.asyncio
async def test_pure_prediction(patch_hiscore):
    patch_hiscore.side_effect = make_fake_backend({
        HSAccountTypes.main: make_player(2000),
        HSAccountTypes.pure: make_player(2000),
    })

    result = await main("bob", HSAccountTypes.pure, None)

    assert result["source_account_type"] == HSAccountTypes.pure.name
    assert set(result["predicted_account_type"]) == {
        HSAccountTypes.pure.name,
    }
    assert "de_ironed" not in result
    assert "de_ulted" not in result
    assert "dead_hc" not in result
    assert result["ruined_pure"] is False
    assert "ruined_skiller" not in result


@pytest.mark.asyncio
async def test_is_ruined_pure(patch_hiscore):
    patch_hiscore.side_effect = make_fake_backend({
        HSAccountTypes.main: make_player(2000),
        HSAccountTypes.pure: make_player(1900),
    })

    result = await main("bob", HSAccountTypes.pure, None)

    assert result["source_account_type"] == HSAccountTypes.pure.name
    assert set(result["predicted_account_type"]) == {
        HSAccountTypes.main.name,
    }
    assert "de_ironed" not in result
    assert "de_ulted" not in result
    assert "dead_hc" not in result
    assert result["ruined_pure"] is True
    assert "ruined_skiller" not in result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "account_type",
    [
        HSAccountTypes.main,
        HSAccountTypes.im,
    ],
)
async def test_im_prediction(patch_hiscore, account_type):
    patch_hiscore.side_effect = make_fake_backend({
        HSAccountTypes.main: make_player(2000),
        HSAccountTypes.im: make_player(2000),
    })

    result = await main("bob", account_type, None)

    assert result["source_account_type"] == account_type.name
    assert set(result["predicted_account_type"]) == {
        HSAccountTypes.im.name,
    }
    assert result["de_ironed"] is False
    assert "de_ulted" not in result
    assert "dead_hc" not in result
    assert "ruined_pure" not in result
    assert "ruined_skiller" not in result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "account_type",
    [
        HSAccountTypes.main,
        HSAccountTypes.im,
    ],
)
async def test_de_ironed(patch_hiscore, account_type):
    patch_hiscore.side_effect = make_fake_backend({
        HSAccountTypes.main: make_player(2000),
        HSAccountTypes.im: make_player(1000),
    })

    result = await main("bob", account_type, None)

    assert result["source_account_type"] == account_type.name
    assert set(result["predicted_account_type"]) == {
        HSAccountTypes.main.name,
    }
    assert result["de_ironed"] is True
    assert "de_ulted" not in result
    assert "dead_hc" not in result
    assert "ruined_pure" not in result
    assert "ruined_skiller" not in result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "account_type",
    [
        HSAccountTypes.main,
        HSAccountTypes.im,
        HSAccountTypes.uim,
    ],
)
async def test_uim_prediction(patch_hiscore, account_type):
    patch_hiscore.side_effect = make_fake_backend({
        HSAccountTypes.main: make_player(2000),
        HSAccountTypes.im: make_player(2000),
        HSAccountTypes.uim: make_player(2000),
    })

    result = await main("bob", account_type, None)

    assert result["source_account_type"] == account_type.name
    assert set(result["predicted_account_type"]) == {
        HSAccountTypes.uim.name,
    }
    assert result["de_ironed"] is False
    assert result["de_ulted"] is False
    assert "dead_hc" not in result
    assert "ruined_pure" not in result
    assert "ruined_skiller" not in result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "account_type",
    [
        HSAccountTypes.main,
        HSAccountTypes.im,
        HSAccountTypes.uim,
    ],
)
async def test_de_ulted_still_iron(patch_hiscore, account_type):
    patch_hiscore.side_effect = make_fake_backend({
        HSAccountTypes.main: make_player(2000),
        HSAccountTypes.im: make_player(2000),
        HSAccountTypes.uim: make_player(1800),
    })

    result = await main("bob", account_type, None)

    assert result["source_account_type"] == account_type.name
    assert set(result["predicted_account_type"]) == {
        HSAccountTypes.im.name,
    }
    assert result["de_ironed"] is False
    assert result["de_ulted"] is True
    assert "dead_hc" not in result
    assert "ruined_pure" not in result
    assert "ruined_skiller" not in result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "account_type",
    [
        HSAccountTypes.main,
        HSAccountTypes.im,
        HSAccountTypes.uim,
    ],
)
async def test_uim_deironed(patch_hiscore, account_type):
    patch_hiscore.side_effect = make_fake_backend({
        HSAccountTypes.main: make_player(2000),
        HSAccountTypes.im: make_player(1900),
        HSAccountTypes.uim: make_player(1800),
    })

    result = await main("bob", account_type, None)

    assert result["source_account_type"] == account_type.name
    assert set(result["predicted_account_type"]) == {
        HSAccountTypes.main.name,
    }
    assert result["de_ironed"] is True
    assert result["de_ulted"] is True
    assert "dead_hc" not in result
    assert "ruined_pure" not in result
    assert "ruined_skiller" not in result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "account_type",
    [
        HSAccountTypes.main,
        HSAccountTypes.im,
        HSAccountTypes.hc,
    ],
)
async def test_hc_prediction(patch_hiscore, account_type):
    patch_hiscore.side_effect = make_fake_backend({
        HSAccountTypes.main: make_player(2000),
        HSAccountTypes.im: make_player(2000),
        HSAccountTypes.hc: make_player(2000),
    })

    result = await main("bob", account_type, None)

    assert result["source_account_type"] == account_type.name
    assert set(result["predicted_account_type"]) == {
        HSAccountTypes.hc.name,
    }
    assert result["de_ironed"] is False
    assert "de_ulted" not in result
    assert result["dead_hc"] is False
    assert "ruined_pure" not in result
    assert "ruined_skiller" not in result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "account_type",
    [
        HSAccountTypes.main,
        HSAccountTypes.im,
        HSAccountTypes.hc,
    ],
)
async def test_hc_deironed(patch_hiscore, account_type):
    patch_hiscore.side_effect = make_fake_backend({
        HSAccountTypes.main: make_player(2000),
        HSAccountTypes.im: make_player(1950),
        HSAccountTypes.hc: make_player(1900),
    })

    result = await main("bob", account_type, None)

    assert result["source_account_type"] == account_type.name
    assert set(result["predicted_account_type"]) == {
        HSAccountTypes.main.name,
    }
    assert result["de_ironed"] is True
    assert "de_ulted" not in result
    assert result["dead_hc"] is True
    assert "ruined_pure" not in result
    assert "ruined_skiller" not in result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "account_type",
    [
        HSAccountTypes.main,
        HSAccountTypes.im,
        HSAccountTypes.hc,
    ],
)
async def test_dead_hc_still_iron(patch_hiscore, account_type):
    patch_hiscore.side_effect = make_fake_backend({
        HSAccountTypes.main: make_player(2000),
        HSAccountTypes.im: make_player(2000),
        HSAccountTypes.hc: make_player(1900),
    })

    result = await main("bob", account_type, None)

    assert result["source_account_type"] == account_type.name
    assert set(result["predicted_account_type"]) == {
        HSAccountTypes.im.name,
    }
    assert result["de_ironed"] is False
    assert "de_ulted" not in result
    assert result["dead_hc"] is True
    assert "ruined_pure" not in result
    assert "ruined_skiller" not in result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "account_type",
    [
        HSAccountTypes.dmm,
        HSAccountTypes.leagues,
        HSAccountTypes.tournament,
        HSAccountTypes.fsw,
    ],
)
async def test_alternate_gamemodes(patch_hiscore, account_type):
    patch_hiscore.side_effect = make_fake_backend({
        HSAccountTypes.main: make_player(2000),
        account_type: make_player(2000),
    })

    result = await main("bob", account_type, None)

    assert result["source_account_type"] == account_type.name
    assert set(result["predicted_account_type"]) == {
        account_type.name,
    }
    assert "de_ironed" not in result
    assert "de_ulted" not in result
    assert "dead_hc" not in result
    assert "ruined_pure" not in result
    assert "ruined_skiller" not in result


def build_results(**kwargs):
    results = {
        HSAccountTypes.main: make_player(100),
    }

    mapping = {
        "main": HSAccountTypes.main,
        "im": HSAccountTypes.im,
        "uim": HSAccountTypes.uim,
        "hc": HSAccountTypes.hc,
        "pure": HSAccountTypes.pure,
        "skiller": HSAccountTypes.skiller,
        "dmm": HSAccountTypes.dmm,
        "leagues": HSAccountTypes.leagues,
        "tournament": HSAccountTypes.tournament,
        "fsw": HSAccountTypes.fsw,
    }

    for account_type, rank in kwargs.items():
        if rank is not None and account_type in mapping:
            results[mapping[account_type]] = make_player(rank)

    return results


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("lookup", "results", "expected"),
    [
        # multiple predicted accounts with iron
        (
            HSAccountTypes.skiller,
            build_results(main=100, im=100, skiller=100),
            {HSAccountTypes.im.name, HSAccountTypes.skiller.name},
        ),
        (
            HSAccountTypes.pure,
            build_results(main=100, im=100, pure=100),
            {HSAccountTypes.im.name, HSAccountTypes.pure.name},
        ),
        (
            HSAccountTypes.pure,
            build_results(main=100, im=100, pure=100, skiller=100),
            {HSAccountTypes.im.name, HSAccountTypes.pure.name},
        ),
        (
            HSAccountTypes.skiller,
            build_results(main=100, im=100, pure=100, skiller=100),
            {HSAccountTypes.im.name, HSAccountTypes.skiller.name},
        ),
        # multiple predicted accounts with uim
        (
            HSAccountTypes.skiller,
            build_results(main=100, im=100, uim=100, skiller=100),
            {HSAccountTypes.uim.name, HSAccountTypes.skiller.name},
        ),
        (
            HSAccountTypes.pure,
            build_results(main=100, im=100, uim=100, pure=100),
            {HSAccountTypes.uim.name, HSAccountTypes.pure.name},
        ),
        (
            HSAccountTypes.pure,
            build_results(main=100, im=100, uim=100, pure=100, skiller=100),
            {HSAccountTypes.uim.name, HSAccountTypes.pure.name},
        ),
        (
            HSAccountTypes.skiller,
            build_results(main=100, im=100, uim=100, pure=100, skiller=100),
            {HSAccountTypes.uim.name, HSAccountTypes.skiller.name},
        ),
        # multiple predicted accounts with hc
        (
            HSAccountTypes.skiller,
            build_results(main=100, im=100, hc=100, skiller=100),
            {HSAccountTypes.hc.name, HSAccountTypes.skiller.name},
        ),
        (
            HSAccountTypes.pure,
            build_results(main=100, im=100, hc=100, pure=100),
            {HSAccountTypes.hc.name, HSAccountTypes.pure.name},
        ),
        (
            HSAccountTypes.pure,
            build_results(main=100, im=100, hc=100, pure=100, skiller=100),
            {HSAccountTypes.hc.name, HSAccountTypes.pure.name},
        ),
        (
            HSAccountTypes.skiller,
            build_results(main=100, im=100, hc=100, pure=100, skiller=100),
            {HSAccountTypes.hc.name, HSAccountTypes.skiller.name},
        ),
        # edge cases
        (
            HSAccountTypes.pure,
            # currently only the acc type gets displayed
            build_results(main=100, im=80, pure=100, skiller=100),
            {HSAccountTypes.pure.name},
        ),
        (
            HSAccountTypes.skiller,
            # currently only the acc type gets displayed
            build_results(main=100, im=80, pure=100, skiller=100),
            {HSAccountTypes.skiller.name},
        ),
        (
            HSAccountTypes.pure,
            build_results(main=100, im=80, hc=50, pure=100),
            {HSAccountTypes.pure.name},
        ),
        (
            HSAccountTypes.pure,
            build_results(main=100, im=80, uim=50, pure=100),
            {HSAccountTypes.pure.name},
        ),
        (
            HSAccountTypes.skiller,
            build_results(main=100, im=80, hc=50, skiller=100),
            {HSAccountTypes.skiller.name},
        ),
        (
            HSAccountTypes.skiller,
            build_results(main=100, im=80, uim=50, skiller=100),
            {HSAccountTypes.skiller.name},
        ),
    ],
)
async def test_multiple_predicted_account_types(
    patch_hiscore,
    lookup,
    results,
    expected,
):
    patch_hiscore.side_effect = make_fake_backend(results)

    output = await main(
        username="bob",
        lookup_account_type=lookup,
        hs_type=None,
    )

    assert set(output["predicted_account_type"]) == expected
