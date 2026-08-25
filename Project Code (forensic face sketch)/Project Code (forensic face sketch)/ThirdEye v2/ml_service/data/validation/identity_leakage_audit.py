class IdentityLeakageAudit:
    @staticmethod
    def audit_splits(train_pids, val_pids, test_pids):
        train_set = set(train_pids)
        val_set = set(val_pids)
        test_set = set(test_pids)

        train_val = list(train_set.intersection(val_set))
        train_test = list(train_set.intersection(test_set))
        val_test = list(val_set.intersection(test_set))

        passed = len(train_val) == 0 and len(train_test) == 0 and len(val_test) == 0
        return {
            "passed": passed,
            "train_val_overlap": train_val,
            "train_test_overlap": train_test,
            "val_test_overlap": val_test
        }
