class IdentityAudit:
    @staticmethod
    def audit_identities(records):
        pids = set()
        modalities = {}
        for r in records:
            pid = r.get("identity_id")
            pids.add(pid)
            mod = r.get("modality")
            modalities[mod] = modalities.get(mod, 0) + 1
        return {
            "unique_identities": len(pids),
            "total_records": len(records),
            "modality_breakdown": modalities
        }
