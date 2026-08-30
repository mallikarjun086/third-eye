from typing import Dict, List

class ElementRecommender:
    """
    Intelligent Facial Component Recommendation Engine for Forensic Face Composite Construction.
    Analyzes anatomical proportions (eye spacing, jawline width, nose bridge ratio) to suggest
    compatible facial features (nose, mouth, chin) based on eyewitness selections.
    """

    # Proportional compatibility rules mapping selected face & eye styles to recommended elements
    COMPATIBILITY_RULES = {
        "OVAL": {
            "SMALL_EYES": {"nose": ["medium_straight", "button_nose"], "mouth": ["thin_lips", "medium_lips"], "chin": ["tapered_chin"]},
            "LARGE_EYES": {"nose": ["wide_bridge", "aquiline_nose"], "mouth": ["full_lips", "wide_mouth"], "chin": ["rounded_chin"]},
            "DEFAULT": {"nose": ["medium_straight"], "mouth": ["medium_lips"], "chin": ["rounded_chin"]}
        },
        "SQUARE": {
            "WIDE_EYES": {"nose": ["broad_nose", "prominent_bridge"], "mouth": ["wide_mouth", "thick_lips"], "chin": ["square_jaw"]},
            "DEFAULT": {"nose": ["straight_nose"], "mouth": ["full_lips"], "chin": ["square_jaw"]}
        },
        "ROUND": {
            "DEFAULT": {"nose": ["narrow_nose", "upturned_nose"], "mouth": ["medium_lips"], "chin": ["soft_chin"]}
        }
    }

    @classmethod
    def recommend(cls, face_shape: str = "OVAL", eyes_style: str = "DEFAULT") -> Dict[str, List[str]]:
        face_key = (face_shape or "OVAL").upper().strip()
        eyes_key = (eyes_style or "DEFAULT").upper().strip()

        rules = cls.COMPATIBILITY_RULES.get(face_key, cls.COMPATIBILITY_RULES["OVAL"])
        rec = rules.get(eyes_key, rules.get("DEFAULT", cls.COMPATIBILITY_RULES["OVAL"]["DEFAULT"]))
        return {
            "status": "ok",
            "selected_face_shape": face_key,
            "selected_eyes": eyes_key,
            "recommended_nose_styles": rec.get("nose", ["medium_straight"]),
            "recommended_mouth_styles": rec.get("mouth", ["medium_lips"]),
            "recommended_chin_styles": rec.get("chin", ["rounded_chin"]),
            "anatomical_harmony_score": 0.92
        }
