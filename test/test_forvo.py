from pyforvo import ForvoEntry, ForvoResults
from unittest.mock import patch
import json
import os

data_dir = 'data'


def create_mock_entry(name):
    with open(os.path.join(data_dir, name)) as json_file:
        data = json.load(json_file)

    return ForvoEntry(data)


def test_forvo_entry():
    fe = create_mock_entry('Shady_arc_идти.txt')

    assert fe.username == 'Shady_arc'
    assert fe.word == 'идти'
    assert fe.sex == 'male'
    assert fe.country == 'Russia'
    assert fe.rating == -1
    assert fe.num_votes == 3
    assert fe.path == 'https://apifree.forvo.com/audio/2i3p351n2d282m2b2h3p3c1m27322q2h3b3g35242g1g262f2n2635222n232529333c3c2j313n2c3d242q36253f3o3l2n212k2g1l1b2e1k2k3n3q2d2l3j3g3h3e272a2c1b2a2d213c34291k3e371h1b2p1k2e3p361j371t1t_2c1n1k2l323g271i323i3a3j32231p3j351o2n2n1f371t1t'


def create_mock_forvo_results(word, pref=None):
    with open('data/{}_forvo.txt'.format(word)) as json_file:
        data = json.load(json_file)

    return ForvoResults(data, pref)


def test_forvo_no_preferred():
    fr = create_mock_forvo_results('идти')

    assert fr.get_preferred() is None


def test_forvo_preferred():
    fr = create_mock_forvo_results('идти', 'luba1980')

    assert fr.get_preferred().username == 'luba1980'
    assert fr.get_preferred().path == 'https://apifree.forvo.com/audio/393c2a2f38272i3p251m1k34233a2m1i271k3d3h1i2d3d3a371n3h3a2k262d1m1o2726241f2l281o2n263n3l2o3q3h3i2a28223e3k1m2f1f2g3c22281j3d3b3f1b363h3f231h273i2n1f381m3p2f1i2e3o3f3c1l2p2h1t1t_383539262i3i3a262d2l3b1g35343g1m3a271l2c29211t1t'




