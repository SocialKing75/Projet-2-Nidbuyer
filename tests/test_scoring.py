"""Tests for the scoring module."""

import pytest
from backend.scoring import score_opportunite, fiche_decision, appliquer_malus

def test_score_opportunite_sous_mediane():
    """Test opportunity score when price is below median."""
    bien = {"prix": 210800, "surface": 68, "quartier": "Mourillon"}
    dvf = {"mediane_prix_m2": 3500}
    res = score_opportunite(bien, dvf)
    assert res["ecart_pct"] < 0
    assert "opportunite" in res
    assert res["opportunite"] == "sous-évalué"

def test_score_opportunite_sur_mediane():
    """Test opportunity score when price is above median."""
    bien = {"prix": 300000, "surface": 68, "quartier": "Mourillon"}
    dvf = {"mediane_prix_m2": 3500}
    res = score_opportunite(bien, dvf)
    assert res["ecart_pct"] > 0
    assert "opportunite" in res
    assert res["opportunite"] == "surévalué"

def test_fiche_decision_contient_conseil():
    """Test that decision sheet contains advice and recommendation."""
    bien = {"prix": 210800, "surface": 68, "quartier": "Mourillon"}
    res = fiche_decision(bien, "INV")
    assert "conseil" in res
    assert "recommandation" in res

def test_malus_travaux_profil_rp():
    """Test malus for 'a_renover' and 'RP' profile."""
    res = appliquer_malus(1.0, "a_renover", "RP")
    assert res == pytest.approx(0.7)

def test_malus_travaux_profil_inv():
    """Test no malus for 'a_renover' and 'INV' profile."""
    res = appliquer_malus(1.0, "a_renover", "INV")
    assert res == pytest.approx(1.0)
