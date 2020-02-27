"""Unit tests for Context"""
from tests.utils import NormTestCase


class ContextTestCase(NormTestCase):
    def setUp(self):
        super().setUp()
        self.execute("""
        alarm
        :: (event: String, ip: String, time: Datetime, tally: Integer)
        := {
               import pandas as pd
               pd.read_parquet('./data/norm/packed_alarms.parquet')
           }
        """)

    def test_with_context(self):
        result = self.execute("with alarm, event like 'Unix' & tally > 3")
        self.assertTrue(result is not None)
        self.assertTrue(not result.positives.empty)

    def test_with_expression_context(self):
        result = self.execute("with alarm(tally < 1000?, event?)),"
                              "     event like 'Unix' & tally > 3")
        self.assertTrue(result is not None)
        self.assertTrue(not result.positives.empty)

    def test_foreach_context(self):
        result = self.execute("foreach event in alarm, "
                              "    tally.sum as total_tally & tally.mean")
        self.assertTrue(result is not None)
        self.assertTrue(not result.positives.empty)
        self.assertTrue('tally.mean' in result.lam)
        self.assertTrue('total_tally' in result.lam)

    def test_foreach_context_multiple_foreach(self):
        result = self.execute("foreach event, ip in alarm, "
                              "    tally.sum as total_tally & tally.mean")
        self.assertTrue(result is not None)
        self.assertTrue(not result.positives.empty)
        self.assertTrue('tally.mean' in result.lam)
        self.assertTrue('total_tally' in result.lam)

    def test_foreach_context_multiple_foreach_three_agg(self):
        result = self.execute("foreach event, ip in alarm, "
                              "      tally.sum as total_tally"
                              "    & tally.mean"
                              "    & tally.count")
        self.assertTrue(result is not None)
        self.assertTrue(not result.positives.empty)
        self.assertTrue('tally.mean' in result.lam)
        self.assertTrue('total_tally' in result.lam)
        self.assertTrue('tally.count' in result.lam)

    def test_foreach_context_multiple_foreach_mixed(self):
        result = self.execute("foreach event, ip in alarm,"
                              "       tally.sum as total_tally"
                              "     & tally.mean"
                              "     & ip like '1.17'")
        self.assertTrue(result is not None)
        self.assertTrue(not result.positives.empty)
        self.assertTrue('tally.mean' in result.lam)
        self.assertTrue('total_tally' in result.lam)
        self.assertTrue(all(result.positives['ip'].str.contains('1.17')))

    def test_foreach_context_multiple_foreach_conditional(self):
        result = self.execute("foreach event, ip in alarm,"
                              "    tally.sum > 100")
        self.assertTrue(result is not None)
        self.assertTrue(not result.positives.empty)
        self.assertTrue('tally.sum' in result.lam)
        self.assertTrue(all(result.positives['tally.sum'] > 100))

    def test_exists_context(self):
        result = self.execute("foreach event in alarm, "
                              "     exist ip in alarm, tally.sum > 100")
        self.assertTrue(result is not None)
        self.assertTrue(not result.positives.empty)
        self.assertTrue(all(result.positives['tally.sum'] > 100))
        self.assertTrue('ip' in result.lam)
        self.assertNoDuplicates(result.positives, 'event')

    def test_exists_context_combined_and(self):
        result = self.execute("foreach event in alarm, "
                              "     exist ip in alarm, "
                              "         tally.sum > 100 & tally.min < 10")
        self.assertTrue(result is not None)
        self.assertTrue(not result.positives.empty)
        self.assertTrue(all(result.positives['tally.sum'] > 100))
        self.assertTrue(all(result.positives['tally.min'] < 10))
        self.assertTrue('ip' in result.columns)
        self.assertNoDuplicates(result.positives, 'event')

    def test_exists_context_combined_and_three(self):
        result = self.execute("foreach event in alarm, "
                              "   exist ip in alarm, "
                              "       tally.sum > 100 & tally.min < 10 & tally.max > 1000")
        self.assertTrue(result is not None)
        self.assertTrue(not result.positives.empty)
        self.assertTrue(all(result.positives['tally.sum'] > 100))
        self.assertTrue(all(result.positives['tally.max'] > 1000))
        self.assertTrue(all(result.positives['tally.min'] < 10))
        self.assertTrue('ip' in result.lam)
        self.assertNoDuplicates(result.positives, 'event')

    def test_exists_context_combined_or(self):
        result = self.execute("foreach event in alarm, "
                              "     exist ip in alarm, "
                              "         tally.sum > 100 | tally.min < 10")
        self.assertTrue(result is not None)
        self.assertTrue(not result.positives.empty)
        self.assertFalse(all(result.positives['tally.sum'] > 100))
        self.assertTrue(all(result.positives[(result['tally.sum'] > 100) | (result['tally.min'] < 10)]))

    def test_forany_context(self):
        result = self.execute("exist ip in alarm, "
                              "     forall event in alarm, tally.sum > 100")
        self.assertTrue(result is not None)
        self.assertTrue(not result.positives.empty)

    def test_single_forany_context(self):
        result = self.execute("forall event in alarm, tally.sum > 0")
        self.assertTrue(result is not None)
        self.assertTrue(not result.positives.empty)

    def test_single_exist_context(self):
        result = self.execute("exist event in alarm, tally.sum > 1000")
        self.assertTrue(result is not None)
        self.assertTrue(not result.positives.empty)
        self.assertTrue(all(result.positives['tally.sum'] > 1000))

    def test_exists_context_non_agg(self):
        result = self.execute("foreach event in alarm, "
                              "     exist ip in alarm, tally > 100")
        self.assertTrue(result is not None)
        self.assertTrue(not result.positives.empty)
        self.assertTrue(all(result.positives['tally'] > 100))
        self.assertTrue('ip' in result.lam)
        self.assertNoDuplicates(result.positives, 'event')

    def test_exists_context_non_agg_multiple(self):
        result = self.execute("foreach event in alarm, "
                              "     exist ip in alarm, tally > 100 & tally < 10000")
        self.assertTrue(result is not None)
        self.assertTrue(not result.positives.empty)
        self.assertTrue(all(result.positives['tally'] > 100))
        self.assertTrue('ip' in result.lam)
        self.assertNoDuplicates(result.positives, 'event')

    def test_conditional_on_aggregation(self):
        result = self.execute("with alarm, tally > tally.mean & event")
        self.assertTrue(result is not None)
        self.assertTrue(not result.positives.empty)
        self.assertTrue(all(result.positives['tally'] > 2))

    def test_conditional_on_arithmetic(self):
        result = self.execute("with alarm, tally > tally.mean + 2 * tally.std & event")
        self.assertTrue(result is not None)
        self.assertTrue(not result.positives.empty)
        self.assertTrue(all(result.positives['tally'] > 2))

    def test_negated_existential_quantifier(self):
        result = self.execute("foreach event in alarm, "
                              "     not exist ip in alarm, tally < tally.min")
        self.assertTrue(result is not None)
        self.assertTrue(not result.positives.empty)
