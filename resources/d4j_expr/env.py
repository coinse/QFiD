import os

class EvoD4jEnv:
    D4J_EXPR = os.environ['D4J_EXPR']
    D4J_EXPR_RESULTS = os.environ['D4J_EXPR_RESULTS']
    D4J_METADATA = os.environ['D4J_METADATA']
    EVOSUITE_CONFIG = os.environ['EVOSUITE_CONFIG']
    EVOSUITE_TEST = os.environ['EVOSUITE_TEST']
    EVOSUITE_REPORT = os.environ['EVOSUITE_REPORT']
    EVOSUITE_COVERAGE = os.environ['EVOSUITE_COVERAGE']
    EVOSUITE_ORACLE = os.environ['EVOSUITE_ORACLE']
    EVOSUITE_FL = os.path.join(D4J_EXPR_RESULTS, "localisation")
    TMP_ROOT = '/tmp'

    def __init__(self, project, version, ts_id):
        cls = self.__class__
        self.project = project
        self.version = version
        self.ts_id = str(ts_id)
        self.d4j_id = "{}-{}".format(self.project, self.version)
        self.buggy_tmp_dir = os.path.join(cls.TMP_ROOT, self.d4j_id + "b")
        self.fixed_tmp_dir = os.path.join(cls.TMP_ROOT, self.d4j_id + "f")
        self.metadata_dir = os.path.join(cls.D4J_METADATA, self.d4j_id)
        self.relevant_classes_file = os.path.join(
          self.metadata_dir, "classes.relevant")
        self.relevant_methods_dir = os.path.join(
          self.metadata_dir, "methods.relevant")
        self.failing_tests = os.path.join(
          self.metadata_dir, "tests.trigger")

        self.buggy_methods_file = os.path.join(cls.D4J_EXPR, "buggy_methods", self.d4j_id)
        self.saved_dir = os.path.join(cls.EVOSUITE_TEST, self.ts_id)
        self.extracted_dir = os.path.join(self.saved_dir, self.d4j_id)
        self.carved_dir = os.path.join(self.saved_dir, self.d4j_id + "-carved")
        self.single_dir = os.path.join(self.saved_dir, self.d4j_id + "-single")
        self.carved_suite_file = self.d4j_id + "-carved.tar.bz2"
        self.single_test_file = self.d4j_id + "-single.tar.bz2"

        self.coverage_dir = os.path.join(cls.EVOSUITE_COVERAGE, self.d4j_id)
        self.evosuite_coverage_dir = os.path.join(self.coverage_dir, self.ts_id)
        self.oracle_path = os.path.join(cls.EVOSUITE_ORACLE, "failing_tests.{}.{}".format(self.d4j_id, self.ts_id))
        self.broken_test_path = os.path.join(cls.EVOSUITE_ORACLE, "broken_tests.{}.{}".format(self.d4j_id, self.ts_id))

        if not os.path.exists(cls.EVOSUITE_FL):
          os.mkdir(cls.EVOSUITE_FL)
        self.localisation_dir = os.path.join(cls.EVOSUITE_FL, str(ts_id))
        if not os.path.exists(self.localisation_dir):
          os.mkdir(self.localisation_dir)
        self.summary_path = os.path.join(self.localisation_dir, "{}-summary.pkl".format(self.d4j_id))
        self.covmat_path = os.path.join(self.localisation_dir, "{}-covmat.pkl".format(self.d4j_id))
        self.oravec_path = os.path.join(self.localisation_dir, "{}-oracle.pkl".format(self.d4j_id))
        self.ranks_path = os.path.join(self.localisation_dir, "{}-ranks.pkl".format(self.d4j_id))
        self.tests_path = os.path.join(self.localisation_dir, "{}-tests.pkl".format(self.d4j_id))
