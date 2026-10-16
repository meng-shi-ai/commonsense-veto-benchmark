import copy
import unittest
import benchmark as b

class ScoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.cases,cls.gold=b.inputs()
    def perfect(self):
        return [{'id':c['id'],'prediction':{'decision':self.gold[c['id']]['decision'],
            'value':self.gold[c['id']]['value'],'evidence_ids':self.gold[c['id']]['evidence_sets'][0]}}
            for c in self.cases]
    def test_gold_and_missing(self):
        self.assertEqual(b.score(self.cases,self.gold,self.perfect())['strict_accuracy'],1)
        self.assertEqual(b.score(self.cases,self.gold,[])['strict_accuracy'],0)
        self.assertEqual(b.score(self.cases,self.gold,self.perfect()[:1])['strict_accuracy'],1/24)
    def test_bad_evidence_not_rewarded(self):
        rows=self.perfect();rows[0]['prediction']['evidence_ids']=['E1']
        report=b.score(self.cases,self.gold,rows)
        self.assertEqual(report['state_accuracy'],1)
        self.assertEqual(report['strict_accuracy'],23/24)
        rows[0]['prediction']['evidence_ids']=['E999']
        self.assertEqual(b.score(self.cases,self.gold,rows)['schema_valid_rate'],23/24)
    def test_pair_success_requires_both(self):
        rows=self.perfect();rows[0]['prediction']['value']='Riverton'
        self.assertEqual(b.score(self.cases,self.gold,rows)['pair_strict_accuracy'],11/12)
    def test_duplicate_and_unknown_ids_rejected(self):
        rows=self.perfect()
        with self.assertRaises(ValueError):b.score(self.cases,self.gold,rows+[rows[0]])
        with self.assertRaises(ValueError):b.score(self.cases,self.gold,[{'id':'C999'}])
    def test_null_and_types_fail_closed(self):
        for invalid in [None,[],True,{'decision':'clarify','value':'Lakeview','evidence_ids':[]},
                        {'decision':'answer','value':{'bad':'value'},'evidence_ids':[]}]:
            rows=self.perfect();rows[0]['prediction']=invalid
            self.assertEqual(b.score(self.cases,self.gold,rows)['schema_valid_rate'],23/24)
    def test_all_clarify_does_not_win(self):
        rows=[{'id':c['id'],'prediction':{'decision':'clarify','value':None,'evidence_ids':[]}} for c in self.cases]
        report=b.score(self.cases,self.gold,rows)
        self.assertEqual(report['state_accuracy'],6/24)
        self.assertEqual(report['unnecessary_clarification_rate'],1)
        self.assertEqual(report['strict_accuracy'],0)
    def test_prompt_excludes_labels(self):
        for c in self.cases:
            p=b.prompt(c)
            self.assertEqual(set(p),{'id','messages'})
            self.assertNotIn('annotation_note',p['messages'][1]['content'])
            self.assertNotIn('pair_id',p['messages'][1]['content'])
    def test_pairs_change_one_evidence_field(self):
        pairs={}
        for c in self.cases:pairs.setdefault(self.gold[c['id']]['pair_id'],[]).append(c)
        for cs in pairs.values():
            self.assertEqual(cs[0]['query'],cs[1]['query'])
            self.assertEqual(len(cs[0]['events']),len(cs[1]['events']))
            changes=sum(a[k]!=z[k] for a,z in zip(cs[0]['events'],cs[1]['events']) for k in a)
            self.assertEqual(changes,1)

if __name__=='__main__':unittest.main()
