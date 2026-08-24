class LeakageAudit:
    @staticmethod
    def verify_no_leakage(train_pids, val_pids, test_pids):
        train_set = set(train_pids)
        val_set = set(val_pids)
        test_set = set(test_pids)

        train_val_overlap = train_set.intersection(val_set)
        train_test_overlap = train_set.intersection(test_set)
        val_test_overlap = val_set.intersection(test_set)

        passed = len(train_val_overlap) == 0 and len(train_test_overlap) == 0 and len(val_test_overlap) == 0
        return {
            "passed": passed,
            "train_val_overlap": list(train_val_overlap),
            "train_test_overlap": list(train_test_overlap),
            "val_test_overlap": list(val_test_overlap)
        }
