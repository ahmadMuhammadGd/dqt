from dqt.definitions import DQSuite
from examples.spark.simple.tests import gender_must_be_f_or_m, not_null, greater_than

my_suite = (
    DQSuite(name="my_test_suite")
    .bind_test(definition=gender_must_be_f_or_m, columns=("gender"))
    .bind_test(definition=not_null, columns=("age"))
    .bind_test(definition=greater_than, columns=("age"), test_kwargs={"num": 24})
)
