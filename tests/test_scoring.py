"""Tests for the scoring module."""

import pytest
from backend.scoring import score_opportunite, fiche_decision, rendement_locatif, MALUS_TRAVAUX


def test_score_opportunite_sous_mediane():
    """Test opportunity score when price is below median."""
    bien = {"prix": 210800, "surface": 68, "quartier": "Mourillon"}
    res = score_opportunite(bien, 3500, "rp")
    assert res["ecart_pct"] < 0
    assert res["score"] > 50


def test_score_opportunite_sur_mediane():
    """Test opportunity score when price is above median."""
    bien = {"prix": 300000, "surface": 68, "quartier": "Mourillon"}
    res = score_opportunite(bien, 3500, "rp")
    assert res["ecart_pct"] > 0
    assert 0 <= res["score"] <= 100


def test_fiche_decision_contient_conseil():
    """Test that decision sheet contains advice and recommendation."""
    bien = {"prix": 210800, "surface": 68, "quartier": "Mourillon", "type": "appartement"}
    res = fiche_decision(bien, {"mediane": 3500}, "investissement")
    assert "conseil" in res
    assert "opportunites" in res
    assert "risques" in res


def test_malus_travaux_profil_rp():
    """Test malus for RP profile."""
    assert MALUS_TRAVAUX["rp"] == pytest.approx(0.3)


def test_malus_travaux_profil_inv():
    """Test no malus for investissement profile."""
    assert MALUS_TRAVAUX["investissement"] == pytest.approx(0.0)


def test_score_label():
    """Test score labels."""
    bien_pas_cher = {"prix": 100000, "surface": 68}
    res = score_opportunite(bien_pas_cher, 3500, "rp")
    assert res["label"] in ["Très bon", "Bon", "Moyen", "À éviter"]


def test_rendement_locatif():
    """Test rental yield calculation."""
    bien = {"prix": 200000}
    res = rendement_locatif(bien, 800)
    assert res["rendement_brut_pct"] > 0
    assert res["rendement_net_pct"] < res["rendement_brut_pct"]
    assert res["loyer_mensuel_estime"] == 800